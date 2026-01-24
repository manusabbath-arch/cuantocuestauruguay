# Post-Deploy Configuration Checklist

Una vez que hayas deployado en Render y Cloudflare Pages, ejecuta estas acciones para validar y finalizar la configuración.

## ✅ Paso 1: Validar Backend en Render

Después que Render termina el deploy (~5 min):

```bash
# En tu terminal local
./scripts/validate-deploy.sh https://tu-url-render.onrender.com
```

Debe mostrar: ✓ API Documentation, ✓ Productos endpoint, ✓ ETL Status

**Si falla:**
- Espera otros 2 min (posible que esté inicializando la BD)
- Chequea logs en Render → Logs
- Verifica que `render.yaml` tenga `dockerContext: ./backend`

---

## ✅ Paso 2: Obtener URL de Render

```
https://preciosregulados-api.onrender.com  (o la que asigne Render)
```

Anota esta URL para el siguiente paso.

---

## ✅ Paso 3: Deploy Frontend en Cloudflare Pages

1. Cloudflare Dashboard → Pages → "+ Create project"
2. "Connect to Git" → Selecciona repo
3. Rama: `main`
4. Build command: `cd frontend && npm install && npm run build`
5. Output dir: `frontend/dist`
6. Click "Save and Deploy"

Espera ~2-3 min a que termine.

---

## ✅ Paso 4: Agregar Env Var en Cloudflare

1. Proyecto → Settings → "Environment variables"
2. "+ Add variable"
   - Name: `VITE_API_URL`
   - Value: `https://preciosregulados-api.onrender.com` (la que obtuviste en Paso 2)
   - Environment: Production
3. Click "Save"

4. Vuelve a Deployments → Last deployment → "Rollback" (para forzar redeploy)
   O espera al próximo push a `main`

---

## ✅ Paso 5: Conectar Dominio

1. Proyecto Cloudflare Pages → Custom domains → "+ Add custom domain"
2. Añade:
   - `cuantocuestauruguay.com`
   - `www.cuantocuestauruguay.com`
3. Cloudflare auto-configura SSL

**Propagación:** 24-48 horas. Puedes revisar estado en Cloudflare → DNS.

---

## ✅ Paso 6: Actualizar CORS en Render (Opcional pero recomendado)

Una vez que el dominio esté activo (`cuantocuestauruguay.com`):

1. Render Dashboard → Proyecto → Environment
2. Busca `CORS_ORIGINS`
3. Actualiza si es necesario a:
   ```
   https://cuantocuestauruguay.com,https://www.cuantocuestauruguay.com
   ```
4. Auto-redeploya

---

## 🧪 Verificación Final

### Test Manual
```bash
# 1. Frontend
https://cuantocuestauruguay.com

# 2. Backend API
curl https://tu-render-url/api/v1/productos

# 3. DevTools (en navegador)
# F12 → Network → Busca requests a la API
# Deben estar en verde (status 200)
```

### Test por Email
Si configuraste funcionalidad de email, verifica que pueda enviar.

---

## 📋 Checklist Final

- [ ] Backend deploy en Render OK (URL obtenida)
- [ ] Frontend deploy en Cloudflare Pages OK
- [ ] `VITE_API_URL` configurado en Pages
- [ ] Dominio `cuantocuestauruguay.com` en Pages
- [ ] Frontend accesible en dominio
- [ ] API responde en `/api/v1/productos`
- [ ] CORS permitido (sin errores en console)
- [ ] Datos cargándose en dashboard

---

## Troubleshooting

### "CORS error" en el navegador
→ Actualiza `CORS_ORIGINS` en Render con tu dominio final

### "Cannot GET /api/v1/productos"
→ Backend no está respondiendo. Revisa logs en Render

### "Page not found" en Cloudflare
→ Espera propagación DNS (24-48h) o revisa custom domains en Pages

### Frontend no carga datos
→ Verifica `VITE_API_URL` en Cloudflare Pages environment

---

## 🎉 ¡Listo!

Una vez que todo esté verde, tu sitio está en producción.

Para cambios futuros:
1. Haz cambios en tu rama local
2. `git push origin main`
3. Render y Cloudflare auto-redeploy
