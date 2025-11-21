"""
Cliente HTTP Seguro para APIs de Círculo de Crédito
Implementa autenticación ECDSA P-384 completa
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from security_manager import CirculoCreditoSecurityManager

logger = logging.getLogger(__name__)

class SecureCirculoCreditoAPI:
    """
    Cliente HTTP que implementa autenticación completa con firma ECDSA
    para todas las APIs de Círculo de Crédito
    """

    def __init__(self, api_key: str, security_manager: CirculoCreditoSecurityManager):
        """
        Inicializa el cliente seguro

        Args:
            api_key: Consumer Key de Círculo de Crédito
            security_manager: Instancia de CirculoCreditoSecurityManager
        """
        self.api_key = api_key
        self.security = security_manager
        self.base_url = "https://services.circulodecredito.com.mx"
        self.session = requests.Session()

        # Configurar headers base
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })

        logger.info("SecureCirculoCreditoAPI inicializado")

    def _make_signed_request(self, method: str, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza una request firmada con autenticación ECDSA

        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Ruta del endpoint (ej: /sandbox/v3/eva/...)
            body: Diccionario JSON a enviar (opcional)

        Returns:
            Response con validación de firma incluida
        """
        url = f"{self.base_url}{endpoint}"

        # Preparar request
        headers = {}
        json_body = None

        if body:
            # Firmar el payload
            signature = self.security.sign_request(body)
            headers["x-signature"] = signature
            json_body = json.dumps(body, separators=(',', ':'), sort_keys=True)

        try:
            # Enviar request
            if method.upper() == "POST":
                response = self.session.post(url, data=json_body, headers=headers, timeout=30)
            elif method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

            response.raise_for_status()

            # Procesar respuesta
            response_text = response.text
            signature_header = response.headers.get('x-signature', '')

            result = {
                "success": True,
                "data": response.json() if response_text else None,
                "status_code": response.status_code,
                "signature_verified": False
            }

            # Verificar firma de respuesta si está presente
            if signature_header:
                is_valid = self.security.verify_response(response_text, signature_header)
                result["signature_verified"] = is_valid

                if not is_valid:
                    logger.warning("Firma de respuesta inválida - posible suplantación")
                    result["warning"] = "Firma de respuesta no pudo ser verificada"

            logger.info(f"Request exitoso: {method} {endpoint} -> {response.status_code}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Error en request HTTP: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando respuesta JSON: {e}")
            return {
                "success": False,
                "error": f"Respuesta JSON inválida: {e}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {"success": False, "error": f"Error interno: {e}"}

    # ==================== MÉTODOS DE API ====================

    def verify_identity(self, curp: str, rfc: str) -> Dict[str, Any]:
        """Valida datos personales"""
        body = {"curp": curp, "rfc": rfc}
        return self._make_signed_request("POST", "/sandbox/v3/identitydata/verification", body)

    def verify_bank_account(self, curp: str, account: str, bank_code: str = "012") -> Dict[str, Any]:
        """Verifica cuenta bancaria (BAVS)"""
        body = {
            "curp": curp,
            "bankAccount": account,
            "bankCode": bank_code
        }
        return self._make_signed_request("POST", "/sandbox/v3/bavs/accounts/verification", body)

    def verify_employment(self, curp: str, first_name: str, last_name: str, state: str = "CDMX") -> Dict[str, Any]:
        """Confirma empleo (EVA v3)"""
        body = {
            "address": {"state": state, "addressLine1": ""},
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp
        }
        return self._make_signed_request("POST", "/sandbox/v3/eva/employmentverifications/withPrivacyNotice", body)

    def check_fraud(self, curp: str, email: str = "") -> Dict[str, Any]:
        """Detección de fraude (Guardian Express)"""
        body = {"curp": curp, "email": email}
        return self._make_signed_request("POST", "/sandbox/v3/guardian/express", body)

    def check_pld(self, first_name: str, last_name: str, curp: str) -> Dict[str, Any]:
        """Validación PLD (sanciones)"""
        body = {
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp
        }
        return self._make_signed_request("POST", "/sandbox/v3/pld/persons", body)

    def get_fico_score(self, curp: str) -> Dict[str, Any]:
        """Puntuación FICO extendida (300-850)"""
        body = {"curp": curp}
        return self._make_signed_request("POST", "/sandbox/v3/scores/fico/extended", body)

    def get_fintech_score(self, curp: str) -> Dict[str, Any]:
        """Score fintech"""
        body = {"curp": curp}
        return self._make_signed_request("POST", "/sandbox/v3/scores/fintech", body)

    def estimate_loan_amount(self, curp: str, income: float, fico_score: int) -> Dict[str, Any]:
        """Estimación de monto de préstamo"""
        body = {
            "ingresos": income,
            "curp": curp,
            "ficoscore": fico_score
        }
        return self._make_signed_request("POST", "/sandbox/v3/loanestimator/montoestimado", body)

    def get_consolidated_report(self, curp: str) -> Dict[str, Any]:
        """Reporte consolidado con FICO y PLD"""
        body = {"curp": curp}
        return self._make_signed_request("POST", "/sandbox/v3/rcc/consolidated/fico-pld", body)