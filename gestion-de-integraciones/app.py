#!/usr/bin/env python3
"""
Aplicación principal para el servicio de Gestión de Integraciones y CRM Partners
"""

from os import environ
from api import crear_app
from config.db import db
from config.logging_config import configure_logging
import threading
import logging
from modulos.partners.infraestructura.eventos.consumidores import generar_consumidores


def main():
    """Función principal para ejecutar la aplicación"""
    # Configurar logging antes que nada
    configure_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando aplicación de Gestión de Integraciones y CRM Partners")

    # Crear la aplicación Flask
    app = crear_app({"SQLALCHEMY_DATABASE_URI": environ.get("SQLALCHEMY_DATABASE_URI")})

    # Crear las tablas de base de datos
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from modulos.partners.infraestructura.dto import PartnerModel, IntegracionModel

        # Crear todas las tablas
        db.create_all()
        logger.info("✅ Tablas de base de datos creadas exitosamente")

    def start_consumer_with_context(app, consumidor):
        """Wrapper function to run consumer with Flask app context"""
        with app.app_context():
            try:
                consumidor.suscribirse()
            except Exception as e:
                logging.getLogger(__name__).error(f"Consumer error: {e}")

    # Inicializar consumidores de eventos en background
    try:
        logger.info("🎧 Iniciando consumidor de eventos externos...")
        consumidores = generar_consumidores()

        for consumidor in consumidores:
            thread_consumidor = threading.Thread(
                target=start_consumer_with_context, args=(app, consumidor), daemon=True
            )
            thread_consumidor.start()
    except Exception as e:
        logger.error(f"❌ Error iniciando consumidor de eventos: {e}")

    return app


if __name__ == "__main__":
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
    logger.info(
        "   - PUT    /api/v1/partners/integraciones/{id}/revocar - Revocar integración"
    )
    logger.info("   - GET    /health                            - Health check")
    logger.info("")

    app.run(host="0.0.0.0", port=5001, debug=True)
