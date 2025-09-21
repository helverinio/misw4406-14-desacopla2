# publicaciones_app/src/domain/ports/publication_repository_port.py

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.modulos.alianzas.domain.models.contrato import Contrato

class ContratoRepositoryPort(ABC):
    """Contrato repository interface."""

    @abstractmethod
    async def create(self, contrato: Contrato) -> Contrato:
        """Create a new contrato."""
        pass
