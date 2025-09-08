# misw4406-14-desacopla2
proyecto analisis y modelado de datos

# alpesPartners
## Sin Docker
### Instalar dependencias con uv
```bash
# Instalar todas las dependencias
uv sync

# O instalar solo las dependencias de producción
uv sync --no-dev
```

### Ejecutar alpespartners.api
```bash
# Con uv (recomendado)
uv run flask --app alpespartners.api run

# O tradicionalmente
flask --app alpespartners.api run
```

Si no encuentra el modulo de alpespartners ejecutar 
```bash
$env:PYTHONPATH="E:\miso\8monoliticas\misw4406-14-desacopla2\src"   
```
e intentar iniciar nuevamente

### Comandos útiles de uv
```bash
# Agregar una nueva dependencia
uv add <package-name>

# Agregar una dependencia de desarrollo
uv add --dev <package-name>

# Actualizar dependencias
uv lock --upgrade

# Ejecutar comandos en el entorno virtual
uv run <command>
```

# Ejecutar la aplicación usando Docker-compose
```bash
docker-compose up --build
```

# Crear carpeta de persistencia de estado de zookeper / bookkeeper y elevar privilegios
```bash
sudo mkdir -p ./data/zookeeper ./data/bookkeeper
sudo chown -R 10000 data
```

## Servicios disponibles

- **Web App**: http://localhost:5000 - Aplicación Flask principal
- **PostgreSQL**: localhost:5433 - Base de datos
- **Apache Pulsar**: 
  - Service URL: pulsar://localhost:6650
  - Admin URL: http://localhost:8080

## Colección de postman
Nuestro servicio cuenta con una coleccion de postman donde puedes interactuar con los siguientes servicios:

1. POST /programas
2. GET /programas/:id

[Link a postman](/postman/AlpesPartners.postman_collection.json)

# Arquitectura del Proyecto (DDD)

## Estructura de Carpetas

```
src/
└── alpespartners/
    ├── api/                     # Capa de Presentación
    │   ├── __init__.py         # Configuración y factory de la aplicación Flask
    │   └── programa.py         # Controladores REST para el módulo de programas
    │
    ├── config/                 # Configuración de infraestructura
    │   └── db.py              # Configuración de SQLAlchemy
    │
    ├── modulos/               # Contextos Acotados (Bounded Contexts)
    │   └── programas/         # Módulo de Programas de Afiliación
    │       ├── aplicacion/    # Capa de Aplicación
    │       │   ├── comandos/  # Comandos (CQS)
    │       │   │   └── crear_programa.py
    │       │   ├── queries/   # Consultas (CQS)
    │       │   │   └── obtener_programa.py
    │       │   ├── dto.py     # Data Transfer Objects
    │       │   ├── mapeadores.py # Mappers entre capas
    │       │   └── servicios.py  # Servicios de aplicación
    │       │
    │       ├── dominio/       # Capa de Dominio
    │       │   ├── entidades.py    # Entidades del dominio (Programa, Afiliacion)
    │       │   ├── eventos.py      # Eventos de dominio
    │       │   ├── excepciones.py  # Excepciones del dominio
    │       │   ├── fabricas.py     # Factory pattern
    │       │   ├── objetos_valor.py # Value Objects (Vigencia, Terminos)
    │       │   └── repositorios.py # Interfaces de repositorios
    │       │
    │       └── infraestructura/ # Capa de Infraestructura
    │           ├── dto.py       # DTOs para persistencia
    │           ├── mapeadores.py # Mappers ORM
    │           └── repositorios.py # Implementación de repositorios
    │
    └── seedwork/              # Código Compartido (Shared Kernel)
        ├── aplicacion/        # Abstracciones de aplicación
        │   ├── comandos.py    # Base para comandos
        │   ├── dto.py         # DTOs base
        │   └── queries.py     # Base para consultas
        │
        └── dominio/           # Abstracciones de dominio
            ├── entidades.py   # Entidad base, Agregación Raíz
            ├── eventos.py     # Eventos base
            ├── excepciones.py # Excepciones base
            ├── mixins.py      # Mixins de validación
            ├── reglas.py      # Reglas de negocio base
            └── repositorio.py # Interfaces base de repositorios
```

## Módulos Desarrollados

### 1. Módulo de Programas (`modulos/programas/`)
Contexto acotado que maneja la gestión de programas de afiliación y sus afiliaciones asociadas.

**Entidades principales:**
- `Programa`: Agregación raíz que representa un programa de afiliación
- `Afiliacion`: Entidad que representa la afiliación de un partner a un programa

**Objetos de Valor:**
- `Vigencia`: Período de tiempo del programa (inicio/fin)
- `Terminos`: Condiciones comerciales (moneda, tarifa base, tope)

**Casos de Uso:**
- Crear programa de afiliación
- Obtener programa por ID
- Gestionar afiliaciones

### 2. Seedwork (`seedwork/`)
Código compartido entre todos los contextos acotados que implementa:

- **Entidades base**: Patrón Entity con ID inmutable
- **Agregación Raíz**: Base para agregaciones con eventos de dominio
- **Comandos y Consultas**: Implementación del patrón CQS
- **Repositorios**: Interfaces base para persistencia
- **Eventos de Dominio**: Infraestructura para comunicación entre módulos

## Capas de la Arquitectura

### Capa de Presentación (`api/`)
- Controladores REST con Flask
- Manejo de rutas HTTP
- Serialización/deserialización JSON

### Capa de Aplicación (`modulos/{modulo}/aplicacion/`)
- Servicios de aplicación
- Comandos y consultas (CQS)
- Coordinación de casos de uso
- Mapeo entre DTOs y entidades

### Capa de Dominio (`modulos/{modulo}/dominio/`)
- Entidades y agregaciones
- Objetos de valor
- Eventos de dominio
- Reglas de negocio
- Interfaces de repositorios

### Capa de Infraestructura (`modulos/{modulo}/infraestructura/`)
- Implementación de repositorios
- Persistencia con SQLAlchemy
- Mapeo ORM
- Adaptadores externos

## Patrones/Filosofia Implementados

- **Domain-Driven Design (DDD)**: Estructura modular por contextos acotados
- **Arquitectura Cebolla**: Dependencias hacia el centro (dominio)
- **Inversión de Dependencias**: Interfaces en dominio, implementaciones en infraestructura
- **CQS (Command Query Separation)**: Separación clara entre comandos y consultas
- **Repository Pattern**: Abstracción de persistencia
- **Factory Pattern**: Creación de objetos complejos
- **Event-Driven Architecture**: Comunicación mediante eventos de dominio
