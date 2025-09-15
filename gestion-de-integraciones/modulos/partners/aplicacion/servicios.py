from datetime import datetime
from typing import List, Optional
from ..dominio.entidades import Partner, Integracion, EstadoPartner, EstadoKYC, TipoIntegracion
from ..dominio.repositorios import RepositorioPartners, RepositorioIntegraciones
from ..dominio.excepciones import (
    PartnerNoEncontrado, EmailYaExiste, IntegracionNoEncontrada, 
    KYCNoValido, PartnerEliminado, IntegracionYaRevocada
)
from .dto import (
    CrearPartnerDTO, ActualizarPartnerDTO, VerificarKYCDTO, 
    CrearIntegracionDTO, RevocarIntegracionDTO, PartnerResponseDTO, IntegracionResponseDTO
)
from .mapeadores import MapeadorPartner, MapeadorIntegracion

class ServicioPartners:
    """Servicio de aplicación para gestión de Partners"""
    
    def __init__(self, repositorio_partners: RepositorioPartners, repositorio_integraciones: RepositorioIntegraciones):
        self.repositorio_partners = repositorio_partners
        self.repositorio_integraciones = repositorio_integraciones
        self.mapeador_partner = MapeadorPartner()
        self.mapeador_integracion = MapeadorIntegracion()
    
    def crear_partner(self, dto: CrearPartnerDTO) -> PartnerResponseDTO:
        """Crear un nuevo partner"""
        # Verificar que el email no exista
        partner_existente = self.repositorio_partners.obtener_por_email(dto.email)
        if partner_existente:
            raise EmailYaExiste(dto.email)
        
        # Crear el partner
        partner = Partner(
            id="",  # Se generará automáticamente
            nombre=dto.nombre,
            email=dto.email,
            telefono=dto.telefono,
            direccion=dto.direccion,
            estado=EstadoPartner.ACTIVO,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=None,
            estado_kyc=EstadoKYC.PENDIENTE,
            documentos_kyc=None,
            integraciones=[]
        )
        
        # Guardar en el repositorio
        partner_guardado = self.repositorio_partners.guardar(partner)
        
        return self.mapeador_partner.entidad_a_dto(partner_guardado)
    
    def actualizar_partner(self, partner_id: str, dto: ActualizarPartnerDTO) -> PartnerResponseDTO:
        """Actualizar un partner existente"""
        partner = self.repositorio_partners.obtener_por_id(partner_id)
        if not partner:
            raise PartnerNoEncontrado(partner_id)
        
        if partner.estado == EstadoPartner.ELIMINADO:
            raise PartnerEliminado(partner_id)
        
        # Actualizar campos
        if dto.nombre:
            partner.nombre = dto.nombre
        if dto.telefono:
            partner.telefono = dto.telefono
        if dto.direccion:
            partner.direccion = dto.direccion
        
        partner.fecha_actualizacion = datetime.utcnow()
        
        # Guardar cambios
        partner_actualizado = self.repositorio_partners.guardar(partner)
        
        return self.mapeador_partner.entidad_a_dto(partner_actualizado)
    
    def eliminar_partner(self, partner_id: str) -> bool:
        """Eliminar un partner (soft delete)"""
        partner = self.repositorio_partners.obtener_por_id(partner_id)
        if not partner:
            raise PartnerNoEncontrado(partner_id)
        
        if partner.estado == EstadoPartner.ELIMINADO:
            raise PartnerEliminado(partner_id)
        
        # Marcar como eliminado y revocar integraciones
        partner.eliminar()
        
        # Guardar cambios
        self.repositorio_partners.guardar(partner)
        
        return True
    
    def verificar_kyc_partner(self, partner_id: str, dto: VerificarKYCDTO) -> PartnerResponseDTO:
        """Verificar KYC de un partner"""
        partner = self.repositorio_partners.obtener_por_id(partner_id)
        if not partner:
            raise PartnerNoEncontrado(partner_id)
        
        if partner.estado == EstadoPartner.ELIMINADO:
            raise PartnerEliminado(partner_id)
        
        try:
            estado_kyc = EstadoKYC(dto.estado_kyc)
        except ValueError:
            raise KYCNoValido(f"Estado KYC inválido: {dto.estado_kyc}")
        
        # Actualizar KYC
        partner.verificar_kyc(estado_kyc, dto.documentos)
        
        # Guardar cambios
        partner_actualizado = self.repositorio_partners.guardar(partner)
        
        return self.mapeador_partner.entidad_a_dto(partner_actualizado)
    
    def revocar_integracion(self, dto: RevocarIntegracionDTO) -> bool:
        """Revocar una integración específica"""
        integracion = self.repositorio_integraciones.obtener_por_id(dto.integracion_id)
        if not integracion:
            raise IntegracionNoEncontrada(dto.integracion_id)
        
        if not integracion.activa:
            raise IntegracionYaRevocada(dto.integracion_id)
        
        # Revocar la integración
        integracion.revocar()
        
        # Guardar cambios
        self.repositorio_integraciones.guardar(integracion)
        
        return True
    
    def obtener_partner(self, partner_id: str) -> PartnerResponseDTO:
        """Obtener un partner por ID"""
        partner = self.repositorio_partners.obtener_por_id(partner_id)
        if not partner:
            raise PartnerNoEncontrado(partner_id)
        
        return self.mapeador_partner.entidad_a_dto(partner)
    
    def listar_partners(self) -> List[PartnerResponseDTO]:
        """Listar todos los partners"""
        partners = self.repositorio_partners.listar_todos()
        return [self.mapeador_partner.entidad_a_dto(partner) for partner in partners]
    
    def crear_integracion(self, dto: CrearIntegracionDTO) -> IntegracionResponseDTO:
        """Crear una nueva integración para un partner"""
        partner = self.repositorio_partners.obtener_por_id(dto.partner_id)
        if not partner:
            raise PartnerNoEncontrado(dto.partner_id)
        
        if partner.estado == EstadoPartner.ELIMINADO:
            raise PartnerEliminado(dto.partner_id)
        
        try:
            tipo_integracion = TipoIntegracion(dto.tipo)
        except ValueError:
            raise ValueError(f"Tipo de integración inválido: {dto.tipo}")
        
        # Crear la integración
        integracion = Integracion(
            id="",  # Se generará automáticamente
            partner_id=dto.partner_id,
            tipo=tipo_integracion,
            nombre=dto.nombre,
            descripcion=dto.descripcion,
            configuracion=dto.configuracion or {},
            activa=True,
            fecha_creacion=datetime.utcnow(),
            fecha_revocacion=None
        )
        
        # Guardar en el repositorio
        integracion_guardada = self.repositorio_integraciones.guardar(integracion)
        
        return self.mapeador_integracion.entidad_a_dto(integracion_guardada)
