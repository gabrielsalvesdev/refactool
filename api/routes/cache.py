from fastapi import APIRouter
from api.src.tasks import redis_cache

router = APIRouter()

@router.delete("/{project_hash}")
async def invalidate_cache(project_hash: str):
    # Aqui, o project_hash já deve vir no formato 'analysis:<hash>'
    deleted = redis_cache.delete(project_hash)
    return {"status": "deleted" if deleted else "not_found"} 