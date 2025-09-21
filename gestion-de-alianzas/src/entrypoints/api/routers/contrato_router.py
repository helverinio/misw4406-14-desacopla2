# publicaciones_app/src/entrypoints/api/routers/publication_router.py
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from src.assembly import build_create_contrato_use_case
from src.modulos.alianzas.domain.models.contrato import Contrato
from src.modulos.alianzas.domain.use_cases.base_use_case import BaseUseCase
from uuid import UUID

router = APIRouter(prefix="/posts")


@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


@router.post("/", response_model=Contrato, response_model_include={"id", "user_id", "created_at"}, status_code=201)
async def create_contrato(contrato: Contrato, use_case: BaseUseCase = Depends(build_create_contrato_use_case)):
    """Create a new contrato."""
    return await use_case.execute(contrato)
