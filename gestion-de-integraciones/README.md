# Gestión de Integraciones y CRM Partners

Servicio independiente para la gestión de partners e integraciones siguiendo arquitectura Domain-Driven Design (DDD).

## Funcionalidades

Este servicio proporciona las siguientes operaciones para la gestión de partners:

1. **Crear Partner** - Registrar un nuevo socio comercial
2. **Actualizar Partner** - Modificar información de un partner existente
3. **Eliminar Partner** - Eliminar un partner del sistema
4. **Verificar KYC Partner** - Gestionar el proceso de verificación KYC
5. **Revocar Integración** - Revocar integraciones técnicas específicas

## Arquitectura

El servicio sigue los principios de Domain-Driven Design (DDD) con la siguiente estructura:

```
gestion-de-integraciones/
├── api/                           # Capa de Presentación
│   ├── __init__.py               # Factory de la aplicación Flask
│   └── partners.py               # Controladores REST para partners
│
├── config/                       # Configuración
│   ├── __init__.py
│   └── db.py                     # Configuración de SQLAlchemy
│
├── modulos/                      # Contextos Acotados
│   └── partners/                 # Módulo de Partners
│       ├── aplicacion/           # Capa de Aplicación
│       │   ├── dto.py           # Data Transfer Objects
│       │   ├── mapeadores.py    # Mappers entre capas
│       │   └── servicios.py     # Servicios de aplicación
│       │
│       ├── dominio/             # Capa de Dominio
│       │   ├── entidades.py     # Entidades (Partner, Integracion)
│       │   ├── excepciones.py   # Excepciones del dominio
│       │   └── repositorios.py  # Interfaces de repositorios
│       │
│       └── infraestructura/     # Capa de Infraestructura
│           ├── dto.py           # Modelos SQLAlchemy
│           ├── mapeadores.py    # Mappers ORM
│           └── repositorios.py  # Implementación de repositorios
│
├── app.py                       # Aplicación principal
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Imagen Docker
├── docker-compose.yml           # Orquestación de servicios
└── README.md                    # Este archivo
```

## Entidades del Dominio

### Partner
- **ID**: Identificador único
- **Nombre**: Nombre del partner
- **Email**: Email único del partner
- **Teléfono**: Número de contacto (opcional)
- **Dirección**: Dirección física (opcional)
- **Estado**: ACTIVO, INACTIVO, SUSPENDIDO, ELIMINADO
- **Estado KYC**: PENDIENTE, APROBADO, RECHAZADO, REQUIERE_DOCUMENTOS
- **Documentos KYC**: Documentos de verificación
- **Integraciones**: Lista de integraciones técnicas

### Integración
- **ID**: Identificador único
- **Partner ID**: Referencia al partner
- **Tipo**: API, WEBHOOK, BATCH, REAL_TIME
- **Nombre**: Nombre descriptivo
- **Descripción**: Descripción detallada (opcional)
- **Configuración**: Configuración técnica (JSON)
- **Activa**: Estado de la integración
- **Fechas**: Creación y revocación

## API Endpoints

### Partners

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/partners` | Crear nuevo partner |
| GET | `/api/v1/partners` | Listar todos los partners |
| GET | `/api/v1/partners/{id}` | Obtener partner por ID |
| PUT | `/api/v1/partners/{id}` | Actualizar partner |
| DELETE | `/api/v1/partners/{id}` | Eliminar partner |
| PUT | `/api/v1/partners/{id}/kyc` | Verificar KYC del partner |

### Integraciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/partners/{id}/integraciones` | Crear integración |
| PUT | `/api/v1/partners/integraciones/{id}/revocar` | Revocar integración |

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificar estado del servicio |

## Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

```bash
# Construir y ejecutar con docker-compose
cd gestion-de-integraciones
docker-compose up --build

# El servicio estará disponible en http://localhost:5001
```

### Opción 2: Instalación Local con uv (Recomendado)

```bash
# Instalar dependencias con uv
cd gestion-de-integraciones
uv sync

# Configurar base de datos PostgreSQL
# Crear base de datos 'partners_db'

# Ejecutar la aplicación
uv run python app.py

# El servicio estará disponible en http://localhost:5001
```

### Comandos útiles de uv

```bash
# Instalar todas las dependencias
uv sync

# Instalar solo las dependencias de producción
uv sync --no-dev

# Agregar una nueva dependencia
uv add <package-name>

# Agregar una dependencia de desarrollo
uv add --dev <package-name>

# Actualizar dependencias
uv lock --upgrade

# Ejecutar comandos en el entorno virtual
uv run <command>
```

### Opción 3: Instalación Local con pip

```bash
# Instalar dependencias
cd gestion-de-integraciones
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
# Crear base de datos 'partners_db'

# Ejecutar la aplicación
python app.py

# El servicio estará disponible en http://localhost:5001
```

## Configuración

### Variables de Entorno

- `SQLALCHEMY_DATABASE_URI`: URL de conexión a PostgreSQL
  - Default: `postgresql://postgres:postgres@localhost:5433/partners_db`
- `FLASK_ENV`: Entorno de Flask (`development` o `production`)
- `FLASK_DEBUG`: Habilitar modo debug (`1` o `0`)

### Base de Datos

El servicio utiliza PostgreSQL como base de datos principal. Las tablas se crean automáticamente al iniciar la aplicación.

**Tablas:**
- `partners`: Información de partners
- `integraciones`: Integraciones técnicas

## Ejemplos de Uso

### Crear Partner

```bash
curl -X POST http://localhost:5001/api/v1/partners \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Empresa ABC",
    "email": "contacto@empresaabc.com",
    "telefono": "+57 300 123 4567",
    "direccion": "Calle 123 #45-67, Bogotá"
  }'
```

### Verificar KYC

```bash
curl -X PUT http://localhost:5001/api/v1/partners/{partner_id}/kyc \
  -H "Content-Type: application/json" \
  -d '{
    "estado_kyc": "APROBADO",
    "documentos": {
      "cedula": "documento_cedula.pdf",
      "rut": "documento_rut.pdf"
    },
    "comentarios": "Documentos verificados correctamente"
  }'
```

### Crear Integración

```bash
curl -X POST http://localhost:5001/api/v1/partners/{partner_id}/integraciones \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "API",
    "nombre": "Integración API REST",
    "descripcion": "Integración para sincronización de datos",
    "configuracion": {
      "endpoint": "https://api.partner.com/webhook",
      "api_key": "secret_key_here"
    }
  }'
```

### Revocar Integración

```bash
curl -X PUT http://localhost:5001/api/v1/partners/integraciones/{integracion_id}/revocar \
  -H "Content-Type: application/json" \
  -d '{
    "motivo": "Cambio de proveedor de servicios"
  }'
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| `DATOS_INVALIDOS` | Datos de entrada inválidos |
| `EMAIL_EXISTENTE` | Email ya registrado |
| `PARTNER_NO_ENCONTRADO` | Partner no existe |
| `PARTNER_ELIMINADO` | Partner está eliminado |
| `INTEGRACION_NO_ENCONTRADA` | Integración no existe |
| `INTEGRACION_YA_REVOCADA` | Integración ya revocada |
| `KYC_INVALIDO` | Estado KYC inválido |
| `ERROR_INTERNO` | Error interno del servidor |

## Desarrollo

### Estructura del Proyecto

El proyecto sigue los principios de Clean Architecture y DDD:

- **Capa de Dominio**: Contiene las reglas de negocio y entidades
- **Capa de Aplicación**: Orquesta casos de uso y coordina el dominio
- **Capa de Infraestructura**: Implementa persistencia y servicios externos
- **Capa de Presentación**: Expone la API REST

### Principios Aplicados

- **Inversión de Dependencias**: Las capas internas no dependen de las externas
- **Separación de Responsabilidades**: Cada capa tiene una responsabilidad específica
- **Repository Pattern**: Abstracción de la persistencia
- **DTO Pattern**: Transferencia de datos entre capas
- **Factory Pattern**: Creación de objetos complejos

## Monitoreo y Logs

El servicio incluye:
- Health check endpoint (`/health`)
- Logging estructurado
- Manejo de excepciones centralizado
- Códigos de error consistentes


## Importante:
 - En caso de correr el servicio de manera aislada, es necesario tener un broker pulsar corriendo en el puerto 6650 lo cual se puede lograr corriendo el comando **docker-compose -f docker-compose.pulsar.yml up -d** en la raiz del proyecto
 - Luego ya puedes correr el servicio con el comando **docker-compose up --build** en el proyecto gestion-de-integraciones