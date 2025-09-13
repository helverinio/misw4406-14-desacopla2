from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.db import db

def crear_app(configuracion={}):
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = configuracion.get(
        'SQLALCHEMY_DATABASE_URI', 
        'postgresql://postgres:postgres@postgres:5432/partners_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar blueprints
    from api.partners import bp as partners_bp
    app.register_blueprint(partners_bp)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'gestion-de-integraciones'}, 200
    
    return app
