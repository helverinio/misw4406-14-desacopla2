# Sistema de Eventos - Gestión de Integraciones

Este documento describe la implementación del sistema de eventos en el servicio de Gestión de Integraciones y CRM Partners, siguiendo los patrones existentes del proyecto.

## Arquitectura de Eventos

### Estructura de Directorios
```
modulos/partners/
├── dominio/
│   └── eventos.py                    # Eventos de dominio
├── infraestructura/
│   └── eventos/
│       ├── schema/v1/
│       │   └── eventos.py           # Esquemas Avro para integración
│       ├── mapeadores.py            # Mapeo dominio → integración
│       ├── despachadores.py         # Publicadores de eventos
│       └── consumidores.py          # Consumidores de eventos
```

## Eventos de Dominio

### Eventos Implementados
1. **PartnerCreado** - Se dispara cuando se crea un nuevo partner
2. **PartnerActualizado** - Se dispara cuando se actualiza un partner
3. **PartnerEliminado** - Se dispara cuando se elimina un partner
4. **KYCVerificado** - Se dispara cuando se verifica el KYC de un partner
5. **IntegracionCreada** - Se dispara cuando se crea una nueva integración
6. **IntegracionRevocada** - Se dispara cuando se revoca una integración

### Ejemplo de Uso
```python
from modulos.partners.dominio.eventos import PartnerCreado
from modulos.partners.infraestructura.eventos.despachadores import DespachadorEventosPartner

# Crear evento
evento = PartnerCreado(
    partner_id="partner-123",
    nombre="Acme Corp",
    email="contact@acme.com",
    estado=EstadoPartner.ACTIVO,
    estado_kyc=EstadoKYC.PENDIENTE
)

# Publicar evento
despachador = DespachadorEventosPartner()
despachador.publicar_evento(evento)
```

## Integración con Pulsar

### Tópicos
- **eventos-partners**: Eventos internos del servicio
- **gestion-de-alianzas**: Eventos externos para consumir
- **administracion-financiera-compliance**: Eventos para compliance

### Configuración
```bash
# Variable de entorno para Pulsar
BROKER_URL=pulsar://localhost:6650
```

## Esquemas de Integración

Los eventos siguen el estándar **CloudEvents** con esquemas **Avro**:

```json
{
  "id": "uuid",
  "time": "timestamp_millis",
  "specversion": "v1",
  "type": "PartnerCreado",
  "datacontenttype": "AVRO",
  "service_name": "gestion-de-integraciones",
  "data": {
    "partner_id": "string",
    "nombre": "string",
    "email": "string",
    "estado": "string"
  }
}
```

## Consumidores

### Tipos de Consumidores
1. **Externos**: Procesan eventos de otros servicios
2. **Internos**: Auditoría y métricas de eventos propios

### Inicialización
Los consumidores se inician automáticamente en `app.py`:
```python
# Ejecutar consumidores en background
thread_consumidor = threading.Thread(target=iniciar_consumidores, daemon=True)
thread_consumidor.start()
```

## Integración en Servicios de Aplicación

Cada operación de negocio publica automáticamente sus eventos:

```python
class ServicioPartners:
    def crear_partner(self, dto: CrearPartnerDTO) -> PartnerResponseDTO:
        # ... lógica de negocio ...
        partner_guardado = self.repositorio_partners.guardar(partner)
        
        # Publicar evento
        evento = PartnerCreado(...)
        self.despachador_eventos.publicar_evento(evento)
        
        return self.mapeador_partner.entidad_a_dto(partner_guardado)
```

## Pruebas

### Script de Prueba
```bash
cd gestion-de-integraciones
python scripts/test_events.py
```

Este script demuestra la publicación de todos los tipos de eventos.

## Beneficios

1. **Desacoplamiento**: Los servicios se comunican a través de eventos
2. **Escalabilidad**: Pulsar maneja la distribución y persistencia
3. **Observabilidad**: Eventos estándar con metadatos consistentes
4. **Evolución de Esquemas**: Avro permite cambios compatibles
5. **Auditoría**: Registro completo de eventos de negocio

## Patrones Seguidos

- **Domain-Driven Design**: Eventos de dominio separados de integración
- **CloudEvents**: Estándar para metadatos de eventos
- **Avro**: Serialización con evolución de esquemas
- **Event Sourcing**: Registro inmutable de cambios de estado
- **CQRS**: Separación entre comandos y eventos

## Próximos Pasos

1. Implementar consumidores específicos según necesidades
2. Agregar métricas y monitoreo de eventos
3. Configurar alertas para eventos críticos
4. Implementar replay de eventos para recuperación
