import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Círculo de Crédito API Configuration
CIRCULO_CREDITO_API_KEY = os.getenv('CIRCULO_CREDITO_API_KEY', 'aLXRxXTlLm6LC8L3T4PVqJHtssH2rfKs')
CIRCULO_CREDITO_BASE_URL = os.getenv('CIRCULO_CREDITO_BASE_URL', 'https://services.circulodecredito.com.mx/sandbox/v3/')

# Security Configuration (ECDSA)
PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', './security/pri_key.pem')
CDC_CERT_PATH = os.getenv('CDC_CERT_PATH', './security/cdc_cert.pem')

# Anthropic Claude API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Environment
AMBIENTE = os.getenv('AMBIENTE', 'SANDBOX')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Security validation
def validate_security_files():
    """Valida que existan los archivos de seguridad necesarios"""
    pri_key = Path(PRIVATE_KEY_PATH)
    cdc_cert = Path(CDC_CERT_PATH)

    missing = []
    if not pri_key.exists():
        missing.append(f"Llave privada: {PRIVATE_KEY_PATH}")
    if not cdc_cert.exists():
        missing.append(f"Certificado CDC: {CDC_CERT_PATH}")

    if missing:
        raise FileNotFoundError(f"Archivos de seguridad faltantes:\n" + "\n".join(missing))

    return True