# 1. PLAN DE WHATSAPP BOT PARA DISTRIBUCIÓN

## Estado actual
- Archivo: `backend/app/whatsapp_bot.py` (229 líneas, 100% implementado)
- Dependencia: Twilio (pip install twilio)
- Estado: **Listo, solo necesita config**

---

## A. Setup de Twilio (15 minutos, gratis hasta $15 USD)

### Pasos:
1. Ir a https://www.twilio.com/console
2. Crear cuenta (número verificado, gratis)
3. Crear proyecto "PreciosRegulados"
4. En Messaging → WhatsApp:
   - Conectar número Twilio (te asignan uno gratis: +1234567890)
   - O usar número propio (si tienes)
5. Copiar credenciales:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
   ```
6. Pegar en `.env` del backend

### Costo inicial:
- **$0 primeros $15 USD** (crédito de prueba)
- Después: ~$0.03 USD por mensaje enviado
- Con 100 usuarios recibiendo 1 tip/semana = ~$0.30/semana = **$15/año**

---

## B. Arquitectura de distribución

### Flujo:
```
Scheduler diario (APScheduler existe)
  ↓
Lee JSON de promos/tips (ver sección 2)
  ↓
Selecciona 1 random o próximo en cola
  ↓
Envía a lista de suscriptores vía Twilio API
  ↓
Loggea envío (para ver tasa de aceptación)
```

### Tipos de mensajes:

**Opción 1: Tip diario (simple)**
```
📊 Ahorro semanal
─────────────────
Bajá de 3 a 1 canalera + usa streaming

Ahorro: $1.200/mes
Pasos: https://cuantocuestauruguay.com/tips/canalaras-streaming

Querés más tips? Escribí "TIPS"
```

**Opción 2: Promo vigente (por vigencia)**
```
🎁 PROMO VIGENTE
─────────────────
Paramount+ gratis 1 año si tienes Flow

Válido hasta: 28/02/2026
Cómo obtener: https://cuantocuestauruguay.com/promo/paramount

Próxima promo: mañana a las 9 AM
```

**Opción 3: Resumen semanal (viernes)**
```
📈 Resumen semanal
─────────────────
✅ Qué bajó: Internet Antel -5%
✅ Qué subió: UTE +2%
📌 Promo nueva: Paramount+ gratis

Ver todas: https://cuantocuestauruguay.com/resumen
```

---

## C. Gestión de suscriptores

### Base de datos (tabla nueva, mínima):
```sql
CREATE TABLE whatsapp_suscriptores (
    id INTEGER PRIMARY KEY,
    numero VARCHAR(20) UNIQUE,      -- +598XXXXXXXXX
    fecha_suscripcion DATE,
    activo BOOLEAN DEFAULT TRUE,
    frecuencia VARCHAR(20),         -- 'diario', 'semanal'
    preferencias TEXT                -- JSON: ['combustibles', 'ute']
);
```

### API para suscripción (3 endpoints):

1. **POST /api/v1/whatsapp/subscribe**
   ```json
   {
     "numero": "+598XXXXXXXXX",
     "frecuencia": "semanal",
     "intereses": ["combustibles", "ute"]
   }
   ```
   → Respuesta: "Confirma escribiendo: CONFIRMAR al número de WhatsApp"

2. **GET /api/v1/whatsapp/webhook** (webhook de Twilio)
   - Recibe confirmaciones/desuscripciones
   - Actualiza base de datos

3. **GET /api/v1/whatsapp/test** (solo admin)
   - Envía mensaje de prueba

---

## D. Suscripción (cómo el usuario se entera)

### Forma 1: QR en sitio web
```
[QR] → https://wa.me/1234567890?text=Suscribirse
```
Usuario toca, abre WhatsApp, escribe "Suscribirse", bot confirma.

### Forma 2: Link directo en footer
"📱 Recibí tips por WhatsApp" → link wa.me

### Forma 3: Call-to-action en páginas
"Quieres que te avise cuando esta promo vuelva?"
→ Botón → Abre WhatsApp → Suscribe

---

## E. Ejemplo de secuencia automática

**Lunes 8 AM:**
```
Hola 👋 Es lunes y tenemos ahorro para ti:
Bajá canaleras de TV y seguí viendo todo con Android TV.
Ahorro: $1.200/mes
Detalles: [link]
```

**Miércoles 2 PM:**
```
⚖️ Derechos del consumidor que casi nadie usa:
Tenés derecho a pedir información clara en tu contrato.
¿Qué preguntar?: [link]
```

**Viernes 9 AM:**
```
📊 Resumen semanal:
✅ UTE bajó 1%
✅ Nueva promo: Paramount+ gratis
❌ Internet Antel sigue igual
Ver todo: [link]
```

---

## F. Métricas simples

Trackear en base de datos:
- `suscriptores_totales`
- `mensajes_enviados`
- `tasa_lectura` (Twilio lo reporta)
- `desuscripciones` (si escriben "PARAR")

---

## G. Implementación (esfuerzo estimado)

| Tarea | Esfuerzo | Notas |
|-------|----------|-------|
| Setup Twilio | 15 min | Una sola vez |
| Crear tabla BD | 10 min | 1 migración |
| Habilitar endpoints | 1 hora | Código ya existe |
| Probar webhook | 30 min | Simulador de Twilio |
| Crear QR + footer web | 20 min | Cambio visual |
| Scheduler de envíos | 1 hora | Agregar al job ETL |
| **Total** | **~4 horas** | **Funcional en 1 sesión** |

---

## H. Next steps
1. Ir a twilio.com, crear cuenta
2. Conectar número WhatsApp
3. Copiar credenciales a `.env`
4. Activar endpoints en backend
5. Publicitar con QR en sitio

Resultado: **Usuarios reciben tips semanales automáticos, sin que hagas nada después de setup**.

