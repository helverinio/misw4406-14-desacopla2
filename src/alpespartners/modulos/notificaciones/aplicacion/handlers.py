
from alpespartners.modulos.programas.dominio.eventos import ProgramaCreado
from alpespartners.seedwork.aplicacion.handlers import Handler


class HandlerProgramaDominio(Handler):

    @staticmethod
    def handle_programa_creado(evento):
        print('================ PROGRAMACREADO ===========')
        

    