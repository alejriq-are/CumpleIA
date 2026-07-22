"""Script de ingesta para la base de conocimiento RAG.

Uso:
    cd backend
    python -m scripts.ingest                        # todos los archivos de /docs/fuentes/
    python -m scripts.ingest --file ruta/ley.txt   # archivo específico
    python -m scripts.ingest --examples            # 3 fragmentos de prueba (sin Voyage AI)
    python -m scripts.ingest --examples --embed    # 3 fragmentos con embeddings reales

Formatos soportados: .txt  .md  .pdf
Fuentes reconocidas en el nombre del archivo: ley_21719, ley_19628, guia_ccs
(resto → "otro")
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Permite ejecutar desde cualquier directorio
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.db.models import KnowledgeChunk

settings = get_settings()

CHUNK_SIZE = 1500  # caracteres objetivo por fragmento
OVERLAP = 200  # solapamiento entre fragmentos
BATCH_SIZE = 20  # máx textos por llamada a Voyage AI (tope adicional al de caracteres)
MAX_BATCH_CHARS = 8000  # ~2000-2300 tokens estimados: margen bajo el techo de 10K TPM
EMBED_PACING_SECONDS = (
    21  # > 60s/3 RPM: espacia llamadas para no gatillar el rate limit
)

FUENTES_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "fuentes"

SOURCE_MAP = {
    "ley_21719": "ley_21719",
    "ley21719": "ley_21719",
    "21719": "ley_21719",
    "ley_19628": "ley_19628",
    "ley19628": "ley_19628",
    "19628": "ley_19628",
    "guia_ccs": "guia_ccs",
    "guia": "guia_ccs",
    "ccs": "guia_ccs",
    "plantilla": "plantilla",
}

# Fuentes con estructura de artículos: se chunkea por "Artículo N°.-" como
# límite estructural (nunca dos artículos en un chunk, nunca uno a la mitad).
FUENTES_CON_ARTICULOS = {"ley_19628", "ley_21719"}

# Chars/página por debajo de este umbral se reportan como posible PDF
# escaneado (imagen sin texto real, necesitaría OCR).
MIN_CHARS_PER_PAGE = 100

EXAMPLE_CHUNKS = [
    {
        "source": "ley_21719",
        "reference": "Artículo 1°",
        "content": (
            "Artículo 1°.- Objeto y ámbito de aplicación. "
            "La presente ley tiene por objeto la protección de las personas naturales "
            "en lo que respecta al tratamiento de sus datos personales. "
            "Sus disposiciones garantizan y protegen el derecho fundamental a la "
            "protección de datos personales y el libre flujo de la información, "
            "conforme al artículo 19 número 4 de la Constitución Política de la República."
        ),
    },
    {
        "source": "ley_21719",
        "reference": "Artículo 3° - Definiciones",
        "content": (
            "Artículo 3°.- Definiciones. Para los efectos de esta ley se entenderá por: "
            "a) Dato personal: toda información sobre una persona natural identificada "
            "o identificable. Se considera identificable toda persona cuya identidad "
            "pueda determinarse, directa o indirectamente, en particular mediante un "
            "identificador, como un nombre, número de identificación, datos de "
            "localización, identificador en línea, o uno o varios elementos propios "
            "de su identidad física, fisiológica, genética, psíquica, económica, "
            "cultural o social. "
            "b) Responsable de datos: persona natural o jurídica, de derecho público "
            "o privado, que decide sobre los fines y medios del tratamiento."
        ),
    },
    {
        "source": "ley_21719",
        "reference": "Artículo 16° - Bases de licitud",
        "content": (
            "Artículo 16°.- Bases de licitud del tratamiento. El tratamiento de datos "
            "personales será lícito cuando concurra alguna de las siguientes bases: "
            "a) Cuando el titular haya dado su consentimiento para uno o varios fines "
            "específicos. "
            "b) Cuando el tratamiento sea necesario para la ejecución de un contrato "
            "en el que el titular es parte, o para la aplicación de medidas "
            "precontractuales a solicitud del titular. "
            "c) Cuando el tratamiento sea necesario para el cumplimiento de una "
            "obligación legal aplicable al responsable. "
            "d) Cuando el tratamiento sea necesario para la satisfacción de intereses "
            "legítimos del responsable o de un tercero, siempre que no prevalezcan "
            "los intereses o los derechos y libertades fundamentales del titular."
        ),
    },
]


# ── Utilidades ────────────────────────────────────────────────────────────────


def detect_source(filename: str) -> str:
    name = Path(filename).stem.lower()
    for key, value in SOURCE_MAP.items():
        if key in name:
            return value
    return "otro"


def extract_reference(chunk: str) -> str | None:
    patterns = [
        r"(Art[íi]culo\s+\d+[°oa]?\.\s*-)",
        r"(Art[íi]culo\s+\d+[°oa]?)",
        r"(Art\.\s+\d+[°oa]?)",
        r"(Secci[óo]n\s+\d+[\.\d]*)",
        r"(Cap[íi]tulo\s+[IVXLCDM]+)",
        r"(Párrafo\s+\d+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, chunk[:300], re.IGNORECASE)
        if m:
            return m.group(1).strip().rstrip("-").strip()
    return None


def _slice_on_word_boundary(text: str, start: int, size: int) -> int:
    """Devuelve el índice de fin de corte, retrocedido al último espacio.

    Evita partir una palabra a la mitad cuando hay que cortar por caracteres.
    Si no hay un espacio razonablemente cerca, corta igual en el límite duro
    (mejor eso que un fragmento minúsculo).
    """
    end = min(start + size, len(text))
    if end >= len(text):
        return end
    espacio = text.rfind(" ", start, end)
    if espacio > start + size // 2:
        return espacio
    return end


def chunk_text(text: str) -> list[str]:
    """Divide el texto en fragmentos con solapamiento, respetando párrafos.

    Cuando un párrafo excede CHUNK_SIZE, el corte por caracteres retrocede al
    último espacio (ver `_slice_on_word_boundary`) para no partir palabras.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= CHUNK_SIZE:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > CHUNK_SIZE:
                start = 0
                while start < len(para):
                    end = _slice_on_word_boundary(para, start, CHUNK_SIZE)
                    chunks.append(para[start:end].strip())
                    if end >= len(para):
                        break
                    start = max(end - OVERLAP, start + 1)
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return [c for c in chunks if len(c) > 50]


def reflow_paragraphs(text: str) -> str:
    """Reconstruye párrafos a partir de texto extraído línea por línea.

    `pypdf.extract_text()` devuelve una línea por cada línea visual del PDF
    (con `\\n`), no párrafos reales: las "líneas en blanco" entre párrafos
    suelen tener solo espacios, no una cadena vacía, así que un simple
    `split("\\n\\n")` nunca las detecta. Aquí se une cada línea envuelta
    (wrap) con espacio dentro de un párrafo, y se corta el párrafo solo en
    líneas que quedan vacías tras `strip()`.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    for line in text.split("\n"):
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


# Encabezado de artículo: "Artículo" + hasta 40 caracteres sin punto + ".-".
# Genérico a propósito para cubrir "Artículo 2°.-", "Artículo 14 ter.-",
# "Artículo 30 quáter.-", "Artículo transitorio.-", "Artículo primero.-",
# etc. sin enumerar cada sufijo/ordinal a mano. Una referencia inline como
# "conforme al artículo 19 número 4" no matchea: no tiene ".-" a continuación.
ARTICULO_HEADING = re.compile(r"(Art[íi]culo\s+[^.\n]{1,40}?\.\s*-)", re.IGNORECASE)


def chunk_by_articulo(text: str) -> list[str]:
    """Chunkea usando "Artículo N°.-" como límite estructural fuerte.

    Un chunk nunca contiene contenido de dos artículos ni corta uno a la
    mitad: cada artículo (encabezado + cuerpo completo, hasta el siguiente
    encabezado) es un único fragmento, sin importar que supere CHUNK_SIZE.
    Preferible a partir por límite de caracteres cuando el documento tiene
    una estructura legal clara, donde cortar a mitad de una definición es
    peor que un fragmento largo.

    Se reconstruyen párrafos ANTES de buscar encabezados (no por segmento
    después): un encabezado como "Artículo 1° transitorio.-" puede venir
    partido por un salto de línea de PDF justo en medio ("Artículo 1°\\n
    transitorio.-"), y `ARTICULO_HEADING` no cruza saltos de línea — sin
    reflow previo, ese encabezado no se detecta y su contenido queda
    mezclado con el artículo anterior.
    """
    text = reflow_paragraphs(text)
    matches = list(ARTICULO_HEADING.finditer(text))
    if not matches:
        # Sin encabezados detectables (no debería pasar en ley_19628/ley_21719):
        # no perder el documento, usar el chunker genérico como red de seguridad.
        return chunk_text(text)

    segments: list[str] = []

    preambulo = text[: matches[0].start()].strip()
    if len(preambulo) > 50:
        segments.append(preambulo)

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segmento = text[start:end].strip()
        if segmento:
            segments.append(segmento)

    return [s for s in segments if len(s) > 50]


def extract_pdf_text(filepath: Path) -> str:
    """Extrae el texto de un PDF, avisando si alguna página parece escaneada.

    Un PDF con texto seleccionable (born-digital) entrega varios cientos de
    caracteres por página; una página escaneada como imagen, sin OCR previo,
    entrega texto vacío o casi vacío. No corrige eso (requeriría un motor de
    OCR aparte) — solo lo reporta para que quede claro qué archivo/página
    necesita revisión manual.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(filepath))
    paginas_con_poco_texto: list[int] = []
    textos: list[str] = []

    for i, page in enumerate(reader.pages, start=1):
        texto_pagina = page.extract_text() or ""
        textos.append(texto_pagina)
        if len(texto_pagina.strip()) < MIN_CHARS_PER_PAGE:
            paginas_con_poco_texto.append(i)

    if paginas_con_poco_texto:
        print(
            f"  ⚠ {filepath.name}: {len(paginas_con_poco_texto)} página(s) con "
            f"< {MIN_CHARS_PER_PAGE} caracteres extraídos (posible escaneo sin "
            f"OCR): {paginas_con_poco_texto}"
        )

    return "\n\n".join(textos)


def read_source_text(filepath: Path) -> str:
    if filepath.suffix.lower() == ".pdf":
        return extract_pdf_text(filepath)
    return filepath.read_text(encoding="utf-8", errors="replace")


def chunk_source(content: str, filepath: Path, source: str) -> list[str]:
    """Elige la estrategia de chunking según la fuente.

    ley_19628/ley_21719: por artículo (ver `chunk_by_articulo`), porque
    partir una ley a mitad de un artículo es peor que tener chunks
    desparejos en tamaño. El resto (guia_ccs, plantilla, otro): párrafos
    reconstruidos (si viene de PDF) + chunker genérico por tamaño.
    """
    if source in FUENTES_CON_ARTICULOS:
        return chunk_by_articulo(content)
    if filepath.suffix.lower() == ".pdf":
        content = reflow_paragraphs(content)
    return chunk_text(content)


RATE_LIMIT_RETRY_SECONDS = 65  # > 60s: alcanza para liberar la ventana de RPM
RATE_LIMIT_MAX_RETRIES = 5


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.voyage_api_key:
        raise RuntimeError("VOYAGE_API_KEY no configurada en el .env")
    import voyageai

    client = voyageai.AsyncClient(api_key=settings.voyage_api_key)

    for intento in range(1, RATE_LIMIT_MAX_RETRIES + 1):
        try:
            result = await client.embed(
                texts=texts, model="voyage-3", input_type="document"
            )
            return result.embeddings
        except voyageai.error.RateLimitError:
            if intento == RATE_LIMIT_MAX_RETRIES:
                raise
            print(
                f"  Rate limit de Voyage AI (cuenta sin método de pago: 3 RPM / "
                f"10K TPM). Reintento {intento}/{RATE_LIMIT_MAX_RETRIES} en "
                f"{RATE_LIMIT_RETRY_SECONDS}s…"
            )
            await asyncio.sleep(RATE_LIMIT_RETRY_SECONDS)

    raise RuntimeError("No debería llegar aquí")  # pragma: no cover


# ── Lógica de ingesta ─────────────────────────────────────────────────────────


def batch_chunks(
    chunks: list[str],
    max_batch_size: int = BATCH_SIZE,
    max_chars: int = MAX_BATCH_CHARS,
) -> list[list[str]]:
    """Agrupa chunks en lotes acotados por cantidad Y por caracteres totales.

    El chunker por artículo produce fragmentos de tamaño muy dispar (desde
    ~150 hasta ~8500 caracteres); un lote de tamaño fijo (p. ej. 20 textos)
    puede superar el techo de 10K TPM de Voyage AI si le tocan varios
    fragmentos grandes, y ni el reintento con backoff lo salva (el mismo
    lote sobredimensionado vuelve a fallar). Acotar también por caracteres
    evita ese caso.
    """
    batches: list[list[str]] = []
    current: list[str] = []
    current_chars = 0

    for chunk in chunks:
        if current and (
            len(current) >= max_batch_size or current_chars + len(chunk) > max_chars
        ):
            batches.append(current)
            current = []
            current_chars = 0
        current.append(chunk)
        current_chars += len(chunk)

    if current:
        batches.append(current)

    return batches


async def ingest_file(
    filepath: Path, source: str, db: AsyncSession, with_embeddings: bool
) -> int:
    print(f"  Leyendo: {filepath.name}")
    content = read_source_text(filepath)
    chunks = chunk_source(content, filepath, source)
    print(f"  Fragmentos: {len(chunks)}")

    batches = batch_chunks(chunks)
    inserted = 0
    for i, batch in enumerate(batches):
        embeddings: list[list[float] | None]

        if with_embeddings:
            if i > 0:
                await asyncio.sleep(EMBED_PACING_SECONDS)
            print(
                f"  Embeddings lote {i + 1}/{len(batches)} "
                f"({len(batch)} fragmentos, {sum(len(c) for c in batch)} chars)…"
            )
            embeddings = await embed_texts(batch)
        else:
            embeddings = [None] * len(batch)

        for text_str, emb in zip(batch, embeddings, strict=True):
            db.add(
                KnowledgeChunk(
                    source=source,
                    reference=extract_reference(text_str),
                    content=text_str,
                    embedding=emb,
                )
            )
        await db.flush()
        inserted += len(batch)

    await db.commit()
    return inserted


async def ingest_examples(db: AsyncSession, with_embeddings: bool) -> int:
    if with_embeddings:
        print(f"  Generando embeddings para {len(EXAMPLE_CHUNKS)} fragmentos…")
        embs = await embed_texts([e["content"] for e in EXAMPLE_CHUNKS])
    else:
        embs = [None] * len(EXAMPLE_CHUNKS)
        print("  Insertando sin embeddings (usa --embed para generarlos con Voyage AI)")

    inserted = 0
    for ex, emb in zip(EXAMPLE_CHUNKS, embs, strict=True):
        existing = await db.execute(
            select(KnowledgeChunk).where(
                KnowledgeChunk.source == ex["source"],
                KnowledgeChunk.reference == ex["reference"],
            )
        )
        if existing.scalar_one_or_none():
            print(f"    Ya existe: {ex['reference']} — omitido")
            continue

        db.add(
            KnowledgeChunk(
                source=ex["source"],
                reference=ex["reference"],
                content=ex["content"],
                embedding=emb,
            )
        )
        inserted += 1

    await db.commit()
    print(f"  Insertados: {inserted} fragmentos de ejemplo")
    return inserted


# ── Punto de entrada ──────────────────────────────────────────────────────────


async def main(args: argparse.Namespace) -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as db:
        if args.examples:
            print("Modo ejemplo:")
            await ingest_examples(db, with_embeddings=args.embed)
            await engine.dispose()
            return

        files: list[tuple[Path, str]] = []
        if args.file:
            fp = Path(args.file)
            files.append((fp, args.source or detect_source(fp.name)))
        else:
            supported = ("*.txt", "*.md", "*.pdf")
            if not FUENTES_DIR.exists() or not any(
                list(FUENTES_DIR.glob(ext)) for ext in supported
            ):
                print(f"No hay archivos en {FUENTES_DIR}")
                print(
                    "Deposita archivos .txt, .md o .pdf ahí, "
                    "o usa --examples para datos de prueba."
                )
                await engine.dispose()
                sys.exit(0)
            for ext in supported:
                for fp in sorted(FUENTES_DIR.glob(ext)):
                    files.append((fp, detect_source(fp.name)))

        total = 0
        for fp, source in files:
            print(f"\nIngesta: {fp.name}  →  fuente={source}")
            n = await ingest_file(fp, source, db, with_embeddings=not args.no_embed)
            total += n
            print(f"  Total insertados: {n}")

        print(f"\nIngesta completa. Fragmentos totales: {total}")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingesta de documentos en la base de conocimiento RAG de CumpleIA"
    )
    parser.add_argument("--file", help="Archivo específico a ingestar")
    parser.add_argument(
        "--source",
        choices=["ley_21719", "ley_19628", "guia_ccs", "plantilla", "otro"],
        help="Fuente del documento (se detecta automáticamente si se omite)",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Insertar 3 fragmentos de ejemplo de la Ley 21.719",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Generar embeddings reales con Voyage AI (requiere VOYAGE_API_KEY)",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Insertar solo el texto, sin embeddings (para pruebas sin Voyage AI)",
    )
    asyncio.run(main(parser.parse_args()))
