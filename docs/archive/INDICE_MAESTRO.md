# 📑 ÍNDICE MAESTRO: Estrategia de Distribución y Colaboración

## Para dónde empezar

Si tienes **15 minutos**: Lee esta sección  
Si tienes **1 hora**: Lee los 3 documentos principales  
Si tienes **4 horas**: Implementa Semana 1  

---

## 📚 Documentos creados (cómo usarlos)

### 1. **ESTRATEGIA_COMPLETA_DISTRIBUCION.md** ← EMPIEZA AQUÍ
   - **Qué es:** Visión completa + roadmap de implementación
   - **Leer cuándo:** Primero, para entender el concepto general
   - **Tiempo:** 15 minutos
   - **Output:** Entiendes PARA QUÉ estás haciendo todo esto
   - **Sección clave:** "Esfuerzo total estimado" (15 horas en 4 semanas)

### 2. **PLAN_CONTENIDO_DESCENTRALIZADO.md** ← SEMANA 1
   - **Qué es:** Cómo guardar y gestionar promos/tips sin código
   - **Leer cuándo:** Cuando vayas a implementar
   - **Tiempo:** 20 minutos
   - **Output:** Entiendes la estructura JSON
   - **Sección clave:** "Estructura de promos.json"

### 3. **PLAN_WHATSAPP_BOT.md** ← SEMANA 3
   - **Qué es:** Cómo activar WhatsApp para distribuir tips
   - **Leer cuándo:** Después de semana 2, antes de implementar
   - **Tiempo:** 20 minutos
   - **Output:** Sabes qué configurar en Twilio
   - **Sección clave:** "Setup de Twilio" (15 minutos)

### 4. **PLAN_COLABORACION_COMUNITARIA.md** ← SEMANA 1 + OPCIONAL
   - **Qué es:** Cómo hacer que usuarios aporten tips
   - **Leer cuándo:** En paralelo con semana 1
   - **Tiempo:** 20 minutos
   - **Output:** Sistema de formulario + validación
   - **Sección clave:** "Backend para formulario"

### 5. **CONTENIDO_INICIAL_LISTO.md** ← SEMANA 1 (EN PARALELO)
   - **Qué es:** 15 promos/tips/casos listos para copiar/pegar
   - **Leer cuándo:** Cuando empieces a llenar los JSONs
   - **Tiempo:** 5 minutos (es copia/pega)
   - **Output:** Tienes contenido inicial para no empezar en blanco
   - **Sección clave:** "JSON READY"

---

## 🛣️ Roadmap de implementación (semana a semana)

### SEMANA 1: Contenido base + formulario web
**Esfuerzo:** 6 horas | **Orden de lectura:** Docs 1, 2, 5

```
Día 1-2:
├─ Leer ESTRATEGIA_COMPLETA (15 min)
├─ Leer PLAN_CONTENIDO_DESCENTRALIZADO (20 min)
└─ Crear carpeta backend/content/

Día 2-3:
├─ Copiar estructura JSON (30 min, usa CONTENIDO_INICIAL_LISTO.md)
├─ Poner 5 promos + 5 tips (1 hora)
└─ Crear endpoints GET /api/v1/contenido/* (1 hora)

Día 3-4:
├─ Crear página /contribuir en frontend (2 horas)
├─ Crear endpoint POST /api/v1/contribuciones (1 hora)
└─ Testear flujo de contribución (30 min)

Día 5:
├─ Agregá banner "Colabora" en Home (30 min)
├─ Hacé commit: "feat: content management + contributions form" (10 min)
└─ Push a producción (10 min)

RESULTADO: Sitio permite aportes, contenido en JSON, puedes agregar cosas sin tocar código.
```

---

### SEMANA 2: Árbol de beneficios + UI mejorada
**Esfuerzo:** 4 horas | **Orden de lectura:** Doc 2

```
Día 1:
├─ Crear servicios_beneficios.json (1 hora)
└─ Documentar estructura (15 min)

Día 2-3:
├─ Crear página "Árbol de beneficios" React (2 horas)
└─ Usuario selecciona servicios ✓

Día 4:
├─ Agregar badges "Sugerencia de Usuario X" en cards (1 hora)
└─ Testear filtrado de beneficios

Día 5:
├─ Hacé commit: "feat: benefits tree + contributor badges" (10 min)
└─ Push a producción (10 min)

RESULTADO: Usuario ve exactamente qué beneficios le aplican.
```

---

### SEMANA 3: WhatsApp Bot setup + scheduler
**Esfuerzo:** 4 horas | **Orden de lectura:** Doc 3

```
Día 1:
├─ Setup Twilio (15 min)
│  └─ Ir a twilio.com, crear cuenta, copiar credenciales
├─ Poner credenciales en .env (5 min)
└─ Crear tabla whatsapp_suscriptores (30 min)

Día 2:
├─ Habilitar endpoints POST/GET /whatsapp/* (1.5 horas)
└─ Testear webhook de Twilio

Día 3:
├─ Agregar job al scheduler para enviar tips (1 hora)
├─ Selecciona 1 tip random del JSON
└─ Envía a todos los suscriptores

Día 4:
├─ Agregar QR en footer (30 min)
├─ Agregar call-to-action en sitio (30 min)
└─ Testear flujo: suscribir → recibir mensaje

Día 5:
├─ Hacé commit: "feat: whatsapp bot integration + scheduler" (10 min)
└─ Push a producción (10 min)

RESULTADO: Usuarios pueden suscribirse, reciben 1 tip/semana automático.
```

---

### SEMANA 4: Validación y lanzamiento
**Esfuerzo:** 1 hora | **Orden de lectura:** Nada, solo testing

```
Día 1-2:
├─ Testear flujo completo
│  ├─ Contribuir via formulario
│  ├─ Tú validar → mergear JSON
│  ├─ Aparece en sitio automáticamente
│  └─ Usuario ve "Sugerencia de [User]"

Día 3:
├─ Testear WhatsApp
│  ├─ Suscribirse via QR
│  └─ Recibir mensaje próximo viernes 9 AM

Día 4:
├─ Documentar para usuarios
│  ├─ Página /guia-colaborar
│  ├─ FAQ sobre promos
│  └─ Cómo contactar si hay dudas

Día 5:
├─ Promover en sitio/redes
└─ LANZAMIENTO 🎉

RESULTADO: Sistema en producción, listo para que usuarios colaboren.
```

---

## 📊 Checksum (qué checkeás semana a semana)

### Después de SEMANA 1
- ✅ Carpeta `backend/content/` existe con JSONs
- ✅ Endpoints GET `/api/v1/contenido/*` devuelven JSON
- ✅ Página `/contribuir` existe y tiene formulario
- ✅ POST `/api/v1/contribuciones` guarda a `pendientes.jsonl`
- ✅ Banner "Colabora" aparece en Home

**Test:** Abre `/api/v1/contenido/promos` → debe devolver JSON con 5+ promos

---

### Después de SEMANA 2
- ✅ Archivo `servicios_beneficios.json` existe
- ✅ Página `/beneficios` (o sección) existe
- ✅ Usuario puede seleccionar servicios ✓
- ✅ Aparecen beneficios filtrados
- ✅ Cards muestran "Sugerencia de Usuario X"

**Test:** Selecciona "Internet Antel" → debe mostrar beneficios de Antel

---

### Después de SEMANA 3
- ✅ Twilio está configurado, credenciales en `.env`
- ✅ Tabla `whatsapp_suscriptores` existe en BD
- ✅ Endpoints `/whatsapp/*` funcionan
- ✅ Scheduler envía 1 tip/semana (puedes testear manualmente)
- ✅ QR en footer del sitio funciona
- ✅ Usuario que escanea QR → abre WhatsApp → dice "Suscribirse"

**Test:** Escanea QR con celular → abre WhatsApp → escribí "Suscribirse" → deberías recibir confirmación

---

### Después de SEMANA 4
- ✅ Contribuir → validar → mergear → aparece en sitio (fin a fin)
- ✅ Usuarios en WhatsApp reciben 1 tip/semana
- ✅ Página `/guia-colaborar` está publicada
- ✅ No hay bugs críticos

**Test:** Haz contribución de prueba, valida, mergea, verifica que aparece en sitio

---

## 🎯 KPIs de éxito (mes 1)

| Métrica | Target | Cómo medir |
|---------|--------|-----------|
| Contribuciones validadas | 5+ | Contar en `promos.json` |
| Suscriptores WhatsApp | 10+ | Query BD: `SELECT COUNT(*) FROM whatsapp_suscriptores WHERE activo=true` |
| Mensajes abiertos | 50%+ | Twilio reporta (tasa de lectura) |
| Aportes rechazados | <10% | Si cumples validaciones |
| Bugs críticos | 0 | Check logs |

---

## 📞 Preguntas frecuentes

**P: "¿Tengo que hacer todo de una?"**  
R: No. Semana 1 es **independiente** de semanas 2-3. Podes lanzar solo la semana 1 y funciona.

**P: "¿Dónde guardo las contribuciones pendientes?"**  
R: Opción A: Archivo JSONL local (`backend/contribuciones/pendientes.jsonl`). Opción B: Tabla en BD. Te recomiendo A por simplicidad.

**P: "¿El contenido se actualiza automáticamente?"**  
R: SÍ. El frontend/bot leen el JSON en GitHub. Al hacer push, en 1-2 minutos aparece en el sitio.

**P: "¿Cuánto cuesta Twilio?"**  
R: Con 100 suscriptores × 1 msg/semana = ~$13/mes. FREE el primer mes. Después ~$0.03 por mensaje.

**P: "¿Qué pasa si alguien envía spam?"**  
R: Tenés validaciones automáticas + tú revisas en 24-48hs. Si es spam, lo marcas como rechazado y no aparece.

**P: "¿Puedo cambiar los JSONs sin redeploy?"**  
R: SÍ. Los JSONs son archivos estáticos en el repo. Edítalo, hace commit/push, y automáticamente se actualiza en producción (1-2 min).

**P: "¿Qué hago si un aporte tiene error después de publicado?"**  
R: Editás el JSON, corriges el error, commits/push. Se actualiza automáticamente. Opcional: escribís email al usuario explicando la corrección.

---

## 🚀 Próximos pasos

1. **Hoy:** Leer ESTRATEGIA_COMPLETA.md (15 min)
2. **Esta semana:** Implementar SEMANA 1 (6 horas)
3. **Próxima semana:** Implementar SEMANA 2 (4 horas)
4. **Semana 3:** Implementar SEMANA 3 (4 horas)
5. **Semana 4:** Validar y lanzar (1 hora)

**Total: 15 horas en 4 semanas.**

---

## 📖 Orden de lectura (por prioridad)

1. **ESTRATEGIA_COMPLETA_DISTRIBUCION.md** (visión general)
2. **CONTENIDO_INICIAL_LISTO.md** (para copiar/pegar)
3. **PLAN_CONTENIDO_DESCENTRALIZADO.md** (estructura técnica)
4. **PLAN_COLABORACION_COMUNITARIA.md** (formulario web)
5. **PLAN_WHATSAPP_BOT.md** (distribución automática)

---

## 💡 Insights clave

- **No es sobre precios.** Es sobre **educación y comunidad.**
- **Los usuarios son tu mejor fuente de contenido.** Ellos descubren ahorros que vos no ves.
- **Simple es mejor.** Un JSON con 5 promos > una BD compleja con 0 ahorros.
- **Descentralizado > centralizado.** GitHub versionado > admin panel cerrado.
- **Validación rápida = confianza rápida.** 24-48hs máximo, siempre responder.

---

**¿Preguntas? Revisa el documento específico.**

**¿Listo para empezar SEMANA 1?**

→ Leer `PLAN_CONTENIDO_DESCENTRALIZADO.md` + `CONTENIDO_INICIAL_LISTO.md`

