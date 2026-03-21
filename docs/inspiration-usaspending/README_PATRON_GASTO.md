# 🏛️ Patrones USAspending Aplicables a P2-A (Gasto Público MEF)

**Contexto**: Acabas de implementar `EjecucionPresupuestal` (modelo) + `GastoPublicoETL` (ETL) + `/api/v1/gasto/*` (endpoints).  
Ahora necesitas el **frontend** para visualizar gasto público de organismos.

---

## 🎯 RECOMENDACIONES INMEDIATAS PARA P2-A

### 1. **Página de Organismos (Búsqueda + Filtro)**
Adaptar `USAspending SearchPage` pero para organismos del MEF.

**Componentes a crear**:
```
frontend/src/pages/GastoPublico.tsx (página principal)
├── components/
│   ├── OrganismoFilter.tsx (checkbox/autocomplete → organismos)
│   ├── AñoFilter.tsx (select/range → años disponibles)
│   ├── MesFilter.tsx (select → meses, opcional)
│   ├── EjecucionTable.tsx (tabla paginada con sorting)
│   └── ComparacionYoY.tsx (gráfico de comparación año-año)
```

**Referencia en documentos**:
- `usaspending_code_examples.md` → Secc. "Componente: AutocompleteFilterCheckbox"
- `usaspending_code_examples.md` → Secc. "Container: SearchPageContainer"

---

### 2. **Estructura Redux para Gasto**
Slice en Redux para estado de filtros + datos.

```typescript
// frontend/src/redux/slices/gasto.ts
export interface GastoFilterState {
  filters: {
    selectedOrganismos: string[];      // incisos seleccionados
    selectedAños: number[];
    selectedMeses: number[] | null;
  };
  data: {
    organismos: Organismo[];           // → GET /api/v1/gasto/organismos
    ejecucion: EjecucionPresupuestal[]; // → GET /api/v1/gasto/ejecucion
    comparacion: ComparacionYoY[];      // → GET /api/v1/gasto/comparacion-anual
  };
  ui: {
    loading: boolean;
    error: string | null;
  };
}
```

**Referencia**: `usaspending_code_examples.md` → Secc. "Redux Slice (Redux Toolkit)"

---

### 3. **API Module Tipificado**
Centralizar calls a los 3 endpoints de gasto.

```typescript
// frontend/src/apis/gasto.ts
export const fetchOrganismos = (año?: number) => 
  apiRequest.get('/gasto/organismos', { params: { anio: año } });

export const fetchEjecucion = (filters: FilterState) =>
  apiRequest.get('/gasto/ejecucion', { params: filters });

export const fetchComparacion = (inciso: string) =>
  apiRequest.get('/gasto/comparacion-anual', { params: { inciso } });
```

**Referencia**: `usaspending_code_examples.md` → Secc. "API Module: spending.ts"

---

### 4. **Gráficos: Comparación YoY**
Usar Recharts (ya lo usas) para visualizar ejecución año-año.

```typescript
// Adaptar endpoint /api/v1/gasto/comparacion-anual
// para devolver estructura compatible con LineChart/BarChart

// POST /api/v1/gasto/comparacion-anual
// Response:
{
  "years": [2022, 2023],
  "data": [
    { "año": 2022, "ejecutado": 850000, "anio_anterior_ejecutado": null },
    { "año": 2023, "ejecutado": 920000, "variacion_pct": 8.2 }
  ]
}
```

**Referencia**: `usaspending_code_examples.md` → Secc. "Componente: BudgetVisualization"

---

## 📚 LECTURA RECOMENDADA (EN ORDEN)

1. **5 min**: Lee `resumen_ejecutivo.md` (seccion "PATRONES CLAVE A IMPLEMENTAR")
2. **15 min**: Revisa `usaspending_code_examples.md`:
   - "Componente: AutocompleteFilterCheckbox"
   - "Container: SearchPageContainer"
   - "API Module: spending.ts"
   - "Redux Slice (Redux Toolkit)"
3. **30 min**: Mira `typescript_tailwind_migration.md` (FASE 1 + FASE 2)
4. **Optional - Profundo**: `usaspending_analysis_es.md` (análisis exhaustivo)

---

## ✅ CHECKLIST PARA IMPLEMENTACIÓN

- [ ] **Paso 1**: Crear Redux slice `gasto.ts` con initialState + reducers
- [ ] **Paso 2**: Crear API module `frontend/src/apis/gasto.ts` 
- [ ] **Paso 3**: Crear custom hook `useGastoFilters()` 
- [ ] **Paso 4**: Crear componentes de filtro (Organismo, Año, Mes)
- [ ] **Paso 5**: Crear `EjecucionTable.tsx` (tabla paginada)
- [ ] **Paso 6**: Crear `ComparacionYoY.tsx` (gráfico Recharts)
- [ ] **Paso 7**: Integrar en página `GastoPublico.tsx`
- [ ] **Paso 8**: Tests con React Testing Library

---

## 🚀 QUICK START (30 min)

Si tienes prisa, solo implementa:

```bash
# 1. Añade a package.json (si falta):
npm install redux-toolkit react-redux reselect

# 2. Copia template de redux slice:
# backend/app/routers/gasto.py usa nombres: 
#   - inciso, nombre_organismo → para filtros
#   - credito_vigente, ejecutado, porcentaje_ejecucion → para table + chart

# 3. Implementa ApiWrapper (apiRequest.ts) si no existe

# 4. Crea primero el componente "dump" más simple:
#    EjecucionTable.tsx (solo recibe props, no Redux)

# 5. Luego envuélvelo en container conectado a Redux
```

---

## 🔗 REFERENCIA RÁPIDA: ENDPOINTS ↔ COMPONENTES

```
GET /api/v1/gasto/organismos
  ↓
OrganismoFilter.tsx (checkbox list)
  ↓
Redux: gasto.filters.selectedOrganismos

GET /api/v1/gasto/ejecucion
  ↓
EjecucionTable.tsx + ComparacionYoY.tsx
  ↓
Redux: gasto.data.ejecucion

GET /api/v1/gasto/comparacion-anual
  ↓
Chart component (LineChart/BarChart)
```

---

## 💡 TIPS USAspending

1. **Paginación**: Usa URL params (`?page=2&limit=50`) + Redux estado
2. **Sorting**: Tabla con `sort=inciso:asc` en URL
3. **Export**: Botón CSV/PDF que serializa tabla actual
4. **Accessibility**: Labels + ARIA en filtros
5. **Performance**: Usualmente pagina en backend, no frontend (smart)

---

**Siguiente paso**: ¿Quieres que te genere el boilerplate inicial de Redux slice + API module tipificado?
