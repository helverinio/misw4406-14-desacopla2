# Gestión de Alianzas

Este proyecto implementa un sistema de gestión de contratos y publicaciones para alianzas, integrando Apache Pulsar para eventos y una base de datos PostgreSQL para persistencia.

## Características principales

- API REST con FastAPI para la gestión de contratos.
- Integración con Apache Pulsar para consumir y publicar eventos.
- Persistencia en PostgreSQL usando SQLAlchemy (async).
- Arquitectura desacoplada por capas: dominio, infraestructura, adaptadores, entrypoints.

## Estructura del proyecto

```
src/
  adapters/           # Adaptadores para DB y otros servicios
  domain/             # Modelos y casos de uso del dominio
  entrypoints/        # API y routers
  infrastructure/     # Modelos, mappers, integración Pulsar
  scripts/            # Scripts utilitarios (ej: publish_mock_contrato.py)
```

## Instalación

1. Clona el repositorio:
	```
	git clone <url>
	```
2. Instala dependencias:
	```
	pip install -r requirements.txt
	```
3. Configura la base de datos PostgreSQL y variables de entorno según `src/config.py`.

## Uso

### Levantar la API

```
uvicorn src.entrypoints.api.main:app --reload
```

### Consumidor y Publicador Pulsar

Al iniciar la app, se lanza automáticamente el consumidor de Pulsar que escucha el tópico `gestion-de-integraciones` y crea contratos en la base de datos. Cada contrato creado se publica en el tópico `administracion-financiera-compliance`.

### Publicar un evento de prueba

Ejecuta el script:
```
python src/scripts/publish_mock_contrato.py
```
Esto enviará un contrato de prueba al tópico `gestion-de-integraciones`.

## Arquitectura

- **Dominio:** Modelos y lógica de negocio (`src/domain`).
- **Infraestructura:** Modelos de BD, mappers, integración Pulsar (`src/infrastructure`).
- **Adaptadores:** Implementaciones de repositorios y servicios externos (`src/adapters`).
- **Entrypoints:** API REST y routers (`src/entrypoints`).

## Requisitos

- Python 3.11+
- PostgreSQL
- Apache Pulsar corriendo en `localhost:6650`

## Créditos

Desarrollado por el equipo de MISW4406-14.
