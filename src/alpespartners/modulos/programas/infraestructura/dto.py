from datetime import date
from decimal import Decimal
from typing import Optional
from alpespartners.config.db import db
from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, ForeignKey, Integer, Table
from enum import Enum as PyEnum

import uuid

Base = db.declarative_base()

class ProgramaEstado(PyEnum):
    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    CERRADO = "CERRADO"

class ProgramaTipo(PyEnum):
    AFILIADOS = "AFILIADOS"
    INFLUENCERS = "INFLUENCERS"
    ADVOCACY = "ADVOCACY"
    SAAS = "SAAS"

class AfiliacionEstado(PyEnum):
    PENDIENTE = "PENDIENTE"
    ACTIVA = "ACTIVA"
    SUSPENDIDA = "SUSPENDIDA"
    BAJA = "BAJA"

class ModeloComision(PyEnum):
    CPA = "CPA"
    CPL = "CPL"
    CPC = "CPC"
    
# ===================== Value Objects (composite) =============================

class Vigencia:
    """VO: inicio, fin"""
    def __init__(self, inicio: date, fin: date):
        self.inicio = inicio
        self.fin = fin

    def __composite_values__(self):
        return self.inicio, self.fin

    def __repr__(self) -> str:
        return f"Vigencia({self.inicio}..{self.fin})"

    def __eq__(self, other):
        return isinstance(other, Vigencia) and self.__composite_values__() == other.__composite_values__()

class Terminos:
    """VO: modelo, moneda, tarifa_base, tope"""
    def __init__(self, modelo: ModeloComision, moneda: str, tarifa_base: Decimal, tope: Optional[Decimal]):
        self.modelo = modelo
        self.moneda = moneda
        self.tarifa_base = tarifa_base
        self.tope = tope

    def __composite_values__(self):
        return self.modelo, self.moneda, self.tarifa_base, self.tope

    def __repr__(self) -> str:
        return f"Terminos(modelo={self.modelo}, moneda={self.moneda}, tarifa_base={self.tarifa_base}, tope={self.tope})"

    def __eq__(self, other):  # igualdad por valor
        return isinstance(other, Terminos) and self.__composite_values__() == other.__composite_values__()

# ===================== Entidades =============================================

# Raiz del agregado
class Programa(db.Model):
    __tablename__ = "programas"
    programa_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estado = db.Column(db.Enum(ProgramaEstado), nullable=False, default=ProgramaEstado.BORRADOR)
    tipo = db.Column(db.Enum(ProgramaTipo), nullable=False)
    brand_id = db.Column(db.UUID(as_uuid=True), nullable=False)

    # --- Vigencia (VO embedido)
    vigencia_inicio = db.Column(db.Date, nullable=True)
    vigencia_fin = db.Column(db.Date, nullable=True)
    vigencia = db.composite(Vigencia, vigencia_inicio, vigencia_fin)

    # Terminos (VO embebido)
    term_modelo = db.Column(db.Enum(ModeloComision), nullable=False)
    term_moneda = db.Column(db.String(3), nullable=False)
    term_tarifa_base = db.Column(db.Numeric(10, 2), nullable=False)
    term_tope = db.Column(db.Numeric(10, 2), nullable=True)
    terminos = db.composite(Terminos, term_modelo, term_moneda, term_tarifa_base, term_tope)

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    afiliaciones = db.relationship("Afiliacion", back_populates="programa", cascade="all, delete-orphan")

class Afiliacion(db.Model):
    __tablename__ = "afiliaciones"
    afiliacion_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    programa_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("programas.programa_id"), nullable=False)
    afiliado_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    estado = db.Column(db.Enum(AfiliacionEstado), nullable=False, default=AfiliacionEstado.PENDIENTE)
    fecha_alta = db.Column(db.Date, nullable=False, server_default=db.func.current_date())
    fecha_baja = db.Column(db.Date, nullable=True)

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    programa = db.relationship("Programa", back_populates="afiliaciones")