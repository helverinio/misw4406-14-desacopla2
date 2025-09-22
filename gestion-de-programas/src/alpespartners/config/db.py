from flask_sqlalchemy import SQLAlchemy
from flask import Flask


db = SQLAlchemy()

def init_db(app: Flask):
    db.init_app(app)