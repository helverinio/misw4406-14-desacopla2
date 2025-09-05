import alpespartners.seedwork.presentacion.api as api


bp = api.crear_blueprint("programa", "/programas")

@bp.route("/programa", methods=["GET"])
def obtener_programa():
    return {"mensaje": "Programa obtenido correctamente"}