import logging
import json
from  alpespartners.modulos.compliance.aplicacion.comandos.registrar_partner import RegistrarPartner
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

        comando: ComandoResultado = ejecutar_commando(RegistrarPartner(
            partner_id=payment_dto.partnerId,
            state=payment_dto.state,
            enable_at=payment_dto.enable_at
        ))

        return Response('{}', status=202, mimetype='application/json')

    except ExceptionDominio as e:
        logger.error(f"Error in compliance registration: {e}")
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')


@bp.route("/check", methods=["GET"])
def check_compliance():
    logger.info("Compliance check executed")
    return {"compliance": "all good"}