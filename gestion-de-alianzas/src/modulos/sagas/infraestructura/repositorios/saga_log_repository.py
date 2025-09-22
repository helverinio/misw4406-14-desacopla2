"""Implementación concreta del repositorio de saga log usando SQLAlchemy async."""
from typing import List, Optional
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from src.seedwork.dominio.repositorio import Repositorio

from ...config.db import get_saga_session

from ..dto import SagaLog as SagaLogDTO, EstadoEventoDTO
from ...dominio.entidades.saga_log import SagaLog, EstadoEvento
from ...dominio.repositorios.saga_log_repository import ISagaLogRepository


class SagaLogRepository(Repositorio):
    """Implementación del repositorio de saga log usando SQLAlchemy async."""
    def __init__(self, session=None):
        self._session = session
        self._owns_session = session is None 

    @property
    def session(self):
        """Obtiene la sesión de BD de forma lazy"""
        if self._session is None:
            self._session = get_saga_session()
        return self._session
    
    def agregar(self, saga_log: SagaLog) -> None:
        try:
            """Agrega un nuevo log de saga."""
            saga_log_dto = self._convertir_entidad_a_dto(saga_log)
            self.session.add(saga_log_dto)
            self.session.commit()
        except Exception as e:
            self.session.rollback()   # ← obligatorio
            raise

    def obtener_por_id(self, log_id: str) -> Optional[SagaLog]:
        """Obtiene un log por su ID."""
        stmt = select(SagaLogDTO).where(SagaLogDTO.id == log_id)
        result = self.session.execute(stmt)
        saga_log_dto = result.scalar_one_or_none()
        
        if saga_log_dto:
            return self._convertir_dto_a_entidad(saga_log_dto)
        return None
    
    def _convertir_entidad_a_dto(self, entidad: SagaLog) -> SagaLogDTO:
        """Convierte una entidad de dominio a DTO."""
        return SagaLogDTO(
            id=entidad.id,
            saga_id=entidad.saga_id,
            tipo_evento=entidad.tipo_evento,
            evento_data=entidad.evento_data,
            estado=self._convertir_estado_a_dto(entidad.estado),
            timestamp=entidad.timestamp,
            mensaje_error=entidad.mensaje_error,
            intentos=entidad.intentos,
            procesado_en=entidad.procesado_en
        )
    
    def _convertir_estado_a_dto(self, estado: EstadoEvento) -> EstadoEventoDTO:
        """Convierte estado de dominio a DTO."""
        mapping = {
            EstadoEvento.RECIBIDO: EstadoEventoDTO.RECIBIDO,
            EstadoEvento.PROCESANDO: EstadoEventoDTO.PROCESANDO,
            EstadoEvento.PROCESADO: EstadoEventoDTO.PROCESADO,
            EstadoEvento.ERROR: EstadoEventoDTO.ERROR,
        }
        return mapping[estado]