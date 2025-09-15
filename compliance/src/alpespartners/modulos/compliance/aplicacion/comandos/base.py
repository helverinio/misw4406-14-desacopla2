
from alpespartners.seedwork.aplicacion.comandos import ComandoHandler
from alpespartners.modulos.compliance.infraestructura.fabricas import FabricaRepositorio
from alpespartners.modulos.compliance.dominio.fabricas import FabricaCompliance

class ComandoBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()
        self._fabrica_compliance: FabricaCompliance = FabricaCompliance()
        
    @property
    def fabrica_repositorio(self):
        return self._fabrica_repositorio
    
    @property
    def fabrica_compliance(self):
        return self._fabrica_compliance