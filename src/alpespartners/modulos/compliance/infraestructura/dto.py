from alpespartners.config.db import db

import uuid

Base = db.declarative_base()
# ===================== Entidades =============================================
class Payment(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = db.Column(db.UUID(as_uuid=True), nullable=False)      
    state = db.Column(db.String(20), nullable=False)  
    money_amount = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=True)
    payment_method_type = db.Column(db.String(50), nullable=True)
    enable_at = db.Column(db.DateTime, nullable=False)
    taxes = db.relationship("Tax", back_populates="payment", cascade="all, delete-orphan")

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

class Tax(db.Model):
    __tablename__ = "taxes"
    tax_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("payments.payment_id"), nullable=False)
    rate = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Timestamps 
    creado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    payment = db.relationship("Payment", back_populates="taxes")