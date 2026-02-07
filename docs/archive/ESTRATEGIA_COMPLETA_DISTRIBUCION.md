# ESTRATEGIA COMPLETA: DISTRIBUCIÓN DESCENTRALIZADA + COLABORACIÓN

## Visión
**"PreciosRegulados.uy: La plataforma donde consumidores uruguayos comparten cómo ahorrar en servicios regulados"**

El valor no es solo mostrar precios. Es:
- 📱 **Recibir tips semanales** por WhatsApp (notificaciones)
- 🌳 **Ver qué beneficios tengo** según mis servicios (árbol de decisión)
- 🤝 **Aportar mis propios tips** que otros usan (comunidad)
- ✅ **Validado colectivamente** (transparencia)

---

## A. Arquitectura general (sin código nuevo, solo config)

```
USUARIO
  ├─ Visita sitio
  │   ├─ Lee tips/promos
  │   ├─ Usa árbol de beneficios
  │   └─ Ve "esto fue sugerido por Usuario X"
  │
  ├─ Se suscribe a WhatsApp
  │   ├─ Llena formulario simple
  │   └─ Recibe 1 tip/semana automático
  │
  └─ Propone nuevo tip/promo
      ├─ Rellena formulario web (/contribuir)
      ├─ Tú validas en 24-48hs
      └─ Si es correcto, aparece con su nombre

INFRAESTRUCTURA
  ├─ backend/content/
  │   ├─ promos.json (promos vigentes)
  │   ├─ tips.json (tips de ahorro)
  │   ├─ derechos.json (derechos del consumidor)
  │   ├─ casos_reales.json (historias de usuarios)
  │   └─ servicios_beneficios.json (árbol de decisión)
  │
  ├─ base de datos (mínima)
  │   └─ whatsapp_suscriptores (números + preferencias)
  │
  ├─ WhatsApp Bot (Twilio)
  │   └─ Envía 1 mensaje/semana automático
  │
  └─ Frontend
      ├─ Página /contribuir (formulario)
      ├─ Sección "Árbol de beneficios"
      └─ Badges "Sugerencia de Usuario X"
```

---

## B. Diferencial competitivo claro

### Sin esto (estado actual):
- Usuario busca "precio nafta uruguay"
- Ve el precio en el sitio
- Se va

### Con esto (propuesta):
- Usuario busca "cómo ahorrar en cable"
- Ve **tip**: "Bajá a 1 canalera + Android TV = $1.200/mes menos"
- Ve **árbol**: "Según mi contrato, tengo acceso a estas promos"
- Se suscribe a WhatsApp
- Recibe tip nuevo cada semana (sin hacer nada)
- Propone su propio ahorro (comunidad)

**Diferencial:** No es un precio más. Es "educación y comunidad sobre ahorros en servicios regulados".

---

## C. Roadmap de implementación (4 semanas, ~15 horas total)

### SEMANA 1: Contenido base + formulario web

**Esfuerzo:** ~6 horas

**Qué hacer:**
1. ✅ Crear carpeta `backend/content/` con JSONs base (1 hora)
   - Copiar estructura de PLAN_CONTENIDO_DESCENTRALIZADO.md
   - Poner 5-10 promos reales + 5 tips reales
2. ✅ Crear endpoints GET `/api/v1/contenido/*` (1 hora)
   - `/contenido/promos`
   - `/contenido/tips`
   - `/contenido/derechos`
3. ✅ Crear página `/contribuir` en frontend (2 horas)
   - Formulario React simple
   - POST a `/api/v1/contribuciones`
4. ✅ Crear endpoint POST `/api/v1/contribuciones` (1 hora)
   - Guarda a `backend/contribuciones/pendientes.jsonl`
5. ✅ Banner en sitio: "Colabora" → `/contribuir` (1 hora)

**Resultado:** Sitio permite contribuciones, contenido vive en JSON.

---

### SEMANA 2: Árbol de beneficios + UI mejorada

**Esfuerzo:** ~4 horas

**Qué hacer:**
1. ✅ Crear `servicios_beneficios.json` (1 hora)
   - Mapeo: servicio → lista de beneficios aplicables
2. ✅ Crear página "Árbol de beneficios" (2 horas)
   - Usuario selecciona servicios ✓
   - Muestra beneficios filtrados
3. ✅ Agregar badges "Sugerencia de Usuario X" a contenido (1 hora)
   - En cards de promos/tips

**Resultado:** Usuario ve qué beneficios aplican a SUS servicios.

---

### SEMANA 3: WhatsApp Bot setup + scheduler

**Esfuerzo:** ~4 horas

**Qué hacer:**
1. ✅ Setup Twilio account (0.5 horas)
   - Crear cuenta, obtener credenciales
   - Poner en `.env`
2. ✅ Habilitar endpoints WhatsApp (1.5 horas)
   - POST `/whatsapp/subscribe`
   - GET `/whatsapp/webhook`
   - POST `/whatsapp/test`
3. ✅ Agregar tabla `whatsapp_suscriptores` a BD (0.5 horas)
   - 1 migración simple
4. ✅ Agregar job al scheduler para enviar tips (1 hora)
   - Lee JSON de tips
   - Selecciona 1 random o próximo en cola
   - Envía a todos los suscriptores
5. ✅ Agregar QR en footer del sitio (0.5 horas)

**Resultado:** Usuarios pueden suscribirse a WhatsApp, reciben 1 tip/semana automático.

---

### SEMANA 4: Validación, pulido, lanzamiento

**Esfuerzo:** ~1 hora (mínimo, el resto es pruebas)

**Qué hacer:**
1. ✅ Testear flujo completo:
   - Contribuir via formulario → Revisar → Mergear → Aparece en sitio
   - Suscribirse a WhatsApp → Recibir mensajes
   - Ver árbol de beneficios → Filtra correctamente
2. ✅ Documentar proceso de contribución
3. ✅ Promover en sitio/redes

**Resultado:** Todo listo para producción.

---

## D. Esfuerzo total estimado

| Semana | Tarea | Horas | Acumulado |
|--------|-------|-------|-----------|
| 1 | Contenido + formulario | 6 | 6 |
| 2 | Árbol de beneficios | 4 | 10 |
| 3 | WhatsApp Bot | 4 | 14 |
| 4 | Pruebas + lanzamiento | 1 | **15** |

**Total: ~15 horas (2-3 sesiones de 5-6 horas)**

---

## E. Costos reales

| Recurso | Costo/mes | Notas |
|---------|-----------|-------|
| Dominio | $1 | Ya tienes |
| Cloudflare | $0 | Free tier |
| Render backend | $0 | Free tier |
| PostgreSQL | $0 | Free tier (1 GB) |
| Twilio (WhatsApp) | $0.30 | 100 suscriptores × 1 msg/semana × $0.03 |
| **TOTAL** | **$1.30/mes** | Menos de $20/año |

---

## F. Flujo usuario final (paso a paso)

### Scenario 1: María quiere ahorrar en cable

```
María entra a cuantocuestauruguay.com
        ↓
Ve sección "Ahorra en servicios regulados"
        ↓
Selecciona: "Tengo cable Directv con 3 canaleras"
        ↓
El sitio muestra:
  ✅ Idea: Baja a 1 canalera + Android TV
  ✅ Ahorro: $1.200/mes
  ✅ Pasos exactos: [1] Llama a Directv, [2] Pide bajar, etc.
  ✅ Este tip fue sugerido por Usuario X
        ↓
María cliquea "Recibir tips así por WhatsApp"
        ↓
Lleна formulario rápido (número + intereses)
        ↓
Recibe confirmación: "Cada semana, nuevo tip a las 9 AM"
        ↓
[Próxima semana, viernes 9 AM]
María recibe en WhatsApp:
  📊 Ahorro semanal
  ─────────────────
  Paramount+ gratis 1 año si tienes Flow
  Ahorro: $300/mes
  Pasos: https://cuantocuestauruguay.com/tips/paramount
  ¿Encontraste un tip? Escribe "CONTRIBUIR"
```

### Scenario 2: Juan descubre una promo

```
Juan renova su internet con Antel
        ↓
Le dicen: "Podés llevar Android TV a precio especial"
        ↓
Entra a cuantocuestauruguay.com
        ↓
Cliquea "Colabora": /contribuir
        ↓
Rellena:
  Tipo: Promo vigente
  Proveedor: Antel
  Descripción: "Renovar internet → Android TV con descuento"
  Link: https://www.antel.com.uy/personas/planes-internet
  Mi nombre: Juan (opcional)
        ↓
[24 horas después]
        ↓
TÚ recibís notificación
Revisas: ✓ Fuente oficial confirmada
Mergeas a promos.json
        ↓
Aparece en sitio con:
  "Sugerencia de Juan"
  "Validado 6 de febrero"
        ↓
Juan recibe email:
  "¡Gracias! Tu aporte fue validado
   140 usuarios leyeron tu promo esta semana"
```

---

## G. Métrica de éxito (mes 1)

| Métrica | Target | Cómo medir |
|---------|--------|-----------|
| Contribuciones validadas | 5+ | Contar en JSON |
| Suscriptores WhatsApp | 10+ | BD de Twilio |
| Visitantes únicos | 50+ | Google Analytics |
| Mensajes abiertos | 50%+ | Twilio reporta |
| Tasa de rechazo | <10% | Logs de contribuciones |

---

## H. Mantenimiento después del lanzamiento

### Operaciones diarias (~5 minutos):
- Revisar contribuciones pendientes (endpoint GET)
- Validar fuentes (Google, links oficiales)
- Mergear JSON si es correcto
- Responder email de agradecimiento

### Operaciones semanales (~30 minutos):
- Seleccionar siguiente tip para enviar
- Revisar si alguna promo expiró
- Actualizar vigencias

### Operaciones mensuales (~30 minutos):
- Revisar analytics
- Responder feedback en Issues
- Crear post en redes con "top contribuidores"

**Total: ~1 hora/semana** (muy manejable)

---

## I. Cómo promover (sin presupuesto)

### En el sitio:
- Banner en Home: "¿Ahorras en servicios? ¡Comparte!"
- Modal al llegar: "Suscribirse a tips por WhatsApp"
- Footer: "Colabora" → `/contribuir`

### En WhatsApp:
- Mensaje semanal: "¿Encontraste una promo? Escribí CONTRIBUIR"

### Redes sociales (si las activas):
```
🇺🇾 "En Uruguay, los servicios son caros.
Pero hay ahorros que casi nadie conoce.

📱 Recibí 1 tip/semana en WhatsApp
🌳 Ve qué beneficios tienes según tu servicio
🤝 Comparte TÚ descubrimientos, apareces en el sitio

Entra: https://cuantocuestauruguay.com
"
```

---

## J. Escalamiento futuro (meses 2-6)

### Si funciona:
1. **Gamificación leve:**
   - Badges: "🌟 Colaborador verificado" después de 3 aportes
   - Ranking: "Top 5 colaboradores del mes"

2. **Integración CRM:**
   - Email newsletter semanal (en lugar de solo WhatsApp)
   - Segmentación: "Tips solo para Antel" si prefieres

3. **API pública:**
   - Otros sitios pueden usar tu contenido
   - "Powered by PreciosRegulados.uy"

4. **Moneda comunitaria:**
   - Puntos por aportes (en futuro, nada ahora)

Pero eso es después. Primero, que funcione lo básico.

---

## K. Documentación para usuarios

Crea en el sitio:

### `/guia-colaborar`
```markdown
# ¿Cómo colaborar en PreciosRegulados.uy?

## Opción 1: Formulario web (más fácil)
Entra a /contribuir y rellena en 2 minutos.

## Opción 2: GitHub
Si sabes editar JSON, haz un PR directo.

## Qué puedo contribuir?
- Promos vigentes (con fuente oficial)
- Tips de ahorro
- Derechos del consumidor poco conocidos
- Mi historia: cómo ahorré

## ¿Qué pasa después?
1. Envías tu aporte
2. Nosotros lo validamos (24-48 horas)
3. Si es correcto, aparece en el sitio con tu nombre
4. Recibirás email de agradecimiento

## ¿Hay requisitos?
- Ser honesto (verificamos fuentes)
- Informar en español
- Incluir link a fuente oficial si aplica
- Máx 300 caracteres en formulario rápido

¡Gracias por ayudar a otros uruguayos!
```

---

## L. Cuándo expandir

**No hagas esto hasta semana 5:**
- Email newsletter
- Gamificación
- Rankings
- Integraciones

Primero: **validar que usuarios contríbuyen y reciben tips.**

Una vez que eso funciona, expandés.

---

## M. Resumen ejecutivo

| Aspecto | Qué es | Por qué |
|---------|--------|--------|
| **Contenido** | Promos/tips en JSON | Fácil de actualizar, versionado |
| **Distribución** | WhatsApp semanal | Alto engagement, push notifications |
| **Comunidad** | Usuarios proponen | Contenido siempre fresco, escalable |
| **Validación** | Tú revisas en 48hs | Confianza, evita spam |
| **Diferencial** | No solo precios; educación | Valor real para el usuario |
| **Costo** | $20/año total | Sostenible |
| **Esfuerzo inicial** | 15 horas | Manejable en 1 mes |
| **Mantenimiento** | 1 hora/semana | Muy liviano |

---

## N. Próximos pasos

1. **Esta semana:** Revisa los 3 documentos (`PLAN_WHATSAPP_BOT.md`, `PLAN_CONTENIDO_DESCENTRALIZADO.md`, `PLAN_COLABORACION_COMUNITARIA.md`)
2. **Semana 2:** Comienza Semana 1 del roadmap (contenido + formulario)
3. **Semana 3-6:** Sigue roadmap paso a paso

El código ya existe. Solo necesita config + contenido inicial.

**¿Preguntas? Revisa el documento específico.**

