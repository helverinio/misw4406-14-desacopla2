"""Repositorios de dominio del módulo de sagas."""
from .saga_log_repository import ISagaLogRepository, ISagaLogRepositorySync

__all__ = ['ISagaLogRepository', 'ISagaLogRepositorySync']