# Ejecución y medición de campañas o programas de afilaición

import json
import logging

from alpespartners.modulos.programas.aplicacion.comandos.crear_programa import CrearPrograma
from alpespartners.modulos.programas.aplicacion.mapeadores import MapeadorProgramaDTOJson
from alpespartners.modulos.programas.aplicacion.queries.obtener_programa import ObtenerPrograma
from alpespartners.seedwork.dominio.excepciones import ExcepcionDominio
import alpespartners.seedwork.presentacion.api as api

from alpespartners.seedwork.aplicacion.comandos import ComandoResultado, ejecutar_commando
from alpespartners.seedwork.aplicacion.queries import QueryResultado, ejecutar_query

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

        comando: ComandoResultado = ejecutar_commando(CrearPrograma(
            estado=programa_dto.estado,
            tipo=programa_dto.tipo,
            brand_id=programa_dto.brand_id,
            vigencia=programa_dto.vigencia,
            terminos=programa_dto.terminos,
            afiliaciones=programa_dto.afiliaciones,
        ))

        return map_programa.dto_a_externo(comando.resultado)
    except ExcepcionDominio as e:
        logger.error(f"Error al crear programa: {e}")
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
        

@bp.route("/<id>", methods=["GET"])
def obtener_programa(id=None):
    if id:
        query: QueryResultado = ejecutar_query(ObtenerPrograma(id=id))
        return  MapeadorProgramaDTOJson().dto_a_externo(query.resultado)
    else:
        return [{'message': 'GET!'}] 