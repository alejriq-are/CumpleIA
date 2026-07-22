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
BATCH_SIZE = 20  # máx textos por llamada a Voyage AI
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


def chunk_text(text: str) -> list[str]:
    """Divide el texto en fragmentos con solapamiento, respetando párrafos."""
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
                # Párrafo muy largo: cortar por caracteres
                start = 0
                while start < len(para):
                    end = min(start + CHUNK_SIZE, len(para))
                    chunks.append(para[start:end].strip())
                    if end == len(para):
                        break
                    start = end - OVERLAP
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return [c for c in chunks if len(c) > 50]


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


async def ingest_file(
    filepath: Path, source: str, db: AsyncSession, with_embeddings: bool
) -> int:
    print(f"  Leyendo: {filepath.name}")
    content = read_source_text(filepath)
    chunks = chunk_text(content)
    print(f"  Fragmentos: {len(chunks)}")

    inserted = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        embeddings: list[list[float] | None]

        if with_embeddings:
            if i > 0:
                await asyncio.sleep(EMBED_PACING_SECONDS)
            print(f"  Embeddings {i + 1}–{i + len(batch)}…")
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
