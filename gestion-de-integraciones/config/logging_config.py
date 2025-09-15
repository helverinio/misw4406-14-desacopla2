import logging
import sys
from datetime import datetime

def configure_logging(level=logging.INFO):
    """
    Configura el sistema de logging para la aplicación
    """
    # Crear formatter personalizado
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Configurar loggers específicos para el módulo de partners
    partners_logger = logging.getLogger('modulos.partners')
    partners_logger.setLevel(logging.DEBUG)  # Más detallado para partners
    
    # Configurar logger para eventos
    eventos_logger = logging.getLogger('modulos.partners.infraestructura.eventos')
    eventos_logger.setLevel(logging.DEBUG)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    print(f"✅ Logging configurado - Nivel: {logging.getLevelName(level)}")
    return root_logger

def get_logger(name):
    """
    Obtiene un logger configurado para el módulo especificado
    """
    return logging.getLogger(name)
