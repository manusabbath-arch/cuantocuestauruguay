# 3. ESTRATEGIA DE COLABORACIÓN COMUNITARIA

## El concepto
**"PreciosRegulados.uy es hecho por y para usuarios uruguayos"**

En lugar de tú hacer todo, los usuarios aportan:
- Tips de ahorro que descubrieron
- Promos que encontraron
- Casos reales de cómo ahorraron
- Errores en facturas que detectaron
- Derechos del consumidor que nadie usa

Tú validas, mergeas, y aparecen en el sitio. Ellos aparecen como "Contribuidor".

---

## A. Formas de contribuir (ranking por facilidad)

### 1️⃣ **Formulario web (más fácil, 2 minutos)**

**Dónde:** Nueva sección en sitio `/contribuir`

**Formulario:**
```
Quiero contribuir:

☐ Una promo que descubrí
☐ Un tip de ahorro
☐ Un derecho que casi nadie usa
☐ Una historia real
☐ Un error en el sitio

Mi aporte (max 300 caracteres):
[textarea]

Mi nombre/usuario (opcional):
[text]

Fuente oficial (si aplica):
[text]

[Enviar]

✅ "Gracias, lo revisamos en 48hs"
```

**Dónde va:** Correo tuyo o formulario en backend (POST /api/v1/contribuciones)

**Costo:** 0, es un formulario

---

### 2️⃣ **GitHub Issues (medio, 5 minutos)**

**Dónde:** https://github.com/tuuser/cuantocuestauruguay/issues

**Template de issue:**
```markdown
**Tipo de aporte:** [Promo / Tip / Derecho / Caso / Error]

**Título:** [descripción corta]

**Contenido:**
[descripción detallada]

**Fuente oficial:**
[link si aplica]

**Mi nombre/usuario:** [opcional]

**Cómo verificación:** [cómo alguien puede confirmar que esto es cierto]
```

**Tú validas:** Revisas, pones tag "validado", convertís a JSON, mergeas

---

### 3️⃣ **Pull Request directo (avanzado, 10 minutos)**

**Para usuarios que saben GitHub:**
- Forquean el repo
- Editan JSON directamente
- Hacen PR con descripción

**Tú revisas y mergeas**

---

## B. Sistema de validación simple

### Niveles de confianza:

| Badge | Criterio | Efecto |
|-------|----------|--------|
| ✅ **Validado** | Admin revisó + verificó fuente oficial | Aparece destacado |
| 🔍 **Pendiente** | En revisión | Aparece con asterisco |
| ⚠️ **Dubtoso** | Admin cree que es incorrecto | Aparece con warning |
| ❌ **Rechazado** | Falso, spam, incompleto | No aparece |

---

## C. Formulario en sitio (UI simple)

### Página `/contribuir`

```
═════════════════════════════════════════════════
🤝 COLABORA CON PRECIOSREGULADOS.UY

Ayudá a otros uruguayos a ahorrar compartiendo:
✓ Promos que no conoce nadie
✓ Tips de ahorro reales
✓ Derechos del consumidor
✓ Tu historia de ahorro

═════════════════════════════════════════════════

[Opción 1] FORMULARIO RÁPIDO
┌─────────────────────────────────────────┐
│ Quiero contribuir:                      │
│ ○ Promo vigente                         │
│ ○ Tip de ahorro                         │
│ ○ Derecho del consumidor                │
│ ○ Mi historia real                      │
│ ○ Un error en el sitio                  │
│                                         │
│ Cuéntame (300 caracteres máx):          │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Mi nombre/usuario (opcional):           │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [ENVIAR]                                │
└─────────────────────────────────────────┘

[Opción 2] GITHUB (Si sabes código)
[Link a issues]

═════════════════════════════════════════════════

Los mejores aportes aparecen con tu nombre
como "Sugerencia de Usuario X"
```

---

## D. Backend para formulario

### Endpoint:
```python
# backend/app/routers/contribuciones.py

@router.post("/api/v1/contribuciones")
async def crear_contribucion(
    tipo: str,  # "promo", "tip", "derecho", "caso", "error"
    contenido: str,
    nombre: Optional[str] = None,
    fuente: Optional[str] = None
):
    """Guarda contribución para revisión manual"""
    
    contribucion = {
        "id": generate_uuid(),
        "tipo": tipo,
        "contenido": contenido,
        "nombre": nombre or "Anónimo",
        "fuente": fuente,
        "fecha": datetime.now(),
        "estado": "pendiente_revision",
        "validado": False
    }
    
    # Guardar en archivo JSON o BD simple
    with open("backend/contribuciones/pendientes.json", "a") as f:
        f.write(json.dumps(contribucion) + "\n")
    
    # Email a ti (opcional)
    # send_email("admin@cuantocuestauruguay.com", 
    #           f"Nueva contribución: {tipo}")
    
    return {
        "status": "recibido",
        "message": "Gracias! Lo revisamos en 48hs",
        "id": contribucion["id"]
    }
```

### Flujo de revisión (manual, 5 minutos por contribución):

1. Recibís POST a `/contribuciones`
2. Se guarda en `backend/contribuciones/pendientes.jsonl`
3. Tú ves lista en admin panel o archivo
4. Validás la fuente (Google, link oficial, etc.)
5. Si es correcto:
   - Copias al JSON correspondiente (promos.json, tips.json, etc.)
   - Agregás: `"contribuyente": "Usuario X"`, `"validado": true`
   - Haces commit y push
6. Si es incorrecto:
   - Marcás como rechazado
   - (Opcional) respondes por email

**Tiempo por contribución:** 5 minutos máximo

---

## E. Badges e incentivos

### En el sitio:
Cada promo/tip/caso que viene de un usuario muestra:
```
Sugerencia de Usuario X
📌 Validado 5 feb 2026
```

### Ranking de contribuidores (opcional):
```
🏆 Top colaboradores

1. Usuario1: 8 aportes
2. Usuario2: 5 aportes
3. Usuario3: 3 aportes
```

### Email de agradecimiento:
```
Hola [Nombre],

Tu aporte fue validado y ahora aparece en PreciosRegulados.uy
Título: [promo/tip]
Impacto: 120 personas leyeron tu aporte este mes

¡Gracias por ayudar a otros uruguayos a ahorrar!

[Link al aporte]
```

---

## F. Gestión de colaboradores activos

### Aumentar confianza a usuarios activos:

Después de 3 aportes validados:
```
🌟 COLABORADOR VERIFICADO

[Usuario X] ha aportado 3 sugerencias validadas.
Sus nuevos aportes se publican automáticamente sin revisión.
```

Eso acelera el ciclo y los usuarios se sienten "parte del equipo".

---

## G. Comunicación (cómo promocionar contribuciones)

### En sitio:
- Banner: "¿Encontraste una promo? ¡Comparte!"
- Footer: "Contribuir" → `/contribuir`
- Modales: "¿Te gustó este tip? Ayuda a otros compartiéndolo o contribuyendo uno nuevo"

### En WhatsApp:
```
💡 Tenés una promo o tip para compartir?
Escribí: CONTRIBUIR
Y aparecés en PreciosRegulados.uy 🌟
```

### En redes (si las activas):
```
🙋 ¿Encontraste un ahorro? ¡Cuéntanos!

DM o comentá:
- Una promo vigente
- Un tip de ahorro
- Tu historia de cómo ahorraste

Los mejores aportes aparecen en el sitio
con tu nombre 👇
[Link a formulario]
```

---

## H. Flujo de colaboración visual

```
Usuario descubre promo
         ↓
Llena formulario web (/contribuir)
         ↓
POST → backend/contribuciones/pendientes.jsonl
         ↓
TÚ recibís notificación (email o panel)
         ↓
TÚ revisas en 24-48 horas
         ↓
¿Es correcto? 
├─ SÍ → Agregás a JSON (promos.json)
│       ↓
│       Commit + Push
│       ↓
│       Aparece en sitio automáticamente
│       ↓
│       Email de agradecimiento al usuario
│
└─ NO → Marcás como "rechazado"
        (Opcional: le explicás por qué)
```

---

## I. Moderación y spam

### Validaciones automáticas:
```python
def validar_contribucion(contrib):
    if len(contrib['contenido']) < 20:
        return False, "Muy corto"
    if "http" not in contrib['contenido'] and contrib['tipo'] in ['promo', 'derecho']:
        return False, "Necesita fuente oficial"
    if spam_detector(contrib['contenido']):
        return False, "Spam detectado"
    return True, "OK"
```

### Reglas simples:
- Mínimo 20 caracteres
- Si es promo/derecho: debe incluir fuente oficial o link
- Sin links sospechosos (acortadores, phishing)
- Sin publicidad (puede auto-rechazarse)

---

## J. Implementación (esfuerzo estimado)

| Tarea | Esfuerzo | Notas |
|-------|----------|-------|
| Endpoint POST /contribuciones | 30 min | Guardar a JSON |
| Página `/contribuir` frontend | 1.5 horas | Form React simple |
| Validaciones automáticas | 1 hora | Regex + checks |
| Panel admin (ver pendientes) | 1 hora | Listar JSONs |
| Documentar proceso | 30 min | README |
| **Total** | **~4.5 horas** | **Listo en 1 sesión** |

---

## K. Ventajas de este modelo

✅ **Tú no generás contenido:** Los usuarios lo hacen  
✅ **Escalable:** Más usuarios = más aportes sin que hagas nada  
✅ **Confiable:** Comunidad auto-valida  
✅ **Actualizado:** Promos y tips siempre frescos  
✅ **Engagement:** Los usuarios se sienten parte  
✅ **Sin costo:** Solo tu tiempo de validación (5 min/aporte)  
✅ **Legítimo:** No inventás, recopilás lo que existe  

---

## L. Ejemplo de impacto

**Mes 1:** 5 contribuciones validadas  
**Mes 2:** 12 contribuciones validadas  
**Mes 3:** 25 contribuciones validadas  

En 3 meses tenés **40+ promos/tips actualizadas** sin que hayas escrito casi nada.

---

## M. Mejores prácticas comunitarias

1. **Responde siempre:** Aunque rechaces, explica por qué
2. **Destaca aportes buenas:** En redes, en boletín, en sitio
3. **Agradecer explícitamente:** Email, mención, badge
4. **Ser transparente:** Que vean el proceso (JSON público en GitHub)
5. **Ser inclusivo:** Acepta aportes anonimizados si la persona prefiere

