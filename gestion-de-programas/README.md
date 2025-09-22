# Gestión de Programas - AlpesPartners

## Descripción

El servicio de **Gestión de Programas** es parte del ecosistema de microservicios de AlpesPartners. Este servicio se encarga de la administración y gestión de programas, proporcionando una API REST para operaciones CRUD y funcionalidades específicas del dominio de programas.

## Características

- **API REST** construida con Flask
- **Base de datos PostgreSQL** para persistencia de datos
- **Integración con Apache Pulsar** para mensajería asíncrona
- **Arquitectura hexagonal** con separación clara de responsabilidades
- **Documentación automática** con Swagger/OpenAPI
- **Containerización** con Docker
- **Gestión de dependencias** con uv

## Tecnologías

- **Backend**: Python 3.9+, Flask 3.1.1
- **Base de datos**: PostgreSQL 16
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Mensajería**: Apache Pulsar con cliente Avro
- **Documentación**: Flask-Swagger
- **Containerización**: Docker
- **Gestión de dependencias**: uv

## Estructura del Proyecto

```
gestion-de-programas/
├── src/
│   └── alpespartners/
│       ├── __init__.py
│       ├── api_programa/          # Capa de API REST
│       ├── config/                # Configuraciones
│       ├── modulos/               # Lógica de negocio
│       └── seedwork/              # Infraestructura compartida
├── Dockerfile                     # Imagen Docker
├── docker-compose.yml            # Orquestación local
├── pyproject.toml                # Configuración del proyecto
├── uv.lock                       # Lock file de dependencias
└── README.md                     # Este archivo
```

## Requisitos Previos

- **Docker** y **Docker Compose**
- **Python 3.9+** (para desarrollo local)
- **uv** (gestor de dependencias Python)
- **PostgreSQL 16** (si se ejecuta sin Docker)

## Instalación y Configuración

### Desarrollo Local

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd gestion-de-programas
   ```

2. **Instalar dependencias**:
   ```bash
   uv sync
   ```

3. **Configurar variables de entorno**:
   ```bash
   export POSTGRES_DB=alpespartners
   export POSTGRES_USER=postgres_user
   export POSTGRES_PASSWORD=1234
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export BROKER_URL=pulsar://localhost:6650
   ```

4. **Ejecutar la aplicación**:
   ```bash
   uv run flask --app src.alpespartners.api:create_app run --host=0.0.0.0 --port=5000
   ```

### Con Docker

1. **Construir y ejecutar con Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Solo construir la imagen**:
   ```bash
   docker build -t gestion-de-programas .
   ```

## Uso

### API Endpoints

Una vez que el servicio esté ejecutándose, la documentación de la API estará disponible en:

- **Swagger UI**: `http://localhost:5000/api/docs`
- **OpenAPI JSON**: `http://localhost:5000/api/spec`

### Ejemplos de Uso

#### Crear un Programa
```bash
curl -X POST http://localhost:5000/api/programas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Programa de Ejemplo",
    "descripcion": "Descripción del programa",
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-12-31"
  }'
```

#### Obtener Programas
```bash
curl http://localhost:5000/api/programas
```

#### Obtener un Programa por ID
```bash
curl http://localhost:5000/api/programas/1
```

## Desarrollo

### Estructura de la Arquitectura

El servicio sigue una **arquitectura hexagonal** con las siguientes capas:

- **API Layer** (`api_programa/`): Controladores REST y validación de entrada
- **Domain Layer** (`modulos/`): Lógica de negocio y entidades del dominio
- **Infrastructure Layer** (`seedwork/`): Acceso a datos, mensajería y servicios externos

### Herramientas de Desarrollo

- **Linting**: `flake8`
- **Formateo**: `black`
- **Type Checking**: `mypy`
- **Testing**: `pytest`

#### Comandos de Desarrollo

```bash
# Formatear código
uv run black src/

# Verificar linting
uv run flake8 src/

# Verificar tipos
uv run mypy src/

# Ejecutar tests
uv run pytest

# Ejecutar tests con cobertura
uv run pytest --cov=src/
```

### Configuración de la Base de Datos

El servicio utiliza PostgreSQL con las siguientes configuraciones por defecto:

- **Base de datos**: `alpespartners`
- **Usuario**: `postgres_user`
- **Contraseña**: `1234`
- **Puerto**: `5432` (5433 en Docker)

### Integración con Pulsar

El servicio se integra con Apache Pulsar para:

- **Eventos de dominio**: Publicación de eventos cuando se crean/modifican programas
- **Comunicación asíncrona**: Con otros microservicios del ecosistema
- **Serialización**: Utiliza Avro para la serialización de mensajes

## Despliegue

### Variables de Entorno de Producción

```bash
POSTGRES_DB=alpespartners
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=<secure-password>
POSTGRES_HOST=<postgres-host>
POSTGRES_PORT=5432
BROKER_URL=pulsar://<pulsar-host>:6650
FLASK_ENV=production
```

### Docker en Producción

```bash
# Construir imagen para producción
docker build -t gestion-de-programas:latest .

# Ejecutar en producción
docker run -d \
  --name gestion-de-programas \
  -p 5000:5000 \
  -e POSTGRES_DB=alpespartners \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=<password> \
  -e POSTGRES_HOST=<host> \
  -e BROKER_URL=pulsar://<host>:6650 \
  gestion-de-programas:latest
```

## Monitoreo y Logs

- **Logs de aplicación**: Disponibles en stdout/stderr del contenedor
- **Health checks**: Endpoint `/health` para verificar el estado del servicio
- **Métricas**: Integración con sistemas de monitoreo a través de la infraestructura

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a la base de datos**:
   - Verificar que PostgreSQL esté ejecutándose
   - Comprobar las variables de entorno de conexión
   - Verificar la conectividad de red

2. **Error de conexión a Pulsar**:
   - Verificar que Apache Pulsar esté ejecutándose
   - Comprobar la URL del broker
   - Verificar la conectividad de red

3. **Error de dependencias**:
   ```bash
   # Reinstalar dependencias
   uv sync --reinstall
   ```

### Logs de Debug

Para habilitar logs detallados:

```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
```

## Contribución

1. **Fork** el repositorio
2. **Crear** una rama para la feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear** un Pull Request

### Estándares de Código

- Seguir las convenciones de `black` para formateo
- Escribir tests para nuevas funcionalidades
- Documentar APIs y funciones complejas
- Mantener cobertura de tests > 80%

## Licencia

Este proyecto es parte del ecosistema AlpesPartners y está sujeto a los términos de licencia del proyecto principal.

## Contacto

Para preguntas o soporte relacionado con este servicio, contactar al equipo de desarrollo de AlpesPartners.

---

**Versión**: 0.1.0  
**Última actualización**: $(date +%Y-%m-%d)
