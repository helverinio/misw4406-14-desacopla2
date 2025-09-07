from pydispatch import dispatcher
from .handlers import HandlerProgramaDominio

dispatcher.connect(HandlerProgramaDominio.handle_programa_creado, signal='ProgramaCreadoDominio')