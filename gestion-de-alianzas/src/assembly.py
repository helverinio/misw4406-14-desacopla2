# publicaciones_app/src/assembly.py

from src.modulos.alianzas.domain.use_cases.create_contrato_use_case import CreateContratoUseCase
from src.modulos.alianzas.domain.use_cases.base_use_case import BaseUseCase
from src.modulos.alianzas.adapters.postgres.contrato_postgres_adapter import PostgresContratoRepository

repository: PostgresContratoRepository = PostgresContratoRepository()

def build_create_contrato_use_case() -> BaseUseCase:
    """Get create contrato use case."""
    return CreateContratoUseCase(repository)
