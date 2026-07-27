from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.providers.embeddings import get_embedding_client

settings = get_settings()


async def _get_query_embedding(query: str) -> list[float]:
    try:
        client = get_embedding_client(settings)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    embeddings = await client.embed(texts=[query], input_type="query")
    return embeddings[0]


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
        text(
            """
            SELECT
                id::text,
                source,
                reference,
                content,
                1 - (embedding <=> CAST(:emb AS vector)) AS similarity
            FROM knowledge_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :limit
        """
        ),
        {"emb": embedding_str, "limit": top_k},
    )

    return [dict(row._mapping) for row in rows.fetchall()]
