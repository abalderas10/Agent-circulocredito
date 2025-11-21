import json
import uuid
import logging
from datetime import datetime
from apis_secure import SecureCirculoCreditoAPI
from security_manager import CirculoCreditoSecurityManager
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CIRCULO_CREDITO_API_KEY, PRIVATE_KEY_PATH, CDC_CERT_PATH, validate_security_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditEvaluationAgent:
    def __init__(self):
        # Validar archivos de seguridad
        validate_security_files()

        # Inicializar gestor de seguridad
        self.security_manager = CirculoCreditoSecurityManager(
            private_key_path=PRIVATE_KEY_PATH,
            cdc_cert_path=CDC_CERT_PATH
        )

        # Inicializar API segura
        self.api = SecureCirculoCreditoAPI(
            api_key=CIRCULO_CREDITO_API_KEY,
            security_manager=self.security_manager
        )

        self.claude = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

    def evaluate_credit_request(self, solicitud):
        """Evalúa una solicitud de crédito siguiendo el flujo definido"""
        solicitud_id = f"CRED-{datetime.now().year}-{uuid.uuid4().hex[:5].upper()}"

        logger.info(f"Iniciando evaluación {solicitud_id}")

        # FASE 1: VALIDACIÓN
        fase1 = self._fase_validacion(solicitud)
        if fase1['estado'] == 'RECHAZADO':
            return self._build_response(solicitud_id, 'RECHAZADO', 1, fase1, None, None, None, None)

        # FASE 2: COMPLIANCE
        fase2 = self._fase_compliance(solicitud)
        if fase2['estado'] == 'RECHAZADO':
            return self._build_response(solicitud_id, 'RECHAZADO', 2, fase1, fase2, None, None, None)

        # FASE 3: ANÁLISIS CREDITICIO
        fase3 = self._fase_crediticio(solicitud)
        if fase3['fico_score'] < 550:
            return self._build_response(solicitud_id, 'RECHAZADO', 3, fase1, fase2, fase3, None, None)

        # FASE 4: CÁLCULO DE MONTO
        fase4 = self._fase_monto(solicitud, fase3['fico_score'])

        # FASE 5: DECISIÓN FINAL
        fase5 = self._fase_decision(solicitud, fase3, fase4)

        estado_final = self._determinar_estado_final(fase3, fase4, solicitud)

        return self._build_response(solicitud_id, estado_final, 5, fase1, fase2, fase3, fase4, fase5)

    def _fase_validacion(self, solicitud):
        """Fase 1: Validación inicial"""
        # Parse names
        names = solicitud['nombre'].split()
        first_name = names[0] if names else ""
        last_name = names[-1] if len(names) > 1 else ""

        identity = self.api.verify_identity(solicitud['curp'], solicitud['rfc'])
        bank = self.api.verify_bank_account(solicitud['curp'], solicitud['cuenta_bancaria'], solicitud.get('banco', '012'))
        employment = self.api.verify_employment(solicitud['curp'], first_name, last_name, solicitud.get('estado', 'CDMX'))

        validado = all([
            identity.get('success', False),
            bank.get('success', False),
            employment.get('success', False)
        ])

        return {
            'estado': 'PASADA' if validado else 'RECHAZADO',
            'identity_data': identity.get('data', {'validado': False}) if identity.get('success') else {'validado': False},
            'bank_verification': bank.get('data', {'validado': False}) if bank.get('success') else {'validado': False},
            'employment_verification': employment.get('data', {'validado': False}) if employment.get('success') else {'validado': False}
        }

    def _fase_compliance(self, solicitud):
        """Fase 2: Compliance y anti-fraude"""
        names = solicitud['nombre'].split()
        first_name = names[0] if names else ""
        last_name = names[-1] if len(names) > 1 else ""

        guardian = self.api.check_fraud(solicitud['curp'], solicitud.get('email', ''))
        pld = self.api.check_pld(first_name, last_name, solicitud['curp'])

        aprobado = (guardian.get('success', False) and not guardian.get('data', {}).get('fraude_detectado', False)) and \
                  (pld.get('success', False) and not pld.get('data', {}).get('en_lista', False))

        return {
            'estado': 'APROBADO' if aprobado else 'RECHAZADO',
            'fraude_detectado': guardian.get('data', {}).get('fraude_detectado', False) if guardian.get('success') else False,
            'pld_check': pld.get('data', {'en_lista': False}) if pld.get('success') else {'en_lista': False}
        }

    def _fase_crediticio(self, solicitud):
        """Fase 3: Análisis crediticio"""
        fico = self.api.get_fico_score(solicitud['curp'])
        fintech = self.api.get_fintech_score(solicitud['curp'])
        reporte = self.api.get_consolidated_report(solicitud['curp'])

        fico_score = fico.get('data', {}).get('score', 0) if fico.get('success') else 0
        fintech_score = fintech.get('data', {}).get('score', 0) if fintech.get('success') else 0

        categoria = self._categorizar_riesgo(fico_score)

        return {
            'fico_score': fico_score,
            'fintech_score': fintech_score,
            'categoria_riesgo': categoria,
            'historial_creditos': reporte.get('data', {}).get('creditos', 0) if reporte.get('success') else 0,
            'deudas_activas': reporte.get('data', {}).get('deudas', 0) if reporte.get('success') else 0,
            'dti': reporte.get('data', {}).get('dti', 0.0) if reporte.get('success') else 0.0
        }

    def _fase_monto(self, solicitud, fico_score):
        """Fase 4: Cálculo de monto"""
        estimator = self.api.estimate_loan_amount(solicitud['curp'], solicitud['ingresos_mensuales'], fico_score)

        return {
            'monto_maximo': estimator.get('data', {}).get('monto_maximo', 0) if estimator.get('success') else 0,
            'tasa_sugerida': estimator.get('data', {}).get('tasa_sugerida', '0%') if estimator.get('success') else '0%',
            'plazo_recomendado': estimator.get('data', {}).get('plazo_recomendado', 12) if estimator.get('success') else 12
        }

    def _fase_decision(self, solicitud, fase3, fase4):
        """Fase 5: Decisión final"""
        reporte = self.api.get_consolidated_report(solicitud['curp'])

        return {
            'reporte_id': f"REP-{datetime.now().year}-{uuid.uuid4().hex[:5].upper()}",
            'recomendacion_final': 'APROBADO',  # Will be determined in _determinar_estado_final
            'motivo': 'Evaluación completada',
            'condiciones': {
                'monto_aprobado': min(solicitud['monto_solicitado'], fase4['monto_maximo']),
                'tasa_interes': fase4['tasa_sugerida'],
                'plazo': solicitud['plazo_meses'],
                'pago_mensual': 0  # Calculate
            }
        }

    def _categorizar_riesgo(self, fico_score):
        if fico_score >= 800:
            return 'MUY_BAJO_RIESGO'
        elif fico_score >= 700:
            return 'BAJO_RIESGO'
        elif fico_score >= 650:
            return 'RIESGO_MODERADO'
        elif fico_score >= 550:
            return 'ALTO_RIESGO'
        else:
            return 'MUY_ALTO_RIESGO'

    def _determinar_estado_final(self, fase3, fase4, solicitud):
        fico = fase3['fico_score']
        monto_solicitado = solicitud['monto_solicitado']

        if fico >= 700 and monto_solicitado <= 500000:
            return 'APROBADO'
        elif fico >= 650 or monto_solicitado > 500000:
            return 'REVISIÓN_MANUAL'
        else:
            return 'RECHAZADO'

    def _build_response(self, solicitud_id, estado, fase_actual, f1, f2, f3, f4, f5):
        response = {
            'solicitud_id': solicitud_id,
            'estado_general': estado,
            'confianza': '95%',  # Placeholder
            'fase_actual': f'{fase_actual}/5',
            'fases': {
                'fase_1_validacion': f1,
                'fase_2_compliance': f2,
                'fase_3_crediticio': f3,
                'fase_4_monto': f4,
                'fase_5_decision': f5
            },
            'resumen_ejecutivo': self._generar_resumen(estado, f3, f4, f5),
            'siguientes_pasos': self._generar_pasos(estado)
        }
        return response

    def _generar_resumen(self, estado, f3, f4, f5):
        if estado == 'APROBADO':
            return f"Solicitante aprobado. FICO {f3['fico_score'] if f3 else 0}, monto máximo {f4['monto_maximo'] if f4 else 0}."
        elif estado == 'REVISIÓN_MANUAL':
            return "Requiere revisión manual por riesgo moderado."
        else:
            return "Solicitud rechazada por criterios de evaluación."

    def _generar_pasos(self, estado):
        if estado == 'APROBADO':
            return ["Enviar oferta por correo", "Solicitar firma digital", "Programar desembolso"]
        elif estado == 'REVISIÓN_MANUAL':
            return ["Transferir a analista humano", "Revisar documentación adicional"]
        else:
            return ["Notificar rechazo", "Proporcionar razones"]