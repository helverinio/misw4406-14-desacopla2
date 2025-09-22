# publicaciones_app/src/infra/repositories.py
from datetime import datetime, timezone
from typing import Iterable, Sequence, Optional, List
from sqlalchemy import and_, func, select, delete
from sqlalchemy.exc import IntegrityError
from src.modulos.alianzas.infrastructure.models import ContratoRow
from src.modulos.alianzas.domain.models.contrato import Contrato
from src.modulos.alianzas.domain.ports.contrato_repository_port import ContratoRepositoryPort
from src.modulos.alianzas.infrastructure.db import SessionFactory
from src.modulos.alianzas.infrastructure.mappers import _domain_to_row, _row_to_domain
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

    async def get_by_id(self, contrato_id: str) -> Optional[Contrato]:
        """Get contrato by ID."""
        async with self._session_factory() as session:
            try:
                stmt = select(ContratoRow).where(ContratoRow.id == UUID(contrato_id))
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                return _row_to_domain(row) if row else None
            except ValueError:
                return None

    async def get_by_partner_id(self, partner_id: str) -> Optional[Contrato]:
        """Get contrato by partner ID."""
        async with self._session_factory() as session:
            try:
                stmt = select(ContratoRow).where(ContratoRow.partner_id == UUID(partner_id))
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                return _row_to_domain(row) if row else None
            except ValueError:
                return None

    async def update(self, contrato: Contrato) -> Contrato:
        """Update an existing contrato."""
        async with self._session_factory() as session:
            async with session.begin():
                # Set update timestamp
                contrato.fecha_actualizacion = datetime.now(timezone.utc)
                
                # Convert to row and merge
                row = _domain_to_row(contrato)
                merged_row = await session.merge(row)
                
            await session.commit()
            await session.refresh(merged_row)
            return _row_to_domain(merged_row)

    async def delete(self, contrato_id: str) -> bool:
        """Delete contrato by ID."""
        async with self._session_factory() as session:
            async with session.begin():
                try:
                    stmt = delete(ContratoRow).where(ContratoRow.id == UUID(contrato_id))
                    result = await session.execute(stmt)
                    await session.commit()
                    return result.rowcount > 0
                except ValueError:
                    return False

    async def list_all(self) -> List[Contrato]:
        """List all contratos."""
        async with self._session_factory() as session:
            stmt = select(ContratoRow)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [_row_to_domain(row) for row in rows]
