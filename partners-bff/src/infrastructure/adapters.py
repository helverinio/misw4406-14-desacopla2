import requests
from src.config import Settings

class PartnersAdapter:
    def __init__(self):
        pass

    def list_partners(self):
        request = requests.get(f"{Settings.integrations_api_url()}/api/v1/partners")

        return request.json()