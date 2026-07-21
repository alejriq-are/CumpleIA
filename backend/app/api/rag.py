from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentProfile
from app.db.session import get_db
from app.services.rag import search_chunks

router = APIRouter(prefix="/rag", tags=["RAG"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class ChunkResult(BaseModel):
    id: str
    source: str
    reference: str | None
    content: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]


@router.post("/search", response_model=SearchResponse)
async def rag_search(
    body: SearchRequest,
    current_profile: CurrentProfile,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Endpoint de prueba: busca fragmentos relevantes en la base de conocimiento.

    Requiere autenticación. La base de conocimiento (`knowledge_chunks`) es
    GLOBAL y compartida (Ley 21.719 / guía CCS): no contiene datos por tenant,
    por lo que no se filtra por organización. Ver hallazgo 4.4 del informe.

    Requiere VOYAGE_API_KEY configurada y al menos un chunk con embedding en la BD.
    """
    results = await search_chunks(body.query, db, top_k=body.top_k)
    return SearchResponse(query=body.query, results=results)
