from typing import List
from ..dominio.entidades import Partner, Integracion
from .dto import PartnerResponseDTO, IntegracionResponseDTO

class MapeadorPartner:
    """Mapeador para convertir entre entidades Partner y DTOs"""
    
    def entidad_a_dto(self, partner: Partner) -> PartnerResponseDTO:
        """Convierte una entidad Partner a DTO de respuesta"""
        mapeador_integracion = MapeadorIntegracion()
        
        integraciones_dto = [
            mapeador_integracion.entidad_a_dto(integracion) 
            for integracion in partner.integraciones
        ]
        
        return PartnerResponseDTO(
            id=partner.id,
            nombre=partner.nombre,
            email=partner.email,
            telefono=partner.telefono,
            direccion=partner.direccion,
            estado=partner.estado.value,
            fecha_creacion=partner.fecha_creacion,
            fecha_actualizacion=partner.fecha_actualizacion,
            estado_kyc=partner.estado_kyc.value,
            documentos_kyc=partner.documentos_kyc,
            integraciones=integraciones_dto
        )

class MapeadorIntegracion:
    """Mapeador para convertir entre entidades Integracion y DTOs"""
    
    def entidad_a_dto(self, integracion: Integracion) -> IntegracionResponseDTO:
        """Convierte una entidad Integracion a DTO de respuesta"""
        return IntegracionResponseDTO(
            id=integracion.id,
            partner_id=integracion.partner_id,
            tipo=integracion.tipo.value,
            nombre=integracion.nombre,
            descripcion=integracion.descripcion,
            activa=integracion.activa,
            fecha_creacion=integracion.fecha_creacion,
            fecha_revocacion=integracion.fecha_revocacion
        )
