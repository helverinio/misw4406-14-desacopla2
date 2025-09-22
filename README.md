# AlpesPartners - Arquitectura de Microservicios Basada en Eventos

## Descripción del Proyecto

AlpesPartners es una plataforma de gestión de alianzas estratégicas implementada mediante una arquitectura de microservicios basada en eventos. El sistema maneja el ciclo completo desde la integración de partners hasta la ejecución de campañas, siguiendo los principios de Domain-Driven Design (DDD) y Event-Driven Architecture (EDA).

## Arquitectura del Sistema

### Microservicios Desarrollados

#### 1. Gestión de Integraciones `gestion-de-integraciones/`
**Responsabilidad**: Registro y gestión de partners externos
- **Tecnología**: Flask + SQLAlchemy
- **Base de Datos**: PostgreSQL (Puerto 5432)
- **API REST**: Puerto 5000
- **Funcionalidades**:
  - Creación de partners
  - Gestión de programas de afiliación
  - Validación de datos de integración

#### 2. Gestión Integral de Alianzas `gestion-de-alianzas/`
**Responsabilidad**: Administración de contratos y términos comerciales
- **Tecnología**: FastAPI + SQLAlchemy
- **Base de Datos**: PostgreSQL (Puerto 5435)
- **API REST**: Puerto 8000
- **Funcionalidades**:
  - Creación automática de contratos
  - Gestión de términos comerciales
  - Estados de contratos (Activo, Inactivo, Vencido)

#### 3. Administración Financiera y Compliance `compliance/`
**Responsabilidad**: Validación financiera y cumplimiento normativo
- **Tecnología**: Flask + SQLAlchemy
- **Base de Datos**: PostgreSQL (Puerto 5434)
- **API REST**: Puerto 5004
- **Funcionalidades**:
  - Alta de partners en sistema financiero
  - Validaciones de compliance
  - Reportes financieros

#### 4. Administración de Campañas `src/alpespartners`
**Responsabilidad**: Gestión de campañas de marketing
- **Estado**: Creacion de campañás

### Flujo de Integración de Partners

```mermaid
graph LR
    A[Cliente API] --> B[Gestión Integraciones]
    B --> C[Evento: Partner Creado]
    C --> D[Gestión Alianzas]
    D --> E[Evento: Contrato Creado]
    E --> F[Compliance]
    F --> G[Partner Activo]
```

1. **Creación de Partner**: Cliente envía datos a Gestión de Integraciones vía API REST
2. **Evento de Integración**: Se genera evento `PartnerCreado` en Apache Pulsar
3. **Creación de Contrato**: Gestión de Alianzas recibe evento y crea contrato automáticamente
4. **Evento de Contrato**: Se genera evento `ContratoCreado` 
5. **Alta Financiera**: Compliance recibe evento y da de alta al partner en sistema financiero

## Decisiones Arquitectónicas

### 1. Comunicación Basada en Eventos

**Patrón Seleccionado**: Eventos de Integración con carga mínima de estado
- **Justificación**: Balance entre acoplamiento débil y eficiencia
- **Tecnología**: Apache Pulsar como message broker
- **Esquema de Eventos**: JSON con validación de esquemas

**Ejemplo de Evento**:
```json
{
  "eventType": "PartnerCreado",
  "timestamp": "2025-09-15T03:38:34Z",
  "partnerId": "uuid-123",
  "data": {
    "nombre": "Partner ABC",
    "tipo": "CORPORATIVO"
  }
}
```

## Decisión sobre Eventos y Esquemas

En este proyecto se optó por utilizar **eventos de integración con carga mínima de estado** en lugar de eventos con el estado completo de la entidad. Esta decisión se tomó para reducir el acoplamiento entre microservicios y facilitar la evolución independiente de cada contexto, permitiendo que cada servicio mantenga su propio modelo de datos y lógica de negocio. Los eventos transportan únicamente la información relevante para la integración, evitando exponer detalles internos innecesarios.

Para la serialización de eventos, se eligió **JSON** como formato inicial por su simplicidad, legibilidad y facilidad de integración con herramientas de desarrollo y debugging. Aunque tecnologías como **Avro** o **Protobuf** ofrecen ventajas en validación de esquemas y eficiencia, se consideró que para esta primera entrega la flexibilidad y rapidez de desarrollo de JSON es más conveniente. Sin embargo, la arquitectura está preparada para migrar a Avro o Protobuf en futuras iteraciones, especialmente si se requiere mayor performance, validación estricta o compatibilidad con un Schema Registry.

Respecto al **versionado de eventos (Event Stream Versioning)**, se sigue una estrategia de evolución controlada: los eventos incluyen un campo de versión y se documentan los cambios en los esquemas. Esto permite que los consumidores puedan adaptarse progresivamente a nuevas versiones sin romper la compatibilidad, facilitando la evolución del sistema a medida que crecen los requerimientos de negocio.

## TODO - diseño de los esquemas

---

## Patrones de Almacenamiento: CRUD vs Event Sourcing

Para el almacenamiento de datos en los microservicios, se ha optado por una estrategia híbrida que combina el modelo clásico **CRUD** y el patrón **Event Sourcing**, seleccionando el más adecuado según las necesidades de cada contexto.

- En los servicios de **Gestión de Integraciones** y **Compliance**, se utiliza un modelo CRUD tradicional, ya que estos dominios requieren operaciones directas y simples sobre los datos, priorizando la eficiencia en consultas y la facilidad de integración con herramientas estándar de bases de datos relacionales.

- En el servicio de **Gestión de Alianzas**, se está explorando el uso de Event Sourcing para el manejo de contratos, permitiendo registrar cada cambio como un evento inmutable. Esto facilita la trazabilidad, auditoría y reconstrucción del estado de los contratos a lo largo del tiempo, lo cual es valioso en escenarios donde la historia de cambios es crítica.

Esta combinación permite aprovechar las ventajas de ambos enfoques: la simplicidad y rendimiento del CRUD donde es suficiente, y la potencia de Event Sourcing donde la trazabilidad y la evolución del dominio lo requieren.

---

### 2. Patrones de Almacenamiento 

**Modelo Híbrido Implementado**:
- **CRUD Clásico**: Gestión de Integraciones, Compliance
  - Justificación: Operaciones simples, consultas directas
- **Event Sourcing**: Gestión de Alianzas (parcial)
  - Justificación: Trazabilidad de cambios en contratos
  - Implementación: Eventos de dominio + snapshots

### 3. Persistencia Descentralizada

Cada microservicio maneja su propia base de datos:
- **Gestión Integraciones**: PostgreSQL independiente
- **Gestión Alianzas**: PostgreSQL independiente  
- **Compliance**: PostgreSQL independiente
- **Ventajas**: Autonomía, escalabilidad independiente, tecnologías específicas

## Infraestructura y Despliegue

### Apache Pulsar Configuración Local
```yaml
services:
  zookeeper:
    image: apachepulsar/pulsar:3.2.4
    ports: ["2181:2181"]
  
  broker:
    image: apachepulsar/pulsar:3.2.4
    ports: ["6650:6650", "8081:8080"]
    
  bookkeeper:
    image: apachepulsar/pulsar:3.2.4
```

### Docker Compose Structure
```bash
# Levantar infraestructura base (Pulsar)
docker-compose -f docker-compose.pulsar.yml up -d

# Levantar microservicios
docker-compose up --build

# Servicios individuales
cd gestion-de-alianzas && docker-compose up --build
cd compliance && docker-compose up --build
```

### Tecnologías Utilizadas

- **Lenguaje**: Python 3.12
- **Frameworks Web**: Flask, FastAPI
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 16
- **Message Broker**: Apache Pulsar 3.2.4
- **Contenedores**: Docker + Docker Compose
- **Gestión de Dependencias**: uv

## APIs Disponibles

### Gestión de Integraciones (Puerto 5000)
```bash
POST /programas        
GET  /programas/{id} 
```

### Gestión de Alianzas (Puerto 8000)
```bash
POST /contratos          
GET  /contratos/{id}     
PUT  /contratos/{id}     
```

### Compliance (Puerto 5004)
```bash
GET  /health           
POST /partners/validate 
```

## Entrega Parcial - Cumplimiento de Requisitos

### Requisitos Completados (Entrega 4)

1. **Arquitectura de Microservicios Basada en Eventos**: 
   - 4 microservicios independientes
   - Comunicación asíncrona con Apache Pulsar

2. **Eventos de Integración con Carga Mínima**:
   - Esquema JSON definido
   - Eventos `PartnerCreado` y `ContratoCreado`

3. **Apache Pulsar como Message Broker**: 
   - Configuración con ZooKeeper y BookKeeper
   - Tópicos: `gestion-de-integraciones`, `administracion-financiera-compliance`

4. **Persistencia Descentralizada**:
   - Cada microservicio con su BD PostgreSQL
   - Puertos independientes

5. **Modelos CRUD y Event Sourcing**:
   - CRUD: Integraciones, Compliance
   - Event Sourcing: Alianzas (eventos de dominio)

6. **Despliegue con Docker**: 
   - Docker Compose para cada servicio
   - Configuración de redes y volúmenes

---

## Implementación de Saga Coreográfica (Entrega 5)

### Descripción General

Se implementó un patrón de **Saga Coreográfica** para gestionar transacciones distribuidas en el flujo de registro de partners y creación de contratos. Este patrón permite mantener la consistencia eventual entre microservicios sin necesidad de un coordinador central.

### Flujo Principal de la Saga

```mermaid
graph TD
    A[CreatePartner] --> B[PartnerCreated]
    B --> C[ContratoCreado]
    C --> D[ContratoAprobado/ContratoRechazado]
    D --> E{Estado Final}
    E -->|Aprobado| F[SAGA_COMPLETADA]
    E -->|Rechazado| G[RevisionContrato]
    G --> H[SAGA_PENDIENTE_REVISION]
```

### Eventos Implementados

#### 1. Eventos Principales
- **`CreatePartner`**: Inicia el proceso con datos de formulario y ID temporal
- **`PartnerCreated`**: Partner creado exitosamente
- **`ContratoCreado`**: Contrato generado automáticamente
- **`ContratoAprobado`**: Contrato aprobado por compliance
- **`ContratoRechazado`**: Contrato rechazado por compliance

#### 2. Eventos de Compensación
- **`PartnerCreationFailed`**: Error en creación de partner
- **`ContratoCreadoFailed`**: Error en creación de contrato
- **`RevisionContrato`**: Requiere revisión manual del contrato

### Reglas de Coreografía

El coordinador define las transiciones permitidas entre eventos:

```python
reglas_coreografia = {
    CreatePartner: [PartnerCreated, PartnerCreationFailed],
    PartnerCreated: [ContratoCreado, ContratoCreadoFailed],
    PartnerCreationFailed: [],  # Fin de saga
    ContratoCreado: [ContratoAprobado, ContratoRechazado],
    ContratoCreadoFailed: [],  # Fin de saga
    ContratoAprobado: [],  # Fin exitoso
    ContratoRechazado: [RevisionContrato],
    RevisionContrato: []  # Pendiente de revisión manual
}
```

### Sistema de Logging y Seguimiento

#### Base de Datos de Saga

Se implementó un sistema completo de logging para seguimiento de sagas:

#### Información Registrada

Cada evento de la saga registra:
- **ID de saga**: Identificador único para seguimiento
- **Tipo de evento**: Nombre del evento procesado
- **Datos del evento**: Payload completo en formato JSON
- **Estado**: RECIBIDO, PROCESADO, ERROR
- **Timestamps**: Momentos de recepción y procesamiento
- **Partner ID**: Tanto temporal como real para trazabilidad

#### Ejemplo de Log de Saga

```json
{
  "saga_id": "98273896-af6f-4a48-ad1c-d4780d63d84f",
  "tipo_evento": "PartnerCreated",
  "evento_data": {
    "partner_id": "dd4e7783-842a-467d-8279-93adde1e1e88",
    "evento_tipo": "PartnerCreated",
    "timestamp": "2025-09-22 04:21:22.409921"
  },
  "estado_procesamiento": "RECIBIDO"
}
```

### Manejo de Estados y Compensaciones

#### Estados de Saga
- **`INICIADA`**: Saga creada por evento PartnerCreated
- **`COMPLETADA`**: Flujo exitoso completado
- **`FALLIDA`**: Error irrecuperable ocurrido
- **`PENDIENTE_REVISION`**: Requiere intervención manual

#### Compensaciones Implementadas

##### 1. Compensación por Creación de Partner Fallida
```python
def _procesar_partner_creation_failed(self, evento):
    logger.error(f"❌ PartnerCreationFailed for: {evento.partner_id}")
    logger.error(f"🚫 Error: {evento.error_message}")
    self.terminar(evento.partner_id, exitoso=False)
```

##### 2. Compensación por Contrato Rechazado
```python
def _procesar_contrato_rechazado(self, evento):
    logger.error(f"❌ ContratoRechazado for partner: {evento.partner_id}")
    logger.error(f"🔍 Compliance rejection: {evento.causa_rechazo}")
    # No termina la saga - permite revisión
```

##### 3. Revisión Manual de Contratos
- **Trigger**: Contrato rechazado por compliance
- **Proceso**: Se envía evento `RevisionContrato` 
- **Acción**: El módulo de alianzas actualiza estado a `RECHAZADO`
- **Seguimiento**: Saga queda en estado `PENDIENTE_REVISION`

### Manejo de IDs Temporales vs Reales


### Consumer de Revisión de Contratos
Se implementó un consumer dedicado para manejar eventos de revisión:

```python
class RevisionContratoConsumer:
    def listen_sync(self):
        while True:
            msg = self.consumer.receive()
            data = json.loads(msg.data().decode('utf-8'))
            
            # Buscar contrato por partner_id
            contrato = await self.repository.get_by_partner_id(partner_id)
            
            # Actualizar estado a RECHAZADO
            contrato.estado = EstadoContrato.RECHAZADO
            await self.repository.update(contrato)
```

### Monitoreo y Observabilidad

#### Logs Estructurados
```python
logger.info(f"🚀 Saga iniciada por PartnerCreated para partner: {partner_id}")
logger.info(f"✅ Revision processed successfully for partner: {partner_id}")
logger.error(f"❌ Error processing revision-contrato message: {e}")
```



## Instalación y Ejecución del ambiente

### Prerrequisitos
- Docker y Docker Compose
- Python 3.12+
- uv (gestor de dependencias)

### Ejecución Completa

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd misw4406-14-desacopla2

# 2. Levantar Apache Pulsar
docker-compose -f docker-compose.pulsar.yml up -d

# 3. Verificar que Pulsar esté corriendo
docker ps | grep pulsar

# 4. Levantar servicios principales
docker-compose up --build

# 5. Levantar servicios adicionales
cd gestion-de-alianzas
docker-compose up --build -d

cd ../compliance  
docker-compose up --build -d
```

### Verificación de Servicios

```bash
# Health checks
curl http://34.111.239.116/health          # Gestión Integraciones
curl http://34.144.243.152/docs           # Gestión Alianzas (Swagger)
curl http://34.111.90.7/health        # Compliance

```

## Desarrollo Local

### Sin Docker

```bash
# Instalar dependencias
uv sync

# Configurar PYTHONPATH
export PYTHONPATH="./src"  # Linux/Mac
$env:PYTHONPATH=".\src"    # Windows PowerShell

# Ejecutar servicios individuales
uv run flask --app alpespartners.api run  # Puerto 5000
cd gestion-de-alianzas && uvicorn src.entrypoints.api.main:app --reload  # Puerto 8000
```

### Con Docker (Recomendado)

Usar los comandos de Docker Compose mostrados anteriormente.

## Contribuciones del Equipo

### Distribución de Actividades

- **Carlos Garcia**: Arquitectura base, configuración Pulsar y despliegue, Gestión de Alianzas, Partners BFF
- **Miguel Gomez**: Gestión de Alianzas (FastAPI), Partners BFF
- **Helvert Wiesner**: Compliance, Gestión de Alianzas, Saga
- **Orlando Arnedo**: Gestión de Integraciones, Saga, Escenarios de calidad y estrategia de pruebas

### Commits y Pull Requests
Las contribuciones están registradas en el control de versiones con commits equitativos entre los miembros del equipo.

---

## Documentación Técnica

### Estructura DDD por Microservicio

Cada microservicio sigue la estructura DDD:

```
src/
├── domain/           # Entidades, Value Objects, Eventos
├── application/      # Use Cases, Comandos, Queries  
├── infrastructure/   # Repositorios, BD, Message Brokers
├── entrypoints/      # APIs REST, Consumidores de eventos
└── adapters/         # Adaptadores externos
```

### Eventos de Dominio Implementados

```python
# Ejemplo: PartnerCreado
@dataclass
class PartnerCreado:
    partner_id: str
    nombre: str
    tipo: TipoPartner
    timestamp: datetime
```

### Video de la entrega 4 
[entrega 4 desacoplados](https://youtu.be/u21-_RgLSeY)


### Entrega 5

#### Activar Infraestructura

  ### Crear red para los servicios
  docker network create misw4406-14-desacopla2_default

  ##### Iniciar Apache Pulsar
  docker-compose -f docker-compose.pulsar.yml up

 ##### Gestión de Integraciones
 docker-compose up --build
 database: 5434
 servicio: 5001

##### Gestión de Alianzas
 docker-compose up --build
 database: 5435
 servicio: 5001

##### Compliance
 docker-compose up --build
 database: 5436
 servicio: 5004
