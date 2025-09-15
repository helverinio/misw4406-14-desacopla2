from typing import Dict, Any
from ...dominio.eventos import (
    EventoPartner,
    PartnerCreado,
    PartnerActualizado,
    PartnerEliminado,
    KYCVerificado,
    IntegracionCreada,
    IntegracionRevocada
)
from .schema.v1.eventos import (
    EventoPartnerCreado as EventoPartnerCreadoIntegracion,
    EventoPartnerActualizado as EventoPartnerActualizadoIntegracion,
    EventoPartnerEliminado as EventoPartnerEliminadoIntegracion,
    EventoKYCVerificado as EventoKYCVerificadoIntegracion,
    EventoIntegracionCreada as EventoIntegracionCreadaIntegracion,
    EventoIntegracionRevocada as EventoIntegracionRevocadaIntegracion,
    PartnerPayload,
    PartnerActualizadoPayload,
    KYCPayload,
    IntegracionPayload,
    IntegracionRevocadaPayload
)

def unix_time_millis(dt):
    """Convert datetime to unix timestamp in milliseconds"""
    import time
    return int(time.mktime(dt.timetuple()) * 1000)

class MapeadorEventoDominioPartner:
    """Mapeador para convertir eventos de dominio a eventos de integración"""
    
    # Versiones aceptadas
    versions = ("v1",)
    LATEST_VERSION = versions[0]

    def __init__(self):
        self.router = {
            PartnerCreado: self._entidad_a_partner_creado,
            PartnerActualizado: self._entidad_a_partner_actualizado,
            PartnerEliminado: self._entidad_a_partner_eliminado,
            KYCVerificado: self._entidad_a_kyc_verificado,
            IntegracionCreada: self._entidad_a_integracion_creada,
            IntegracionRevocada: self._entidad_a_integracion_revocada,
        }

    def es_version_valida(self, version):
        return version in self.versions

    def _entidad_a_partner_creado(self, evento: PartnerCreado, version=LATEST_VERSION) -> EventoPartnerCreadoIntegracion:
        def v1(evento: PartnerCreado):
            payload = PartnerPayload(
                partner_id=evento.partner_id,
                nombre=evento.nombre,
                email=evento.email,
                telefono=evento.telefono or "",
                direccion=evento.direccion or "",
                estado=evento.estado.value,
                estado_kyc=evento.estado_kyc.value
            )
            
            evento_integracion = EventoPartnerCreadoIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="PartnerCreado",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        if not self.es_version_valida(version):
            raise Exception(f"No se sabe procesar la version {version}")

        return v1(evento)

    def _entidad_a_partner_actualizado(self, evento: PartnerActualizado, version=LATEST_VERSION) -> EventoPartnerActualizadoIntegracion:
        def v1(evento: PartnerActualizado):
            payload = PartnerActualizadoPayload(
                partner_id=evento.partner_id,
                nombre=evento.nombre,
                email=evento.email,
                telefono=evento.telefono or "",
                direccion=evento.direccion or "",
                estado=evento.estado.value,
                estado_anterior=evento.estado_anterior.value
            )
            
            evento_integracion = EventoPartnerActualizadoIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="PartnerActualizado",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        return v1(evento)

    def _entidad_a_partner_eliminado(self, evento: PartnerEliminado, version=LATEST_VERSION) -> EventoPartnerEliminadoIntegracion:
        def v1(evento: PartnerEliminado):
            payload = PartnerPayload(
                partner_id=evento.partner_id,
                nombre=evento.nombre,
                email=evento.email,
                telefono="",
                direccion="",
                estado="ELIMINADO",
                estado_kyc=""
            )
            
            evento_integracion = EventoPartnerEliminadoIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="PartnerEliminado",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        return v1(evento)

    def _entidad_a_kyc_verificado(self, evento: KYCVerificado, version=LATEST_VERSION) -> EventoKYCVerificadoIntegracion:
        def v1(evento: KYCVerificado):
            payload = KYCPayload(
                partner_id=evento.partner_id,
                estado_kyc_anterior=evento.estado_kyc_anterior.value,
                estado_kyc_nuevo=evento.estado_kyc_nuevo.value,
                observaciones=evento.observaciones or ""
            )
            
            evento_integracion = EventoKYCVerificadoIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="KYCVerificado",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        return v1(evento)

    def _entidad_a_integracion_creada(self, evento: IntegracionCreada, version=LATEST_VERSION) -> EventoIntegracionCreadaIntegracion:
        def v1(evento: IntegracionCreada):
            payload = IntegracionPayload(
                integracion_id=evento.integracion_id,
                partner_id=evento.partner_id,
                tipo=evento.tipo.value,
                nombre=evento.nombre,
                descripcion=evento.descripcion or ""
            )
            
            evento_integracion = EventoIntegracionCreadaIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="IntegracionCreada",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        return v1(evento)

    def _entidad_a_integracion_revocada(self, evento: IntegracionRevocada, version=LATEST_VERSION) -> EventoIntegracionRevocadaIntegracion:
        def v1(evento: IntegracionRevocada):
            payload = IntegracionRevocadaPayload(
                integracion_id=evento.integracion_id,
                partner_id=evento.partner_id,
                nombre=evento.nombre,
                motivo=evento.motivo or ""
            )
            
            evento_integracion = EventoIntegracionRevocadaIntegracion(
                id=str(evento.id),
                time=unix_time_millis(evento.fecha_evento),
                specversion=str(version),
                type="IntegracionRevocada",
                datacontenttype="AVRO",
                service_name="gestion-de-integraciones",
                data=payload
            )
            
            return evento_integracion

        return v1(evento)

    def entidad_a_dto(self, evento: EventoPartner, version=LATEST_VERSION):
        """Convierte un evento de dominio a un evento de integración"""
        func = self.router.get(evento.__class__, None)
        
        if not func:
            raise Exception(f"No existe implementación para el tipo de evento {evento.__class__}")
        
        return func(evento, version=version)
