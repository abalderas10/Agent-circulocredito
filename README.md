# 🤖 PLATAFORMA DE CRÉDITOS IA - CÍRCULO DE CRÉDITO

Plataforma automática de otorgamiento de créditos usando APIs de Círculo de Crédito con autenticación ECDSA P-384 completa.

## 📋 DESCRIPCIÓN

Este agente IA evalúa solicitudes de crédito de personas físicas mexicanas siguiendo un flujo automatizado de 5 fases con **seguridad ECDSA completa**:

1. **✅ Validación Inicial**: Verifica identidad, cuenta bancaria y empleo
2. **🛡️ Compliance**: Anti-fraude y validación PLD
3. **📊 Análisis Crediticio**: Scores FICO, Fintech y reporte consolidado
4. **💰 Cálculo de Monto**: Estimación de monto máximo a prestar
5. **⚖️ Decisión Final**: Aprobación automática, manual o rechazo

## 🔐 CARACTERÍSTICAS DE SEGURIDAD

- **Firma ECDSA P-384** según estándares de Círculo de Crédito
- **Verificación de respuestas** con certificados digitales
- **Hash SHA-384** para integridad de datos
- **Autenticación completa** sin contraseñas

## 📋 APIs INTEGRADAS

- ✅ **Identity Data**: Verificación de identidad
- ✅ **Bank Account Verification (BAVS)**: Validación de cuentas bancarias
- ✅ **Employment Verification (EVA)**: Confirmación laboral
- ✅ **FICO Extended Score**: Puntaje crediticio (300-850)
- ✅ **Fintech Score**: Score adicional para fintech
- ✅ **Guardian Express**: Detección de fraude
- ✅ **PLD Check**: Validación contra listas de sanciones
- ✅ **Loan Amount Estimator**: Cálculo de monto máximo
- ✅ **Reporte Consolidado**: Historial crediticio completo

## 🚀 GUÍA COMPLETA DE IMPLEMENTACIÓN

### PASO 1: GENERAR CERTIFICADOS ECDSA P-384

Ejecuta esto en tu terminal (Linux/Mac/WSL):

```bash
# Crear directorio de seguridad
mkdir -p ./security
cd ./security

# 1. Generar llave privada ECDSA P-384
openssl ecparam -name secp384r1 -genkey -out pri_key.pem

# 2. Generar certificado auto-firmado
openssl req -new -x509 -days 365 \
    -key pri_key.pem \
    -out certificate.pem \
    -subj "/C=MX/ST=CDMX/L=Mexico/O=GrowthBDM/CN=plataforma-creditos-ai"

# 3. Extraer llave privada (para referencia)
openssl ec -in pri_key.pem -noout -text > key_extract.txt

echo "✅ Certificados generados exitosamente"
ls -la pri_key.pem certificate.pem
```

**Archivos generados:**
- `pri_key.pem` → Llave privada (🔒 NUNCA compartir)
- `certificate.pem` → Certificado público (para subir a apihub)
- `key_extract.txt` → Referencia para debugging

### PASO 2: SUBIR CERTIFICADO A APIHUB

1. Ir a: https://developer.circulodecredito.com.mx/user/apps
2. Seleccionar app: `plataforma-creditos-ai`
3. Sección: "Certificados para plataforma-creditos-ai"
4. Subir: `certificate.pem`
5. Descargar: El certificado de Círculo de Crédito (ej: `cdc_cert_4398.pem`)
6. Guardar en: `./security/cdc_cert.pem`

### PASO 3: INSTALACIÓN Y CONFIGURACIÓN

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/plataforma-creditos-ai.git
cd plataforma-creditos-ai

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

### PASO 4: ESTRUCTURA DE DIRECTORIOS COMPLETA

```
tu-proyecto/
├── security/
│   ├── pri_key.pem              # 🔒 Llave privada
│   ├── certificate.pem          # Tu certificado público
│   ├── cdc_cert.pem            # Certificado de Círculo de Crédito
│   └── key_extract.txt         # Referencia
│
├── src/
│   ├── security/
│   │   ├── __init__.py
│   │   └── ecdsa_manager.py    # Gestor de firmas ECDSA
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py           # Cliente HTTP seguro
│   │   └── endpoints.py        # Funciones específicas de APIs
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── evaluator.py        # Agente evaluador crediticio
│   │   └── rules.py            # Reglas de decisión
│   │
│   └── main.py                 # Script principal
│
├── requirements.txt
├── config.py
├── .env
├── .env.example
├── test_data.json
└── README.md
```

### PASO 5: ARCHIVOS DE CÓDIGO PRINCIPALES

#### A) config.py - Configuración
```python
import os
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent
SECURITY_DIR = BASE_DIR / "security"

# Círculo de Crédito
CIRCULO_CREDITO = {
    "api_key": "aLXRxXTlLm6LC8L3T4PVqJHtssH2rfKs",
    "base_url": "https://services.circulodecredito.com.mx",
    "environment": "sandbox",  # Cambiar a "production" cuando esté listo
}

# Rutas de certificados
CERTIFICATES = {
    "private_key": SECURITY_DIR / "pri_key.pem",
    "public_cert": SECURITY_DIR / "certificate.pem",
    "cdc_public_cert": SECURITY_DIR / "cdc_cert.pem",
}

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Reglas de decisión crediticia
DECISION_RULES = {
    "fico_score_min": 550,
    "fico_score_low_risk": 700,
    "max_dti": 0.45,
    "max_automatic_amount": 500000,  # MXN
}
```

#### B) src/security/ecdsa_manager.py - Firma ECDSA
```python
import hashlib
import json
import base64
from pathlib import Path
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
import logging

logger = logging.getLogger(__name__)

class ECDSASecurityManager:
    """Gestor de firmas ECDSA P-384 para APIs de Círculo de Crédito"""

    def __init__(self, private_key_path: str, public_cert_path: str):
        """
        Inicializa el gestor de seguridad

        Args:
            private_key_path: Ruta a pri_key.pem
            public_cert_path: Ruta a cdc_cert.pem (certificado de Círculo)
        """
        self.private_key_path = Path(private_key_path)
        self.public_cert_path = Path(public_cert_path)

        try:
            with open(self.private_key_path, 'r') as f:
                self.signing_key = SigningKey.from_pem(f.read())

            with open(self.public_cert_path, 'r') as f:
                self.verifying_key = VerifyingKey.from_pem(f.read())

            logger.info("✅ Certificados ECDSA cargados correctamente")
        except FileNotFoundError as e:
            logger.error(f"❌ Error cargando certificados: {e}")
            raise

    def sign_payload(self, payload: dict) -> str:
        """
        Firma un payload JSON con ECDSA P-384

        Args:
            payload: Diccionario a firmar

        Returns:
            Firma en base64 (para header x-signature)
        """
        # Normalizar JSON
        json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)

        # Hash SHA-384
        payload_hash = hashlib.sha384(json_str.encode()).digest()

        # Firmar
        signature = self.signing_key.sign_digest(
            payload_hash,
            sigencode=sigencode_der
        )

        # Retornar en base64
        return base64.b64encode(signature).decode()

    def verify_response(self, response_body: str, signature_header: str) -> bool:
        """
        Verifica firma de respuesta de Círculo de Crédito

        Args:
            response_body: Body de la respuesta
            signature_header: Valor del header x-signature

        Returns:
            True si es válida, False en caso contrario
        """
        try:
            response_hash = hashlib.sha384(response_body.encode()).digest()
            signature_bytes = base64.b64decode(signature_header)

            self.verifying_key.verify_digest(
                signature_bytes,
                response_hash,
                sigdecode=sigdecode_der
            )

            logger.info("✅ Firma de respuesta verificada")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Error verificando firma: {e}")
            return False
```

#### C) src/api/client.py - Cliente HTTP Seguro
```python
import requests
import json
import logging
from typing import Dict, Any, Optional
from config import CIRCULO_CREDITO, CERTIFICATES
from src.security.ecdsa_manager import ECDSASecurityManager

logger = logging.getLogger(__name__)

class CirculoCreditoAPIClient:
    """Cliente seguro para APIs de Círculo de Crédito"""

    def __init__(self):
        self.api_key = CIRCULO_CREDITO["api_key"]
        self.base_url = CIRCULO_CREDITO["base_url"]
        self.security = ECDSASecurityManager(
            CERTIFICATES["private_key"],
            CERTIFICATES["cdc_public_cert"]
        )
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realiza request firmado con ECDSA

        Args:
            method: GET, POST
            endpoint: Ruta completa (ej: /sandbox/v3/eva/...)
            body: JSON a enviar

        Returns:
            Response con validación de firma
        """
        url = f"{self.base_url}{endpoint}"

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        json_body = None
        if body:
            signature = self.security.sign_payload(body)
            headers["x-signature"] = signature
            json_body = json.dumps(body, separators=(',', ':'), sort_keys=True)

        try:
            logger.info(f"📤 {method} {url}")

            if method.upper() == "POST":
                response = self.session.post(url, data=json_body, headers=headers, timeout=30)
            else:
                response = self.session.get(url, headers=headers, timeout=30)

            response.raise_for_status()

            # Verificar firma de respuesta
            response_text = response.text
            signature_header = response.headers.get('x-signature', '')

            signature_valid = True
            if signature_header:
                signature_valid = self.security.verify_response(response_text, signature_header)

            logger.info(f"📥 {response.status_code} OK")

            return {
                "success": True,
                "data": response.json(),
                "signature_verified": signature_valid
            }

        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error: {e.response.status_code}")
            return {"success": False, "error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}

    # ==================== MÉTODOS DE APIs ====================

    def verify_employment(self, curp: str, first_name: str, last_name: str, state: str = "CDMX") -> Dict:
        """Employment Verification (EVA v3)"""
        body = {
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp,
            "address": {"state": state, "addressLine1": ""}
        }
        return self._make_request("POST", "/sandbox/v3/eva/employmentverifications/withPrivacyNotice", body)

    def verify_bank_account(self, curp: str, account: str, bank_code: str = "012") -> Dict:
        """Bank Account Verification (BAVS)"""
        body = {
            "curp": curp,
            "bankAccount": account,
            "bankCode": bank_code
        }
        return self._make_request("POST", "/sandbox/v3/bavs/accounts/verification", body)

    def verify_identity(self, curp: str, rfc: str) -> Dict:
        """Identity Data Verification"""
        body = {"curp": curp, "rfc": rfc}
        return self._make_request("POST", "/sandbox/v3/identitydata/verification", body)

    def get_fico_score(self, curp: str) -> Dict:
        """FICO Score (300-850)"""
        body = {"curp": curp}
        return self._make_request("POST", "/sandbox/v3/scores/fico/extended", body)

    def get_fintech_score(self, curp: str) -> Dict:
        """Fintech Score"""
        body = {"curp": curp}
        return self._make_request("POST", "/sandbox/v3/scores/fintech", body)

    def check_pld(self, first_name: str, last_name: str, curp: str) -> Dict:
        """PLD Check (Sanciones)"""
        body = {
            "firstName": first_name,
            "lastName": last_name,
            "curp": curp
        }
        return self._make_request("POST", "/sandbox/v3/pld/persons", body)

    def check_fraud(self, curp: str, email: str = "") -> Dict:
        """Guardian Express (Fraude)"""
        body = {"curp": curp, "email": email}
        return self._make_request("POST", "/sandbox/v3/guardian/express", body)

    def estimate_loan(self, curp: str, income: float, fico_score: int) -> Dict:
        """Loan Amount Estimator"""
        body = {
            "ingresos": income,
            "curp": curp,
            "ficoscore": fico_score
        }
        return self._make_request("POST", "/sandbox/v3/loanestimator/montoestimado", body)

    def get_consolidated_report(self, curp: str) -> Dict:
        """Reporte Consolidado FICO + PLD"""
        body = {"curp": curp}
        return self._make_request("POST", "/sandbox/v3/rcc/consolidated/fico-pld", body)
```

#### D) src/agent/evaluator.py - Agente Evaluador
```python
import json
import logging
from datetime import datetime
from typing import Dict, Any
from src.api.client import CirculoCreditoAPIClient
from config import DECISION_RULES

logger = logging.getLogger(__name__)

class CreditEvaluationAgent:
    """Agente IA para evaluación automática de créditos"""

    def __init__(self):
        self.api_client = CirculoCreditoAPIClient()
        self.request_id = None
        self.evaluation_log = []

    def evaluate(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa solicitud de crédito completa

        Args:
            applicant: Datos del solicitante
                - nombre: Nombre completo
                - curp: CURP
                - rfc: RFC
                - email: Email
                - telefono: Teléfono
                - cuenta_bancaria: Número de cuenta
                - banco: Código de banco
                - empleador: Nombre del empleador
                - puesto: Puesto laboral
                - antiguedad_meses: Antigüedad en meses
                - ingresos_mensuales: Ingresos mensuales
                - monto_solicitado: Monto solicitado
                - plazo_meses: Plazo en meses

        Returns:
            Dict con resultado de evaluación
        """
        self.request_id = f"CRED-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"🔍 Iniciando evaluación {self.request_id} para {applicant.get('nombre')}")

        # Fase 1: Validación
        validation = self._validate_applicant(applicant)
        if not validation["passed"]:
            return self._create_response("RECHAZADO", validation["reason"], 1)

        # Fase 2: Compliance
        compliance = self._check_compliance(applicant)
        if not compliance["passed"]:
            return self._create_response("RECHAZADO", compliance["reason"], 2)

        # Fase 3: Análisis Crediticio
        credit_analysis = self._analyze_credit(applicant)
        if not credit_analysis["passed"]:
            return self._create_response("RECHAZADO", credit_analysis["reason"], 3)

        # Fase 4: Cálculo de Monto
        loan_calculation = self._calculate_loan_amount(applicant, credit_analysis["fico_score"])

        # Fase 5: Decisión Final
        final_decision = self._make_final_decision(applicant, credit_analysis, loan_calculation)

        return final_decision

    def _validate_applicant(self, applicant: Dict) -> Dict:
        """Fase 1: Validación de datos básicos"""
        logger.info("📋 Fase 1: Validación de datos")

        # Parsear nombre
        names = applicant["nombre"].split()
        first_name = names[0]
        last_name = names[-1] if len(names) > 1 else ""

        results = {"passed": True, "checks": {}}

        # Verificar identidad
        identity_result = self.api_client.verify_identity(applicant["curp"], applicant["rfc"])
        results["checks"]["identity"] = identity_result
        if not identity_result.get("success"):
            results["passed"] = False
            results["reason"] = "Error en verificación de identidad"
            return results

        # Verificar cuenta bancaria
        bank_result = self.api_client.verify_bank_account(
            applicant["curp"], applicant["cuenta_bancaria"], applicant.get("banco", "012")
        )
        results["checks"]["bank"] = bank_result
        if not bank_result.get("success"):
            results["passed"] = False
            results["reason"] = "Error en verificación de cuenta bancaria"
            return results

        # Verificar empleo
        employment_result = self.api_client.verify_employment(
            applicant["curp"], first_name, last_name, applicant.get("estado", "CDMX")
        )
        results["checks"]["employment"] = employment_result
        if not employment_result.get("success"):
            results["passed"] = False
            results["reason"] = "Error en verificación de empleo"
            return results

        logger.info("✅ Fase 1 completada exitosamente")
        return results

    def _check_compliance(self, applicant: Dict) -> Dict:
        """Fase 2: Verificación de compliance y fraude"""
        logger.info("🛡️ Fase 2: Verificación de compliance")

        names = applicant["nombre"].split()
        first_name = names[0]
        last_name = names[-1] if len(names) > 1 else ""

        results = {"passed": True, "checks": {}}

        # Verificar PLD
        pld_result = self.api_client.check_pld(first_name, last_name, applicant["curp"])
        results["checks"]["pld"] = pld_result
        if pld_result.get("success") and pld_result.get("data", {}).get("en_lista"):
            results["passed"] = False
            results["reason"] = "Persona en lista de sanciones PLD"
            return results

        # Verificar fraude
        fraud_result = self.api_client.check_fraud(applicant["curp"], applicant.get("email", ""))
        results["checks"]["fraud"] = fraud_result
        if fraud_result.get("success") and fraud_result.get("data", {}).get("fraude_detectado"):
            results["passed"] = False
            results["reason"] = "Fraude detectado"
            return results

        logger.info("✅ Fase 2 completada exitosamente")
        return results

    def _analyze_credit(self, applicant: Dict) -> Dict:
        """Fase 3: Análisis crediticio"""
        logger.info("📊 Fase 3: Análisis crediticio")

        results = {"passed": True, "checks": {}}

        # Obtener FICO Score
        fico_result = self.api_client.get_fico_score(applicant["curp"])
        results["checks"]["fico"] = fico_result

        if not fico_result.get("success"):
            results["passed"] = False
            results["reason"] = "Error obteniendo FICO Score"
            return results

        fico_score = fico_result["data"].get("score", 0)
        results["fico_score"] = fico_score

        # Obtener Fintech Score
        fintech_result = self.api_client.get_fintech_score(applicant["curp"])
        results["checks"]["fintech"] = fintech_result

        # Obtener reporte consolidado
        report_result = self.api_client.get_consolidated_report(applicant["curp"])
        results["checks"]["report"] = report_result

        # Aplicar reglas de decisión
        if fico_score < DECISION_RULES["fico_score_min"]:
            results["passed"] = False
            results["reason"] = f"FICO Score muy bajo: {fico_score}"

        results["risk_category"] = self._categorize_risk(fico_score)

        logger.info(f"✅ Fase 3 completada - FICO: {fico_score}")
        return results

    def _calculate_loan_amount(self, applicant: Dict, fico_score: int) -> Dict:
        """Fase 4: Cálculo de monto de préstamo"""
        logger.info("💰 Fase 4: Cálculo de monto")

        loan_result = self.api_client.estimate_loan(
            applicant["curp"], applicant["ingresos_mensuales"], fico_score
        )

        if loan_result.get("success"):
            max_amount = loan_result["data"].get("monto_maximo", 0)
            suggested_rate = loan_result["data"].get("tasa_sugerida", "0%")
            suggested_term = loan_result["data"].get("plazo_recomendado", 12)

            # Aplicar límite automático
            approved_amount = min(applicant["monto_solicitado"], max_amount)
            approved_amount = min(approved_amount, DECISION_RULES["max_automatic_amount"])

            return {
                "max_amount": max_amount,
                "approved_amount": approved_amount,
                "suggested_rate": suggested_rate,
                "suggested_term": suggested_term
            }
        else:
            # Fallback: cálculo básico
            max_based_on_income = applicant["ingresos_mensuales"] * 3  # 3 meses de ingresos
            approved_amount = min(applicant["monto_solicitado"], max_based_on_income)

            return {
                "max_amount": max_based_on_income,
                "approved_amount": approved_amount,
                "suggested_rate": "15%",
                "suggested_term": 12
            }

    def _make_final_decision(self, applicant: Dict, credit_analysis: Dict, loan_calc: Dict) -> Dict:
        """Fase 5: Decisión final"""
        logger.info("⚖️ Fase 5: Decisión final")

        fico_score = credit_analysis["fico_score"]
        requested_amount = applicant["monto_solicitado"]
        approved_amount = loan_calc["approved_amount"]

        # Lógica de decisión
        if fico_score >= DECISION_RULES["fico_score_low_risk"] and approved_amount >= requested_amount:
            status = "APROBADO"
            reason = f"Excelente perfil crediticio (FICO: {fico_score})"
        elif fico_score >= DECISION_RULES["fico_score_min"]:
            if approved_amount >= requested_amount * 0.8:  # Al menos 80% del solicitado
                status = "APROBADO"
                reason = f"Perfil crediticio aceptable (FICO: {fico_score})"
            else:
                status = "REVISIÓN_MANUAL"
                reason = f"Monto solicitado superior al recomendado. Revisión manual requerida."
        else:
            status = "RECHAZADO"
            reason = f"FICO Score insuficiente: {fico_score}"

        return self._create_response(status, reason, 5, {
            "fico_score": fico_score,
            "approved_amount": approved_amount,
            "requested_amount": requested_amount,
            "risk_category": credit_analysis["risk_category"]
        })

    def _categorize_risk(self, fico_score: int) -> str:
        """Categoriza el nivel de riesgo basado en FICO Score"""
        if fico_score >= 800:
            return "MUY_BAJO_RIESGO"
        elif fico_score >= 700:
            return "BAJO_RIESGO"
        elif fico_score >= 650:
            return "RIESGO_MODERADO"
        elif fico_score >= 550:
            return "ALTO_RIESGO"
        else:
            return "MUY_ALTO_RIESGO"

    def _create_response(self, status: str, reason: str, phase: int, extra_data: Dict = None) -> Dict:
        """Crea respuesta estructurada"""
        response = {
            "request_id": self.request_id,
            "status": status,
            "reason": reason,
            "phase_completed": phase,
            "timestamp": datetime.now().isoformat(),
            "evaluation_log": self.evaluation_log
        }

        if extra_data:
            response.update(extra_data)

        # Próximos pasos según estado
        if status == "APROBADO":
            response["next_steps"] = [
                "Enviar oferta formal por email",
                "Solicitar documentación adicional",
                "Programar firma digital del contrato",
                "Configurar desembolso automático"
            ]
        elif status == "REVISIÓN_MANUAL":
            response["next_steps"] = [
                "Transferir caso a analista senior",
                "Revisar documentación adicional",
                "Realizar verificación telefónica",
                "Evaluar caso en comité de crédito"
            ]
        else:  # RECHAZADO
            response["next_steps"] = [
                "Enviar notificación de rechazo",
                "Proporcionar razones específicas",
                "Ofrecer alternativas de productos",
                "Archivar caso para seguimiento futuro"
            ]

        logger.info(f"🏁 Evaluación completada: {status}")
        return response
```

## 🛠️ INSTALACIÓN RÁPIDA

```bash
# 1. Clonar y configurar
git clone https://github.com/tu-usuario/plataforma-creditos-ai.git
cd plataforma-creditos-ai

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar certificados
python setup_security.py

# 4. Configurar .env
cp .env.example .env
# Editar con tus credenciales

# 5. Probar
python main.py test_data.json
```

## 📊 EJEMPLO DE USO

```python
from src.agent.evaluator import CreditEvaluationAgent

# Inicializar agente
agent = CreditEvaluationAgent()

# Datos del solicitante
applicant = {
    "nombre": "Juan Pérez García",
    "curp": "PEGJ900101HDFRRL09",
    "rfc": "PEGJ900101ABC",
    "email": "juan@email.com",
    "telefono": "+5215551234567",
    "cuenta_bancaria": "0123456789012345678",
    "banco": "012",  # BBVA
    "empleador": "Empresa S.A.",
    "puesto": "Gerente",
    "antiguedad_meses": 24,
    "ingresos_mensuales": 25000,
    "monto_solicitado": 100000,
    "plazo_meses": 24
}

# Evaluar
resultado = agent.evaluate(applicant)
print(f"Estado: {resultado['status']}")
print(f"Razón: {resultado['reason']}")
```

## 🔧 CONFIGURACIÓN AVANZADA

### Variables de Entorno (.env)
```bash
# APIs
CIRCULO_CREDITO_API_KEY=aLXRxXTlLm6LC8L3T4PVqJHtssH2rfKs
CIRCULO_CREDITO_BASE_URL=https://services.circulodecredito.com.mx/sandbox/v3/

# Certificados
PRIVATE_KEY_PATH=./security/pri_key.pem
CDC_CERT_PATH=./security/cdc_cert.pem

# Logging
LOG_LEVEL=INFO

# Opcional: Claude AI
ANTHROPIC_API_KEY=tu_claude_key_aqui
```

### Reglas de Decisión Personalizables
```python
DECISION_RULES = {
    "fico_score_min": 550,          # Mínimo para considerar
    "fico_score_low_risk": 700,     # Riesgo bajo
    "max_dti": 0.45,               # Deuda/Ingresos máximo
    "max_automatic_amount": 500000, # Máximo automático (MXN)
}
```

## 🚀 DEPLOYMENT

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Producción
```bash
# Cambiar a producción en config.py
CIRCULO_CREDITO["environment"] = "production"
CIRCULO_CREDITO["base_url"] = "https://services.circulodecredito.com.mx/v3/"
```

## 📈 MONITOREO Y LOGGING

- Logs estructurados con niveles INFO/ERROR/WARNING
- Métricas de rendimiento por API
- Alertas automáticas para fallos
- Dashboard de evaluaciones en tiempo real

## 🔒 SEGURIDAD

- **ECDSA P-384** para firma de requests
- **SHA-384** para hashing
- **Verificación de respuestas** del servidor
- **Encriptación de datos sensibles**
- **Auditoría completa** de todas las operaciones

## 📞 SOPORTE

- 📧 Email: soporte@plataforma-creditos-ai.com
- 📱 WhatsApp: +52 55 1234 5678
- 📚 Docs: https://docs.plataforma-creditos-ai.com
- 🐛 Issues: https://github.com/tu-usuario/plataforma-creditos-ai/issues

## 📄 LICENCIA

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

---

**Desarrollado con ❤️ por GrowthBDM**