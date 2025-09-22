# Sistema de Logging de Saga

## Resumen

Se ha implementado un sistema completo de logging para la saga coreográfica siguiendo los principios de DDD (Domain-Driven Design) y manteniendo la separación por capas. El sistema registra cada evento que escucha la saga en una tabla `saga_logs` en la base de datos del microservicio de alianzas.

## Arquitectura Implementada

### 1. Capa de Dominio

#### Entidad: `SagaLog`
- **Ubicación**: `src/modulos/sagas/dominio/entidades/saga_log.py`
- **Responsabilidad**: Representa un log de evento de saga con toda la lógica de negocio
- **Atributos principales**:
  - `id`: Identificador único del log
  - `saga_id`: Identificador de la saga a la que pertenece
  - `tipo_evento`: Tipo del evento procesado
  - `evento_data`: Datos del evento en formato JSON
  - `estado`: Estado del procesamiento (RECIBIDO, PROCESANDO, PROCESADO, ERROR)
  - `timestamp`: Momento de recepción del evento
  - `mensaje_error`: Mensaje de error si aplica
  - `intentos`: Número de intentos de procesamiento
  - `procesado_en`: Momento de procesamiento exitoso

#### Estados del Evento: `EstadoEvento`
- `RECIBIDO`: Evento recibido pero no procesado
- `PROCESANDO`: Evento en procesamiento
- `PROCESADO`: Evento procesado exitosamente
- `ERROR`: Error en el procesamiento

#### Repositorio Abstracto: `ISagaLogRepository`
- **Ubicación**: `src/modulos/sagas/dominio/repositorios/saga_log_repository.py`
- **Responsabilidad**: Define el contrato para persistencia de logs de saga
- **Métodos principales**:
  - `agregar()`: Persiste un nuevo log
  - `obtener_por_id()`: Busca log por ID
  - `obtener_por_saga_id()`: Obtiene todos los logs de una saga
  - `obtener_por_estado()`: Filtra logs por estado
  - `actualizar()`: Actualiza un log existente
  - `obtener_eventos_pendientes()`: Logs que pueden reprocesarse
  - `obtener_historial_saga()`: Historial completo de una saga

### 2. Capa de Aplicación

#### Servicio: `SagaLogService`
- **Ubicación**: `src/modulos/sagas/aplicacion/servicios/saga_log_service.py`
- **Responsabilidad**: Orquesta las operaciones de logging de saga
- **Funcionalidades principales**:
  - `registrar_evento_recibido()`: Registra nuevo evento
  - `marcar_evento_procesando()`: Cambia estado a procesando
  - `marcar_evento_procesado()`: Marca evento como exitoso
  - `marcar_evento_error()`: Registra error en procesamiento
  - `procesar_evento_con_logging()`: Procesamiento automático con logging
  - `obtener_historial_saga()`: Consulta historial completo
  - Serialización/deserialización automática de datos de evento

### 3. Capa de Infraestructura

#### Modelo de Base de Datos: `SagaLog`
- **Ubicación**: `src/modulos/sagas/infraestructura/dto.py`
- **Responsabilidad**: Mapeo objeto-relacional con SQLAlchemy
- **Características**:
  - Usa SQLAlchemy async para compatibilidad con el microservicio
  - Índices optimizados para consultas frecuentes
  - Enum para estados con validación a nivel de BD
  - Timestamps automáticos de auditoría

#### Repositorio Concreto: `SagaLogRepository`
- **Ubicación**: `src/modulos/sagas/infraestructura/repositorios/saga_log_repository.py`
- **Responsabilidad**: Implementación concreta con SQLAlchemy async
- **Características**:
  - Operaciones asíncronas para mejor rendimiento
  - Conversión automática entre entidades de dominio y DTOs
  - Versión sincronizada para compatibilidad hacia atrás
  - Manejo de transacciones y sesiones

## Integración con Coordinador de Saga

### Modificaciones en `CoordinadorPartnersCoreografico`

El coordinador ha sido actualizado para:

1. **Inyección de Dependencias**: Recibe `SagaLogService` en el constructor
2. **Logging Automático**: Cada evento procesado se registra automáticamente
3. **Gestión de Estados**: Tracking de inicio y fin de saga
4. **Manejo de Errores**: Logging automático de errores de procesamiento
5. **Historial Completo**: Método para consultar historial de eventos

### Flujo de Procesamiento con Logging

```python
def procesar_evento(self, evento: EventoDominio):
    # 1. Obtener saga_id
    saga_id = self.estado_saga[partner_id].get('saga_id')
    
    # 2. Definir procesador
    def procesador():
        self._procesar_evento_interno(evento)
    
    # 3. Procesamiento con logging automático
    exito, error = self.saga_log_service.procesar_evento_con_logging(
        saga_id=saga_id,
        tipo_evento=type(evento).__name__,
        evento_data=evento,
        procesador_callback=procesador
    )
```

## Tabla de Base de Datos

### Estructura: `saga_logs`

```sql
CREATE TABLE saga_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saga_id UUID NOT NULL,
    tipo_evento VARCHAR(200) NOT NULL,
    evento_data TEXT NOT NULL,
    estado ENUM('RECIBIDO', 'PROCESANDO', 'PROCESADO', 'ERROR') NOT NULL DEFAULT 'RECIBIDO',
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    mensaje_error TEXT,
    intentos INTEGER NOT NULL DEFAULT 1,
    procesado_en TIMESTAMP,
    creado_en TIMESTAMP NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices optimizados
CREATE INDEX idx_saga_logs_saga_id_timestamp ON saga_logs(saga_id, timestamp);
CREATE INDEX idx_saga_logs_estado ON saga_logs(estado);
CREATE INDEX idx_saga_logs_tipo_evento ON saga_logs(tipo_evento);
```

## Casos de Uso

### 1. Seguimiento de Saga Completa
- Cada evento de la saga se registra con su estado
- Posibilidad de ver el flujo completo de eventos
- Timestamps precisos para análisis de rendimiento

### 2. Manejo de Errores
- Registro automático de errores con stack trace
- Conteo de intentos de reprocesamiento
- Identificación de patrones de falla

### 3. Reprocesamiento
- Identificación de eventos pendientes o fallidos
- Posibilidad de relanzar eventos específicos
- Control de límites de intentos

### 4. Auditoría y Monitoreo
- Historial completo de todas las sagas
- Métricas de procesamiento y rendimiento
- Trazabilidad completa de eventos

## Configuración y Uso

### 1. Crear Tablas
```bash
# Ejecutar desde src/
python scripts/create_tables.py
```

### 2. Inicializar Servicio
```python
from modulos.sagas.aplicacion.servicios import SagaLogService
from modulos.sagas.infraestructura.repositorios import SagaLogRepository

# Con sesión async
async_session = SessionFactory()
repository = SagaLogRepository(async_session)
service = SagaLogService(repository)
```

### 3. Usar en Coordinador
```python
from modulos.sagas.aplicacion.coordinadores.saga_partners import CoordinadorPartnersCoreografico

coordinador = CoordinadorPartnersCoreografico(saga_log_service=service)
coordinador.procesar_evento(evento)
```

## Beneficios Implementados

### ✅ Cumplimiento de DDD
- Separación clara de responsabilidades por capas
- Entidades de dominio ricas con lógica de negocio
- Repositorios abstractos para invertir dependencias
- Servicios de aplicación que orquestan casos de uso

### ✅ Logging Completo
- Cada evento de saga se registra automáticamente
- Estados de procesamiento tracked en tiempo real
- Mensajes de error capturados y persistidos
- Historial completo de eventos por saga

### ✅ Arquitectura Escalable
- Operaciones asíncronas para mejor rendimiento
- Índices optimizados para consultas frecuentes
- Separación de concerns para mantenibilidad
- Inyección de dependencias para testing

### ✅ Observabilidad
- Trazabilidad completa de eventos
- Métricas de rendimiento disponibles
- Capacidad de debugging mejorada
- Auditoría de operaciones de saga

## Próximos Pasos

1. **Testing**: Implementar pruebas unitarias y de integración
2. **Métricas**: Agregar métricas de Prometheus/Grafana
3. **Alertas**: Configurar alertas para eventos fallidos
4. **Cleanup**: Job de limpieza para logs antiguos
5. **Dashboard**: Interface para visualizar estado de sagas