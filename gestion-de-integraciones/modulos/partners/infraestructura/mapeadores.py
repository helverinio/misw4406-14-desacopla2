from typing import List
from ..dominio.entidades import Partner, Integracion, EstadoPartner, EstadoKYC, TipoIntegracion
from .dto import PartnerModel, IntegracionModel

class MapeadorPartnerInfraestructura:
    """Mapeador para convertir entre entidades de dominio y modelos de infraestructura"""
    
    def modelo_a_entidad(self, modelo: PartnerModel) -> Partner:
        """Convierte un modelo de base de datos a entidad de dominio"""
        # Mapear integraciones
        integraciones = []
        if modelo.integraciones:
            mapeador_integracion = MapeadorIntegracionInfraestructura()
            integraciones = [
                mapeador_integracion.modelo_a_entidad(integracion_modelo)
                for integracion_modelo in modelo.integraciones
            ]
        
        return Partner(
            id=modelo.id,
            nombre=modelo.nombre,
            email=modelo.email,
            telefono=modelo.telefono,
            direccion=modelo.direccion,
            estado=EstadoPartner(modelo.estado),
            fecha_creacion=modelo.fecha_creacion,
            fecha_actualizacion=modelo.fecha_actualizacion,
            estado_kyc=EstadoKYC(modelo.estado_kyc),
            documentos_kyc=modelo.documentos_kyc,
            integraciones=integraciones
        )
    
    def entidad_a_modelo(self, entidad: Partner, modelo: PartnerModel = None) -> PartnerModel:
        """Convierte una entidad de dominio a modelo de base de datos"""
        if modelo is None:
            modelo = PartnerModel()
        
        modelo.id = entidad.id
        modelo.nombre = entidad.nombre
        modelo.email = entidad.email
        modelo.telefono = entidad.telefono
        modelo.direccion = entidad.direccion
        modelo.estado = entidad.estado.value
        modelo.fecha_creacion = entidad.fecha_creacion
        modelo.fecha_actualizacion = entidad.fecha_actualizacion
        modelo.estado_kyc = entidad.estado_kyc.value
        modelo.documentos_kyc = entidad.documentos_kyc
        
        return modelo

class MapeadorIntegracionInfraestructura:
    """Mapeador para convertir entre entidades Integracion y modelos de infraestructura"""
    
    def modelo_a_entidad(self, modelo: IntegracionModel) -> Integracion:
        """Convierte un modelo de base de datos a entidad de dominio"""
        return Integracion(
            id=modelo.id,
            partner_id=modelo.partner_id,
            tipo=TipoIntegracion(modelo.tipo),
            nombre=modelo.nombre,
            descripcion=modelo.descripcion,
            configuracion=modelo.configuracion or {},
            activa=modelo.activa,
            fecha_creacion=modelo.fecha_creacion,
            fecha_revocacion=modelo.fecha_revocacion
        )
    
    def entidad_a_modelo(self, entidad: Integracion, modelo: IntegracionModel = None) -> IntegracionModel:
        """Convierte una entidad de dominio a modelo de base de datos"""
        if modelo is None:
            modelo = IntegracionModel()
        
        modelo.id = entidad.id
        modelo.partner_id = entidad.partner_id
        modelo.tipo = entidad.tipo.value
        modelo.nombre = entidad.nombre
        modelo.descripcion = entidad.descripcion
        modelo.configuracion = entidad.configuracion
        modelo.activa = entidad.activa
        modelo.fecha_creacion = entidad.fecha_creacion
        modelo.fecha_revocacion = entidad.fecha_revocacion
        
        return modelo
