#!/usr/bin/env python3
"""
Script de prueba para verificar que el logging de saga funciona correctamente
"""
import sys
import os
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar componentes necesarios
from modulos.sagas.aplicacion.servicios.saga_log_service_factory import SagaLogServiceFactory
from modulos.sagas.dominio.eventos import CreatePartner, ContratoCreado
from modulos.sagas.aplicacion.coordinadores.saga_partners import CoordinadorPartnersCoreografico

async def test_saga_logging():
    """Prueba el sistema de logging de saga completo"""
    
    print("🧪 Testing Saga Logging System")
    print("=" * 50)
    
    try:
        # 1. Crear servicio de logging real
        print("1. Creating real saga log service...")
        saga_log_service = SagaLogServiceFactory.crear_servicio()
        print(f"   ✅ Service created: {type(saga_log_service).__name__}")
        
        # 2. Crear coordinador con el servicio real
        print("2. Creating choreography coordinator...")
        coordinador = CoordinadorPartnersCoreografico(saga_log_service)
        print("   ✅ Coordinator created")
        
        # 3. Crear eventos de prueba
        print("3. Creating test events...")
        partner_id = "test-partner-12345"
        
        evento_create = CreatePartner(
            partner_id=partner_id,
            nombre="Test Partner",
            email="test@example.com"
        )
        
        evento_contrato = ContratoCreado(
            partner_id=partner_id,
            contrato_id="test-contract-67890",
            monto=1000.0,
            moneda="USD"
        )
        
        print(f"   ✅ Events created for partner: {partner_id}")
        
        # 4. Procesar eventos
        print("4. Processing events...")
        print("   Processing CreatePartner event...")
        coordinador.procesar_evento(evento_create)
        print("   ✅ CreatePartner processed")
        
        print("   Processing ContratoCreado event...")
        coordinador.procesar_evento(evento_contrato)
        print("   ✅ ContratoCreado processed")
        
        # 5. Verificar estado de la saga
        print("5. Checking saga state...")
        estado = coordinador.obtener_estado_saga(partner_id)
        print(f"   Saga ID: {estado.get('saga_id')}")
        print(f"   Estado: {estado.get('estado')}")
        print(f"   Eventos: {estado.get('eventos', [])}")
        
        # 6. Obtener historial de la saga
        print("6. Getting saga history...")
        historial = coordinador.obtener_historial_saga(partner_id)
        print(f"   ✅ History entries found: {len(historial)}")
        
        if historial:
            for i, entry in enumerate(historial, 1):
                print(f"   Entry {i}: {entry}")
        
        print("\n🎉 Saga logging test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """Prueba la conexión a la base de datos"""
    
    print("\n🔍 Testing Database Connection")
    print("=" * 50)
    
    try:
        from modulos.sagas.infraestructura.repositorios import RepositorioSagaLogSQLAlchemy
        from modulos.sagas.dominio.entidades import SagaLog, EstadoEvento
        
        print("1. Creating repository...")
        repo = RepositorioSagaLogSQLAlchemy()
        print("   ✅ Repository created")
        
        print("2. Testing database connection...")
        
        # Crear un log de prueba
        saga_log = SagaLog(
            saga_id="test-saga-db-connection",
            tipo_evento="TEST_EVENT",
            evento_data={"test": "database_connection"},
            estado=EstadoEvento.RECIBIDO
        )
        
        # Intentar guardarlo
        await repo.agregar(saga_log)
        print("   ✅ Test saga log saved to database")
        
        # Intentar recuperarlo
        logs = await repo.obtener_por_saga_id("test-saga-db-connection")
        print(f"   ✅ Found {len(logs)} logs for test saga")
        
        print("🎉 Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal que ejecuta todas las pruebas"""
    
    print("🚀 Starting Saga Logging System Tests")
    print("=" * 60)
    
    # Test 1: Database connection
    db_success = await test_database_connection()
    
    # Test 2: Saga logging system
    saga_success = await test_saga_logging()
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"Saga Logging System: {'✅ PASS' if saga_success else '❌ FAIL'}")
    
    if db_success and saga_success:
        print("\n🎉 All tests passed! Saga logging system is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)