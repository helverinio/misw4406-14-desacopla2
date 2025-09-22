"""
Comando para procesar compliance de contratos
"""
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
import pulsar
from pulsar.schema import JsonSchema, Record
import uuid

from alpespartners.modulos.compliance.aplicacion.dto import PaymentDTO
from alpespartners.modulos.compliance.aplicacion.mapeadores import MapeadorPayment
from alpespartners.modulos.compliance.infraestructura.repositorios import RepositorioPaymentPostgress
from .base import ComandoBaseHandler
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.modulos.compliance.dominio.entidades import Payment
import alpespartners.modulos.compliance.dominio.objetos_valor as ov

logger = logging.getLogger(__name__)


@dataclass
class ProcesarComplianceContrato(Comando):
    partner_id: str
    contrato_id: str
    monto: float
    moneda: str
    estado: str
    tipo: str = None
    fecha_inicio: str = None
    fecha_fin: str = None


class ContratoAprobado(Record):
    """Evento para contrato aprobado"""
    partner_id = pulsar.schema.String()
    contrato_id = pulsar.schema.String()
    monto = pulsar.schema.Double()
    moneda = pulsar.schema.String()
    estado = pulsar.schema.String()
    tipo = pulsar.schema.String()
    fecha_aprobacion = pulsar.schema.String()
    validaciones_pasadas = pulsar.schema.Array(pulsar.schema.String())


class ContratoRechazado(Record):
    """Evento para contrato rechazado"""
    partner_id = pulsar.schema.String()
    contrato_id = pulsar.schema.String()
    monto = pulsar.schema.Double()
    moneda = pulsar.schema.String()
    estado = pulsar.schema.String()
    tipo = pulsar.schema.String()
    fecha_rechazo = pulsar.schema.String()
    causa_rechazo = pulsar.schema.String()
    validacion_fallida = pulsar.schema.String()


class ProcesarComplianceContratoHandler(ComandoBaseHandler):
    def __init__(self):
        super().__init__()
        self.cliente_pulsar = None
        self.producer_aprobado = None
        self.producer_rechazado = None
        self._inicializar_pulsar()
    
    def _inicializar_pulsar(self):
        """Inicializa cliente y productores de Pulsar"""
        try:
            broker_url = os.getenv('BROKER_URL', 'pulsar://broker:6650')
            self.cliente_pulsar = pulsar.Client(broker_url)
            
            # Crear productores para los eventos de saga usando JSON en lugar de Avro
            self.producer_aprobado = self.cliente_pulsar.create_producer(
                'contrato-aprobado',
                schema=pulsar.schema.StringSchema()  # Cambiar a JSON string
            )
            
            self.producer_rechazado = self.cliente_pulsar.create_producer(
                'contrato-rechazado', 
                schema=pulsar.schema.StringSchema()  # Cambiar a JSON string
            )
            
            logger.info("✅ Cliente Pulsar inicializado para eventos de saga (JSON)")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo conectar a Pulsar: {e}")
            self.cliente_pulsar = None

    def handle(self, comando: ProcesarComplianceContrato):
        resultado_validacion = None
        causa_rechazo = None
        validacion_fallida = None
        
        try:
            logger.info(f"💼 Procesando compliance para partner {comando.partner_id}, contrato {comando.contrato_id}")
            
            # 1. Validar compliance del contrato
            resultado_validacion = self._validar_compliance(comando)
            
            # 2. Crear instancia del repositorio de infraestructura
            repositorio = RepositorioPaymentPostgress()
            
            # 3. Verificar si el partner existe
            partner_existente = self._consultar_partner_existente(repositorio, comando.partner_id)
            
            if partner_existente:
                # 4a. Actualizar partner existente
                self._actualizar_partner_existente(repositorio, partner_existente, comando)
            else:
                # 4b. Registrar nuevo partner
                self._registrar_nuevo_partner(repositorio, comando)
            
            logger.info(f"✅ Compliance procesado exitosamente para partner {comando.partner_id}")
            
            # 5. Publicar evento de contrato aprobado
            self._publicar_contrato_aprobado(comando)
            
        except ValueError as e:
            # Error de validación
            causa_rechazo = str(e)
            validacion_fallida = self._identificar_validacion_fallida(str(e))
            logger.error(f"❌ Validación fallida: {e}")
            
            # Publicar evento de contrato rechazado
            self._publicar_contrato_rechazado(comando, causa_rechazo, validacion_fallida)
            
        except Exception as e:
            # Error técnico
            causa_rechazo = f"Error técnico en procesamiento: {str(e)}"
            validacion_fallida = "ERROR_TECNICO"
            logger.error(f"❌ Error técnico procesando compliance: {e}")
            
            # Publicar evento de contrato rechazado
            self._publicar_contrato_rechazado(comando, causa_rechazo, validacion_fallida)
            
        finally:
            self._cerrar_conexiones()

    def _publicar_contrato_aprobado(self, comando: ProcesarComplianceContrato):
        """Publica evento de contrato aprobado para continuar la saga"""
        if not self.producer_aprobado:
            logger.warning("⚠️ Producer no disponible para contrato-aprobado")
            return
            
        try:
            # Crear el evento como diccionario JSON en lugar de objeto Avro
            evento_data = {
                "partner_id": comando.partner_id,
                "contrato_id": comando.contrato_id,
                "monto": comando.monto,
                "moneda": comando.moneda,
                "estado": comando.estado,
                "tipo": comando.tipo or "STANDARD",
                "fecha_aprobacion": datetime.now().isoformat(),
                "validaciones_pasadas": [
                    "monto_y_limites",
                    "moneda_y_jurisdiccion", 
                    "partner_y_reputacion",
                    "estado_y_vigencia"
                ]
            }
            
            # Enviar como JSON string
            evento_json = json.dumps(evento_data)
            self.producer_aprobado.send(evento_json)
            logger.info(f"📢 Evento ContratoAprobado (JSON) publicado para contrato {comando.contrato_id}")
            logger.info(f"📋 Datos enviados: {evento_json}")
            
        except Exception as e:
            logger.error(f"❌ Error publicando evento aprobado: {e}")

    def _publicar_contrato_rechazado(self, comando: ProcesarComplianceContrato, causa_rechazo: str, validacion_fallida: str):
        """Publica evento de contrato rechazado para terminar la saga"""
        if not self.producer_rechazado:
            logger.warning("⚠️ Producer no disponible para contrato-rechazado")
            return
            
        try:
            # Crear el evento como diccionario JSON en lugar de objeto Avro
            evento_data = {
                "partner_id": comando.partner_id,
                "contrato_id": comando.contrato_id,
                "monto": comando.monto,
                "moneda": comando.moneda,
                "estado": comando.estado,
                "tipo": comando.tipo or "STANDARD",
                "fecha_rechazo": datetime.now().isoformat(),
                "causa_rechazo": causa_rechazo,
                "validacion_fallida": validacion_fallida
            }
            
            # Enviar como JSON string
            evento_json = json.dumps(evento_data)
            self.producer_rechazado.send(evento_json)
            logger.info(f"📢 Evento ContratoRechazado (JSON) publicado para contrato {comando.contrato_id}: {causa_rechazo}")
            logger.info(f"📋 Datos enviados: {evento_json}")
            
        except Exception as e:
            logger.error(f"❌ Error publicando evento rechazado: {e}")

    def _identificar_validacion_fallida(self, mensaje_error: str) -> str:
        """Identifica qué validación específica falló"""
        if "monto" in mensaje_error.lower() or "límite" in mensaje_error.lower():
            return "MONTO_INVALIDO"
        elif "moneda" in mensaje_error.lower():
            return "MONEDA_NO_PERMITIDA"
        elif "partner" in mensaje_error.lower():
            return "PARTNER_INVALIDO"
        elif "estado" in mensaje_error.lower():
            return "ESTADO_INVALIDO"
        else:
            return "VALIDACION_GENERAL"

    def _cerrar_conexiones(self):
        """Cierra las conexiones de Pulsar"""
        try:
            if self.producer_aprobado:
                self.producer_aprobado.close()
            if self.producer_rechazado:
                self.producer_rechazado.close()
            if self.cliente_pulsar:
                self.cliente_pulsar.close()
        except Exception as e:
            logger.warning(f"⚠️ Error cerrando conexiones Pulsar: {e}")

    def _validar_compliance(self, comando: ProcesarComplianceContrato):
        self._validar_monto_y_limites(comando.monto, comando.contrato_id, comando.tipo)
        self._validar_moneda_y_jurisdiccion(comando.moneda)
        self._validar_partner_y_reputacion(comando.partner_id)
        self._validar_estado_y_vigencia(comando.estado, comando)
        
        if comando.tipo:
            self._validar_por_tipo_contrato(comando.tipo, comando)

    def _validar_monto_y_limites(self, monto: float, contrato_id: str, tipo: str):
        if monto > 50000:
            logger.error(f"🚨 Contrato {contrato_id} excede límite máximo permitido: {monto}")
            raise ValueError(f"Monto {monto} excede límite máximo de 50,000")
        
        if monto > 10000:
            logger.warning(f"⚠️ Contrato {contrato_id} requiere aprobación adicional por monto alto: {monto}")
        
        if tipo == "PREMIUM" and monto < 1000:
            logger.warning(f"⚠️ Contrato PREMIUM con monto muy bajo: {monto}")

    def _validar_moneda_y_jurisdiccion(self, moneda: str):
        monedas_permitidas = ["USD", "EUR", "COP", "MXN"]
        
        if moneda not in monedas_permitidas:
            logger.error(f"🚨 Moneda {moneda} no permitida")
            raise ValueError(f"Moneda {moneda} no está en la lista de permitidas")

    def _validar_partner_y_reputacion(self, partner_id: str):
        if not partner_id or len(partner_id) < 10:
            logger.error(f"🚨 Partner ID inválido: {partner_id}")
            raise ValueError("Partner ID inválido")

    def _validar_estado_y_vigencia(self, estado: str, comando: ProcesarComplianceContrato):
        logger.info(f"🔍 Validando estado y vigencia del contrato {comando.contrato_id} con estado {estado}")
        estados_validos = ["ACTIVO", "PENDIENTE", "SUSPENDIDO"]

        if estado.upper() not in estados_validos:
            logger.error(f"🚨 Estado {estado} no válido")
            raise ValueError(f"Estado {estado} no válido")

    def _validar_por_tipo_contrato(self, tipo: str, comando: ProcesarComplianceContrato):
        logger.info(f"🔍 Aplicando validaciones para contrato {tipo}")

    def _consultar_partner_existente(self, repositorio, partner_id: str):
        try:
            partner = repositorio.obtener_por_partner_id(partner_id)
            logger.info(f"✅ Partner {partner_id} encontrado en el sistema")
            return partner
            
        except Exception as e:
            logger.info(f"📋 Partner {partner_id} no encontrado, se creará uno nuevo")
            return None

    def _actualizar_partner_existente(self, repositorio, partner_existente: Payment, comando: ProcesarComplianceContrato):
        logger.info(f"🔄 Actualizando partner existente: {comando.partner_id}")
        
        # Actualizar estado a ACTIVE y fecha de habilitación
        partner_existente.state = ov.PartnerState.ACTIVE
        partner_existente.enable_at = datetime.now().isoformat()
        
        # Actualizar en el repositorio
        repositorio.actualizar(partner_existente)
        
        logger.info(f"✅ Partner {comando.partner_id} actualizado a ACTIVE")

    def _registrar_nuevo_partner(self, repositorio, comando: ProcesarComplianceContrato):
        logger.info(f"➕ Registrando nuevo partner: {comando.partner_id}")
        
        # Crear DTO para el nuevo partner
        payment_dto = PaymentDTO(
            partnerId=comando.partner_id,
            state="ACTIVE", 
            enable_at=datetime.now().isoformat()
        )
        
        # Mapear a entidad de dominio usando la fábrica del repositorio
        payment: Payment = repositorio.fabrica_payment.crear_objeto(
            payment_dto, MapeadorPayment()
        )
        
        # Agregar al repositorio
        repositorio.agregar(payment)
        payment.registrar_partner(payment)
        
        logger.info(f"✅ Nuevo partner {comando.partner_id} registrado exitosamente")


@comando.register(ProcesarComplianceContrato)
def ejecutar_comando_procesar_compliance(
    comando: ProcesarComplianceContrato,
) -> None:
    handler = ProcesarComplianceContratoHandler()
    return handler.handle(comando)