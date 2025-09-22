# Partners BFF (Backend for Frontend)

Este proyecto implementa un servicio Backend for Frontend (BFF) para la gestión de partners, utilizando FastAPI como framework web y Apache Pulsar para la comunicación basada en eventos.

## Características principales

- **API REST con FastAPI**: Servicio web moderno y de alto rendimiento
- **Arquitectura BFF**: Patrón Backend for Frontend para simplificar la comunicación con el frontend
- **Integración con Apache Pulsar**: Publicación de eventos para comunicación asíncrona
- **Integración con Integrations Service**: Comunicación directa con el servicio de integraciones
- **Arquitectura hexagonal**: Separación clara de responsabilidades por capas
- **Health checks**: Endpoint `/ping` para monitoreo de salud del servicio

## Arquitectura del sistema

El Partners BFF actúa como una capa intermedia entre el frontend y los servicios backend, proporcionando:

- **Agregación de datos**: Combina información de múltiples servicios
- **Transformación de datos**: Adapta respuestas para las necesidades del frontend
- **Gestión de eventos**: Publica eventos de creación de partners a través de Pulsar
- **Simplificación de APIs**: Expone endpoints optimizados para el frontend

## Estructura del proyecto

```
src/
├── application/          # Capa de aplicación - servicios y casos de uso
│   └── services.py      # PartnersService - lógica de negocio
├── infrastructure/       # Capa de infraestructura
│   ├── adapters.py      # PartnersAdapter - comunicación con integrations service
│   ├── mappers.py       # Mapeadores de eventos y DTOs
│   ├── pulsar_integration.py  # Integración con Apache Pulsar
│   └── eventos/         # Definiciones de eventos
├── presentation/         # Capa de presentación
│   └── api/            # API REST con FastAPI
│       ├── main.py     # Aplicación principal FastAPI
│       └── routers/    # Definición de endpoints
│           └── v1/     # Versión 1 de la API
│               └── partners_router.py  # Endpoints de partners
├── config.py           # Configuración de la aplicación
└── exceptions.py       # Manejo de excepciones
```

## Instalación y configuración

### Prerrequisitos

- Python 3.11+
- Apache Pulsar (configurado en el cluster)
- Acceso al servicio de integraciones

### Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <url>
   cd partners-bff
   ```

2. **Instala dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura variables de entorno**:
   ```bash
   export APP_NAME="Partners BFF app"
   export LOG_LEVEL="INFO"
   export INTEGRATIONS_API_URL="http://integrations-service:8000"
   export BROKER_URL="pulsar://pulsar-broker.pulsar.svc.cluster.local:6650"
   ```

## Uso

### Desarrollo local

```bash
# Ejecutar en modo desarrollo
uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Despliegue con Docker

```bash
# Construir imagen
docker build -t partners-bff .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e INTEGRATIONS_API_URL="http://integrations-service:8000" \
  -e BROKER_URL="pulsar://pulsar-broker:6650" \
  partners-bff
```

### Despliegue con Helm

```bash
# Instalar chart
helm install partners-bff ./helm/partners-bff

# Verificar despliegue
kubectl get pods -l app.kubernetes.io/name=partners-bff
```

## API Endpoints

### Health Check
- **GET** `/ping` - Verificación de salud del servicio
  - Respuesta: `"pong"`

### Partners
- **GET** `/api/v1/partners/` - Listar todos los partners
  - Integra con el servicio de integraciones
  - Respuesta: Lista de partners

- **POST** `/api/v1/partners/` - Crear un nuevo partner
  - Publica evento de creación en Pulsar
  - Respuesta: `{"message": "Evento de creación de partner publicado"}`
  - Status: `202 Accepted`

## Integración con servicios

### Integrations Service
- **Comunicación**: HTTP REST
- **Endpoints utilizados**:
  - `GET /api/v1/partners` - Obtener lista de partners
  - `POST /api/v1/partners` - Crear partner (a través de eventos)

### Apache Pulsar
- **Propósito**: Publicación de eventos de creación de partners
- **Configuración**: URL del broker configurable via `BROKER_URL`
- **Eventos**: Eventos de creación de partners para procesamiento asíncrono

## Configuración

### Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `APP_NAME` | Nombre de la aplicación | "Gestion de alianzas app" |
| `LOG_LEVEL` | Nivel de logging | "DEBUG" |
| `INTEGRATIONS_API_URL` | URL del servicio de integraciones | "http://localhost:5001" |
| `BROKER_URL` | URL del broker Pulsar | Configurado en Helm |

### Configuración de Helm

El servicio se despliega con las siguientes configuraciones por defecto:

- **Réplicas**: 2
- **Recursos**: 250m CPU, 256Mi memoria (requests)
- **Límites**: 500m CPU, 512Mi memoria
- **Health checks**: `/ping` endpoint
- **Ingress**: Habilitado con clase GCE

## Monitoreo y observabilidad

### Health Checks
- **Liveness Probe**: `/ping` endpoint
- **Readiness Probe**: `/ping` endpoint
- **Health Check**: Verificación de conectividad con servicios externos

### Logging
- Logs estructurados con nivel configurable
- Integración con Cloud Logging (en GKE)
- Trazabilidad de requests y eventos

### Métricas
- Métricas de FastAPI disponibles en `/docs`
- Endpoint OpenAPI en `/openapi.json`
- Métricas de aplicación disponibles para Prometheus

## Arquitectura de capas

### Capa de Presentación (`presentation/`)
- **Responsabilidad**: Manejo de HTTP requests/responses
- **Tecnología**: FastAPI
- **Componentes**: Routers, middleware, manejo de excepciones

### Capa de Aplicación (`application/`)
- **Responsabilidad**: Lógica de negocio y orquestación
- **Componentes**: Services, casos de uso
- **Ejemplo**: `PartnersService` - orquesta operaciones de partners

### Capa de Infraestructura (`infrastructure/`)
- **Responsabilidad**: Integración con servicios externos
- **Componentes**: Adapters, mappers, integración Pulsar
- **Ejemplo**: `PartnersAdapter` - comunicación con integrations service

## Flujo de datos

### Creación de Partner
1. **Frontend** → **Partners BFF** (POST `/api/v1/partners/`)
2. **Partners BFF** → **Pulsar** (Publica evento de creación)
3. **Integrations Service** → **Pulsar** (Consume evento)
4. **Integrations Service** → **Base de datos** (Persiste partner)

### Consulta de Partners
1. **Frontend** → **Partners BFF** (GET `/api/v1/partners/`)
2. **Partners BFF** → **Integrations Service** (GET `/api/v1/partners`)
3. **Integrations Service** → **Base de datos** (Consulta partners)
4. **Integrations Service** → **Partners BFF** (Respuesta)
5. **Partners BFF** → **Frontend** (Respuesta transformada)

## Troubleshooting

### Problemas comunes

1. **Error de conexión con Integrations Service**:
   ```bash
   # Verificar conectividad
   kubectl exec -it <pod-name> -- curl http://integrations-service:8000/api/v1/partners
   ```

2. **Error de conexión con Pulsar**:
   ```bash
   # Verificar configuración del broker
   kubectl get configmap partners-bff-config -o yaml
   ```

3. **Health check fallando**:
   ```bash
   # Verificar logs
   kubectl logs -l app.kubernetes.io/name=partners-bff
   ```

### Comandos útiles

```bash
# Ver logs en tiempo real
kubectl logs -f -l app.kubernetes.io/name=partners-bff

# Port forward para testing local
kubectl port-forward svc/partners-bff 8000:80

# Verificar configuración
kubectl describe pod -l app.kubernetes.io/name=partners-bff

# Test de conectividad
curl http://localhost:8000/ping
curl http://localhost:8000/api/v1/partners/
```

## Desarrollo

### Estructura de desarrollo
- **Testing**: pytest para pruebas unitarias
- **Linting**: Configuración de código estándar
- **Type hints**: Uso de tipos para mejor mantenibilidad
- **Documentación**: Docstrings y documentación automática

### Agregar nuevos endpoints
1. Crear router en `src/presentation/api/routers/v1/`
2. Implementar servicio en `src/application/services.py`
3. Agregar adapter en `src/infrastructure/adapters.py`
4. Actualizar documentación

## Créditos

Desarrollado por el equipo de MISW4406-14 como parte del proyecto AlpesPartners.
