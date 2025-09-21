# partners-bff/src/presentation/api/routers/v1/partners_router.py
from fastapi import APIRouter

from src.application.services import PartnersService

router = APIRouter(prefix="/v1/partners")

@router.get("/", status_code=200)
async def list_partners():
    service = PartnersService()
    partners = service.list_partners()

    return partners
