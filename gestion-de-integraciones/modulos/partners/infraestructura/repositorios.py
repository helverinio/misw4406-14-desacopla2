from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from config.db import db
from ..dominio.entidades import Partner, Integracion
from ..dominio.repositorios import RepositorioPartners, RepositorioIntegraciones
from ..dominio.excepciones import EmailYaExiste
from .dto import PartnerModel, IntegracionModel
from .mapeadores import MapeadorPartnerInfraestructura, MapeadorIntegracionInfraestructura

class RepositorioPartnersSQLAlchemy(RepositorioPartners):
    """Implementación del repositorio de Partners usando SQLAlchemy"""
    
    def __init__(self):
        self.mapeador = MapeadorPartnerInfraestructura()
    
    def obtener_por_id(self, partner_id: str) -> Optional[Partner]:
        """Obtiene un partner por su ID"""
        modelo = PartnerModel.query.filter_by(id=partner_id).first()
        if modelo:
            return self.mapeador.modelo_a_entidad(modelo)
        return None
    
    def obtener_por_email(self, email: str) -> Optional[Partner]:
        """Obtiene un partner por su email"""
        modelo = PartnerModel.query.filter_by(email=email).first()
        if modelo:
            return self.mapeador.modelo_a_entidad(modelo)
        return None
    
    def guardar(self, partner: Partner) -> Partner:
        """Guarda un partner"""
        try:
            # Buscar si ya existe
            modelo_existente = PartnerModel.query.filter_by(id=partner.id).first()
            
            if modelo_existente:
                # Actualizar existente
                modelo = self.mapeador.entidad_a_modelo(partner, modelo_existente)
            else:
                # Crear nuevo
                modelo = self.mapeador.entidad_a_modelo(partner)
                db.session.add(modelo)
            
            db.session.commit()
            
            # Recargar para obtener relaciones actualizadas
            modelo_actualizado = PartnerModel.query.filter_by(id=partner.id).first()
            return self.mapeador.modelo_a_entidad(modelo_actualizado)
            
        except IntegrityError as e:
            db.session.rollback()
            if 'email' in str(e):
                raise EmailYaExiste(partner.email)
            raise e
    
    def eliminar(self, partner_id: str) -> bool:
        """Elimina un partner (hard delete)"""
        modelo = PartnerModel.query.filter_by(id=partner_id).first()
        if modelo:
            db.session.delete(modelo)
            db.session.commit()
            return True
        return False
    
    def listar_todos(self) -> List[Partner]:
        """Lista todos los partners"""
        modelos = PartnerModel.query.all()
        return [self.mapeador.modelo_a_entidad(modelo) for modelo in modelos]

class RepositorioIntegracionesSQLAlchemy(RepositorioIntegraciones):
    """Implementación del repositorio de Integraciones usando SQLAlchemy"""
    
    def __init__(self):
        self.mapeador = MapeadorIntegracionInfraestructura()
    
    def obtener_por_id(self, integracion_id: str) -> Optional[Integracion]:
        """Obtiene una integración por su ID"""
        modelo = IntegracionModel.query.filter_by(id=integracion_id).first()
        if modelo:
            return self.mapeador.modelo_a_entidad(modelo)
        return None
    
    def obtener_por_partner(self, partner_id: str) -> List[Integracion]:
        """Obtiene todas las integraciones de un partner"""
        modelos = IntegracionModel.query.filter_by(partner_id=partner_id).all()
        return [self.mapeador.modelo_a_entidad(modelo) for modelo in modelos]
    
    def guardar(self, integracion: Integracion) -> Integracion:
        """Guarda una integración"""
        # Buscar si ya existe
        modelo_existente = IntegracionModel.query.filter_by(id=integracion.id).first()
        
        if modelo_existente:
            # Actualizar existente
            modelo = self.mapeador.entidad_a_modelo(integracion, modelo_existente)
        else:
            # Crear nuevo
            modelo = self.mapeador.entidad_a_modelo(integracion)
            db.session.add(modelo)
        
        db.session.commit()
        
        # Recargar para obtener datos actualizados
        modelo_actualizado = IntegracionModel.query.filter_by(id=integracion.id).first()
        return self.mapeador.modelo_a_entidad(modelo_actualizado)
    
    def eliminar(self, integracion_id: str) -> bool:
        """Elimina una integración (hard delete)"""
        modelo = IntegracionModel.query.filter_by(id=integracion_id).first()
        if modelo:
            db.session.delete(modelo)
            db.session.commit()
            return True
        return False
