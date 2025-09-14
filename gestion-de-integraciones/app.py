#!/usr/bin/env python3
"""
Aplicación principal para el servicio de Gestión de Integraciones y CRM Partners
"""

from api import crear_app
from config.db import db
import threading

def main():
    """Función principal para ejecutar la aplicación"""
    # Crear la aplicación Flask
    app = crear_app()
    
    # Crear las tablas de base de datos
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from modulos.partners.infraestructura.dto import PartnerModel, IntegracionModel
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas de base de datos creadas exitosamente")
    
    # Inicializar consumidores de eventos en background
    def iniciar_consumidores():
        from modulos.partners.infraestructura.eventos.consumidores import iniciar_consumidor_eventos
        try:
            print("🎧 Iniciando consumidor de eventos externos...")
            iniciar_consumidor_eventos('externos')
        except Exception as e:
            print(f"❌ Error iniciando consumidor de eventos: {e}")
    
    # Ejecutar consumidores en thread separado
    thread_consumidor = threading.Thread(target=iniciar_consumidores, daemon=True)
    thread_consumidor.start()
    
    return app

if __name__ == '__main__':
    app = main()
    print("🚀 Iniciando servicio de Gestión de Integraciones y CRM Partners...")
    print("📍 Endpoints disponibles:")
    print("   - POST   /api/v1/partners                    - Crear partner")
    print("   - GET    /api/v1/partners                    - Listar partners")
    print("   - GET    /api/v1/partners/{id}              - Obtener partner")
    print("   - PUT    /api/v1/partners/{id}              - Actualizar partner")
    print("   - DELETE /api/v1/partners/{id}              - Eliminar partner")
    print("   - PUT    /api/v1/partners/{id}/kyc          - Verificar KYC")
    print("   - POST   /api/v1/partners/{id}/integraciones - Crear integración")
    print("   - PUT    /api/v1/partners/integraciones/{id}/revocar - Revocar integración")
    print("   - GET    /health                            - Health check")
    print()
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
