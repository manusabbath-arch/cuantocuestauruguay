# 2. SISTEMA DE CONTENIDO DESCENTRALIZADO

## El problema
Promos cambian constantemente. No puedes actualizar código cada semana. Necesitas que el contenido (tips, promos, derechos) esté **versionado, editable y colaborativo**.

## La solución: Archivo JSON en el repo

---

## A. Estructura de carpeta

```
backend/
├── content/
│   ├── README.md                    (instrucciones)
│   ├── promos.json                  (promos vigentes)
│   ├── tips.json                    (tips de ahorro)
│   ├── derechos.json                (derechos del consumidor)
│   ├── casos_reales.json            (historias de usuarios)
│   └── changelog.md                 (histórico de cambios)
```

---

## B. Estructura de promos.json

```json
{
  "promos": [
    {
      "id": "paramount-flow-2026",
      "titulo": "Paramount+ gratis 1 año con Flow",
      "descripcion_corta": "Si tienes contrato activo de Flow, accedes a Paramount+ sin costo por 12 meses",
      "servicio": "TV/Streaming",
      "proveedor": "Directv/Flow",
      "requisitos": [
        "Tener contrato activo de Flow",
        "Descargar app Paramount+ o usar en Smart TV"
      ],
      "pasos": [
        "Entrá a https://flow.com.uy/paramount",
        "Ingresá con tus datos de Flow",
        "Confirmá activación",
        "Listo, mirá gratis por 1 año"
      ],
      "ahorro_estimado": "$300/mes",
      "vigencia_desde": "2026-01-01",
      "vigencia_hasta": "2026-12-31",
      "fuente_oficial": "https://flow.com.uy/paramount",
      "contribuyente": "Usuario anónimo",
      "validado": true,
      "validado_por": "Admin",
      "fecha_validacion": "2026-02-05",
      "tags": ["streaming", "tv", "directv", "paramount"]
    },
    {
      "id": "antel-android-renovacion",
      "titulo": "Android TV Box 100% descuento al renovar internet",
      "descripcion_corta": "Si renovás tu contrato de internet con Antel, accedés a Android TV Box sin costo",
      "servicio": "Internet/TV",
      "proveedor": "Antel",
      "requisitos": [
        "Contrato de internet activo",
        "Renovar plan por 24 meses"
      ],
      "pasos": [
        "Llamá a Antel: 911 (desde celular) o 1004 (desde teléfono)",
        "Pedí: 'Quiero renovar mi contrato y tengo derecho a Android TV Box'",
        "Acordá plan nuevo",
        "Confirma en contrato que incluye equipamiento"
      ],
      "ahorro_estimado": "$2.200 (precio del equipo)",
      "vigencia_desde": "2025-12-01",
      "vigencia_hasta": "2026-06-30",
      "fuente_oficial": "https://www.antel.com.uy/personas/planes-internet",
      "contribuyente": "Tu usuario (ejemplo)",
      "validado": true,
      "validado_por": "Admin",
      "fecha_validacion": "2026-02-05",
      "tags": ["internet", "equipamiento", "antel", "renovacion"]
    }
  ],
  "version": "1.2.0",
  "ultima_actualizacion": "2026-02-05"
}
```

---

## C. Estructura de tips.json

```json
{
  "tips": [
    {
      "id": "tip-canaleras-streaming",
      "titulo": "Bajá de 3 a 1 canalera + streaming = ahorro de $1.200",
      "categoria": "TV/Streaming",
      "dificultad": "facil",
      "tiempo_lectura": "3 min",
      "contenido": {
        "resumen": "Si tenés 3 canaleras de TV (cable clásico), bajar a 1 + contratar Android TV para streaming te sale más barato",
        "contexto": "En Uruguay, un contrato de 3 canaleras cuesta ~$2.600/mes. 1 canalera + streaming cuesta ~$1.400/mes",
        "pasos": [
          "Llamá a tu proveedor (Directv, Claro, etc.)",
          "Pedí bajar a 1 sola canalera",
          "Comprá Android TV Box (Omm $1.600, Antel $2.200)",
          "Suscribite a streaming (Netflix/Disney+ ~$300/mes)",
          "Resultado: pagas $1.400/mes en lugar de $2.600"
        ],
        "ahorro": {
          "antes": "$2.600/mes",
          "despues": "$1.400/mes",
          "ahorro_mensual": "$1.200",
          "ahorro_anual": "$14.400"
        },
        "consideraciones": [
          "Necesitas WiFi para Android TV",
          "El Android TV permite usar múltiples apps (Netflix, Disney+, Flow, etc.)",
          "No pierdes canales en vivo; puedes seguir viendo con 1 canalera"
        ]
      },
      "contribuyente": "Tu usuario (ejemplo)",
      "validado": true,
      "validado_por": "Admin",
      "fecha_creacion": "2026-02-05",
      "tags": ["tv", "streaming", "ahorro", "basico"]
    }
  ],
  "version": "1.0.0"
}
```

---

## D. Estructura de derechos.json

```json
{
  "derechos": [
    {
      "id": "derecho-informacion-clara",
      "titulo": "Derecho a información clara en tu contrato",
      "normativa": "Ley de Protección del Consumidor (Ley 17.250)",
      "descripcion": "El proveedor debe informarte de forma clara y comprensible todos los términos del contrato",
      "que_debes_saber": [
        "Tarifa base mensual (sin extras)",
        "Qué está incluido y qué no",
        "Permanencia mínima (si existe)",
        "Cómo rescindir el contrato",
        "Forma de pago aceptadas"
      ],
      "como_activarlo": [
        "Pedí una copia del contrato por escrito",
        "Marcá en rojo lo que no entiendes",
        "Llamá y preguntá: 'No entiendo esto, explicá'",
        "Pedí confirmación por escrito (email)"
      ],
      "si_no_cumplen": [
        "Podés reclamar a URSEC/URSEA (según el servicio)",
        "Tenés derecho a una respuesta en máximo 15 días hábiles"
      ],
      "fuente_oficial": "https://www.gub.uy/ministerio-economia-finanzas/",
      "contribuyente": "Admin",
      "tags": ["derechos", "contrato", "informacion"]
    }
  ],
  "version": "1.0.0"
}
```

---

## E. Cómo el frontend/bot leen estos JSONs

### Opción 1: Desde URL directa (más simple)
```typescript
// Frontend
const promos = await fetch(
  'https://raw.githubusercontent.com/tuuser/cuantocuestauruguay/main/backend/content/promos.json'
).then(r => r.json())
```

### Opción 2: Endpoint en backend (más robusto)
```python
# backend/app/routers/contenido.py
@router.get("/api/v1/contenido/promos")
def obtener_promos():
    with open("backend/content/promos.json") as f:
        return json.load(f)

@router.get("/api/v1/contenido/tips")
def obtener_tips(categoria: Optional[str] = None):
    # Filtra por categoría si es necesario
    pass
```

### Opción 3: WhatsApp bot lee JSON
```python
# bot selecciona tip random del JSON y lo envía
promos = json.load(open("backend/content/promos.json"))
promo_vigente = [p for p in promos['promos'] if p['validado']]
mensaje = f"{promo_vigente[0]['titulo']}\n{promo_vigente[0]['descripcion_corta']}"
bot.send_message(numero, mensaje)
```

---

## F. Página de "Árbol de beneficios" (concepto)

### Idea visual:
```
TUS BENEFICIOS SEGÚN TUS SERVICIOS
════════════════════════════════════

¿Qué servicios tienes?

[Seleccionar]
☑ Internet Antel
☑ TV Directv  
☐ UTE
☐ OSE
☐ Móvil

[Ver mis beneficios]

════════════════════════════════════

TUS BENEFICIOS:

📱 Internet Antel:
  ├─ Renovar → Android TV Box gratis
  ├─ Planes convergentes → ahorrar $X
  └─ Cambiar a doble horario → revisar si baja costo

📺 TV Directv:
  ├─ Bajar a 1 canalera + Paramount+ gratis
  ├─ Playoff gratis si sos cliente antiguo
  └─ Bonificación por débito automático

════════════════════════════════════
Última actualización: 5 de febrero
```

### Implementación:
1. Crear página React simple
2. Leer JSON de "servicios_beneficios.json"
3. Usuario selecciona ✓
4. Muestra árbol filtrado

Archivo: `backend/content/servicios_beneficios.json`
```json
{
  "servicios": {
    "antel_internet": {
      "nombre": "Internet Antel",
      "beneficios": [
        "paramount-flow-2026",
        "antel-android-renovacion"
      ]
    },
    "directv": {
      "nombre": "TV Directv",
      "beneficios": [
        "tip-canaleras-streaming"
      ]
    }
  }
}
```

---

## G. Versionado (changelog.md)

```markdown
# Histórico de cambios

## [1.2.0] - 2026-02-05
- Agregada promo: Android TV Box 100% descuento Antel
- Actualizada vigencia: Paramount+ hasta 31/12
- Validadas 3 nuevas promos de usuarios

## [1.1.0] - 2026-01-28
- Creado archivo inicial
- 5 promos iniciales
- 8 tips de ahorro

Contribuyentes: Admin, Usuario1, Usuario2
```

---

## H. Permisos y versionado en GitHub

### Estructura:
```
main branch:
  └─ backend/content/
      └─ *.json (versionado, protegido)

Cómo agregan contenido los usuarios:
  1. Fork del repo
  2. Editan JSON (o via formulario web simple)
  3. Hacen Pull Request con descripción
  4. Tu revísas, validas, mergeas
  5. Automáticamente se actualiza en producción
```

---

## I. Implementación (esfuerzo estimado)

| Tarea | Esfuerzo | Notas |
|-------|----------|-------|
| Crear carpeta + JSONs base | 1 hora | Copiar estructura |
| Endpoint GET /contenido/* | 30 min | 3 endpoints simples |
| Página "Árbol de beneficios" | 2 horas | Component React |
| Documentar cómo contribuir | 30 min | README en /content |
| **Total** | **~4 horas** | **Listo en 1 sesión** |

---

## J. Ventajas

✅ **Descentralizado:** El contenido vive en GitHub, no en código  
✅ **Versionado:** Cada cambio queda registrado  
✅ **Colaborativo:** Los usuarios pueden proponer via PR  
✅ **Sin BD:** No requiere tabla extra, solo JSON  
✅ **Fácil de mantener:** Editar JSON es más simple que código  
✅ **Público:** El contenido es transparent, cualquiera puede revisar el histórico  

---

## Ejemplo de PR de usuario

```
Título: [PROMO] Paramount+ gratis con Flow
Descripción:
Proveedor: Directv/Flow
Período: 01/01/2026 - 31/12/2026
Fuente oficial: https://flow.com.uy/paramount

Cambios:
- Agregada promo en promos.json con ID "paramount-flow-2026"
- Validada contra fuente oficial
```

Tu revisas, ves que es correcta, mergeas → automáticamente aparece en el sitio.

