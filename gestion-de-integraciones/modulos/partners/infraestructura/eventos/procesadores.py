from modulos.partners.aplicacion.servicios import ServicioPartners
from modulos.partners.aplicacion.dto import CrearPartnerDTO
from modulos.partners.infraestructura.eventos.schema.v1.eventos import ComandoCrearPartner
from modulos.partners.infraestructura.repositorios import RepositorioPartnersSQLAlchemy, RepositorioIntegracionesSQLAlchemy

repositorio_partners = RepositorioPartnersSQLAlchemy()
repositorio_integraciones = RepositorioIntegracionesSQLAlchemy()

def procesar_comando_crear_partner(evento: ComandoCrearPartner):
    """Procesar el comando de creación de partner"""
    print(f"Procesando comando de creación de partner: {evento}")
    servicio_partners = ServicioPartners(repositorio_partners, repositorio_integraciones)

    dto = CrearPartnerDTO(
        nombre=evento.data.nombre,
        email=evento.data.email,
        telefono=evento.data.telefono,
        direccion=evento.data.direccion
    )

    servicio_partners.crear_partner(dto)