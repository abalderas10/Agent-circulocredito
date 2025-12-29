# Notas de Despliegue - Agent-circulocredito

## 🔐 Configuración de Certificado CDC

### Problema Común
El certificado descargado de Círculo de Crédito es un certificado X.509 completo, pero el código necesita solo la clave pública.

### Solución
Después de descargar el certificado de Círculo de Crédito:

```bash
# Extraer la clave pública del certificado
cd security
openssl x509 -pubkey -noout -in cdc_cert.pem > cdc_public_key.pem
```

### Configuración en .env
Actualizar el archivo `.env` para usar la clave pública extraída:

```bash
CDC_CERT_PATH=./security/cdc_public_key.pem
```

### Verificación
El sistema debe mostrar en los logs:

```
INFO:security_manager:Certificado de Circulo de Credito cargado correctamente
INFO:security_manager:CirculoCreditoSecurityManager inicializado correctamente
```

## 📋 Archivos de Seguridad Requeridos

```
security/
├── pri_key.pem              # Generado con setup_security.py
├── certificate.pem          # Generado con setup_security.py (subir a CDC)
├── cdc_cert.pem            # Descargado de Círculo de Crédito
└── cdc_public_key.pem      # Extraído de cdc_cert.pem (usar en .env)
```

## 🚀 Despliegue con Docker

```bash
# 1. Generar certificados
python setup_security.py

# 2. Subir certificate.pem al portal de Círculo de Crédito
# 3. Descargar certificado de CDC y guardarlo como cdc_cert.pem

# 4. Extraer clave pública
cd security
openssl x509 -pubkey -noout -in cdc_cert.pem > cdc_public_key.pem

# 5. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales
# Asegurarse de que CDC_CERT_PATH=./security/cdc_public_key.pem

# 6. Desplegar con Docker
docker-compose up -d --build
```

## 📊 Verificación del Despliegue

```bash
# Ver logs
docker logs plataforma-creditos-ai

# Verificar que el certificado se cargó correctamente
docker logs plataforma-creditos-ai | grep "Certificado de Circulo de Credito"
```

## ⚠️ Troubleshooting

### Error: "Unable to load PEM file. MalformedFraming"
**Causa**: Intentando cargar el certificado X.509 completo en lugar de la clave pública.

**Solución**: Extraer la clave pública como se indica arriba.

### Errores 404 o 401 en APIs
**Causa**: Problemas de configuración con Círculo de Crédito.

**Solución**:
1. Verificar que la API key tenga permisos para todos los productos
2. Confirmar que los endpoints coincidan con la documentación actual
3. Validar que los productos estén contratados y activos

## 📞 Soporte

Para más información, consulta:
- Documentación de Círculo de Crédito: https://developer.circulodecredito.com.mx/docs
- Portal de desarrolladores: https://developer.circulodecredito.com.mx/

---

**Última actualización**: 29 de diciembre de 2025
