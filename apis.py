import requests
import json
import logging
from config import CIRCULO_CREDITO_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CirculoCreditoAPI:
    def __init__(self):
        self.base_url = "https://services.circulodecredito.com.mx"
        self.headers = {
            "x-api-key": CIRCULO_CREDITO_API_KEY,
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint, method='POST', data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=self.headers, params=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def verify_identity(self, curp, rfc):
        """Valida datos personales"""
        data = {
            "curp": curp,
            "rfc": rfc
        }
        return self._make_request("/sandbox/v3/identitydata/verification", data=data)

    def verify_bank_account(self, curp, cuenta_bancaria, banco="012"):
        """Verifica cuenta bancaria (BAVS)"""
        data = {
            "curp": curp,
            "bankAccount": cuenta_bancaria,
            "bankCode": banco
        }
        return self._make_request("/sandbox/v3/bavs/accounts/verification", data=data)

    def verify_employment(self, curp, first_name, last_name, state="CDMX"):
        """Confirma empleo (EVA v3)"""
        data = {
            "address": {
                "state": state,
                "addressLine1": ""
            },
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp
        }
        return self._make_request("/sandbox/v3/eva/employmentverifications/withPrivacyNotice", data=data)

    def check_fraud(self, curp, email=""):
        """Detección de fraude (Guardian Express)"""
        data = {
            "curp": curp,
            "email": email
        }
        return self._make_request("/sandbox/v3/guardian/express", data=data)

    def check_pld(self, first_name, last_name, curp):
        """Validación PLD (sanciones)"""
        data = {
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp
        }
        return self._make_request("/sandbox/v3/pld/persons", data=data)

    def get_fico_score(self, curp):
        """Puntuación FICO extendida (300-850)"""
        data = {"curp": curp}
        return self._make_request("/sandbox/v3/scores/fico/extended", data=data)

    def get_fintech_score(self, curp):
        """Score fintech"""
        data = {"curp": curp}
        return self._make_request("/sandbox/v3/scores/fintech", data=data)

    def estimate_loan_amount(self, curp, ingresos_mensuales, fico_score):
        """Estimación de monto de préstamo"""
        data = {
            "ingresos": ingresos_mensuales,
            "curp": curp,
            "ficoscore": fico_score
        }
        return self._make_request("/sandbox/v3/loanestimator/montoestimado", data=data)

    def get_consolidated_report(self, curp):
        """Reporte consolidado con FICO y PLD"""
        data = {"curp": curp}
        return self._make_request("/sandbox/v3/rcc/consolidated/fico-pld", data=data)

    # Legacy method names for compatibility
    def identity_data(self, curp, rfc, nombre):
        names = nombre.split()
        return self.verify_identity(curp, rfc)

    def bank_account_verification(self, cuenta_bancaria, banco):
        # This needs CURP from context, but for now return None
        logger.warning("bank_account_verification needs CURP parameter")
        return None

    def employment_verification(self, empleador, puesto, antiguedad_meses):
        # This needs names and CURP
        logger.warning("employment_verification needs name and CURP parameters")
        return None

    def guardian_express(self, curp, nombre):
        return self.check_fraud(curp)

    def pld_check(self, curp, rfc):
        # This needs names
        logger.warning("pld_check needs name parameters")
        return None

    def fico_extended_score(self, curp):
        return self.get_fico_score(curp)

    def fintech_score(self, curp):
        return self.get_fintech_score(curp)

    def reporte_consolidado_fico(self, curp):
        return self.get_consolidated_report(curp)

    def loan_amount_estimator(self, ingresos_mensuales, fico_score, dti):
        # This needs CURP
        logger.warning("loan_amount_estimator needs CURP parameter")
        return None

    def reporte_consolidado_completo(self, curp):
        return self.get_consolidated_report(curp)