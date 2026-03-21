# Guidía de Adaptación: PropTypes → TypeScript + SCSS → Tailwind

Pasos concretos para adaptar los patrones de USAspending al stack preferido.

---

## 🔄 FASE 1: PROPTYPE A TYPESCRIPT

### Problema
USAspending usa PropTypes; `cuantocuestauruguay` usa TypeScript directo.

### Patrón Original (PropTypes)
```jsx
// src/components/shared/AutocompleteFilterCheckbox.jsx
import PropTypes from 'prop-types';

const propTypes = {
    filterType: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        count: PropTypes.number
    })).isRequired,
    selectedIds: PropTypes.arrayOf(PropTypes.string).isRequired,
    onToggle: PropTypes.func.isRequired,
    loading: PropTypes.bool
};

export const AutocompleteFilterCheckbox = ({ 
    filterType, 
    items, 
    selectedIds = [], 
    onToggle, 
    loading = false 
}) => {
    // ...
};

AutocompleteFilterCheckbox.propTypes = propTypes;
```

### Conversión a TypeScript
```typescript
// src/components/shared/AutocompleteFilterCheckbox.tsx
import React, { FC, useState, useCallback } from 'react';

interface FilterItem {
    id: string;
    label: string;
    count?: number;
}

interface AutocompleteFilterCheckboxProps {
    filterType: string;
    items: FilterItem[];
    selectedIds: string[];
    onToggle: (id: string, isSelected: boolean) => void;
    onToggleAll?: (allSelected: boolean) => void;
    loading?: boolean;
    error?: boolean;
    errorMessage?: string;
}

export const AutocompleteFilterCheckbox: FC<AutocompleteFilterCheckboxProps> = ({
    filterType,
    items = [],
    selectedIds = [],
    onToggle,
    onToggleAll,
    loading = false,
    error = false,
    errorMessage = ''
}) => {
    const [searchTerm, setSearchTerm] = useState('');

    // ... resto del código
};
```

### Convertidor Rápido: Tabla de Equivalencias

| PropType | TypeScript |
|----------|-----------|
| `PropTypes.string` | `string` |
| `PropTypes.number` | `number` |
| `PropTypes.bool` | `boolean` |
| `PropTypes.array` | `Array<T>` o `T[]` |
| `PropTypes.object` | `object` o `Record<string, any>` |
| `PropTypes.arrayOf(PropTypes.string)` | `string[]` |
| `PropTypes.shape({ id, name })` | `interface { id: string; name: string; }` |
| `PropTypes.oneOf(['a', 'b', 'c'])` | `'a' \| 'b' \| 'c'` |
| `PropTypes.func` | `(...args: any[]) => void` o tipos específicos |
| `PropTypes.node` | `React.ReactNode` |
| `.isRequired` | No `:` al final (ej: `string` no `string?`) |
| `.isRequired` + default | `?: type = defaultValue` |

---

## 🎨 FASE 2: SCSS A TAILWIND

### Problema
USAspending usa SCSS modular; Tailwind es utility-first sin archivos CSS separados.

### Patrón Original (SCSS)
```scss
// src/scss/components/_autofilter.scss

.filter-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f9f9f9;

  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;

    h3 {
      font-size: 1.125rem;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .filter-search {
    padding: 0.75rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    font-size: 0.875rem;
    margin-bottom: 1rem;

    &:focus {
      outline: none;
      border-color: #3b7fe6;
      box-shadow: 0 0 0 3px rgba(59, 127, 230, 0.1);
    }
  }

  .checkbox-list {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
    max-height: 300px;
    overflow-y: auto;
  }

  .checkbox-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;

    input[type="checkbox"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
    }

    .label-text {
      font-size: 0.875rem;
      color: #555;

      .count {
        color: #999;
        font-size: 0.75rem;
        margin-left: 0.25rem;
      }
    }

    &:hover {
      background-color: #f0f0f0;
      padding: 0.25rem;
      border-radius: 2px;
    }
  }

  .error-message {
    padding: 0.75rem;
    border-left: 4px solid #f44336;
    background-color: #ffebee;
    color: #d32f2f;
    font-size: 0.875rem;
    border-radius: 2px;
  }

  .no-results {
    padding: 1rem;
    text-align: center;
    color: #999;
    font-size: 0.875rem;
  }

  .spinner {
    text-align: center;
    padding: 1rem;
    color: #3b7fe6;
  }
}
```

### Conversión a Tailwind
```tsx
// src/components/shared/AutocompleteFilterCheckbox.tsx

export const AutocompleteFilterCheckbox: FC<AutocompleteFilterCheckboxProps> = ({
    filterType,
    items = [],
    selectedIds = [],
    onToggle,
    onToggleAll,
    loading = false,
    error = false,
    errorMessage = ''
}) => {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredItems = searchTerm
        ? items.filter(item =>
            item.label.toLowerCase().includes(searchTerm.toLowerCase())
          )
        : items;

    const allSelected = filteredItems.every(item =>
        selectedIds.includes(item.id)
    );

    return (
        <div className="flex flex-col gap-4 p-6 border border-gray-200 rounded bg-gray-50">
            {/* Header */}
            <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-gray-800 m-0">
                    {filterType}
                </h3>
                <button
                    onClick={() => onToggleAll?.(!allSelected)}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium transition"
                >
                    {allSelected ? 'Deseleccionar todo' : 'Seleccionar todo'}
                </button>
            </div>

            {/* Search Input */}
            <input
                type="text"
                placeholder={`Buscar ${filterType.toLowerCase()}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition"
            />

            {/* Loading State */}
            {loading && (
                <div className="text-center py-4 text-blue-600">
                    <span className="animate-spin inline-block">⊙</span> Cargando...
                </div>
            )}

            {/* Error State */}
            {error && (
                <div className="px-4 py-3 border-l-4 border-red-500 bg-red-50 text-red-700 text-sm rounded">
                    {errorMessage || 'Error al cargar opciones'}
                </div>
            )}

            {/* No Results */}
            {!loading && !error && filteredItems.length === 0 && (
                <div className="py-4 text-center text-gray-500 text-sm">
                    Sin resultados
                </div>
            )}

            {/* Checkbox List */}
            <div className="flex flex-col gap-1 max-h-80 overflow-y-auto">
                {filteredItems.map(item => (
                    <label
                        key={item.id}
                        className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 px-1 py-1 rounded transition"
                    >
                        <input
                            type="checkbox"
                            checked={selectedIds.includes(item.id)}
                            onChange={(e) => onToggle(item.id, e.target.checked)}
                            className="w-4.5 h-4.5 cursor-pointer accent-blue-600"
                        />
                        <span className="text-sm text-gray-700">
                            {item.label}
                            {item.count !== undefined && (
                                <span className="text-gray-500 text-xs ml-1">
                                    ({item.count})
                                </span>
                            )}
                        </span>
                    </label>
                ))}
            </div>
        </div>
    );
};
```

### Clases Tailwind Comunes

| Propiedad CSS | Tailwind |
|---|---|
| `display: flex` | `flex` |
| `flex-direction: column` | `flex-col` |
| `gap: 1rem` | `gap-4` |
| `padding: 1.5rem` | `p-6` |
| `padding: 0.75rem` | `px-3 py-2` |
| `border: 1px solid` | `border border-gray-300` |
| `border-radius: 4px` | `rounded` |
| `background-color: #f9f9f9` | `bg-gray-50` |
| `margin: 0` | `m-0` |
| `font-size: 1.125rem` | `text-lg` |
| `font-weight: 600` | `font-semibold` |
| `color: #333` | `text-gray-800` |
| `max-height: 300px; overflow-y: auto` | `max-h-80 overflow-y-auto` |
| `:hover` | `hover:*` |
| `:focus` | `focus:*` |
| `box-shadow: 0 0 0 3px` | `ring-2 ring-offset-* shadow-*` |
| Transición suave | `transition` |
| `cursor: pointer` | `cursor-pointer` |

---

## 🚀 FASE 3: PATRONES DE API - TYPESCRIPT

### Original (JavaScript)

```jsx
// src/apis/apiRequest.js
export const apiRequest = (axiosParams = {}) => {
    const cancelToken = CancelToken.source();
    return {
        promise: axios(params(axiosParams)),
        cancel: () => cancelToken.cancel()
    };
};
```

### Versión TypeScript

```typescript
// src/apis/apiRequest.ts
import Axios, { AxiosRequestConfig, CancelTokenSource } from 'axios';

interface ApiRequestConfig extends AxiosRequestConfig {
    url: string;
    method?: string;
    data?: Record<string, any>;
    params?: Record<string, any>;
}

interface ApiResponse<T = any> {
    promise: Promise<{ data: T }>;
    cancel: (reason?: string) => void;
}

export const apiRequest = <T = any>(
    axiosParams: ApiRequestConfig
): ApiResponse<T> => {
    const defaultHeaders: Record<string, string> = {
        'X-Requested-With': 'CuántoCuestaUY',
        'Content-Type': 'application/json'
    };

    const cancelToken = Axios.CancelToken.source();

    const finalConfig: AxiosRequestConfig = {
        baseURL: process.env.REACT_APP_API_URL || 'https://api.example.com/api/',
        timeout: 30000,
        cancelToken: cancelToken.token,
        headers: {
            ...defaultHeaders,
            ...axiosParams.headers
        },
        ...axiosParams
    };

    return {
        promise: Axios(finalConfig),
        cancel: (reason?: string) => cancelToken.cancel(reason || 'Request cancelled')
    };
};
```

### Types Para Respuestas API

```typescript
// src/types/api.ts

export interface ApiResponse<T> {
    results: T[];
    page_metadata: {
        total: number;
        page: number;
        page_size: number;
    };
}

export interface Organismos {
    id: string;
    name: string;
    budget: number;
    year: number;
}

export interface SpendingRecord {
    id: string;
    organismo_id: string;
    amount: number;
    description: string;
    date: string;
    category: string;
    status: 'aprobado' | 'pendiente' | 'rechazado';
}

export interface FilterParams {
    organismos: string[];
    minYear: number;
    maxYear: number;
    minAmount: number;
    maxAmount: number;
}

export interface PaginationParams {
    limit: number;
    page: number;
    sort: string;
    order: 'asc' | 'desc';
}
```

### Endpoint Modules con TypeScript

```typescript
// src/apis/spending.ts
import { apiRequest } from './apiRequest';
import { ApiResponse, SpendingRecord, FilterParams } from 'types/api';

export const fetchSpendingDetail = (params: {
    filter: FilterParams;
    pagination: {
        limit: number;
        page: number;
        sort: string;
        order: 'asc' | 'desc';
    };
}) => apiRequest<SpendingRecord>({
    url: 'v2/spending/detail/',
    method: 'post',
    data: params
});

export const fetchSpendingExport = (
    format: 'csv' | 'json' | 'pdf',
    params: FilterParams
) => apiRequest<Blob>({
    url: `v2/spending/export/${format}/`,
    method: 'post',
    data: params,
    responseType: format === 'csv' ? 'blob' : 'json'
});
```

---

## 🎣 FASE 4: HOOKS PERSONALIZADOS TYPESCRIPT

### Hook de API Call

```typescript
// src/hooks/useApiCall.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { AxiosError } from 'axios';

interface UseApiCallOptions<T> {
    immediate?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: AxiosError) => void;
}

interface UseApiCallReturn<T> {
    data: T | null;
    loading: boolean;
    error: AxiosError | null;
    execute: (...args: any[]) => Promise<T>;
    refetch: (...args: any[]) => Promise<T>;
}

export function useApiCall<T = any>(
    apiFunction: (...args: any[]) => { promise: Promise<T>; cancel: () => void },
    options: UseApiCallOptions<T> = {}
): UseApiCallReturn<T> {
    const { immediate = true, onSuccess, onError } = options;

    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(immediate);
    const [error, setError] = useState<AxiosError | null>(null);

    const requestRef = useRef<{ promise: Promise<T>; cancel: () => void } | null>(null);

    const execute = useCallback(
        async (...args: any[]): Promise<T> => {
            if (requestRef.current) {
                requestRef.current.cancel();
            }

            setLoading(true);
            setError(null);

            try {
                requestRef.current = apiFunction(...args);
                const response = await requestRef.current.promise as any;
                const result = response.data;

                setData(result);
                onSuccess?.(result);
                return result;
            } catch (err) {
                const axiosError = err as AxiosError;
                if (axiosError.message !== 'Request cancelled') {
                    setError(axiosError);
                    onError?.(axiosError);
                }
                throw err;
            } finally {
                setLoading(false);
            }
        },
        [apiFunction, onSuccess, onError]
    );

    useEffect(() => {
        if (immediate) {
            execute();
        }

        return () => {
            if (requestRef.current) {
                requestRef.current.cancel();
            }
        };
    }, [execute, immediate]);

    return { data, loading, error, execute, refetch: execute };
}
```

### Hook de Filtros Redux

```typescript
// src/hooks/useFilters.ts
import { useDispatch, useSelector } from 'react-redux';
import { useCallback } from 'react';
import { RootState } from 'redux/store';
import * as filtersActions from 'redux/slices/filtersSlice';

export function useFilters() {
    const dispatch = useDispatch();
    const filters = useSelector((state: RootState) => state.filters);

    const setOrganismos = useCallback(
        (ids: string[]) => {
            dispatch(filtersActions.setOrganismos(ids));
        },
        [dispatch]
    );

    const setYears = useCallback(
        (years: number[]) => {
            dispatch(filtersActions.setYears(years));
        },
        [dispatch]
    );

    const resetFilters = useCallback(() => {
        dispatch(filtersActions.resetFilters());
    }, [dispatch]);

    return {
        filters,
        setOrganismos,
        setYears,
        resetFilters
    };
}
```

---

## 🧬 FASE 5: REDUX CON TYPESCRIPT

### Reducers con Slice Pattern

```typescript
// src/redux/slices/filtersSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface FiltersState {
    organismos: string[];
    years: number[];
    minAmount: number;
    maxAmount: number;
    spendingType: string[];
    currentPage: number;
    pageSize: number;
    sortField: string;
    sortOrder: 'asc' | 'desc';
}

const initialState: FiltersState = {
    organismos: [],
    years: [2023, 2024, 2025],
    minAmount: 0,
    maxAmount: 10000000000,
    spendingType: [],
    currentPage: 1,
    pageSize: 20,
    sortField: 'amount',
    sortOrder: 'desc'
};

export const filtersSlice = createSlice({
    name: 'filters',
    initialState,
    reducers: {
        setOrganismos: (state, action: PayloadAction<string[]>) => {
            state.organismos = action.payload;
            state.currentPage = 1;
        },
        setYears: (state, action: PayloadAction<number[]>) => {
            state.years = action.payload;
            state.currentPage = 1;
        },
        setAmountRange: (
            state,
            action: PayloadAction<{ min: number; max: number }>
        ) => {
            state.minAmount = action.payload.min;
            state.maxAmount = action.payload.max;
            state.currentPage = 1;
        },
        setSpendingType: (state, action: PayloadAction<string[]>) => {
            state.spendingType = action.payload;
            state.currentPage = 1;
        },
        setPagination: (
            state,
            action: PayloadAction<{ page: number; pageSize: number }>
        ) => {
            state.currentPage = action.payload.page;
            state.pageSize = action.payload.pageSize;
        },
        setSort: (
            state,
            action: PayloadAction<{ field: string; order: 'asc' | 'desc' }>
        ) => {
            state.sortField = action.payload.field;
            state.sortOrder = action.payload.order;
        },
        resetFilters: () => initialState
    }
});

export const {
    setOrganismos,
    setYears,
    setAmountRange,
    setSpendingType,
    setPagination,
    setSort,
    resetFilters
} = filtersSlice.actions;

export default filtersSlice.reducer;
```

### Selectors Tipificados

```typescript
// src/redux/selectors/filtersSelectors.ts
import { RootState } from 'redux/store';

export const selectOrganismos = (state: RootState) => state.filters.organismos;
export const selectYears = (state: RootState) => state.filters.years;
export const selectCurrentPage = (state: RootState) => state.filters.currentPage;
export const selectPageSize = (state: RootState) => state.filters.pageSize;

export const selectActiveFilterCount = (state: RootState) => {
    const { organismos, years, spendingType } = state.filters;
    return organismos.length + years.length + spendingType.length;
};
```

---

## ✅ CHECKLIST DE ADAPTACIÓN

- [ ] **Paso 1**: Convertir todos los archivos `.jsx` a `.tsx`
- [ ] **Paso 2**: Reemplazar `PropTypes` con interfaces TypeScript en cabeça de archivo
- [ ] **Paso 3**: Instalar Tailwind: `npm install -D tailwindcss postcss autoprefixer`
- [ ] **Paso 4**: Crear `tailwind.config.js` personalizado
- [ ] **Paso 5**: Reemplazar clases SCSS con Tailwind (iniciar con componentes compartidos)
- [ ] **Paso 6**: Migrar Redux a Redux Toolkit con slices
- [ ] **Paso 7**: Actualizar todos los imports de las carpetas `src/types/`
- [ ] **Paso 8**: Tests: adaptar jest config para TypeScript

### Comando de Setup Rápido

```bash
# Crear proyecto con TypeScript
npx create-react-app cuantocuesta-uy --template typescript

# Instalar dependencias clave
npm install react-redux redux @reduxjs/toolkit recharts d3 axios

# Instalar Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Instalar tipos
npm install --save-dev @types/axios @types/redux @types/d3
```

