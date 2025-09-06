

from alpespartners.modulos.programas.dominio.entidades import Programa
from alpespartners.modulos.programas.dominio.objetos_valor import Terminos, Vigencia
from alpespartners.seedwork.dominio.repositorio import Mapeador
from .dto import Programa as ProgramaDTO
from .dto import Afiliacion as AfiliacionDTO
import logging

logging = logging.getLogger(__name__)

class MapeadorPrograma(Mapeador):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def _procesar_afiliaciones(self, afiliacion: any) -> list[AfiliacionDTO]:
        logging.info(f"Procesando afiliacion: {afiliacion}")
        dto = AfiliacionDTO()
        dto.afiliado_id = afiliacion.afiliado_id
        dto.estado = afiliacion.estado
        dto.fecha_alta = afiliacion.fecha_alta
        dto.fecha_baja = afiliacion.fecha_baja
        return [dto]

    def obtener_tipo(self) -> type:
        return Programa.__class__
    
    def entidad_a_dto(self, entidad: Programa) -> ProgramaDTO:
        logging.info(f"Convirtiendo entidad a DTO: {entidad}")
        logging.info(f"brand_id: {entidad.brand_id}")

        programa_dto = ProgramaDTO()
        programa_dto.creado_en = entidad.fecha_creacion
        programa_dto.actualizado_en = entidad.fecha_actualizacion
        programa_dto.programa_id = str(entidad.id)

        programa_dto.estado = entidad.estado.value
        programa_dto.tipo = entidad.tipo.value
        programa_dto.brand_id = str(entidad.brand_id)

        programa_dto.vigencia_inicio = entidad.vigencia.inicio
        programa_dto.vigencia_fin = entidad.vigencia.fin

        programa_dto.term_modelo = entidad.terminos.modelo
        programa_dto.term_moneda = entidad.terminos.moneda
        programa_dto.term_tarifa_base = entidad.terminos.tarifa_base
        programa_dto.term_tope = entidad.terminos.tope

        programa_dto.creado_en = entidad.fecha_creacion
        programa_dto.actualizado_en = entidad.fecha_actualizacion

        afiliaciones_dto = list()

        for afiliacion in entidad.afiliaciones:
            afiliaciones_dto.extend(self._procesar_afiliaciones(afiliacion))
        
        if afiliaciones_dto:
            programa_dto.afiliaciones = afiliaciones_dto 

        return programa_dto


    def dto_a_entidad(self, dto: ProgramaDTO) -> Programa:
        vigencia: Vigencia = Vigencia(dto.vigencia_inicio, dto.vigencia_fin)
        terminos: Terminos = Terminos(dto.term_moneda, dto.term_tarifa_base, dto.term_tope)
        programa = Programa(vigencia=vigencia, terminos=terminos)
        # TODO completar con los demas campos
        return programa