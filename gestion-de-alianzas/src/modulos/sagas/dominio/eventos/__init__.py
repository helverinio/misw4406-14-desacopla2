"""
Eventos de dominio para la saga de Partners y Contratos
Siguiendo DDD, los eventos están separados por agregados de dominio
"""

# Eventos del agregado Partners
from .partner_eventos import (
    CreatePartner,
    PartnerCreated, 
    PartnerCreationFailed,
    PartnerUpdated,
    PartnerDeleted
)

# Eventos del agregado Contratos
from .contrato_eventos import (
    ContratoCreado,
    ContratoCreadoFailed,
    ContratoActualizado,
    ContratoTerminado,
    ContratoSuspendido,
    ContratoReactivado
)

# Exportar todos los eventos para facilitar importación
__all__ = [
    # Partner events
    'CreatePartner',
    'PartnerCreated',
    'PartnerCreationFailed', 
    'PartnerUpdated',
    'PartnerDeleted',
    
    # Contrato events
    'ContratoCreado',
    'ContratoCreadoFailed',
    'ContratoActualizado',
    'ContratoTerminado',
    'ContratoSuspendido',
    'ContratoReactivado'
]