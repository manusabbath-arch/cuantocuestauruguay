# ⚡ PLAN EJECUCIÓN: PRÓXIMAS 24 HORAS

**Documento:** PLAN_24_HORAS.md  
**Fecha:** 28 de Enero 2026  
**Hora de creación:** ~14:00 (tarde)  
**Objetivo:** Tener BOT LIVE mañana, LANDING PAGE LIVE mañana, VIRAL POSTS miércoles

---

## HOY (Lunes 28) - Preparación [~2 horas]

### 14:00 - 14:10: Team Alignment (10 min)
```
ACCIÓN: Llamada rápida (10 min máximo)

AGENDA:
□ ¿Cree el team en hipótesis de "rabia contenida"?
□ ¿Consenso en prioridad: Bot > Blog?
□ ¿OK gastar 16 horas Semana 1?
□ ¿Twilio setup HOY o retrasar?

DECISIÓN CRÍTICA:
- Go: Continuar con plan
- No-go: Revisar hipótesis
(Si No-go: reconvenirse, volver a LA_VERDADERA_TESIS.md)

TIMEBOX: 10 min máximo. No debates largos.
```

### 14:10 - 14:40: Reading (30 min)
```
ACCIÓN: Lectura de documentos estratégicos

DOCUMENTO 1: ACTIVISMO_DE_DATOS_PILAR_4.md (15 min)
- Leer sección "Contexto: Por Qué Uruguay"
- Leer sección "Pilar 1: WhatsApp Bot"
- Leer sección "Pilar 2: Peticiones"
- SKIP: Detalles técnicos (verás después)

DOCUMENTO 2: LA_VERDADERA_TESIS.md (15 min)
- Leer "La pregunta fundamental"
- Leer "El triángulo imposible"
- Leer "La hipótesis"
- Leer "Por qué no puede fallar"

OBJETIVO: Entender WHY, no HOW (HOW = mañana)
```

### 14:40 - 15:50: Twilio Setup (1 hour)
```
ACCIÓN: Crear cuenta Twilio + obtener credenciales

PASO 1: Crear cuenta (10 min)
□ Ir a twilio.com
□ Sign up (usa email)
□ Verificar email
□ Crear contraseña fuerte

PASO 2: WhatsApp Integration (20 min)
□ En dashboard: Messaging → WhatsApp
□ Click "Connect with Twilio"
□ Seleccionar: "Business Account Setup"
□ Sigue pasos (phone number validation)
□ GUARDAR: Account SID, Auth Token, WhatsApp Number

PASO 3: Testing (20 min)
□ En Twilio Console: Messaging → Try it out
□ Enviar WhatsApp message a tu número (+598 ...)
□ Recibir respuesta (confirma cuenta funciona)

PASO 4: Documentación (10 min)
□ Crear archivo: backend/.env.twilio
   TWILIO_ACCOUNT_SID=xxxxx
   TWILIO_AUTH_TOKEN=xxxxx
   TWILIO_WHATSAPP_NUMBER=+1234567890
   TWILIO_WEBHOOK_URL=https://api.cuantocuesta.uy/webhook/whatsapp
□ NO commitear a git (add .env.twilio a .gitignore)

RESULTADO ESPERADO:
- Cuenta Twilio creada
- WhatsApp número obtenido
- Credenciales guardadas en .env.twilio
- Test message enviado y recibido

TIME CHECK: 15:50 = listo para mañana
```

---

## MAÑANA (Martes 29) - BUILD FASE [~8 HORAS]

### 08:00 - 12:00: Bot Development [4 HORAS]

#### Paso 1: FastAPI Webhook Endpoint (1 hora)
```
ARCHIVO: backend/app/api/v1/whatsapp.py (NEW)

CÓDIGO BASE:
from fastapi import APIRouter, Request, HTTPException
from twilio.rest import Client
import os

router = APIRouter(prefix="/api/v1", tags=["whatsapp"])

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@router.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request):
    """
    Recibe mensajes WhatsApp via Twilio webhook
    """
    form = await request.form()
    incoming_msg = form.get("Body", "").lower()
    sender = form.get("From")
    
    # Parse comando
    if incoming_msg.startswith("/nafta"):
        response = await get_nafta_price()
    elif incoming_msg.startswith("/ute"):
        response = await get_ute_price()
    elif incoming_msg.startswith("/supermercado"):
        response = await get_supermarket_price()
    else:
        response = "Comandos: /nafta, /ute, /supermercado"
    
    # Enviar respuesta
    await send_whatsapp_message(sender, response)
    
    return {"status": "ok"}

async def send_whatsapp_message(to_phone, message):
    message = client.messages.create(
        body=message,
        from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
        to=f"whatsapp:{to_phone}"
    )
    return message.sid

CHECKLIST:
□ Archivo creado
□ Imports correctos
□ Webhook endpoint funciona
□ Respuesta básica ("ok") recibida
```

#### Paso 2: Price Query Functions (1 hora)
```
FUNCIÓN: get_nafta_price()

LÓGICA:
1. Query tabla combustibles WHERE producto = 'nafta 95'
2. ORDER BY fecha DESC LIMIT 1
3. Formatear precio actual
4. Comparar con precio 7 días atrás
5. Calcular variación %
6. Query tabla peticiones WHERE status = 'active'
7. Contar firmas en petición 'Transparencia ANCAP'
8. Retornar mensaje formateado:

⛽ NAFTA 95 OCTANOS
Precio hoy: $68.20
Variación: ↑ 4.5% (esta semana)
Tendencia: 📈 subiendo

542 personas firman:
"Exigimos TRANSPARENCIA ANCAP"
[FIRMAR] [HISTORIAL]

SIMILAR: get_ute_price(), get_supermarket_price()

CHECKLIST:
□ Funciones retornan datos correctos
□ Formato de mensaje limpio
□ Emojis funcionan en WhatsApp
□ Precio numérico correcto
□ Petición contador actualizado
```

#### Paso 3: Database Schema (30 min)
```
TABLA 1: usuarios_whatsapp (NEW)
CREATE TABLE usuarios_whatsapp (
    id INTEGER PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    created TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP NULL,
    last_message TIMESTAMP DEFAULT NOW()
);

TABLA 2: peticiones (EXPAND existing)
ALTER TABLE peticiones ADD COLUMN:
    status VARCHAR(50) DEFAULT 'active'
    launch_date TIMESTAMP
    target_firmas INTEGER

TABLA 3: firmas (NEW)
CREATE TABLE firmas (
    id INTEGER PRIMARY KEY,
    peticion_id INTEGER NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20) NULL,
    created TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'whatsapp'
);

MIGRATION:
□ Crear archivo: backend/migrations/add_whatsapp_schema.sql
□ Ejecutar: sqlite3 preciosregulados.db < migrations/add_whatsapp_schema.sql
□ Verificar: SELECT * FROM usuarios_whatsapp (vacío, ok)
```

#### Paso 4: Twilio Webhook Configuration (30 min)
```
EN TWILIO CONSOLE:
1. Messaging → WhatsApp → Settings
2. Webhook URL: https://api.cuantocuesta.uy/api/v1/webhook/whatsapp
3. Method: POST
4. Save

EN CÓDIGO:
- Verificar signature Twilio (security)
- Agregar middleware: validate_twilio_signature()

TESTING:
□ Send WhatsApp: /nafta
□ Recibir respuesta con precio actual
□ Check logs: mensaje fue procesado
□ Verificar: usuario agregado a DB
```

### 12:00 - 13:00: LUNCH [1 HORA]
(You deserve it. Fuera del keyboard.)

### 13:00 - 17:00: Landing Page Development [4 HORAS]

#### Paso 1: Project Setup (30 min)
```
ACCIÓN: Crear Next.js proyecto

COMANDO:
$ cd frontend
$ npx create-next-app@latest peticiones \
  --typescript \
  --tailwind \
  --app-dir \
  --skip-eslint

cd peticiones

ESTRUCTURA:
peticiones/
├── app/
│   ├── page.tsx (home redirect)
│   └── peticion/
│       └── [id]/
│           └── page.tsx (landing template)
├── public/
│   └── og-image.png (share image)
└── .env.local (configuración)

DEPLOY SETUP:
□ Crear cuenta Vercel (si no tienes)
□ Conectar GitHub repo
□ Deploy: `vercel --prod`
```

#### Paso 2: Petición Landing Template (2 horas)
```
ARCHIVO: app/peticion/[id]/page.tsx

ESTRUCTURA (COPIA EMOCIONAL PRIMERO):

HERO SECTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H1: "¿CUÁL ES EL SECRETO DE ANCAP?
    Suben nafta sin explicar.
    BASTA."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA SECTION:
"ANCAP subió nafta 28% en 6 meses (vs 12% gasolina internacional)
Nunca comunican cambios
Directorio cobra $500K en bonificaciones"

PETITION IFRAME:
<iframe src="https://tally.so/..." />

SOCIAL PROOF:
[542 personas ya firmaron]
[Ver comentarios últimas firmas]

CTA GIGANTE:
[FIRMAR AHORA]

SHARE BUTTONS:
[WhatsApp] [Twitter] [Facebook]

TECH STACK:
- Next.js + Tailwind
- Tally.so embedded form
- Open Graph meta tags (para sharing)
- Mobile responsive

CHECKLIST:
□ Landing page responsive (mobile + desktop)
□ Tally.so form embebido funciona
□ Share buttons comparten correctamente
□ Social meta tags (og:image, og:title, etc.)
□ Vercel deployment live

DEPLOY:
$ git add .
$ git commit -m "feat: landing page transparencia ANCAP"
$ git push origin main
(Vercel autodeploy)
```

#### Paso 3: Newsletter Integration (1 hora)
```
ACCIÓN: Conectar Tally.so → MailerLite

TALLY.SO SETUP:
1. Ir a tally.so
2. Create new form
3. Field 1: Email
4. Field 2: Newsletter preferences
5. Configurar webhook: https://api.mailerlite.com/webhooks

MAILERLITE SETUP:
1. Crear cuenta (free tier: 1,000 subscribers)
2. Obtener API key
3. Crear segment: "WhatsApp Bot + Peticiones"
4. Webhook: Auto-add email when firma from WhatsApp

INTEGRACIÓN BOT:
Cuando usuario firma vía WhatsApp:
□ Enviar email a MailerLite API
□ Auto-add a segment
□ Send welcome email: "Bienvenido al movimiento"

CHECKLIST:
□ Tally form submissions → MailerLite
□ Email validation working
□ Welcome email sent
□ Segment visible en MailerLite
```

---

## MIÉRCOLES (30 de Enero) - LAUNCH [~6 HORAS]

### 08:00 - 10:00: Final Testing [2 HORAS]

```
BOT TESTING:
□ /nafta → respuesta correcta
□ /ute → respuesta correcta
□ /supermercado → respuesta correcta
□ Usuario agregado a DB
□ Petición contador actualizado
□ Respuesta tiempo < 2 segundos

LANDING PAGE TESTING:
□ Landing page loads < 3 segundos
□ Form submission funciona
□ MailerLite recibe email
□ Share buttons funcionan
□ Mobile responsiveness OK

FINAL CHECKS:
□ Logs limpios (sin errores)
□ Error handling en lugar
□ Rate limiting configurado
□ Webhooks secured (signature validation)
□ Backups de DB configured
```

### 10:00 - 13:00: Viral Content [3 HORAS]

#### Post 1: Twitter/X (30 min)
```
"¿Cuánto REALMENTE cuesta tu nafta?
ANCAP la subió 28% en 6 meses sin explicar.
Nosotros hicimos un bot para mostrar la verdad.
Prueba: Escribe 'Hola' al bot en WhatsApp
[Link a bot] [Link a petición]"

ELEMENTOS:
□ Headline emocional
□ Dato específico (28%)
□ CTA clara (probar bot)
□ Links a ambos canales
□ Hashtags relevantes: #Uruguay #ANCAP #Transparencia

PUBLISH: 10:00 (horario peak)
RETWEET: Con cuenta oficial CCCUY
```

#### Post 2: Instagram Stories (30 min)
```
VISUAL: Screenshot de precio nafta + variación
TEXT: "542 personas como vos dicen: TRANSPARENCIA ANCAP
Sumáte a la petición [Link]
O prueba el bot en WhatsApp [Link]"

ELEMENTS:
□ Screenshot real de bot
□ Copy emocional
□ Links sticker
□ Call to action explícito

PUBLISH: 10:30
SHARE: A 5-10 amigos (viral seed)
```

#### Post 3: LinkedIn (30 min)
```
COPY (PROFESSIONAL ANGLE):
"La opacidad de precios en monopolios estatales.
Caso de estudio: ANCAP en Uruguay.

Hicimos un análisis de 6 meses de datos.
Resultado: Precio sube sin comunicación.

Herramienta: Bot que muestra transparencia real.
Movimiento: Ciudadanos pidiendo cambios.

¿Qué monopolios afectan tu economía?"

ELEMENTOS:
□ Profesional pero emocional
□ Pregunta provocadora
□ Link a petición
□ Engagement hook

PUBLISH: 11:00
COMMENT: Responder rápido a comentarios
```

### 13:00 - 15:00: Influencer Outreach [2 HORAS]

```
LISTA: 10 personas clave

[1] @periodista_economia
    Message: "Vi tu análisis sobre inflación ANCAP.
    Hicimos algo que te va a interesar..."
    
[2] @ong_consumidores
    Message: "Matching goals. Colaboración?"
    
[3] @economist_uy
    Message: "Data you might find interesting..."

[4-10] Similar outreach (personalizado)

TEMPLATE (no copy-paste):
"Hola [NOMBRE],
Vi tu reciente artículo sobre [TOPIC].
Hicimos una herramienta que complementa...
Sin pressure, pero thought you'd care.
[Link a petición]"

TIMEBOX: 2 minutos por persona
NO FOLLOW UP yet (let them engage organically)

RESULT ESPERADO:
- 1-2 shares organicos
- 1 media mention (en 3-7 días)
```

### 15:00 - 18:00: Monitor + Optimize [3 HORAS]

```
REAL-TIME MONITORING:

PRIMERA HORA (15:00-16:00):
□ Bot responses: Latency, errors
□ Landing page: Traffic, bounces
□ Form submissions: Conversion rate
□ Social media: Engagement, share

SEGUNDA HORA (16:00-17:00):
□ Database: User count, firmas count
□ MailerLite: Email deliverability
□ Influencer responses: DMs, mentions
□ Media checks: Google News alerts

TERCERA HORA (17:00-18:00):
□ Problem resolution: Fix bugs
□ A/B test if needed: Tweak copy
□ Respond to DMs/mentions
□ Documentation: What worked

SUCCESS METRICS (END OF DAY):
✓ 100+ WhatsApp users (target)
✓ 50+ firmas (target)
✓ 10+ newsletter subscribers (target)
✓ 3+ shares organicos (target)
✓ 1 media mention (aspirational)
✓ 0 critical errors (requirement)

GO/NO-GO DECISION:
- If >50 users + 20 firmas: CONTINUE at full speed
- If <50 users: ANALYZE why, pivot messaging
- If critical error: FIX, re-launch
```

---

## CHECKLIST FINAL (BEFORE STARTING)

- [ ] Team aligned on hypothesis
- [ ] Twilio credentials ready
- [ ] GitHub branches ready (`feature/bot-whatsapp`)
- [ ] Database backups configured
- [ ] Vercel account ready for deployment
- [ ] Error monitoring (Sentry) configured
- [ ] Slack notifications for alerts
- [ ] Content calendar prepared (3 posts)
- [ ] Influencer list prepared (10 names)

---

## TIMELINE SUMMARY

```
TODAY (Lunes 28):
14:00-14:10: Team alignment
14:10-14:40: Reading
14:40-15:50: Twilio setup
STATUS: Ready for build

TOMORROW (Martes 29):
08:00-12:00: Bot development (4h)
12:00-13:00: Lunch
13:00-17:00: Landing page (4h)
STATUS: Both systems LIVE

WEDNESDAY (Miércoles 30):
08:00-10:00: Testing (2h)
10:00-13:00: Viral posts (3h)
13:00-15:00: Influencer outreach (2h)
15:00-18:00: Monitor (3h)
STATUS: Campaign running, data flowing

END OF WEEK:
SUCCESS: 100+ bot users, 50+ firmas, 10+ newsletter
DECISION: Continue or pivot messaging
```

---

## CONTINGENCY PLANS

### If Twilio setup fails today:
- Alternative: Use Whatsapp Business API directly (15 min setup)
- Fallback: Use Telegram bot instead (1 hour setup)

### If bot deployment fails tomorrow:
- Simplify MVP: Text-only responses (1h fix)
- Deploy to AWS Lambda instead of Render (1h fix)

### If landing page doesn't convert:
- A/B test copy: "Transparency" vs "Rights" messaging
- Add video testimonial (1h create + edit)

### If no influencer response:
- Expand to 20 people instead of 10
- Use paid micro-influencers (small budget)
- Focus on organic social growth

---

## RESOURCES NEEDED

**Software/Services:**
- Twilio account (paid, ~$50/mes)
- Vercel account (free tier ok)
- MailerLite account (free, 1K subscribers)
- Tally.so form (free)

**Team Hours:**
- Dev 1 (Bot): 4h
- Dev 2 (Landing): 4h
- Content: 3h
- Outreach: 2h
- Monitoring: 3h
- **TOTAL: 16 hours** (doable in 3 days)

**Cost:**
- Twilio: $50/mes
- Vercel: $0 (free tier)
- MailerLite: $0 (free tier, 1K limit)
- Domain: Already have
- **TOTAL: $50/mes**

---

## SIGN-OFF

This plan is detailed enough to execute without guessing.

It's aggressive (16 hours in 3 days) but doable.

Success metric: 100 bot users + 50 firmas by Friday EOD.

If we hit that, we scale. If we miss, we pivot.

Either way, we'll have REAL DATA about product-market fit.

---

**Documento:** PLAN_24_HORAS.md  
**Estado:** ✅ LISTO PARA EJECUTAR  
**Próximo paso:** Twilio setup HOY  
**Revisión:** Mañana 08:00 (antes de comenzar bot dev)
