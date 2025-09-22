from typing import Dict, Any
from .eventos.schema.v1.eventos import (
    ComandoCrearPartner,
    CrearPartnerPayload
)
import uuid
from datetime import datetime

def unix_time_millis(dt):
    """Convert datetime to unix timestamp in milliseconds"""
    import time
    return int(time.mktime(dt.timetuple()) * 1000)


class MapeadorComandoCrearPartner:
    """Mapeador para convertir eventos de dominio a eventos de integración"""
    
    # Versiones aceptadas
    versions = ("v1",)
    LATEST_VERSION = versions[0]

    def es_version_valida(self, version):
        return version in self.versions

    def v1(self, obj: dict):
        payload = CrearPartnerPayload(
            nombre = obj.get("nombre"),
            email = obj.get("email"),
            telefono = obj.get("telefono"),
            direccion = obj.get("direccion")
        )
        
        evento_integracion = ComandoCrearPartner(
            id=str(uuid.uuid4()),
            time=unix_time_millis(datetime.now()),
            specversion="v1",
            type="ComandoCrearPartner",
            datacontenttype="AVRO",
            service_name="partners-bff",
            data=payload
        )
        
        return evento_integracion


    def parse_dict(self, obj: dict, version=LATEST_VERSION):
        if not self.es_version_valida(version):
            raise Exception(f"No se sabe procesar la version {version}")

        if version == "v1":
            return self.v1(obj)
        else:
            raise Exception(f"No se sabe procesar la version {version}")
