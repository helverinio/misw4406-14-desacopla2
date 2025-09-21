"""Implementación concreta del repositorio de saga log usando SQLAlchemy async."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from ..dto import SagaLog as SagaLogDTO, EstadoEventoDTO
from ...dominio.entidades.saga_log import SagaLog, EstadoEvento
from ...dominio.repositorios.saga_log_repository import ISagaLogRepository


class SagaLogRepository(ISagaLogRepository):
    """Implementación del repositorio de saga log usando SQLAlchemy async."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def agregar(self, saga_log: SagaLog) -> None:
        """Agrega un nuevo log de saga."""
        saga_log_dto = self._convertir_entidad_a_dto(saga_log)
        self.session.add(saga_log_dto)
        await self.session.commit()
    
    async def obtener_por_id(self, log_id: str) -> Optional[SagaLog]:
        """Obtiene un log por su ID."""
        stmt = select(SagaLogDTO).where(SagaLogDTO.id == log_id)
        result = await self.session.execute(stmt)
        saga_log_dto = result.scalar_one_or_none()
        
        if saga_log_dto:
            return self._convertir_dto_a_entidad(saga_log_dto)
        return None
    
    async def obtener_por_saga_id(self, saga_id: str) -> List[SagaLog]:
        """Obtiene todos los logs de una saga específica."""
        stmt = select(SagaLogDTO).where(
            SagaLogDTO.saga_id == saga_id
        ).order_by(SagaLogDTO.timestamp.asc())
        
        result = await self.session.execute(stmt)
        saga_logs_dto = result.scalars().all()
        
        return [self._convertir_dto_a_entidad(dto) for dto in saga_logs_dto]
    
    async def obtener_por_estado(self, estado: EstadoEvento) -> List[SagaLog]:
        """Obtiene logs por estado específico."""
        estado_dto = self._convertir_estado_a_dto(estado)
        stmt = select(SagaLogDTO).where(
            SagaLogDTO.estado == estado_dto
        ).order_by(SagaLogDTO.timestamp.desc())
        
        result = await self.session.execute(stmt)
        saga_logs_dto = result.scalars().all()
        
        return [self._convertir_dto_a_entidad(dto) for dto in saga_logs_dto]
    
    async def actualizar(self, saga_log: SagaLog) -> None:
        """Actualiza un log existente."""
        stmt = select(SagaLogDTO).where(SagaLogDTO.id == saga_log.id)
        result = await self.session.execute(stmt)
        saga_log_dto = result.scalar_one_or_none()
        
        if saga_log_dto:
            saga_log_dto.estado = self._convertir_estado_a_dto(saga_log.estado)
            saga_log_dto.mensaje_error = saga_log.mensaje_error
            saga_log_dto.intentos = saga_log.intentos
            saga_log_dto.procesado_en = saga_log.procesado_en
            await self.session.commit()
    
    async def obtener_eventos_pendientes(self, max_intentos: int = 3) -> List[SagaLog]:
        """Obtiene eventos que pueden ser reprocesados."""
        stmt = select(SagaLogDTO).where(
            and_(
                or_(
                    SagaLogDTO.estado == EstadoEventoDTO.RECIBIDO,
                    SagaLogDTO.estado == EstadoEventoDTO.ERROR
                ),
                SagaLogDTO.intentos <= max_intentos
            )
        ).order_by(SagaLogDTO.timestamp.asc())
        
        result = await self.session.execute(stmt)
        saga_logs_dto = result.scalars().all()
        
        return [self._convertir_dto_a_entidad(dto) for dto in saga_logs_dto]
    
    async def obtener_historial_saga(self, saga_id: str, limit: int = 100) -> List[SagaLog]:
        """Obtiene el historial completo de una saga ordenado por timestamp."""
        stmt = select(SagaLogDTO).where(
            SagaLogDTO.saga_id == saga_id
        ).order_by(SagaLogDTO.timestamp.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        saga_logs_dto = result.scalars().all()
        
        return [self._convertir_dto_a_entidad(dto) for dto in saga_logs_dto]
    
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
    
    def _convertir_dto_a_entidad(self, dto: SagaLogDTO) -> SagaLog:
        """Convierte un DTO a entidad de dominio."""
        return SagaLog(
            id=str(dto.id),
            saga_id=str(dto.saga_id),
            tipo_evento=dto.tipo_evento,
            evento_data=dto.evento_data,
            estado=self._convertir_estado_dto_a_dominio(dto.estado),
            timestamp=dto.timestamp,
            mensaje_error=dto.mensaje_error,
            intentos=dto.intentos,
            procesado_en=dto.procesado_en
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
    
    def _convertir_estado_dto_a_dominio(self, estado_dto: EstadoEventoDTO) -> EstadoEvento:
        """Convierte estado DTO a dominio."""
        mapping = {
            EstadoEventoDTO.RECIBIDO: EstadoEvento.RECIBIDO,
            EstadoEventoDTO.PROCESANDO: EstadoEvento.PROCESANDO,
            EstadoEventoDTO.PROCESADO: EstadoEvento.PROCESADO,
            EstadoEventoDTO.ERROR: EstadoEvento.ERROR,
        }
        return mapping[estado_dto]


# Versión sincronizada para compatibilidad hacia atrás si es necesaria
class SagaLogRepositorySync(ISagaLogRepository):
    """Wrapper sincronizado del repositorio async para casos donde se necesite compatibilidad."""
    
    def __init__(self, async_repo: SagaLogRepository):
        self.async_repo = async_repo
    
    def agregar(self, saga_log: SagaLog) -> None:
        """Agrega un nuevo log de saga (versión sync)."""
        import asyncio
        asyncio.create_task(self.async_repo.agregar(saga_log))
    
    def obtener_por_id(self, log_id: str) -> Optional[SagaLog]:
        """Obtiene un log por su ID (versión sync)."""
        import asyncio
        return asyncio.run(self.async_repo.obtener_por_id(log_id))
    
    def obtener_por_saga_id(self, saga_id: str) -> List[SagaLog]:
        """Obtiene todos los logs de una saga específica (versión sync)."""
        import asyncio
        return asyncio.run(self.async_repo.obtener_por_saga_id(saga_id))
    
    def obtener_por_estado(self, estado: EstadoEvento) -> List[SagaLog]:
        """Obtiene logs por estado específico (versión sync)."""
        import asyncio
        return asyncio.run(self.async_repo.obtener_por_estado(estado))
    
    def actualizar(self, saga_log: SagaLog) -> None:
        """Actualiza un log existente (versión sync)."""
        import asyncio
        asyncio.create_task(self.async_repo.actualizar(saga_log))
    
    def obtener_eventos_pendientes(self, max_intentos: int = 3) -> List[SagaLog]:
        """Obtiene eventos que pueden ser reprocesados (versión sync)."""
        import asyncio
        return asyncio.run(self.async_repo.obtener_eventos_pendientes(max_intentos))
    
    def obtener_historial_saga(self, saga_id: str, limit: int = 100) -> List[SagaLog]:
        """Obtiene el historial completo de una saga (versión sync)."""
        import asyncio
        return asyncio.run(self.async_repo.obtener_historial_saga(saga_id, limit))