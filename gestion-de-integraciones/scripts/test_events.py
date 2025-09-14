#!/usr/bin/env python3
"""
Script de prueba para demostrar el sistema de eventos en gestion-de-integraciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulos.partners.dominio.eventos import (
    PartnerCreado, PartnerActualizado, KYCVerificado, IntegracionCreada
)
from modulos.partners.dominio.entidades import EstadoPartner, EstadoKYC, TipoIntegracion
from modulos.partners.infraestructura.eventos.despachadores import DespachadorEventosPartner
import time

def test_publicar_eventos():
    """Prueba la publicación de eventos"""
    print("🧪 Iniciando prueba de eventos...")
    
    despachador = DespachadorEventosPartner()
    
    try:
        # Evento 1: Partner creado
        print("\n📤 Publicando evento: PartnerCreado")
        evento_partner = PartnerCreado(
            partner_id="partner-123",
            nombre="Acme Corp",
            email="contact@acme.com",
            telefono="+1234567890",
            direccion="123 Main St",
            estado=EstadoPartner.ACTIVO,
            estado_kyc=EstadoKYC.PENDIENTE
        )
        despachador.publicar_evento(evento_partner)
        time.sleep(1)
        
        # Evento 2: KYC verificado
        print("\n📤 Publicando evento: KYCVerificado")
        evento_kyc = KYCVerificado(
            partner_id="partner-123",
            estado_kyc_anterior=EstadoKYC.PENDIENTE,
            estado_kyc_nuevo=EstadoKYC.APROBADO,
            documentos={"cedula": "12345678", "rut": "987654321"},
            observaciones="Documentos verificados correctamente"
        )
        despachador.publicar_evento(evento_kyc)
        time.sleep(1)
        
        # Evento 3: Integración creada
        print("\n📤 Publicando evento: IntegracionCreada")
        evento_integracion = IntegracionCreada(
            integracion_id="int-456",
            partner_id="partner-123",
            tipo=TipoIntegracion.API,
            nombre="API REST Integration",
            descripcion="Integración para sincronización de datos",
            configuracion={"endpoint": "https://api.acme.com", "version": "v1"}
        )
        despachador.publicar_evento(evento_integracion)
        time.sleep(1)
        
        # Evento 4: Partner actualizado
        print("\n📤 Publicando evento: PartnerActualizado")
        evento_actualizado = PartnerActualizado(
            partner_id="partner-123",
            nombre="Acme Corporation",
            email="info@acme.com",
            telefono="+1234567890",
            direccion="456 Business Ave",
            estado=EstadoPartner.ACTIVO,
            estado_anterior=EstadoPartner.ACTIVO
        )
        despachador.publicar_evento(evento_actualizado)
        
        print("\n✅ Todos los eventos fueron publicados exitosamente!")
        print("📊 Resumen de eventos publicados:")
        print("   - PartnerCreado")
        print("   - KYCVerificado") 
        print("   - IntegracionCreada")
        print("   - PartnerActualizado")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Iniciando script de prueba de eventos para gestion-de-integraciones")
    print("📋 Este script demuestra la publicación de eventos siguiendo los patrones existentes")
    print("🔗 Los eventos se publican en el tópico 'eventos-partners' usando Pulsar")
    print()
    
    test_publicar_eventos()
    
    print("\n🎯 Próximos pasos:")
    print("   1. Asegúrate de que Pulsar esté ejecutándose (docker-compose up -d)")
    print("   2. Los eventos se pueden consumir desde otros servicios")
    print("   3. Revisa los logs de Pulsar para verificar la entrega de mensajes")
    print("   4. Implementa consumidores específicos según las necesidades del negocio")
