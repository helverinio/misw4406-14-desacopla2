import logging
import json
import alpespartners.seedwork.presentacion.api as api
import alpespartners.seedwork.dominio.excepciones as ExceptionDominio

from alpespartners.modulos.compliance.aplicacion.mapeadores import MapeadorComplianceDTOJson
from alpespartners.seedwork.aplicacion.comandos import ComandoResultado, ejecutar_commando
from alpespartners.seedwork.aplicacion.queries import QueryResultado, ejecutar_query


from flask import request
from flask import Response

logger = logging.getLogger(__name__)

bp = api.crear_blueprint("compliance", "/compliance")

@bp.route("register", methods=["POST"])
def register_compliance():
    try:
        data = request.json
        logger.info(f"Received compliance registration data: {data}")

        map_payment = MapeadorComplianceDTOJson()
        payment_dto = map_payment.externo_a_dto(data)
        logger.info(f"Mapped payment DTO: {payment_dto}")

        comando: ComandoResultado = ejecutar_commando()

        return map_payment.dto_a_externo(payment_dto)

    except ExceptionDominio as e:
        logger.error(f"Error in compliance registration: {e}")
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')


@bp.route("/check", methods=["GET"])
def check_compliance():
    logger.info("Compliance check executed")
    return {"compliance": "all good"}