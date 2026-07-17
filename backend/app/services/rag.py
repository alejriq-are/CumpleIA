from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

settings = get_settings()


async def _get_query_embedding(query: str) -> list[float]:
    if not settings.voyage_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VOYAGE_API_KEY no configurada. Agrega la clave en el .env.",
        )
    import voyageai

    client = voyageai.AsyncClient(api_key=settings.voyage_api_key)
    result = await client.embed(
        texts=[query],
        model="voyage-3",
        input_type="query",
    )
    return result.embeddings[0]


async def search_chunks(
    query: str,
    db: AsyncSession,
    top_k: int = 5,
) -> list[dict]:
    """Busca los fragmentos más relevantes por similitud coseno."""
    embedding = await _get_query_embedding(query)
    # Formatear como literal de vector para pgvector
    embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

    rows = await db.execute(
        text("""
            SELECT
                id::text,
                source,
                reference,
                content,
                1 - (embedding <=> :emb::vector) AS similarity
            FROM knowledge_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :emb::vector
            LIMIT :limit
        """),
        {"emb": embedding_str, "limit": top_k},
    )

    return [dict(row._mapping) for row in rows.fetchall()]
