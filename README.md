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