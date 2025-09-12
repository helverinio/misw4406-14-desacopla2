import logging
import alpespartners.seedwork.presentacion.api as api


logger = logging.getLogger(__name__)

bp = api.crear_blueprint("compliance", "/compliance")

@bp.route("register", methods=["POST"])
def register_compliance():
    logger.info("Compliance registration executed")
    return {"status": "registered"}

@bp.route("/check", methods=["GET"])
def check_compliance():
    logger.info("Compliance check executed")
    return {"compliance": "all good"}