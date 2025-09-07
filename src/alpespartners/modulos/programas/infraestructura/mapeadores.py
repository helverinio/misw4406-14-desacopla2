from alpespartners.modulos.programas.dominio.entidades import Afiliacion, Programa
from alpespartners.modulos.programas.dominio.eventos import (
    EventoPrograma,
    ProgramaCreado,
)
from alpespartners.modulos.programas.dominio.objetos_valor import Terminos, Vigencia
from alpespartners.modulos.programas.infraestructura.excepciones import (
    NoExisteImplementacionParaTipoFabricaExcepcion,
)
from alpespartners.seedwork.infrastructura.utils import unix_time_millis
from alpespartners.seedwork.dominio.repositorio import Mapeador

from .schema.v1.eventos import ProgramaCreadoPayload, EventoProgramaCreado
from .dto import Programa as ProgramaDTO
from .dto import Afiliacion as AfiliacionDTO
import logging

logging = logging.getLogger(__name__)


class MapeadorPrograma(Mapeador):
    _FORMATO_FECHA = "%Y-%m-%dT%H:%M:%SZ"

    def _procesar_afiliaciones(self, afiliacion: any) -> list[AfiliacionDTO]:
        logging.info(f"Procesando afiliacion: {afiliacion}")
        dto = AfiliacionDTO()
        dto.afiliado_id = afiliacion.afiliado_id
        dto.estado = afiliacion.estado
        dto.fecha_alta = afiliacion.fecha_alta
        dto.fecha_baja = afiliacion.fecha_baja
        return [dto]

    def _procesar_afiliacion_dto(self, afiliaciones_dto: list) -> list[Afiliacion]:
        afiliaciones = list()
        for afiliacion_dto in afiliaciones_dto:
            afiliacion = Afiliacion(
                afiliado_id=afiliacion_dto.afiliado_id,
                estado=afiliacion_dto.estado,
                fecha_alta=afiliacion_dto.fecha_alta,
                fecha_baja=afiliacion_dto.fecha_baja,
            )
            afiliaciones.append(afiliacion)
        return afiliaciones

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
        terminos: Terminos = Terminos(
            dto.term_modelo, dto.term_moneda, dto.term_tarifa_base, dto.term_tope
        )
        programa = Programa(
            id=dto.programa_id,
            estado=dto.estado,
            tipo=dto.tipo,
            brand_id=dto.brand_id,
            vigencia=vigencia,
            terminos=terminos,
        )

        programa.afiliaciones = list()

        afiliaciones_dto: list[AfiliacionDTO] = dto.afiliaciones

        programa.afiliaciones.extend(self._procesar_afiliacion_dto(afiliaciones_dto))
        return programa


class MapeadorEventoDominioPrograma(Mapeador):

    # Versiones aceptadas
    versions = ("v1",)

    LATEST_VERSION = versions[0]

    def __init__(self):
        self.router = {
            ProgramaCreado: self._entidad_a_programa_creado,
        }

    def obtener_tipo(self) -> type:
        return EventoPrograma.__class__

    def es_version_valida(self, version):
        for v in self.versions:
            if v == version:
                return True
        return False

    def _entidad_a_programa_creado(
        self, evento: ProgramaCreado, version=LATEST_VERSION
    ) -> EventoProgramaCreado:
        def v1(evento: ProgramaCreado):
            payload = ProgramaCreadoPayload(
                id_reserva=str(evento.id_programa),
                estado=str(evento.estado),
            )
            evento_integracion = EventoProgramaCreado(id=str(evento.id))
            evento_integracion.id = str(evento.id)
            evento_integracion.time = int(unix_time_millis(evento.fecha_evento))
            evento_integracion.specversion = str(version)
            evento_integracion.type = "ReservaCreada"
            evento_integracion.datacontenttype = "AVRO"
            evento_integracion.service_name = "alpespartners"
            evento_integracion.data = payload

            return evento_integracion

        if not self.es_version_valida(version):
            raise Exception(f"No se sabe procesar la version {version}")

        if version == "v1":
            return v1(evento)

    def entidad_a_dto(
        self, evento: EventoPrograma, version=LATEST_VERSION
    ) -> EventoProgramaCreado:
        func = self.router.get(evento.__class__, None)

        if not func:
            raise NoExisteImplementacionParaTipoFabricaExcepcion

        return func(evento, version=version)

    def dto_a_entidad(self, dto: ProgramaDTO, version=LATEST_VERSION) -> Programa:
        raise NotImplementedError
