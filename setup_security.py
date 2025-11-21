#!/usr/bin/env python3
"""
Script de configuración de seguridad para Círculo de Crédito
Genera certificados ECDSA P-384 y configura el entorno
"""

import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
import base64

def create_self_signed_certificate(private_key, output_path):
    """Crea un certificado auto-firmado simple (para demo)"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    import datetime

    # Crear subject y issuer
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CDMX"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Mexico"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "TuEmpresa"),
        x509.NameAttribute(NameOID.COMMON_NAME, "TuApp"),
    ])

    # Crear certificado
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).sign(private_key, hashes.SHA256())

    # Guardar certificado
    with open(output_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def main():
    """Configuración completa de seguridad usando Python"""
    print("[SEC] CONFIGURACION DE SEGURIDAD - CIRCULO DE CREDITO")
    print("=" * 60)

    # Crear directorio de seguridad
    security_dir = Path("./security")
    security_dir.mkdir(exist_ok=True)
    print(f"[DIR] Directorio de seguridad creado: {security_dir.absolute()}")

    try:
        # Paso 1: Generar llave privada ECDSA P-384
        print("\n[1/4] GENERANDO LLAVE PRIVADA ECDSA P-384")
        private_key = ec.generate_private_key(ec.SECP384R1())
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        pri_key_path = security_dir / "pri_key.pem"
        with open(pri_key_path, 'w') as f:
            f.write(private_key_pem)
        print(f"[OK] Llave privada guardada en: {pri_key_path}")

        # Paso 2: Generar certificado público
        print("\n[2/4] GENERANDO CERTIFICADO PUBLICO")
        cert_path = security_dir / "certificate.pem"
        create_self_signed_certificate(private_key, cert_path)
        print(f"[OK] Certificado guardado en: {cert_path}")

        # Paso 3: Mostrar información
        print("\n[3/4] INFORMACION DE LAS LLAVES")
        print("Llave privada generada correctamente")
        print("Certificado auto-firmado creado (para testing)")

        # Paso 4: Crear archivo de instrucciones
        print("\n[4/4] CREANDO ARCHIVO DE INSTRUCCIONES")
        instructions_path = security_dir / "INSTRUCCIONES.txt"
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write("""INSTRUCCIONES PARA CONFIGURAR CERTIFICADOS EN CIRCULO DE CREDITO

1. Ve a: https://developer.circulodecredito.com.mx/user/apps
2. Selecciona tu aplicacion: plataforma-creditos-ai
3. Ve a la seccion: Certificados
4. Sube el archivo: certificate.pem (generado automaticamente)
5. Descarga el certificado de Circulo de Credito
6. Guardalo como: cdc_cert.pem en esta carpeta
7. El agente estara listo para funcionar!

NOTA: El certificado generado es auto-firmado para testing.
Para produccion, usa una Autoridad Certificadora reconocida.
""")

        print(f"[OK] Instrucciones guardadas en: {instructions_path}")

        # Verificar archivos generados
        pri_key = security_dir / "pri_key.pem"
        cert = security_dir / "certificate.pem"
        instructions = security_dir / "INSTRUCCIONES.txt"

        print("\n[INFO] ARCHIVOS GENERADOS:")
        print(f"[KEY] Llave privada: {pri_key} {'[OK]' if pri_key.exists() else '[FAIL]'}")
        print(f"[CERT] Certificado: {cert} {'[OK]' if cert.exists() else '[FAIL]'}")
        print(f"[TXT] Instrucciones: {instructions} {'[OK]' if instructions.exists() else '[FAIL]'}")

        if pri_key.exists() and cert.exists():
            print("\n[SUCCESS] CONFIGURACION COMPLETADA EXITOSAMENTE")
            print("\n[NEXT] PROXIMOS PASOS:")
            print("1. Lee el archivo ./security/INSTRUCCIONES.txt")
            print("2. Sube certificate.pem al apihub de Circulo de Credito")
            print("3. Descarga y guarda el certificado de Circulo como cdc_cert.pem")
            print("4. Ejecuta: python main.py test_data.json")

            return True
        else:
            print("\n[ERROR] No se generaron todos los archivos necesarios")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error durante la configuracion: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)