import logging
import os

# importar blueprint
from alpespartners.api_compliance import compliance

from flask import Flask, jsonify
from flask_swagger import swagger
from sqlalchemy import text

def importar_modelos_alchemy():
    import alpespartners.modulos.compliance.infraestructura.dto

def comenzar_consumidor(app):
    import threading
    import alpespartners.modulos.compliance.infraestructura.consumidores as compliance

    # Suscripción a eventos con contexto de aplicación
    def consumidor_con_contexto():
        with app.app_context():
            compliance.suscribirse_a_eventos()
    
    threading.Thread(target=consumidor_con_contexto).start()

def create_app(configuracion={}):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("alpespartners.api_compliance")
    logger.info("Iniciando la aplicación Flask de Compliance...")
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
            comenzar_consumidor(app)

        logger.info("Base de datos de compliance inicializada correctamente.")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos de compliance: {e}")

    app.register_blueprint(compliance.bp)

    @app.route("/spec")
    def spec():
        logger = logging.getLogger("alpespartners.api_compliance")
        logger.info("Ruta /spec llamada")
        swag = swagger(app)
        swag['info']['title'] = "API de Compliance de Alpes Partners"
        swag['info']['version'] = "1.0"
        return jsonify(swag)
    
    @app.route("/health")
    def health():
        # Prueba de conexión a la base de datos
        import logging
        logger = logging.getLogger("alpespartners.api_compliance")
        logger.info("Ruta /health llamada")

        try:
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
            logger.info("Conexión a la base de datos de compliance exitosa.")
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error(f"Error de conexión a la base de datos de compliance: {e}")
        return {"status": "up", "db_status": db_status}

    logger.info("Aplicación Flask de compliance inicializada correctamente.")
    return app