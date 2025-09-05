# misw4406-14-desacopla2
proyecto analisis y modelado de datos

# alpesPartners
## Sin Docker
### Instalar dependencias
```bash
pip install -r src/alpespartners/requirements.txt
```

### Ejecutar alpespartners.api
```bash
flask --app alpespartners.api run
```

Si no encuentra el modulo de alpespartners ejecutar 
```bash
$env:PYTHONPATH="E:\miso\8monoliticas\misw4406-14-desacopla2\src"   
```
e intentar iniciar nuevamente

# Ejecutar la aplicación usando Docker-compose
```bash
docker-compose up --build
```


# Requerimientos
[ ]  La comunicación entre los diferentes módulos del servicio DEBE HACERSE por medio de eventos de dominio. Ello implica, que como mínimo su servicio debe contar con dos módulos.
[ ] El servicio DEBE USAR un manejador de base de datos para la persistencia y consulta de los datos.
[ ] Usa un patrón CQS para proveer el claro uso de comandos y eventos en el servicio.
    [ ] tener un comando
    [ ] una consulta
    [ ] eventos relacionados a dicha transacción
[ ] Links al repositorio de acceso público 
[ ] Link con un video 
[ ] usar los patrones, tácticas y métodos aprendidos durante el curso
    [ ] agregaciones
    [ ] contextos acotados
    [ ] inversión de dependencias
    [ ] capas
    [ ] arquitectura cebolla 
