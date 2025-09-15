import functools

from flask import(
    Blueprint
)

def crear_blueprint(identificador:str, prefijo_url:str=""):
    bp = Blueprint(identificador, __name__, url_prefix=prefijo_url)
    return bp