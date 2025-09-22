# partners-bff/src/presentation/api/routers/v1/partners_router.py
from fastapi import APIRouter

from src.application.services import PartnersService
from src.infrastructure.pulsar_integration import PulsarContratoPublisher
from fastapi import status
from src.infrastructure.mappers import MapeadorComandoCrearPartner

router = APIRouter(prefix="/v1/partners")

@router.get("/", status_code=200)
async def list_partners():
    service = PartnersService()
    partners = service.list_partners()

    return partners

@router.post("/", status_code=202)
async def create_partner(partner_data: dict):
    """
    Publish a new partner creation event to Pulsar.
    """
    publisher = PulsarContratoPublisher()
    try:
        evento = MapeadorComandoCrearPartner().parse_dict(partner_data)

        publisher.producer.send(evento)
    finally:
        publisher.close()
    return {"message": "Evento de creación de partner publicado"}, status.HTTP_202_ACCEPTED
