from src.infrastructure.adapters import PartnersAdapter

class PartnersService:
    def __init__(self):
        self.partners_adapter = PartnersAdapter()

    def list_partners(self):
        return self.partners_adapter.list_partners()
    
    def create_partner(self, partner_data: dict):
        return self.partners_adapter.create_partner(partner_data)