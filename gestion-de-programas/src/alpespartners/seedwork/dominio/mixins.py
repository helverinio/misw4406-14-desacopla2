from .reglas import ReglaNegocio
from .excepciones import ReglaNegocioExcepcion

class ValidarReglasMixin:
    def validar_reglas(self, regla: ReglaNegocio):
        if not regla.es_valido():
            raise ReglaNegocioExcepcion(regla)
