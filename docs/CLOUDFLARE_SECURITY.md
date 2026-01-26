# Cloudflare Security Configuration Checklist

## 🛡️ Configuración de Seguridad en Cloudflare

Este documento detalla las configuraciones de seguridad recomendadas para `cuantocuestauruguay.com` en Cloudflare.

---

## 1. SSL/TLS Configuration

**Dashboard → SSL/TLS**

### ✅ Configuración Actual
- [ ] **SSL/TLS encryption mode:** Full (Strict)
  - Path: SSL/TLS → Overview → Encryption mode
  - Seleccionar: "Full (strict)"
  - Esto valida el certificado SSL del servidor origen (Render.com)

### ✅ Edge Certificates
- [ ] **Always Use HTTPS:** ON
  - Path: SSL/TLS → Edge Certificates
  - Redirige automáticamente HTTP → HTTPS

- [ ] **Minimum TLS Version:** 1.2
  - Path: SSL/TLS → Edge Certificates
  - Deshabilita TLS 1.0 y 1.1 (inseguros)

- [ ] **Opportunistic Encryption:** ON
  - Habilita HTTP/2 y HTTP/3 (QUIC)

- [ ] **TLS 1.3:** ON
  - Última versión del protocolo, más seguro y rápido

- [ ] **Automatic HTTPS Rewrites:** ON
  - Reescribe URLs internas HTTP → HTTPS

- [ ] **Certificate Transparency Monitoring:** ON
  - Notifica si se emite un certificado no autorizado

### ✅ HSTS (HTTP Strict Transport Security)
- [ ] **Enable HSTS:** ON
  - Path: SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)
  - **Max Age:** 12 months (31536000 seconds)
  - **Include subdomains:** ON
  - **Preload:** ON (opcional, para incluir en lista de navegadores)

---

## 2. Firewall Rules

**Dashboard → Security → WAF**

### ✅ Web Application Firewall (WAF)
- [ ] **Managed Rules:** ON
  - Path: Security → WAF → Managed rules
  - **Cloudflare Managed Ruleset:** ON
  - **Cloudflare OWASP Core Ruleset:** ON
  - **Cloudflare Exposed Credentials Check:** ON (si disponible)

### ✅ Custom Firewall Rules
Path: Security → WAF → Firewall rules

#### Regla 1: Bloquear países sospechosos (opcional)
```
(ip.geoip.country ne "UY" and ip.geoip.country ne "AR" and ip.geoip.country ne "BR" and ip.geoip.country ne "US" and ip.geoip.country ne "ES")
```
**Acción:** Challenge (CAPTCHA)  
**Nota:** Ajustar según audiencia esperada

#### Regla 2: Rate Limiting en endpoints ETL
```
(http.request.uri.path contains "/api/v1/etl/run" and http.request.method eq "POST")
```
**Acción:** Rate Limit → 5 requests per 10 minutes

#### Regla 3: Bloquear métodos HTTP innecesarios
```
(http.request.method in {"PUT" "DELETE" "PATCH" "TRACE" "CONNECT"})
```
**Acción:** Block

#### Regla 4: Proteger endpoints sensibles
```
(http.request.uri.path contains "/docs" or http.request.uri.path contains "/redoc")
```
**Acción:** Challenge (si quieres restringir acceso a docs)  
**Nota:** Considera permitir solo desde IPs conocidas en producción

---

## 3. Rate Limiting

**Dashboard → Security → Rate Limiting Rules**

### ✅ Configuración de Límites

#### Rate Limit 1: API Global
- **Matching Request:** `(http.request.uri.path contains "/api/")`
- **Requests:** 100 per 1 minute
- **Action:** Block for 60 seconds
- **Response:** Custom JSON
  ```json
  {
    "error": "Rate limit exceeded",
    "retry_after": 60
  }
  ```

#### Rate Limit 2: ETL Endpoints
- **Matching Request:** `(http.request.uri.path contains "/api/v1/etl/" and http.request.method eq "POST")`
- **Requests:** 5 per 10 minutes
- **Action:** Block for 600 seconds

#### Rate Limit 3: Búsqueda
- **Matching Request:** `(http.request.uri.path contains "/api/v1/productos")`
- **Requests:** 60 per 1 minute
- **Action:** Challenge (CAPTCHA)

---

## 4. Bot Fight Mode

**Dashboard → Security → Bots**

### ✅ Configuración de Bots
- [ ] **Bot Fight Mode:** ON (Free plan)
  - Desafía bots maliciosos automáticamente
  - **Super Bot Fight Mode** (si tienes plan Pro+):
    - Definitely automated: Block
    - Likely automated: Challenge
    - Verified bots: Allow (Googlebot, etc.)

---

## 5. DDoS Protection

**Dashboard → Security → DDoS**

### ✅ Configuración DDoS
- [ ] **HTTP DDoS Attack Protection:** ON (automático en todos los planes)
- [ ] **Network-layer DDoS Attack Protection:** ON (automático)
- [ ] **Sensitivity Level:** Medium (ajustar si hay falsos positivos)

---

## 6. Page Rules

**Dashboard → Rules → Page Rules**

### ✅ Reglas de Página

#### Regla 1: Force HTTPS en todo el dominio
- **URL:** `http://*cuantocuestauruguay.com/*`
- **Settings:**
  - Always Use HTTPS: ON
- **Order:** 1

#### Regla 2: Caché para assets estáticos
- **URL:** `cuantocuestauruguay.com/*.{js,css,png,jpg,jpeg,gif,svg,woff,woff2,ttf,eot}`
- **Settings:**
  - Browser Cache TTL: 1 month
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
- **Order:** 2

#### Regla 3: Security Level para API
- **URL:** `cuantocuestauruguay.com/api/*`
- **Settings:**
  - Security Level: High
  - Browser Integrity Check: ON
- **Order:** 3

---

## 7. Security Level

**Dashboard → Security → Settings**

### ✅ Nivel de Seguridad Global
- [ ] **Security Level:** Medium
  - Low: Mínima protección (solo amenazas obvias)
  - Medium: Protección balanceada ✅
  - High: Más estricto, puede generar falsos positivos
  - I'm Under Attack: Máxima protección (solo emergencias)

- [ ] **Browser Integrity Check:** ON
  - Verifica que el navegador sea legítimo (no bots mal diseñados)

- [ ] **Privacy Pass Support:** ON
  - Permite tokens de privacidad para reducir CAPTCHAs

---

## 8. Security Headers (complementario al backend)

**Dashboard → Rules → Transform Rules → Managed Transforms**

### ✅ Activar Security Headers
- [ ] **Add security headers:** ON
  - Cloudflare añade automáticamente headers básicos
  - Complementa los headers del backend

---

## 9. DNS Security

**Dashboard → DNS → Settings**

### ✅ DNSSEC
- [ ] **DNSSEC:** ON
  - Protege contra DNS spoofing/hijacking
  - Requiere configuración en registrador de dominio

### ✅ Proxied DNS (Orange Cloud)
- [ ] Verificar que registros A/AAAA/CNAME tengan nube naranja (proxied)
  - `cuantocuestauruguay.com` → 🟠 Proxied
  - `www.cuantocuestauruguay.com` → 🟠 Proxied
  - Esto activa todas las protecciones de Cloudflare

---

## 10. Analytics and Logging

**Dashboard → Analytics & Logs**

### ✅ Web Analytics
- [ ] **Cloudflare Web Analytics:** ON (respeta privacidad)
  - Sin cookies
  - Cumple GDPR

### ✅ Logs (si tienes plan Enterprise)
- [ ] **Logpush/Logpull:** Configurar para análisis de seguridad
  - Útil para detectar patrones de ataque

---

## 11. Content Security Policy (CSP)

**Dashboard → Rules → Transform Rules → Modify Response Header**

### ✅ Añadir CSP Header (si no está en backend)
- **Rule name:** Add CSP Header
- **If:** All incoming requests
- **Then:**
  - Set static → Header name: `Content-Security-Policy`
  - Value: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://preciosregulados-api.onrender.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`

**Nota:** Mejor implementar en backend (ya está en security middleware)

---

## 12. Custom Error Pages

**Dashboard → Custom Pages**

### ✅ Personalizar Páginas de Error
- [ ] **500 Class Errors:** Subir HTML personalizado
  - Mensaje amigable: "Estamos experimentando problemas técnicos"
- [ ] **1000 Class Errors (Cloudflare):** Personalizar
  - Ejemplo: Error 1020 (Access Denied)

---

## 13. Email Routing (opcional)

**Dashboard → Email → Email Routing**

### ✅ Configurar Email de Contacto
- [ ] Crear alias: `security@cuantocuestauruguay.com`
- [ ] Redirigir a tu email personal
- [ ] Usar para reportes de seguridad

---

## 14. Two-Factor Authentication (2FA)

**Dashboard → My Profile → Authentication**

### ✅ Proteger Cuenta de Cloudflare
- [ ] **Two-Factor Authentication:** ON
  - Usar app de autenticación (Google Authenticator, Authy)
  - Guardar códigos de recuperación

---

## 15. Access Control (si tienes plan Pro+)

**Dashboard → Zero Trust → Access**

### ✅ Restringir Acceso a Endpoints Sensibles
- [ ] Configurar Access Policy para `/docs` y `/redoc`
  - Solo permitir IPs conocidas
  - Requiere autenticación

---

## 🎯 Checklist de Implementación

### Prioridad Alta (Hacer Ahora)
- [ ] SSL/TLS → Full (Strict)
- [ ] Always Use HTTPS → ON
- [ ] HSTS → Enable (12 meses)
- [ ] WAF Managed Rules → ON
- [ ] Bot Fight Mode → ON
- [ ] Rate Limiting → Configurar 3 reglas básicas
- [ ] Security Level → Medium
- [ ] Browser Integrity Check → ON
- [ ] 2FA en cuenta Cloudflare → ON

### Prioridad Media (Esta Semana)
- [ ] Firewall Rules personalizadas → 4 reglas
- [ ] Page Rules → 3 reglas
- [ ] DNS Proxied → Verificar nube naranja
- [ ] Custom Error Pages → 500 y 1000

### Prioridad Baja (Próximo Mes)
- [ ] DNSSEC → ON
- [ ] Firewall Rules avanzadas (geolocalización)
- [ ] Analytics → Configurar
- [ ] Email Routing → security@

---

## 🧪 Testing de Seguridad

Después de implementar, verificar:

### 1. SSL Labs Test
```bash
# Visitar:
https://www.ssllabs.com/ssltest/analyze.html?d=cuantocuestauruguay.com
# Objetivo: Grado A+
```

### 2. Security Headers
```bash
# Visitar:
https://securityheaders.com/?q=cuantocuestauruguay.com
# Objetivo: Grado A
```

### 3. HSTS Preload
```bash
# Verificar en:
https://hstspreload.org/?domain=cuantocuestauruguay.com
```

### 4. Rate Limiting
```bash
# Probar con múltiples requests:
for i in {1..110}; do
  curl https://cuantocuestauruguay.com/api/v1/productos
done
# Debe bloquear después de 100
```

### 5. Firewall Rules
```bash
# Intentar método no permitido:
curl -X PUT https://cuantocuestauruguay.com/api/v1/productos
# Debe devolver 403 Forbidden
```

---

## 📊 Monitoreo Continuo

### Alertas a Configurar
- Email cuando:
  - Hay un pico de tráfico inusual (DDoS)
  - Se bloquean >100 requests en 5 minutos
  - Cambia el certificado SSL
  - Hay errores 5xx >10 en 1 minuto

**Path:** Notifications → Create a notification → Seleccionar triggers

---

## 📚 Recursos Adicionales

- [Cloudflare Security Docs](https://developers.cloudflare.com/fundamentals/basic-tasks/protect-your-site/)
- [WAF Configuration Guide](https://developers.cloudflare.com/waf/)
- [Rate Limiting Best Practices](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [SSL/TLS Best Practices](https://developers.cloudflare.com/ssl/)

---

**Última actualización:** 26 de enero de 2026  
**Responsable:** Equipo de DevSecOps  
**Próxima revisión:** 26 de febrero de 2026
