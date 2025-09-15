from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from config.db import db

class PartnerModel(db.Model):
    """Modelo SQLAlchemy para Partner"""
    __tablename__ = 'partners'
    
    id = db.Column(db.String(36), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='ACTIVO')
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, nullable=True)
    estado_kyc = db.Column(db.String(30), nullable=False, default='PENDIENTE')
    documentos_kyc = db.Column(db.JSON, nullable=True)
    
    # Relación con integraciones
    integraciones = db.relationship('IntegracionModel', backref='partner', lazy=True)
    
    def __repr__(self):
        return f'<Partner {self.nombre} ({self.email})>'

class IntegracionModel(db.Model):
    """Modelo SQLAlchemy para Integracion"""
    __tablename__ = 'integraciones'
    
    id = db.Column(db.String(36), primary_key=True)
    partner_id = db.Column(db.String(36), db.ForeignKey('partners.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    configuracion = db.Column(db.JSON, nullable=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_revocacion = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Integracion {self.nombre} ({self.tipo})>'
