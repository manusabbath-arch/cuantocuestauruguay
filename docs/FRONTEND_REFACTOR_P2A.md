# Refactorización P2-A Frontend (Opción A - 21 Marzo 2026)

## Resumen de Cambios

Se han extraído y refactorizado componentes de `GastoPublico.tsx` según patrones USAspending para mejorar reutilización y mantenimiento:

### ✅ Nuevos Archivos Creados

#### 1. **`frontend/src/services/gasto.ts`** (110 líneas)
API service centralizado para Gasto Público.

**Qué hace:**
- Tipificación completa de endpoints (`/api/v1/gasto/*`)
- Query key factory para TanStack Query
- Manejo consistente de errores
- Interfaz limpia para componentes

**Uso:**
```typescript
import { gastoService } from '../services/gasto'

const organismos = await gastoService.getOrganismos(anio)
const ejecucion = await gastoService.getEjecucion({ anio, inciso })
const comparacion = await gastoService.getComparacionAnual(inciso)
```

#### 2. **`frontend/src/hooks/useGasto.ts`** (165 líneas)
Custom hooks para gestionar queries de gastoPublico.

**Hooks disponibles:**
- `useGasto(filters)` — Todas las queries a la vez
- `useGastoOrganismos(anio)` — Solo organismos
- `useGastoEjecucion(filters)` — Solo ejecución
- `useGastoComparacion(inciso)` — Solo comparación

**Uso:**
```typescript
import { useGasto, useGastoOrganismos } from '../hooks/useGasto'

// Hook completo
const { organismos, ejecucion, isLoading } = useGasto({ anio: 2023 })

// Hooks granulares
const { data: orgs } = useGastoOrganismos(2023)
const { data: ejecucion } = useGastoEjecucion({ anio: 2023, inciso: '02' })
```

#### 3. **`frontend/src/components/OrganismoFilter.tsx`** (130 líneas)
Filtro reutilizable para seleccionar organismos.

**Features:**
- Búsqueda por nombre/código
- Multiselect con checkboxes
- Seleccionar/Deseleccionar todos
- Estados loading/error

**Uso:**
```typescript
import { OrganismoFilter } from '../components/OrganismoFilter'

function MyComponent() {
  const [selected, setSelected] = useState<string[]>([])
  
  return (
    <OrganismoFilter
      selectedIncisos={selected}
      onToggle={(inciso) => {
        setSelected(prev => 
          prev.includes(inciso)
            ? prev.filter(i => i !== inciso)
            : [...prev, inciso]
        )
      }}
      anio={2023}
    />
  )
}
```

#### 4. **`frontend/src/components/AñoFilter.tsx`** (45 líneas)
Filtro reutilizable para seleccionar años.

**Features:**
- Grid de años disponibles
- Año por defecto = año actual
- Personalizable (minYear, maxYear)

**Uso:**
```typescript
import { AñoFilter } from '../components/AñoFilter'

function MyComponent() {
  const [year, setYear] = useState(new Date().getFullYear())
  
  return (
    <AñoFilter
      selectedYear={year}
      onChangeYear={setYear}
      minYear={2020}
      maxYear={2024}
    />
  )
}
```

---

## Próximos Pasos

### **Opción A.1: Mantener estructura actual**
`GastoPublico.tsx` puede seguir siendo monolítica. Los nuevos módulos pueden usarse opcionalmente en:
- Componentes nuevos que necesiten filtros
- Páginas complementarias (estadísticas, exportar)

### **Opción A.2: Refactorizar GastoPublico.tsx** (recomendado)
Reemplazar la lógica interna inline de GastoPublico.tsx con:

```typescript
// Antes (inline en GastoPublico.tsx):
const gastoService = {
  getEjecucion: async (...) => { /* lógica */ },
  getOrganismos: async (...) => { /* lógica */ },
  // ...
}

// Después:
import { useGasto } from '../hooks/useGasto'
import { OrganismoFilter } from '../components/OrganismoFilter'

export default function GastoPublico() {
  const [selectedIncisos, setSelectedIncisos] = useState<string[]>([])
  const [year, setYear] = useState(new Date().getFullYear())
  
  const { organismos, ejecucion, comparacion, isLoading } = useGasto({
    anio: year,
    inciso: selectedIncisos[0], // si hay selección
  })

  return (
    <div className="space-y-4">
      <AñoFilter selectedYear={year} onChangeYear={setYear} />
      <OrganismoFilter
        selectedIncisos={selectedIncisos}
        onToggle={(inciso) => {
          setSelectedIncisos(prev =>
            prev.includes(inciso)
              ? prev.filter(i => i !== inciso)
              : [...prev, inciso]
          )
        }}
        anio={year}
      />
      
      {isLoading && <div>Cargando...</div>}
      {/* Renderizar gráficos con ejecucion.data */}
    </div>
  )
}
```

---

## Testing

Los hooks y componentes están diseñados para ser testeables:

```typescript
// Ejemplo test de OrganismoFilter
import { render, screen, fireEvent } from '@testing-library/react'
import { OrganismoFilter } from './OrganismoFilter'

test('debería toggle una selección', async () => {
  const onToggle = vi.fn()
  render(
    <OrganismoFilter
      selectedIncisos={[]}
      onToggle={onToggle}
    />
  )
  
  const checkbox = await screen.findByRole('checkbox', { name: /seleccionar todos/i })
  fireEvent.click(checkbox)
  expect(onToggle).toHaveBeenCalled()
})
```

---

## Dependencias

Todos los nuevos módulos usan:
- ✅ React 18 (hooks)
- ✅ @tanstack/react-query (ya en package.json)
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ lucide-react (icons)

No requieren instalación de nuevas librerías.

---

## Compatibilidad

- ✅ GastoPublico.tsx existente sigue compilando sin cambios
- ✅ Nuevos módulos son **opt-in** (no rompen código existente)
- ✅ Compilación: sin errores, sin warnings

---

## Métricas

| Métrica | Valor |
|---------|-------|
| Líneas nuevas | ~450 |
| Tests unitarios creados | 0 (listos para agregar) |
| Componentes reutilizables | 2 |
| Hooks personalizados | 4 |
| Breaking changes | 0 |

---

## Referencia: Patrones Aplicados

- ✅ **API Service Module**: Centralización de calls
- ✅ **Query Key Factory**: Caching consistente (TanStack Query)
- ✅ **Custom Hooks**: Lógica separada de UI
- ✅ **Componentes Dump**: Props-driven, reutilizables
- ✅ **Tipificación total**: TypeScript end-to-end

Ver `docs/inspiration-usaspending/README_PATRON_GASTO.md` para detalles.

---

**Status**: ✅ IMPLEMENTADO - Lista para usar
**Próximo trabajo**: Tests unitarios + refactorización de GastoPublico.tsx (Opción A.2)
