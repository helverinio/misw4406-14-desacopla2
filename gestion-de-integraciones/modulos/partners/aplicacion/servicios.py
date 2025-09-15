import logging
from datetime import datetime
from typing import List
from ..dominio.entidades import Partner, Integracion, EstadoPartner, EstadoKYC, TipoIntegracion
from ..dominio.repositorios import RepositorioPartners, RepositorioIntegraciones
from ..dominio.excepciones import (
    PartnerNoEncontrado, EmailYaExiste, IntegracionNoEncontrada, 
    KYCNoValido, PartnerEliminado, IntegracionYaRevocada
)
from ..dominio.eventos import (
    PartnerCreado, PartnerActualizado, PartnerEliminado as EventoPartnerEliminado,
    KYCVerificado, IntegracionCreada, IntegracionRevocada
)
from .dto import (
    CrearPartnerDTO, ActualizarPartnerDTO, VerificarKYCDTO, 
    CrearIntegracionDTO, RevocarIntegracionDTO, PartnerResponseDTO, IntegracionResponseDTO
)
from .mapeadores import MapeadorPartner, MapeadorIntegracion
from ..infraestructura.eventos.despachadores import DespachadorEventosPartner

class ServicioPartners:
    """Servicio de aplicación para gestión de Partners"""
    
    def __init__(self, repositorio_partners: RepositorioPartners, repositorio_integraciones: RepositorioIntegraciones):
        self.repositorio_partners = repositorio_partners
        self.repositorio_integraciones = repositorio_integraciones
        self.mapeador_partner = MapeadorPartner()
        self.mapeador_integracion = MapeadorIntegracion()
        self.despachador_eventos = DespachadorEventosPartner()
        self.logger = logging.getLogger(__name__)
    
    def crear_partner(self, dto: CrearPartnerDTO) -> PartnerResponseDTO:
        """Crear un nuevo partner"""
        self.logger.info(f"Iniciando creación de partner con email: {dto.email}")
        
        try:
            # Verificar que el email no exista
            self.logger.debug(f"Verificando si el email {dto.email} ya existe")
            partner_existente = self.repositorio_partners.obtener_por_email(dto.email)
            if partner_existente:
                self.logger.warning(f"Email {dto.email} ya existe, lanzando excepción")
                raise EmailYaExiste(dto.email)
            
            self.logger.debug("Email no existe, procediendo con la creación")
            
            # Crear el partner
            self.logger.debug("Creando entidad Partner")
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
            
            self.logger.debug(f"Partner creado en memoria: {partner.nombre} - {partner.email}")
            
            # Guardar en el repositorio
            self.logger.debug("Guardando partner en repositorio")
            partner_guardado = self.repositorio_partners.guardar(partner)
            self.logger.info(f"Partner guardado exitosamente con ID: {partner_guardado.id}")
            
            # Publicar evento de partner creado
            self.logger.debug("Preparando evento PartnerCreado")
            try:
                evento = PartnerCreado(
                    partner_id=partner_guardado.id
                )
                self.logger.debug(f"Evento PartnerCreado creado: {evento}")
                
                self.logger.debug("Publicando evento PartnerCreado")
                evento_publicado = self.despachador_eventos.publicar_evento(evento)
                if evento_publicado:
                    self.logger.info(f"Evento PartnerCreado publicado exitosamente para partner ID: {partner_guardado.id}")
                else:
                    self.logger.warning(f"Evento PartnerCreado no se pudo publicar para partner ID: {partner_guardado.id} - Pulsar no disponible")
                
            except Exception as e:
                self.logger.error(f"Error al crear o publicar evento PartnerCreado: {str(e)}", exc_info=True)
                # Re-lanzar la excepción para que el error sea visible
                raise
            
            # Mapear a DTO de respuesta
            self.logger.debug("Mapeando partner a DTO de respuesta")
            response_dto = self.mapeador_partner.entidad_a_dto(partner_guardado)
            self.logger.info(f"Partner creado exitosamente: {partner_guardado.id}")
            
            return response_dto
            
        except Exception as e:
            self.logger.error(f"Error en crear_partner: {str(e)}", exc_info=True)
            raise
    
    def actualizar_partner(self, partner_id: str, dto: ActualizarPartnerDTO) -> PartnerResponseDTO:
        """Actualizar un partner existente"""
        partner = self.repositorio_partners.obtener_por_id(partner_id)
        if not partner:
            raise PartnerNoEncontrado(partner_id)
        
        if partner.estado == EstadoPartner.ELIMINADO:
            raise PartnerEliminado(partner_id)
        
        # Capturar estado anterior para el evento
        estado_anterior = partner.estado
        
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
        
        # Publicar evento de partner actualizado
        evento = PartnerActualizado(
            partner_id=partner_actualizado.id,
            nombre=partner_actualizado.nombre,
            email=partner_actualizado.email,
            telefono=partner_actualizado.telefono,
            direccion=partner_actualizado.direccion,
            estado=partner_actualizado.estado,
            estado_anterior=estado_anterior
        )
        evento_publicado = self.despachador_eventos.publicar_evento(evento)
        if not evento_publicado:
            self.logger.warning(f"Evento PartnerActualizado no se pudo publicar para partner ID: {partner_actualizado.id} - Pulsar no disponible")
        
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
        
        # Publicar evento de partner eliminado
        evento = EventoPartnerEliminado(
            partner_id=partner.id,
            nombre=partner.nombre,
            email=partner.email,
            fecha_eliminacion=datetime.utcnow()
        )
        evento_publicado = self.despachador_eventos.publicar_evento(evento)
        if not evento_publicado:
            self.logger.warning(f"Evento PartnerEliminado no se pudo publicar para partner ID: {partner.id} - Pulsar no disponible")
        
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
        except ValueError as exc:
            raise KYCNoValido(f"Estado KYC inválido: {dto.estado_kyc}") from exc
        
        # Capturar estado anterior para el evento
        estado_kyc_anterior = partner.estado_kyc
        
        # Actualizar KYC
        partner.verificar_kyc(estado_kyc, dto.documentos)
        
        # Guardar cambios
        partner_actualizado = self.repositorio_partners.guardar(partner)
        
        # Publicar evento de KYC verificado
        evento = KYCVerificado(
            partner_id=partner_actualizado.id,
            estado_kyc_anterior=estado_kyc_anterior,
            estado_kyc_nuevo=estado_kyc,
            documentos=dto.documentos,
            observaciones=getattr(dto, 'observaciones', None)
        )
        evento_publicado = self.despachador_eventos.publicar_evento(evento)
        if not evento_publicado:
            self.logger.warning(f"Evento KYCVerificado no se pudo publicar para partner ID: {partner_actualizado.id} - Pulsar no disponible")
        
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
        
        # Publicar evento de integración revocada
        evento = IntegracionRevocada(
            integracion_id=integracion.id,
            partner_id=integracion.partner_id,
            nombre=integracion.nombre,
            fecha_revocacion=datetime.utcnow(),
            motivo=getattr(dto, 'motivo', None)
        )
        evento_publicado = self.despachador_eventos.publicar_evento(evento)
        if not evento_publicado:
            self.logger.warning(f"Evento IntegracionRevocada no se pudo publicar para integración ID: {integracion.id} - Pulsar no disponible")
        
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
        except ValueError as exc:
            raise ValueError(f"Tipo de integración inválido: {dto.tipo}") from exc
        
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
        
        # Publicar evento de integración creada
        evento = IntegracionCreada(
            integracion_id=integracion_guardada.id,
            partner_id=integracion_guardada.partner_id,
            tipo=integracion_guardada.tipo,
            nombre=integracion_guardada.nombre,
            descripcion=integracion_guardada.descripcion,
            configuracion=integracion_guardada.configuracion
        )
        evento_publicado = self.despachador_eventos.publicar_evento(evento)
        if not evento_publicado:
            self.logger.warning(f"Evento IntegracionCreada no se pudo publicar para integración ID: {integracion_guardada.id} - Pulsar no disponible")
        
        return self.mapeador_integracion.entidad_a_dto(integracion_guardada)
