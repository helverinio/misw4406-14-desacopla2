from datetime import date
from decimal import Decimal
from typing import Optional
from alpespartners.config.db import db
from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, ForeignKey, Integer, Table
from enum import Enum as PyEnum

import uuid

Base = db.declarative_base()

# ===================== Entidades =============================================

# Raiz del agregado
class Programa(db.Model):
    __tablename__ = "programas"
    programa_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estado = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(200), nullable=False)
    brand_id = db.Column(db.UUID(as_uuid=True), nullable=False)

    # --- Vigencia (VO embedido)
    vigencia_inicio = db.Column(db.Date, nullable=True)
    vigencia_fin = db.Column(db.Date, nullable=True)

    # Terminos (VO embebido)
    term_modelo = db.Column(db.String(200), nullable=False)
    term_moneda = db.Column(db.String(3), nullable=False)
    term_tarifa_base = db.Column(db.Numeric(10, 2), nullable=False)
    term_tope = db.Column(db.Numeric(10, 2), nullable=True)

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    afiliaciones = db.relationship("Afiliacion", back_populates="programa", cascade="all, delete-orphan")

class Afiliacion(db.Model):
    __tablename__ = "afiliaciones"
    afiliacion_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    programa_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("programas.programa_id"), nullable=False)
    afiliado_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    estado = db.Column(db.String(200), nullable=False)
    fecha_alta = db.Column(db.Date, nullable=False, server_default=db.func.current_date())
    fecha_baja = db.Column(db.Date, nullable=True)

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    programa = db.relationship("Programa", back_populates="afiliaciones")