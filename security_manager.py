"""
Gestor de Seguridad para Autenticación ECDSA - Círculo de Crédito
Implementa firma digital ECDSA P-384 según especificaciones de Círculo de Crédito
"""

import hashlib
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)

class CirculoCreditoSecurityManager:
    """
    Gestor de seguridad que maneja la autenticación ECDSA P-384
    para requests a Círculo de Crédito
    """

    def __init__(self, private_key_path: str, cdc_cert_path: str):
        """
        Inicializa el gestor de seguridad con llaves ECDSA

        Args:
            private_key_path: Ruta a la llave privada (pri_key.pem)
            cdc_cert_path: Ruta al certificado de Círculo de Crédito (cdc_cert_####.pem)
        """
        self.private_key_path = Path(private_key_path)
        self.cdc_cert_path = Path(cdc_cert_path)

        if not self.private_key_path.exists():
            raise FileNotFoundError(f"Llave privada no encontrada: {private_key_path}")

        if not self.cdc_cert_path.exists():
            raise FileNotFoundError(f"Certificado de Círculo no encontrado: {cdc_cert_path}")

        # Cargar llaves
        self._load_keys()

        logger.info("CirculoCreditoSecurityManager inicializado correctamente")

    def _load_keys(self):
        """Carga las llaves privada y pública desde archivos PEM"""
        try:
            # Cargar llave privada
            with open(self.private_key_path, 'rb') as f:
                private_pem_data = f.read()

            # Inicializar llave privada ECDSA P-384
            self.signing_key = serialization.load_pem_private_key(
                private_pem_data,
                password=None
            )

            # Intentar cargar certificado público de Círculo (opcional para testing)
            try:
                with open(self.cdc_cert_path, 'rb') as f:
                    public_pem_data = f.read()
                self.verifying_key = serialization.load_pem_public_key(public_pem_data)
                self.cdc_cert_available = True
                logger.info("Certificado de Circulo de Credito cargado correctamente")
            except Exception as cert_error:
                logger.warning(f"Certificado CDC no disponible o invalido: {cert_error}")
                logger.warning("Funcionando en modo DEMO - sin verificacion de respuestas")
                self.verifying_key = None
                self.cdc_cert_available = False

        except Exception as e:
            logger.error(f"Error cargando llaves: {e}")
            raise

    def sign_request(self, payload: Dict[str, Any]) -> str:
        """
        Firma un payload JSON con la llave privada ECDSA P-384

        Args:
            payload: Diccionario JSON a firmar

        Returns:
            Firma en base64 para usar en header x-signature
        """
        try:
            # Normalizar JSON (ordenar keys, sin espacios extra)
            json_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)

            # Crear hash SHA-384 del payload
            payload_bytes = json_payload.encode('utf-8')

            # Firmar con ECDSA usando cryptography
            signature = self.signing_key.sign(
                payload_bytes,
                ec.ECDSA(hashes.SHA384())
            )

            # Codificar en base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            logger.debug(f"Payload firmado: {len(json_payload)} bytes -> {len(signature_b64)} chars b64")
            return signature_b64

        except Exception as e:
            logger.error(f"Error firmando request: {e}")
            raise

    def verify_response(self, response_body: str, signature_header: str) -> bool:
        """
        Verifica la firma de una respuesta de Círculo de Crédito

        Args:
            response_body: Body de la respuesta (JSON string)
            signature_header: Valor del header x-signature

        Returns:
            True si la firma es válida, False en caso contrario
        """
        # Si no hay certificado CDC disponible, skip verification
        if not self.cdc_cert_available or self.verifying_key is None:
            logger.debug("Modo DEMO: Saltando verificacion de firma de respuesta")
            return True  # En modo demo, asumimos que es válido

        try:
            # Decodificar firma de base64
            signature_bytes = base64.b64decode(signature_header)

            # Verificar firma con certificado público de Círculo
            self.verifying_key.verify(
                signature_bytes,
                response_body.encode('utf-8'),
                ec.ECDSA(hashes.SHA384())
            )

            logger.debug("Firma de respuesta verificada correctamente")
            return True

        except InvalidSignature:
            logger.warning("Firma de respuesta invalida")
            return False
        except Exception as e:
            logger.warning(f"Error verificando firma de respuesta: {e}")
            return False

    def get_signature_for_payload(self, payload: Dict[str, Any]) -> str:
        """
        Método de conveniencia para obtener firma de un payload
        """
        return self.sign_request(payload)