"""Modelos de base de datos para el módulo de sagas."""
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from modulos.alianzas.infrastructure.db import Base
import uuid
from datetime import datetime
from enum import Enum as PyEnum


class EstadoEventoDTO(PyEnum):
    """Estados posibles para el procesamiento de eventos en la saga."""
    RECIBIDO = "RECIBIDO"
    PROCESANDO = "PROCESANDO"
    PROCESADO = "PROCESADO"
    ERROR = "ERROR"


class SagaLog(Base):
    """Modelo de base de datos para el log de eventos de saga."""
    
    __tablename__ = "saga_logs"
    __table_args__ = (
        Index('idx_saga_logs_saga_id_timestamp', 'saga_id', 'timestamp'),
        Index('idx_saga_logs_estado', 'estado'),
        Index('idx_saga_logs_tipo_evento', 'tipo_evento'),
        {'extend_existing': True}  # Permitir redefinir la tabla si ya existe
    )
    
    # Atributos de identidad
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    saga_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Información del evento
    tipo_evento = Column(String(200), nullable=False)
    evento_data = Column(Text, nullable=False)  # JSON serializado del evento
    
    # Información de procesamiento
    estado = Column(Enum(EstadoEventoDTO), nullable=False, default=EstadoEventoDTO.RECIBIDO)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Información adicional
    mensaje_error = Column(Text, nullable=True)
    intentos = Column(Integer, nullable=False, default=1)
    procesado_en = Column(DateTime, nullable=True)
    
    # Timestamps de auditoría
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)