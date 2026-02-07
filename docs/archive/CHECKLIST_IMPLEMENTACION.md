# ✅ CHECKLIST DE IMPLEMENTACIÓN (paso a paso)

> Copia este checklist, marcá con ✅ cada paso conforme lo hagas.
> Si algo no entienden, referencia el doc específico.

---

## SEMANA 1: Contenido base + formulario web (6 horas)

### Día 1-2: Preparación (1.5 horas)

- [ ] Leí `ESTRATEGIA_COMPLETA_DISTRIBUCION.md`
- [ ] Leí `PLAN_CONTENIDO_DESCENTRALIZADO.md`
- [ ] Leí `CONTENIDO_INICIAL_LISTO.md`
- [ ] Entiendo que esto es sobre educación + comunidad, no solo precios
- [ ] Abrí terminal en `/backend`
- [ ] Creé carpeta `mkdir -p content/`

### Estructura de carpeta

```
backend/
├── content/
│   ├── README.md                    ← AHORA
│   ├── promos.json                  ← AHORA
│   ├── tips.json                    ← AHORA
│   ├── derechos.json                ← Opcional semana 1
│   ├── casos_reales.json            ← Opcional semana 1
│   └── changelog.md                 ← Opcional semana 1
```

### Día 2-3: Crear JSONs iniciales (1.5 horas)

- [ ] Cree `backend/content/promos.json` con estructura base
  - [ ] Copié estructura de `CONTENIDO_INICIAL_LISTO.md`
  - [ ] Agregué 5 promos reales (del documento o búsqueda)
  - [ ] Validé JSON (sin errores de sintaxis)
  
  **Comando de validación:**
  ```bash
  python -m json.tool backend/content/promos.json > /dev/null && echo "OK"
  ```

- [ ] Cree `backend/content/tips.json` con estructura base
  - [ ] Agregué 5 tips de ahorro
  - [ ] Validé JSON

- [ ] Cree `backend/content/README.md` explicando estructura
  ```markdown
  # Contenido de PreciosRegulados.uy
  
  Los archivos JSON en esta carpeta contienen:
  - promos.json: Promociones vigentes
  - tips.json: Tips de ahorro
  - derechos.json: Derechos del consumidor (próximamente)
  - casos_reales.json: Historias de usuarios (próximamente)
  
  ## Cómo actualizar
  1. Editá el JSON
  2. Validá con: python -m json.tool archivo.json
  3. Haz commit: git add archivo.json && git commit -m "...
  4. Push: git push
  5. En 1-2 min aparece en el sitio
  ```

- [ ] Hice primer commit
  ```bash
  git add backend/content/
  git commit -m "feat: create content management system with 5 promos + 5 tips"
  git push
  ```

### Día 3-4: Crear endpoints (1.5 horas)

- [ ] Creé archivo `backend/app/routers/contenido.py`
  ```python
  from fastapi import APIRouter
  import json
  from pathlib import Path
  
  router = APIRouter(prefix="/api/v1/contenido", tags=["contenido"])
  
  @router.get("/promos")
  async def obtener_promos():
      with open(Path(__file__).parent.parent.parent / "content/promos.json") as f:
          return json.load(f)
  
  @router.get("/tips")
  async def obtener_tips():
      with open(Path(__file__).parent.parent.parent / "content/tips.json") as f:
          return json.load(f)
  ```

- [ ] Registré router en `backend/app/main.py`
  ```python
  from app.routers.contenido import router as contenido_router
  app.include_router(contenido_router)
  ```

- [ ] Testeé endpoints en navegador
  - [ ] `http://localhost:8000/api/v1/contenido/promos` → devuelve JSON
  - [ ] `http://localhost:8000/api/v1/contenido/tips` → devuelve JSON

- [ ] Hice commit
  ```bash
  git add backend/app/routers/contenido.py backend/app/main.py
  git commit -m "feat: add content endpoints /api/v1/contenido/{promos,tips}"
  git push
  ```

### Día 4-5: Formulario web de contribuciones (2 horas)

- [ ] Creé endpoint para guardar contribuciones
  ```python
  # backend/app/routers/contribuciones.py
  from fastapi import APIRouter
  import json
  from datetime import datetime
  from pathlib import Path
  
  router = APIRouter(prefix="/api/v1", tags=["contribuciones"])
  
  @router.post("/contribuciones")
  async def crear_contribucion(
      tipo: str,
      contenido: str,
      nombre: str = "Anónimo",
      fuente: str = None
  ):
      contribucion = {
          "id": str(datetime.now().timestamp()),
          "tipo": tipo,
          "contenido": contenido,
          "nombre": nombre,
          "fuente": fuente,
          "fecha": datetime.now().isoformat(),
          "estado": "pendiente_revision"
      }
      
      # Guardar a JSONL
      with open(Path(__file__).parent.parent.parent / "contribuciones/pendientes.jsonl", "a") as f:
          f.write(json.dumps(contribucion) + "\n")
      
      return {"status": "recibido", "message": "Gracias, revisamos en 48hs"}
  ```

- [ ] Registré router en `backend/app/main.py`
  ```python
  from app.routers.contribuciones import router as contrib_router
  app.include_router(contrib_router)
  ```

- [ ] Creé carpeta para contribuciones pendientes
  ```bash
  mkdir -p backend/contribuciones
  touch backend/contribuciones/pendientes.jsonl
  ```

- [ ] Creé página `/contribuir` en frontend
  **Archivo:** `frontend/src/pages/Contribuir.tsx`
  ```tsx
  import { useState } from 'react'
  import { useNavigate } from 'react-router-dom'
  import api from '../services/api'
  
  export default function Contribuir() {
    const [tipo, setTipo] = useState('promo')
    const [contenido, setContenido] = useState('')
    const [nombre, setNombre] = useState('')
    const [fuente, setFuente] = useState('')
    const [enviado, setEnviado] = useState(false)
    
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault()
      try {
        await api.post('/contribuciones', {
          tipo,
          contenido,
          nombre,
          fuente
        })
        setEnviado(true)
        setTimeout(() => window.location.href = '/', 3000)
      } catch (error) {
        alert('Error al enviar')
      }
    }
    
    if (enviado) {
      return (
        <div className="max-w-2xl mx-auto p-6 text-center">
          <h2 className="text-2xl font-bold mb-4">✅ ¡Gracias!</h2>
          <p>Tu aporte fue recibido. Lo revisamos en 48 horas.</p>
          <p>Redirigiendo...</p>
        </div>
      )
    }
    
    return (
      <div className="max-w-2xl mx-auto p-6 space-y-6">
        <h1 className="text-3xl font-bold">🤝 Colaborá con nosotros</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-semibold mb-2">Tipo de aporte</label>
            <select 
              value={tipo} 
              onChange={(e) => setTipo(e.target.value)}
              className="w-full border rounded p-2"
            >
              <option value="promo">Promo vigente</option>
              <option value="tip">Tip de ahorro</option>
              <option value="derecho">Derecho del consumidor</option>
              <option value="caso">Mi historia de ahorro</option>
              <option value="error">Error en el sitio</option>
            </select>
          </div>
          
          <div>
            <label className="block font-semibold mb-2">
              Cuéntame (máximo 300 caracteres)
            </label>
            <textarea 
              value={contenido}
              onChange={(e) => setContenido(e.target.value)}
              maxLength={300}
              rows={5}
              className="w-full border rounded p-2"
              placeholder="Describe tu aporte en detalle..."
              required
            />
            <p className="text-sm text-gray-500">{contenido.length}/300</p>
          </div>
          
          <div>
            <label className="block font-semibold mb-2">
              Mi nombre/usuario (opcional)
            </label>
            <input 
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full border rounded p-2"
              placeholder="Anónimo si dejas vacío"
            />
          </div>
          
          <div>
            <label className="block font-semibold mb-2">
              Fuente oficial (si aplica)
            </label>
            <input 
              type="url"
              value={fuente}
              onChange={(e) => setFuente(e.target.value)}
              className="w-full border rounded p-2"
              placeholder="https://ejemplo.com"
            />
          </div>
          
          <button 
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700"
          >
            ENVIAR APORTE
          </button>
        </form>
      </div>
    )
  }
  ```

- [ ] Agregué ruta en `frontend/src/App.tsx`
  ```tsx
  import Contribuir from './pages/Contribuir'
  
  // En <Routes>:
  <Route path="/contribuir" element={<Contribuir />} />
  ```

- [ ] Testeé flujo
  - [ ] Fui a `http://localhost:5173/contribuir`
  - [ ] Llené formulario
  - [ ] Presioné "ENVIAR"
  - [ ] Verifiqué que se creó archivo `backend/contribuciones/pendientes.jsonl`

- [ ] Hice commit
  ```bash
  git add backend/app/routers/contribuciones.py
  git add frontend/src/pages/Contribuir.tsx
  git add frontend/src/App.tsx
  git commit -m "feat: add contribution system with form endpoint"
  git push
  ```

### Día 5: Banner y promoción (1 hora)

- [ ] Edité `frontend/src/pages/Home.tsx`
  - [ ] Agregué banner "Colaborá" arriba del listado de precios
  ```tsx
  <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white mb-6">
    <h3 className="text-xl font-bold mb-2">🤝 ¿Encontraste un ahorro?</h3>
    <p className="mb-4">Comparte tu descubrimiento y ayudá a otros uruguayos a ahorrar.</p>
    <button 
      onClick={() => navigate('/contribuir')}
      className="bg-white text-purple-600 px-4 py-2 rounded font-semibold hover:bg-gray-100"
    >
      → Colaborar
    </button>
  </div>
  ```

- [ ] Edité `frontend/src/components/Layout.tsx`
  - [ ] Agregué link "Colaborar" en footer
  ```tsx
  <a href="/contribuir" className="hover:text-blue-600">
    Colaborar
  </a>
  ```

- [ ] Hice commit
  ```bash
  git add frontend/src/pages/Home.tsx frontend/src/components/Layout.tsx
  git commit -m "feat: add collaboration CTA in home and footer"
  git push
  ```

### Validación final SEMANA 1

- [ ] Carpeta `backend/content/` existe con JSONs
- [ ] Endpoints `/api/v1/contenido/{promos,tips}` devuelven JSON ✅
- [ ] Página `/contribuir` existe y funciona
- [ ] Formulario guarda a `backend/contribuciones/pendientes.jsonl`
- [ ] Banner en Home redirecciona a `/contribuir`
- [ ] Link en footer apunta a `/contribuir`
- [ ] Todos los cambios están en `main` (git push)

**Comando de verificación rápida:**
```bash
# En terminal
curl http://localhost:8000/api/v1/contenido/promos | head -20
# Debería devolver JSON
```

---

## SEMANA 2: Árbol de beneficios (4 horas)

### Día 1: Crear servicios_beneficios.json (1 hora)

- [ ] Creé `backend/content/servicios_beneficios.json`
  ```json
  {
    "servicios": {
      "antel_internet": {
        "nombre": "Internet Antel",
        "iconos": "📱",
        "beneficios": [
          "paramount-flow-2026",
          "antel-android-renovacion",
          "antel-descuento-fidelidad"
        ]
      },
      "directv_tv": {
        "nombre": "TV Directv",
        "icono": "📺",
        "beneficios": [
          "tip-canaleras-streaming"
        ]
      }
    }
  }
  ```

- [ ] Validé JSON
  ```bash
  python -m json.tool backend/content/servicios_beneficios.json > /dev/null && echo "OK"
  ```

- [ ] Agregué endpoint en `backend/app/routers/contenido.py`
  ```python
  @router.get("/servicios-beneficios")
  async def obtener_servicios_beneficios():
      with open(Path(...) / "content/servicios_beneficios.json") as f:
          return json.load(f)
  ```

### Día 2-3: Crear página Árbol de beneficios (2 horas)

- [ ] Creé `frontend/src/pages/BeneficiosArbol.tsx`
  ```tsx
  import { useState, useEffect } from 'react'
  import api from '../services/api'
  
  export default function BeneficiosArbol() {
    const [servicios, setServicios] = useState({})
    const [seleccionados, setSeleccionados] = useState<string[]>([])
    const [promos, setPromos] = useState([])
    const [tips, setTips] = useState([])
    
    useEffect(() => {
      const cargar = async () => {
        const [srv, prms, tps] = await Promise.all([
          api.get('/contenido/servicios-beneficios'),
          api.get('/contenido/promos'),
          api.get('/contenido/tips')
        ])
        setServicios(srv.data.servicios)
        setPromos(prms.data.promos)
        setTips(tps.data.tips)
      }
      cargar()
    }, [])
    
    const toggleServicio = (servicio: string) => {
      setSeleccionados(prev => 
        prev.includes(servicio)
          ? prev.filter(s => s !== servicio)
          : [...prev, servicio]
      )
    }
    
    const beneficiosAplicables = () => {
      const beneficios: any[] = []
      
      for (const servicio of seleccionados) {
        const servicioData = servicios[servicio]
        if (!servicioData) continue
        
        for (const beneficioId of servicioData.beneficios) {
          const promo = promos.find(p => p.id === beneficioId)
          if (promo) beneficios.push(promo)
          const tip = tips.find(t => t.id === beneficioId)
          if (tip) beneficios.push(tip)
        }
      }
      
      return beneficios
    }
    
    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">🌳 Árbol de beneficios</h1>
        
        <p className="text-gray-600 mb-6">
          Selecciona los servicios que tenés y descubrí qué ahorros aplican a ti.
        </p>
        
        <div className="grid grid-cols-2 gap-4 mb-8">
          {Object.entries(servicios).map(([key, srv]: [string, any]) => (
            <button
              key={key}
              onClick={() => toggleServicio(key)}
              className={`p-4 border-2 rounded-lg font-semibold transition ${
                seleccionados.includes(key)
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-300 bg-white'
              }`}
            >
              <span className="text-2xl">{srv.icono}</span>
              {srv.nombre}
            </button>
          ))}
        </div>
        
        {seleccionados.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold mb-4">
              ✨ Tus beneficios ({beneficiosAplicables().length})
            </h2>
            <div className="space-y-4">
              {beneficiosAplicables().map((item) => (
                <div key={item.id} className="border rounded-lg p-4 bg-blue-50">
                  <h3 className="font-semibold text-lg">{item.titulo}</h3>
                  <p className="text-gray-600 text-sm">{item.descripcion_corta}</p>
                  {item.ahorro_estimado && (
                    <p className="text-green-600 font-semibold mt-2">
                      💰 Ahorro: {item.ahorro_estimado}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
  ```

- [ ] Agregué ruta en `frontend/src/App.tsx`
  ```tsx
  <Route path="/beneficios" element={<BeneficiosArbol />} />
  ```

- [ ] Agregué link en navegación
  - [ ] En `frontend/src/components/Layout.tsx`
  ```tsx
  <nav>
    ...
    <a href="/beneficios">🌳 Árbol de beneficios</a>
    ...
  </nav>
  ```

### Día 4: Agregar badges de contribuidores (1 hora)

- [ ] Edité componente que muestra promos
  - [ ] En `frontend/src/pages/Home.tsx` o donde muestres promos
  ```tsx
  {promo.contribuyente && (
    <p className="text-xs text-gray-500 mt-2">
      📌 Sugerencia de {promo.contribuyente}
    </p>
  )}
  ```

- [ ] Lo mismo para tips

### Validación final SEMANA 2

- [ ] Archivo `servicios_beneficios.json` existe
- [ ] Endpoint `/api/v1/contenido/servicios-beneficios` funciona
- [ ] Página `/beneficios` existe y funciona
- [ ] Usuario puede seleccionar servicios ✓
- [ ] Se muestran beneficios filtrados
- [ ] Badges "Sugerencia de Usuario X" aparecen en promos/tips
- [ ] Todos los cambios están en `main`

---

## SEMANA 3: WhatsApp Bot (4 horas)

### Día 1: Setup Twilio (30 minutos)

- [ ] Fui a https://www.twilio.com/console
- [ ] Creé cuenta (verificación de número)
- [ ] Creé proyecto "PreciosRegulados"
- [ ] En Messaging → Try it → WhatsApp Sandbox
- [ ] Copié credenciales:
  - [ ] TWILIO_ACCOUNT_SID
  - [ ] TWILIO_AUTH_TOKEN
  - [ ] TWILIO_WHATSAPP_NUMBER (ej: whatsapp:+1234567890)
- [ ] Pegué en `backend/.env`
  ```
  TWILIO_ACCOUNT_SID=ACxxxxxxxx
  TWILIO_AUTH_TOKEN=xxxxx
  TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
  ```
- [ ] Instalé dependencia (si no está)
  ```bash
  pip install twilio
  ```

### Día 2: Crear tabla de suscriptores (1 hora)

- [ ] Creé migration en `backend/alembic/versions/`
  **Archivo:** `backend/alembic/versions/xxx_add_whatsapp_subscribers.py`
  ```python
  from alembic import op
  import sqlalchemy as sa
  
  def upgrade():
      op.create_table(
          'whatsapp_suscriptores',
          sa.Column('id', sa.Integer, primary_key=True, index=True),
          sa.Column('numero', sa.String(20), unique=True, nullable=False),
          sa.Column('fecha_suscripcion', sa.DateTime, default=sa.func.now()),
          sa.Column('activo', sa.Boolean, default=True),
          sa.Column('frecuencia', sa.String(20), default='semanal'),
          sa.Column('intereses', sa.Text)
      )
  
  def downgrade():
      op.drop_table('whatsapp_suscriptores')
  ```

- [ ] Ejecuté migration
  ```bash
  cd backend
  alembic upgrade head
  ```

- [ ] Creé model en `backend/app/models/models.py`
  ```python
  class WhatsAppSuscriptor(Base):
      __tablename__ = "whatsapp_suscriptores"
      
      id = Column(Integer, primary_key=True, index=True)
      numero = Column(String(20), unique=True, nullable=False)
      fecha_suscripcion = Column(DateTime, default=func.now())
      activo = Column(Boolean, default=True)
      frecuencia = Column(String(20), default="semanal")
      intereses = Column(Text)  # JSON string
  ```

### Día 3-4: Crear endpoints WhatsApp (1.5 horas)

- [ ] Creé `backend/app/routers/whatsapp.py`
  ```python
  from fastapi import APIRouter, HTTPException, Depends
  from sqlalchemy.orm import Session
  from app.models.models import WhatsAppSuscriptor
  from app.core.database import get_db
  from app.whatsapp_bot import WhatsAppBot
  
  router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])
  
  @router.post("/subscribe")
  async def suscribirse(
      numero: str,
      frecuencia: str = "semanal",
      db: Session = Depends(get_db)
  ):
      # Validar que sea número de WhatsApp válido
      if not numero.startswith("+"):
          raise HTTPException(status_code=400, detail="Número debe incluir +")
      
      # Guardar o actualizar
      suscriptor = db.query(WhatsAppSuscriptor).filter_by(numero=numero).first()
      if suscriptor:
          suscriptor.activo = True
      else:
          suscriptor = WhatsAppSuscriptor(
              numero=numero,
              frecuencia=frecuencia
          )
          db.add(suscriptor)
      
      db.commit()
      
      # Enviar confirmación via WhatsApp
      bot = WhatsAppBot()
      bot.send_message(
          numero,
          "✅ ¡Suscripción confirmada!\nRecibirás 1 tip cada viernes a las 9 AM.\nPara cancelar, escribí PARAR."
      )
      
      return {"status": "suscrito", "message": "Confirmación enviada por WhatsApp"}
  
  @router.post("/unsubscribe")
  async def desuscribirse(numero: str, db: Session = Depends(get_db)):
      suscriptor = db.query(WhatsAppSuscriptor).filter_by(numero=numero).first()
      if not suscriptor:
          raise HTTPException(status_code=404, detail="No encontrado")
      
      suscriptor.activo = False
      db.commit()
      
      return {"status": "desuscrito"}
  
  @router.get("/webhook")
  async def webhook_get():
      # Twilio verifica el webhook con GET
      return {"status": "ok"}
  
  @router.post("/webhook")
  async def webhook_post(
      From: str = None,
      Body: str = None,
      db: Session = Depends(get_db)
  ):
      # Twilio envía mensajes aquí
      numero = From.replace("whatsapp:", "")
      mensaje = Body.lower()
      
      if "suscribir" in mensaje or "subscribir" in mensaje:
          # Suscribir
          suscriptor = db.query(WhatsAppSuscriptor).filter_by(numero=numero).first()
          if not suscriptor:
              suscriptor = WhatsAppSuscriptor(numero=numero)
              db.add(suscriptor)
          suscriptor.activo = True
          db.commit()
          
          bot = WhatsAppBot()
          bot.send_message(numero, "✅ ¡Suscrito! Recibirás tips cada viernes.")
      
      elif "parar" in mensaje or "cancelar" in mensaje:
          # Desuscribir
          suscriptor = db.query(WhatsAppSuscriptor).filter_by(numero=numero).first()
          if suscriptor:
              suscriptor.activo = False
              db.commit()
          
          bot = WhatsAppBot()
          bot.send_message(numero, "❌ Desuscrito. ¡Nos vemos pronto!")
      
      return {"status": "ok"}
  ```

- [ ] Registré router en `backend/app/main.py`
  ```python
  from app.routers.whatsapp import router as whatsapp_router
  app.include_router(whatsapp_router)
  ```

### Día 5: Agregar scheduler de envíos (1 hora)

- [ ] Edité `backend/app/scheduler.py`
  ```python
  async def send_weekly_whatsapp_tips():
      """Envía tips por WhatsApp cada viernes 9 AM"""
      db = SessionLocal()
      
      try:
          # Obtener suscriptores activos
          suscriptores = db.query(WhatsAppSuscriptor)\
              .filter(WhatsAppSuscriptor.activo == True)\
              .all()
          
          if not suscriptores:
              logger.info("No active WhatsApp subscribers")
              return
          
          # Obtener todos los tips
          with open("backend/content/tips.json") as f:
              tips = json.load(f)["tips"]
          
          if not tips:
              logger.error("No tips available")
              return
          
          # Seleccionar tip random
          import random
          tip = random.choice(tips)
          
          # Formar mensaje
          mensaje = f"""
  📊 {tip['titulo']}
  ─────────────────
  {tip['contenido']['resumen']}
  
  💰 Ahorro: {tip['contenido'].get('ahorro', {}).get('ahorro_mensual', 'N/A')}
  
  Más detalles: https://cuantocuestauruguay.com/tips/{tip['id']}
  
  ¿Encontraste un tip? Escribí CONTRIBUIR
          """.strip()
          
          # Enviar a todos
          bot = WhatsAppBot()
          for suscriptor in suscriptores:
              try:
                  bot.send_message(suscriptor.numero, mensaje)
                  logger.info(f"Enviado a {suscriptor.numero}")
              except Exception as e:
                  logger.error(f"Error enviando a {suscriptor.numero}: {e}")
      
      finally:
          db.close()
  
  # En start_scheduler():
  scheduler.add_job(
      send_weekly_whatsapp_tips,
      trigger=CronTrigger(day_of_week=4, hour=9, minute=0),  # Viernes 9 AM
      id="whatsapp_weekly_tips",
      name="Weekly WhatsApp Tips"
  )
  ```

### Validación final SEMANA 3

- [ ] Credenciales Twilio en `.env`
- [ ] Tabla `whatsapp_suscriptores` existe
- [ ] Endpoints `/whatsapp/subscribe` y `/whatsapp/webhook` funcionan
- [ ] Scheduler está configurado para viernes 9 AM
- [ ] Podes testear manualmente (opcional)
  ```python
  # En terminal Python
  from app.whatsapp_bot import WhatsAppBot
  bot = WhatsAppBot()
  bot.send_message("whatsapp:+598XXXXXXXXX", "Test mensaje")
  ```

---

## SEMANA 4: Validación y lanzamiento (1 hora)

### Testeo fin a fin

- [ ] **Test 1: Contribuir**
  - [ ] Voy a `/contribuir`
  - [ ] Relleno formulario
  - [ ] Presiono enviar
  - [ ] Archivo `pendientes.jsonl` se actualiza

- [ ] **Test 2: Revisar contribución**
  - [ ] Abro `backend/contribuciones/pendientes.jsonl`
  - [ ] Valido que es correcta
  - [ ] Copio contenido a `promos.json` o `tips.json`
  - [ ] Hago commit/push
  - [ ] En 1-2 min aparece en sitio

- [ ] **Test 3: Árbol de beneficios**
  - [ ] Voy a `/beneficios`
  - [ ] Selecciono un servicio ✓
  - [ ] Aparecen beneficios filtrados
  - [ ] Presiono uno, veo detalles

- [ ] **Test 4: WhatsApp (opcional, requiere Twilio activo)**
  - [ ] Escaneo QR en sitio
  - [ ] Abre WhatsApp
  - [ ] Escribo "Suscribirse"
  - [ ] Recibo confirmación

### Documentación

- [ ] Creé página `/guia-colaborar`
  ```markdown
  # Cómo colaborar en PreciosRegulados.uy
  
  ## Opción 1: Formulario web (más fácil)
  [Link a /contribuir]
  
  ## ¿Qué puedo contribuir?
  - Promos vigentes
  - Tips de ahorro
  - Derechos del consumidor
  - Mi historia de ahorro
  
  ## Proceso
  1. Rellenas el formulario
  2. Nosotros validamos en 24-48 horas
  3. Aparece en el sitio con tu nombre
  4. Recibirás email de agradecimiento
  ```

- [ ] Actualizé footer con links
  - [ ] "Colaborar" → `/contribuir`
  - [ ] "Guía de colaboración" → `/guia-colaborar`

### Lanzamiento

- [ ] Hice último commit
  ```bash
  git add .
  git commit -m "feat: complete distribution and collaboration system v1.0"
  git push
  ```

- [ ] Verifiqué que todo está en `main`
  - [ ] GitHub muestra último commit

- [ ] Probé en producción (si está deployada)
  - [ ] https://cuantocuestauruguay.com/contribuir funciona
  - [ ] `/api/v1/contenido/promos` devuelve JSON
  - [ ] `/beneficios` muestra árbol

---

## ✅ Checklist final

- [ ] SEMANA 1 completada (contenido + formulario)
- [ ] SEMANA 2 completada (árbol de beneficios)
- [ ] SEMANA 3 completada (WhatsApp bot)
- [ ] SEMANA 4 completada (testing + docs)
- [ ] Todas las secciones están en `main`
- [ ] Sitio en producción está actualizado
- [ ] No hay errores en logs

---

**🎉 ¡LANZAMIENTO COMPLETADO!**

Tu plataforma ahora:
✅ Recopila promos/tips de usuarios  
✅ Muestra beneficios personalizados  
✅ Distribuyé tips por WhatsApp  
✅ Escalable sin que hagas todo manualmente  

**Próximo paso:** Monitorear contribuciones y validar 1-2 por día.

