# partners-bff/src/presentation/api/routers/v1/partners_router.py
from fastapi import APIRouter

from src.application.services import PartnersService

router = APIRouter(prefix="/v1/partners")

@router.get("/", status_code=200)
async def list_partners():
    service = PartnersService()
    partners = service.list_partners()

    return partners

@router.post("/", status_code=201)
async def create_partner(partner_data: dict):
    """Create a new partner.

    Args:
        partner_data (dict): The data of the partner to create.
        nombre (str): The name of the partner.
        email (str): The email of the partner.
        telefono (str, optional): The phone number of the partner.
        direccion (str, optional): The address of the partner.

    Returns:
        _type_: _description_
    """
    service = PartnersService()
    response, status_code = service.create_partner(partner_data)

    return response, status_code
