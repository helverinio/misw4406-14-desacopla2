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

# Requerimientos
[x]  La comunicación entre los diferentes módulos del servicio DEBE HACERSE por medio de eventos de dominio. Ello implica, que como mínimo su servicio debe contar con dos módulos.
[X] El servicio DEBE USAR un manejador de base de datos para la persistencia y consulta de los datos.
[x] Usa un patrón CQS para proveer el claro uso de comandos y eventos en el servicio.
    [x] tener un comando
    [x] una consulta
    [x] eventos relacionados a dicha transacción
[x] Links al repositorio de acceso público 
[ ] Link con un video 
[x] usar los patrones, tácticas y métodos aprendidos durante el curso
    [X] agregaciones
    [X] contextos acotados
    [X] inversión de dependencias
    [X] capas
    [X] arquitectura cebolla 
