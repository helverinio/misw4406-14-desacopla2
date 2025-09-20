"""
Comando para procesar compliance de contratos
"""
from dataclasses import dataclass
from datetime import datetime
from alpespartners.modulos.compliance.aplicacion.dto import PaymentDTO
from alpespartners.modulos.compliance.aplicacion.mapeadores import MapeadorPayment
from alpespartners.modulos.compliance.infraestructura.repositorios import RepositorioPaymentPostgress
from .base import ComandoBaseHandler
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.modulos.compliance.dominio.entidades import Payment
import alpespartners.modulos.compliance.dominio.objetos_valor as ov

import logging

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


class ProcesarComplianceContratoHandler(ComandoBaseHandler):
    def handle(self, comando: ProcesarComplianceContrato):
        try:
            logger.info(f"💼 Procesando compliance para partner {comando.partner_id}, contrato {comando.contrato_id}")
            
            # 1. Validar compliance del contrato
            self._validar_compliance(comando)
            
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
            
        except Exception as e:
            logger.error(f"❌ Error procesando compliance: {e}")
            raise

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