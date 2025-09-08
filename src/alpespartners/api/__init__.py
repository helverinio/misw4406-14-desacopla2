import logging

#importar blueprint
from alpespartners.api import programa

from flask import Flask, jsonify
from flask_swagger import swagger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

def importar_modelos_alchemy():
    import alpespartners.modulos.programas.infraestructura.dto

def comenzar_consumidor():
    import threading
    import alpespartners.modulos.notificaciones.infraestructura.consumidores as notificaciones

    # Suscripción a eventos
    threading.Thread(target=notificaciones.suscribirse_a_eventos).start()


def create_app(configuracion={}):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("alpespartners.api")
    logger.info("Iniciando la aplicación Flask...")
    # Init de la aplicación e Flask
    app = Flask(__name__, instance_relative_config=True)


    # Configuración de la base de datos PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.getenv('POSTGRES_HOST', 'db')}:{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'postgres')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #inicializa la BD
    try:
        from alpespartners.config.db import db, init_db
        init_db(app)
        importar_modelos_alchemy()
        
        with app.app_context():
            db.create_all()
            comenzar_consumidor()

        logger.info("Base de datos inicializada correctamente.")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")

    app.register_blueprint(programa.bp)

    @app.route("/spec")
    def spec():
        logger = logging.getLogger("alpespartners.api")
        logger.info("Ruta /spec llamada")
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "My API"
        return jsonify(swag)

    @app.route("/health")
    def health():
        # Prueba de conexión a la base de datos
        import logging
        logger = logging.getLogger("alpespartners.api")
        logger.info("Ruta /health llamada")

        try:
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
            logger.info("Conexión a la base de datos exitosa.")
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error(f"Error de conexión a la base de datos: {e}")
        return {"status": "up", "db_status": db_status}

    logger.info("Aplicación Flask inicializada correctamente.")
    return app
