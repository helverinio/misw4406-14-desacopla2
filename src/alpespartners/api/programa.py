# Ejecución y medición de campañas o programas de afilaición

import json
import logging

from alpespartners.modulos.programas.aplicacion.mapeadores import MapeadorProgramaDTOJson
from alpespartners.modulos.programas.aplicacion.servicio_create import ServicioProgramaCreate
from alpespartners.modulos.programas.aplicacion.servicio_query import ServicioProgramaQuery
from alpespartners.seedwork.dominio.excepciones import ExcepcionDominio
import alpespartners.seedwork.presentacion.api as api


from flask import request
from flask import Response

logger = logging.getLogger(__name__)

bp = api.crear_blueprint("programa", "/programas")

@bp.route("", methods=["POST"])
def crear_programa():
    try:
        programa_dict = request.json

        map_programa = MapeadorProgramaDTOJson()
        programa_dto = map_programa.externo_a_dto(programa_dict)

        logger.info(f"Programa DTO: {programa_dto}")

        sr = ServicioProgramaCreate()
        dto_final = sr.crear_programa(programa_dto)

        return map_programa.dto_a_externo(dto_final)
    except ExcepcionDominio as e:
        logger.error(f"Error al crear programa: {e}")
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
        

@bp.route("/<id>", methods=["GET"])
def obtener_programa(id=None):
    if id:
        sr = ServicioProgramaQuery()

        return sr.obtener_programa_por_id(id)
    else:
        return [{'message': 'GET!'}] 