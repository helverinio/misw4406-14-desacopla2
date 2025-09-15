# publicaciones_app/src/infra/repositories.py
from datetime import datetime, timezone
from typing import Iterable, Sequence, Optional, List
from sqlalchemy import and_, func, select, delete
from sqlalchemy.exc import IntegrityError
from src.infrastructure.models import ContratoRow
from src.domain.models.contrato import Contrato
from src.domain.ports.contrato_repository_port import ContratoRepositoryPort
from src.infrastructure.db import SessionFactory
from src.infrastructure.mappers import _domain_to_row, _row_to_domain
from uuid import UUID

class PostgresContratoRepository(ContratoRepositoryPort):
    """Adaptador PostgreSQL (async) usando SQLAlchemy 2.0."""

    def __init__(self, session_factory=SessionFactory):
        self._session_factory = session_factory

    async def create(self, contrato: Contrato) -> Contrato:
        print(f"Creating contrato in DB: {contrato}")
        async with self._session_factory() as session:
            async with session.begin():
                row = _domain_to_row(contrato)
                session.add(row)
            await session.commit()
            await session.refresh(row)
        return _row_to_domain(row)
