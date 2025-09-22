# contrato_repository_port.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.modulos.alianzas.domain.models.contrato import Contrato

class ContratoRepositoryPort(ABC):
    """Contrato repository interface."""

    @abstractmethod
    async def create(self, contrato: Contrato) -> Contrato:
        """Create a new contrato."""
        pass

    @abstractmethod
    async def get_by_id(self, contrato_id: str) -> Optional[Contrato]:
        """Get contrato by ID."""
        pass

    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> Optional[Contrato]:
        """Get contrato by partner ID."""
        pass

    @abstractmethod
    async def update(self, contrato: Contrato) -> Contrato:
        """Update an existing contrato."""
        pass

    @abstractmethod
    async def delete(self, contrato_id: str) -> bool:
        """Delete contrato by ID."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Contrato]:
        """List all contratos."""
        pass
