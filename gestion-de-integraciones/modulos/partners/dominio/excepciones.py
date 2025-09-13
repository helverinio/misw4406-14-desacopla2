class PartnerException(Exception):
    """Excepción base para el dominio de Partners"""
    pass

class PartnerNoEncontrado(PartnerException):
    """Excepción cuando no se encuentra un partner"""
    def __init__(self, partner_id: str):
        self.partner_id = partner_id
        super().__init__(f"Partner con ID {partner_id} no encontrado")

class EmailYaExiste(PartnerException):
    """Excepción cuando el email ya está registrado"""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Ya existe un partner con el email {email}")

class IntegracionNoEncontrada(PartnerException):
    """Excepción cuando no se encuentra una integración"""
    def __init__(self, integracion_id: str):
        self.integracion_id = integracion_id
        super().__init__(f"Integración con ID {integracion_id} no encontrada")

class KYCNoValido(PartnerException):
    """Excepción cuando el KYC no es válido"""
    def __init__(self, mensaje: str):
        super().__init__(f"KYC no válido: {mensaje}")

class PartnerEliminado(PartnerException):
    """Excepción cuando se intenta operar con un partner eliminado"""
    def __init__(self, partner_id: str):
        self.partner_id = partner_id
        super().__init__(f"No se puede operar con el partner {partner_id} porque está eliminado")

class IntegracionYaRevocada(PartnerException):
    """Excepción cuando se intenta revocar una integración ya revocada"""
    def __init__(self, integracion_id: str):
        self.integracion_id = integracion_id
        super().__init__(f"La integración {integracion_id} ya está revocada")
