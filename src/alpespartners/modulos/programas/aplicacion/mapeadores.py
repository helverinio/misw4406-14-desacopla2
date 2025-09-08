from alpespartners.modulos.programas.dominio.entidades import Afiliacion, Programa
from alpespartners.modulos.programas.dominio.objetos_valor import Terminos, Vigencia
from .dto import ProgramaDTO, AfiliacionDTO, TerminosDTO, VigenciaDTO
from alpespartners.seedwork.aplicacion.dto import Mapeador as AppMap
from alpespartners.seedwork.dominio.repositorio import Mapeador as RepMap
import logging

logging = logging.getLogger(__name__)


class MapeadorProgramaDTOJson(AppMap):
    def _procesar_afiliaciones(self, afiliacion: dict) -> AfiliacionDTO:
        return AfiliacionDTO(
            afiliado_id=afiliacion.get("afiliado_id", ""),
            estado=afiliacion.get("estado", ""),
            fecha_alta=afiliacion.get("fecha_alta", ""),
            fecha_baja=afiliacion.get("fecha_baja", ""),
        )

    def externo_a_dto(self, externo: dict) -> ProgramaDTO:
        estado = externo.get("estado", "inactivo")
        tipo = externo.get("tipo", "basico")
        brand_id = externo.get("brand_id", "")
        vigencia = VigenciaDTO(
            inicio=externo.get("vigencia_inicio", ""),
            fin=externo.get("vigencia_fin", ""),
        )
        terminos = TerminosDTO(
            modelo=externo.get("term_modelo", "cpa"),
            moneda=externo.get("term_moneda", "USD"),
            tarifa_base=externo.get("term_tarifa_base", 0.0),
            tope=externo.get("term_tope", 0.0),
        )

        programa_dto = ProgramaDTO(
            estado=estado,
            tipo=tipo,
            brand_id=brand_id,
            vigencia=vigencia,
            terminos=terminos,
        )

        for afiliacion in externo.get("afiliaciones", list()):
            programa_dto.afiliaciones.append(self._procesar_afiliaciones(afiliacion))

        return programa_dto

    def dto_a_externo(self, dto: ProgramaDTO) -> dict:
        return dto.__dict__


class MapeadorPrograma(RepMap):
    _FORMATO_FECHA = "%Y-%m-%dT%H:%M:%SZ"

    def _obtener_valor_o_texto(self, campo):
        """Obtiene el .value si es un enum, o el valor directo si es string"""
        return campo.value if hasattr(campo, 'value') else campo

    def _procesar_vigencia(self, vigencia_dto: VigenciaDTO) -> Vigencia:
        return Vigencia(inicio=vigencia_dto.inicio, fin=vigencia_dto.fin)

    def _procesar_terminos(self, terminos_dto: TerminosDTO) -> Terminos:
        return Terminos(
            modelo=terminos_dto.modelo,
            moneda=terminos_dto.moneda,
            tarifa_base=terminos_dto.tarifa_base,
            tope=terminos_dto.tope,
        )

    def _procesar_afiliacion(self, afiliacion_dto: AfiliacionDTO) -> any:
        return Afiliacion(
            afiliado_id=afiliacion_dto.afiliado_id,
            estado=afiliacion_dto.estado,
            fecha_alta=afiliacion_dto.fecha_alta,
            fecha_baja=afiliacion_dto.fecha_baja,
        )
    
    def procesar_afiliacion_dto(self, afiliacion: Afiliacion) -> AfiliacionDTO:
        return AfiliacionDTO(
            afiliacion_id=str(afiliacion.id),
            programa_id=str(afiliacion.programa_id) if hasattr(afiliacion, 'programa_id') else "",
            afiliado_id=afiliacion.afiliado_id,
            estado=afiliacion.estado if hasattr(afiliacion.estado, 'value') else afiliacion.estado,
            fecha_alta=afiliacion.fecha_alta,
            fecha_baja=afiliacion.fecha_baja,
            creado_en=afiliacion.fecha_creacion,
            actualizado_en=afiliacion.fecha_actualizacion
        )
    
    def obtener_tipo(self) -> type:
        return Programa.__class__

    def entidad_a_dto(self, entidad: Programa) -> ProgramaDTO:
        logging.info(f"POST=>Convirtiendo entidad a DTO: {entidad}")

        vigencia = VigenciaDTO(
            inicio=entidad.vigencia.inicio,
            fin=entidad.vigencia.fin
        ) if entidad.vigencia else VigenciaDTO()

        terminos = TerminosDTO(
            modelo=entidad.terminos.modelo,
            moneda=entidad.terminos.moneda,
            tarifa_base=entidad.terminos.tarifa_base,
            tope=entidad.terminos.tope
        ) if entidad.terminos else TerminosDTO()

        afiliaciones_dto = list()
        for afiliacion in entidad.afiliaciones:
            logging.info(f"Afiliacion en entidad_a_dto: {afiliacion}")
            afiliaciones_dto.append(self.procesar_afiliacion_dto(afiliacion))

        return ProgramaDTO(entidad.id, self._obtener_valor_o_texto(entidad.estado), self._obtener_valor_o_texto(entidad.tipo), entidad.brand_id, vigencia, terminos,entidad.fecha_creacion, entidad.fecha_actualizacion, afiliaciones_dto)

    def dto_a_entidad(self, dto: ProgramaDTO) -> Programa:
        logging.info(f"Convirtiendo DTO a entidad: {dto}")
        programa = Programa()
        
        programa.vigencia=self._procesar_vigencia(dto.vigencia)
        programa.terminos=self._procesar_terminos(dto.terminos)
        programa.brand_id=dto.brand_id
        programa.afiliaciones = list()

        afiliaciones_dto: list[AfiliacionDTO] = dto.afiliaciones
        for afiliacion_dto in afiliaciones_dto:
            programa.afiliaciones.append(self._procesar_afiliacion(afiliacion_dto))

        return programa
