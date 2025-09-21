"""Entidades de dominio del módulo de sagas."""
from .saga_log import SagaLog, EstadoEvento

__all__ = ['SagaLog', 'EstadoEvento']