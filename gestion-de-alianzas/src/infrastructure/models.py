# publicaciones_app/src/infra/models.py
import uuid
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.db import Base


class ContratoRow(Base):
    __tablename__ = "contratos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Identificador único del contrato"
    )

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Referencia al socio (Partner) relacionado"
    )

    tipo: Mapped[String] = mapped_column(
        String(20),
        nullable=False,
        doc="Tipo de contrato (CPA, CPL, CPC, REVSHARE, FIJO)"
    )

    fecha_inicio: Mapped[date] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Fecha de inicio del contrato"
    )

    fecha_fin: Mapped[date] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha de fin del contrato, si aplica"
    )

    monto: Mapped[float] = mapped_column(
        nullable=True,
        doc="Monto total o comisión asociada"
    )

    moneda: Mapped[String] = mapped_column(
        String(10),
        nullable=True,
        default="USD",
        doc="Moneda del contrato"
    )

    condiciones: Mapped[String] = mapped_column(
        String(255),
        nullable=True,
        doc="Términos y condiciones adicionales"
    )

    estado: Mapped[String] = mapped_column(
        String(20),
        nullable=False,
        default="activo",
        doc="Estado actual del contrato"
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Fecha y hora de creación del contrato"
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Fecha y hora de última actualización"
    )
