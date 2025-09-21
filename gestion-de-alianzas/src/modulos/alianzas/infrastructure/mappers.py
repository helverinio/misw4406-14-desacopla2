# publicaciones_app/src/infrastructure/mappers.py
import uuid
from src.modulos.alianzas.infrastructure.models import ContratoRow
from src.modulos.alianzas.domain.models.contrato import Contrato, TipoContrato, EstadoContrato

def _domain_to_row(c: Contrato) -> ContratoRow:
    return ContratoRow(
        # id is optional, DB will autogenerate if not provided
        id=uuid.UUID(c.id) if c.id else None,
        partner_id=uuid.UUID(c.partner_id),
        tipo=c.tipo.value if isinstance(c.tipo, TipoContrato) else str(c.tipo),
        fecha_inicio=c.fecha_inicio,
        fecha_fin=c.fecha_fin,
        monto=c.monto,
        moneda=c.moneda,
        condiciones=c.condiciones,
        estado=c.estado.value if isinstance(c.estado, EstadoContrato) else str(c.estado),
        fecha_creacion=c.fecha_creacion,
        fecha_actualizacion=c.fecha_actualizacion
    )

def _row_to_domain(r: ContratoRow) -> Contrato:
    return Contrato(
        id=str(r.id) if r.id else None,
        partner_id=str(r.partner_id),
        tipo=TipoContrato(r.tipo),
        fecha_inicio=r.fecha_inicio.date() if hasattr(r.fecha_inicio, 'date') else r.fecha_inicio,
        fecha_fin=r.fecha_fin.date() if r.fecha_fin and hasattr(r.fecha_fin, 'date') else r.fecha_fin,
        monto=r.monto,
        moneda=r.moneda,
        condiciones=r.condiciones,
        estado=EstadoContrato(r.estado),
        fecha_creacion=r.fecha_creacion,
        fecha_actualizacion=r.fecha_actualizacion
    )
