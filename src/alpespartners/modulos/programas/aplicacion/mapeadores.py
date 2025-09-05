from .dto import ProgramaDTO, AfiliacionDTO
from alpespartners.seedwork.aplicacion.dto import Mapeador as AppMap

class MapeadorProgramaDTOJson(AppMap):
    def _procesar_afiliaciones(self, afiliacion:dict) -> AfiliacionDTO:
        return AfiliacionDTO(
            afiliado_id=afiliacion.get("afiliado_id", ""),
            estado=afiliacion.get("estado", ""),
            fecha_alta=afiliacion.get("fecha_alta", ""),
            fecha_baja=afiliacion.get("fecha_baja", ""),
        )
    
    def externo_a_dto(self, externo:dict) -> ProgramaDTO:     
        estado = externo.get("estado", "inactivo")
        tipo = externo.get("tipo", "basico")
        brand_id = externo.get("brand_id", "")
        vigencia_inicio = externo.get("vigencia_inicio", "")
        vigencia_fin = externo.get("vigencia_fin", "")
        term_modelo = externo.get("term_modelo", "mensual")
        term_moneda = externo.get("term_moneda", "USD")
        term_tarifa_base = externo.get("term_tarifa_base", 0.0)
        term_tope = externo.get("term_tope", 0.0)

        programa_dto = ProgramaDTO(estado=estado, tipo=tipo, brand_id=brand_id,
                                   vigencia_inicio=vigencia_inicio, vigencia_fin=vigencia_fin,
                                   term_modelo=term_modelo, term_moneda=term_moneda,
                                   term_tarifa_base=term_tarifa_base, term_tope=term_tope)

        for afiliacion in externo.get("afiliaciones", list()):
            programa_dto.afiliaciones.append(self._procesar_afiliaciones(afiliacion))

        return programa_dto
    
    def dto_a_externo(self, dto:ProgramaDTO) -> dict:
        return dto.__dict__
