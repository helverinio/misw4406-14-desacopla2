#!/usr/bin/env python3
"""
Aplicación principal para el servicio de Gestión de Integraciones y CRM Partners
"""

from api import crear_app
from config.db import db
from config.logging_config import configure_logging
import threading
import logging

def main():
    """Función principal para ejecutar la aplicación"""
    # Configurar logging antes que nada
    configure_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando aplicación de Gestión de Integraciones y CRM Partners")
    
    # Crear la aplicación Flask
    app = crear_app()
    
    # Crear las tablas de base de datos
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from modulos.partners.infraestructura.dto import PartnerModel, IntegracionModel
        
        # Crear todas las tablas
        db.create_all()
        logger.info("✅ Tablas de base de datos creadas exitosamente")
    
    # Inicializar consumidores de eventos en background
    def iniciar_consumidores():
        from modulos.partners.infraestructura.eventos.consumidores import iniciar_consumidor_eventos
        try:
            logger.info("🎧 Iniciando consumidor de eventos externos...")
            iniciar_consumidor_eventos('externos')
        except Exception as e:
            logger.error(f"❌ Error iniciando consumidor de eventos: {e}")
    
    # Ejecutar consumidores en thread separado
    thread_consumidor = threading.Thread(target=iniciar_consumidores, daemon=True)
    thread_consumidor.start()
    
    return app

if __name__ == '__main__':
    app = main()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando servicio de Gestión de Integraciones y CRM Partners...")
    logger.info("📍 Endpoints disponibles:")
    logger.info("   - POST   /api/v1/partners                    - Crear partner")
    logger.info("   - GET    /api/v1/partners                    - Listar partners")
    logger.info("   - GET    /api/v1/partners/{id}              - Obtener partner")
    logger.info("   - PUT    /api/v1/partners/{id}              - Actualizar partner")
    logger.info("   - DELETE /api/v1/partners/{id}              - Eliminar partner")
    logger.info("   - PUT    /api/v1/partners/{id}/kyc          - Verificar KYC")
    logger.info("   - POST   /api/v1/partners/{id}/integraciones - Crear integración")
    logger.info("   - PUT    /api/v1/partners/integraciones/{id}/revocar - Revocar integración")
    logger.info("   - GET    /health                            - Health check")
    logger.info("")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )