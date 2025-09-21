# publicaciones_app/src/domain/use_cases/create_contrato_use_case.py
from src.modulos.alianzas.domain.models.contrato import Contrato
from src.modulos.alianzas.domain.ports.contrato_repository_port import ContratoRepositoryPort
from src.modulos.alianzas.domain.use_cases.base_use_case import BaseUseCase


class CreateContratoUseCase(BaseUseCase):
    """Use case for saving a contrato."""

    def __init__(self, contrato_repository: ContratoRepositoryPort):
        self.contrato_repository = contrato_repository

    async def execute(self, contrato: Contrato) -> Contrato:
        """Create a new contrato."""
        return await self.contrato_repository.create(contrato)