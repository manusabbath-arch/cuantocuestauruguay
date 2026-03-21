# Ejemplos de código práctico - USAspending patterns para Uruguay

Patrones de código listos para adaptar a `cuantocuestauruguay`.

---

## 📋 1. WRAPPER DE API CENTRALIZADO

```jsx
// src/apis/apiRequest.js
import Axios, { CancelToken } from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'https://api.example.com/api/';

export const apiRequest = (axiosParams = {}) => {
    const defaultHeaders = { 
        'X-Requested-With': 'CuántoCuestaUY',
        'Content-Type': 'application/json'
    };
    const cancelToken = CancelToken.source();
    
    const defaultParams = {
        baseURL: API_BASE,
        cancelToken: cancelToken.token,
        headers: { ...defaultHeaders, ...axiosParams.headers }
    };
    
    const mergedParams = {
        ...defaultParams,
        ...axiosParams
    };

    return {
        promise: Axios(mergedParams),
        cancel: () => cancelToken.cancel('Request cancelled')
    };
};
```

```jsx
// src/apis/spending.js
import { apiRequest } from './apiRequest';

// Gasto macro por organismo
export const fetchSpendingByOrganismo = (year) => apiRequest({
    url: 'v2/organismos/spending/overview/',
    params: { year }
});

// Desglose detallado con paginación
export const fetchSpendingDetail = (params) => apiRequest({
    url: 'v2/spending/detail/',
    method: 'post',
    data: params
});

// Series temporales
export const fetchSpendingTimeSeries = (filtersConfig) => apiRequest({
    url: 'v2/spending/over_time/',
    method: 'post',
    data: filtersConfig
});

// Exportar datos
export const fetchSpendingExport = (format, params) => apiRequest({
    url: `v2/spending/export/${format}/`,
    method: 'post',
    data: params,
    responseType: format === 'csv' ? 'blob' : 'json'
});
```

---

## 🎨 2. COMPONENTE FILTRO CHECKBOX REUTILIZABLE

```jsx
// src/components/shared/AutocompleteFilterCheckbox.jsx
import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

const propTypes = {
    filterType: PropTypes.string.isRequired,        // "Organismos", "Años"
    items: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        count: PropTypes.number
    })).isRequired,
    selectedIds: PropTypes.arrayOf(PropTypes.string).isRequired,
    onToggle: PropTypes.func.isRequired,            // (id, isSelected)
    onToggleAll: PropTypes.func.isRequired,         // (allSelected)
    loading: PropTypes.bool,
    error: PropTypes.bool,
    errorMessage: PropTypes.string
};

export const AutocompleteFilterCheckbox = ({
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

    const handleClearAll = useCallback(() => {
        filteredItems.forEach(item => {
            if (selectedIds.includes(item.id)) {
                onToggle(item.id, false);
            }
        });
    }, [filteredItems, selectedIds, onToggle]);

    const handleSelectAll = useCallback(() => {
        filteredItems.forEach(item => {
            if (!selectedIds.includes(item.id)) {
                onToggle(item.id, true);
            }
        });
    }, [filteredItems, selectedIds, onToggle]);

    return (
        <div className="filter-checkbox-group">
            <div className="filter-header">
                <h3>{filterType}</h3>
                <button 
                    onClick={() => onToggleAll(!allSelected)}
                    className="toggle-all-btn"
                >
                    {allSelected ? 'Deseleccionar todo' : 'Seleccionar todo'}
                </button>
            </div>

            <input
                type="text"
                placeholder={`Buscar ${filterType.toLowerCase()}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="filter-search"
            />

            {loading && <div className="spinner">Cargando...</div>}
            
            {error && (
                <div className="error-message">
                    {errorMessage || 'Error al cargar opciones'}
                </div>
            )}

            {!loading && !error && filteredItems.length === 0 && (
                <div className="no-results">Sin resultados</div>
            )}

            <div className="checkbox-list">
                {filteredItems.map(item => (
                    <label key={item.id} className="checkbox-item">
                        <input
                            type="checkbox"
                            checked={selectedIds.includes(item.id)}
                            onChange={(e) => onToggle(item.id, e.target.checked)}
                        />
                        <span className="label-text">
                            {item.label}
                            {item.count !== undefined && (
                                <span className="count"> ({item.count})</span>
                            )}
                        </span>
                    </label>
                ))}
            </div>
        </div>
    );
};

export default AutocompleteFilterCheckbox;
```

---

## 📊 3. CONTENEDOR CON MANEJO DE PAGINACIÓN Y FILTROS

```jsx
// src/containers/SpendingDetailContainer.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { isCancel } from 'axios';

import { fetchSpendingDetail } from 'apis/spending';
import SpendingDetailView from 'components/spending/SpendingDetailView';

const INITIAL_PAGE_SIZE = 20;

export const SpendingDetailContainer = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [totalItems, setTotalItems] = useState(0);
    
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(INITIAL_PAGE_SIZE);
    const [sortField, setSortField] = useState('amount');
    const [sortOrder, setSortOrder] = useState('desc');
    
    const [filters, setFilters] = useState({
        organismos: [],
        minYear: 2023,
        maxYear: 2025,
        minAmount: 0
    });

    const requestRef = useRef(null);

    const fetchData = useCallback(() => {
        if (requestRef.current) {
            requestRef.current.cancel('New request initiated');
        }

        setLoading(true);
        setError(false);

        const params = {
            filter: filters,
            pagination: {
                limit: pageSize,
                page: currentPage,
                sort: sortField,
                order: sortOrder
            }
        };

        requestRef.current = fetchSpendingDetail(params);

        requestRef.current.promise
            .then((response) => {
                setData(response.data.results);
                setTotalItems(response.data.page_metadata.total);
                setLoading(false);
            })
            .catch((err) => {
                if (!isCancel(err)) {
                    setError(true);
                    console.error('Error fetching spending:', err);
                }
                setLoading(false);
            });

    }, [filters, currentPage, pageSize, sortField, sortOrder]);

    useEffect(() => {
        fetchData();
        
        return () => {
            if (requestRef.current) {
                requestRef.current.cancel();
            }
        };
    }, [fetchData]);

    const handleFilterChange = useCallback((newFilters) => {
        setFilters(newFilters);
        setCurrentPage(1);  // Reset a primera página
    }, []);

    const handlePageChange = useCallback((newPage) => {
        setCurrentPage(newPage);
        // Scroll al tope de tabla
        document.querySelector('.spending-table')?.scrollIntoView();
    }, []);

    const handleSort = useCallback((field) => {
        if (sortField === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortOrder('desc');
        }
    }, [sortField, sortOrder]);

    const totalPages = Math.ceil(totalItems / pageSize);

    return (
        <SpendingDetailView
            data={data}
            loading={loading}
            error={error}
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={pageSize}
            sortField={sortField}
            sortOrder={sortOrder}
            filters={filters}
            onFilterChange={handleFilterChange}
            onPageChange={handlePageChange}
            onSort={handleSort}
        />
    );
};

export default SpendingDetailContainer;
```

---

## 📈 4. GRÁFICO SANKEY PARA FLUJOS DE PRESUPUESTO

```jsx
// src/components/charts/BudgetFlowSankey.jsx
import React, { useEffect, useState } from 'react';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';
import { scaleSequential } from 'd3-scale';
import { interpolateBlues } from 'd3-scale-chromatic';
import PropTypes from 'prop-types';

const propTypes = {
    nodes: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        color: PropTypes.string
    })).isRequired,
    links: PropTypes.arrayOf(PropTypes.shape({
        source: PropTypes.number.isRequired,  // índice en nodes
        target: PropTypes.number.isRequired,
        value: PropTypes.number.isRequired
    })).isRequired,
    width: PropTypes.number,
    height: PropTypes.number,
    onNodeClick: PropTypes.func
};

export const BudgetFlowSankey = ({
    nodes = [],
    links = [],
    width = 960,
    height = 500,
    onNodeClick
}) => {
    const [layout, setLayout] = useState(null);

    useEffect(() => {
        // Generar layout Sankey
        const sankey_generator = sankey()
            .nodeWidth(60)
            .nodePadding(200)
            .extent([[1, 1], [width - 1, height - 6]]);

        const graph = sankey_generator({
            nodes: nodes.map((d, i) => ({ ...d, index: i })),
            links: links.map(d => ({ ...d }))
        });

        setLayout(graph);
    }, [nodes, links, width, height]);

    if (!layout) return null;

    const colorScale = scaleSequential(interpolateBlues);
    const maxValue = Math.max(...links.map(l => l.value));

    return (
        <svg width={width} height={height} className="sankey-chart">
            {/* Links (líneas) */}
            <g className="links" opacity={0.5}>
                {layout.links.map((link, i) => (
                    <path
                        key={i}
                        d={sankeyLinkHorizontal()(link)}
                        stroke={colorScale(link.value / maxValue)}
                        strokeWidth={Math.max(1, link.width)}
                        fill="none"
                    />
                ))}
            </g>

            {/* Nodes (rectángulos) */}
            <g className="nodes">
                {layout.nodes.map((node, i) => (
                    <g key={i} className="node">
                        <rect
                            x={node.x0}
                            y={node.y0}
                            width={node.x1 - node.x0}
                            height={node.y1 - node.y0}
                            fill={node.color || '#69b3e7'}
                            onClick={() => onNodeClick?.(node)}
                            style={{ cursor: 'pointer' }}
                        />
                        <text
                            x={node.x0 < width / 2 ? node.x1 + 6 : node.x0 - 6}
                            y={(node.y1 + node.y0) / 2}
                            dy="0.35em"
                            textAnchor={node.x0 < width / 2 ? 'start' : 'end'}
                            fontSize="12"
                            fontWeight="bold"
                        >
                            {node.label}
                        </text>
                    </g>
                ))}
            </g>
        </svg>
    );
};

BudgetFlowSankey.propTypes = propTypes;
export default BudgetFlowSankey;

// Uso:
// <BudgetFlowSankey
//     nodes={[
//         { id: 'mec', label: 'Educación', color: '#1f77b4' },
//         { id: 'salud', label: 'Salud', color: '#ff7f0e' },
//         { id: 'spent', label: 'Gastado', color: '#2ca02c' }
//     ]}
//     links={[
//         { source: 0, target: 2, value: 5000000000 },
//         { source: 1, target: 2, value: 3000000000 }
//     ]}
// />
```

---

## 🔍 5. REDUX STATE PARA FILTROS

```jsx
// src/redux/reducers/filtersReducer.js
import { Map, Set } from 'immutable';

export const initialState = {
    organismos: Set(),
    years: Set(),
    minAmount: 0,
    maxAmount: 10000000000,
    spendingType: Set(),  // gasto, inversión, etc
    
    // Paginación
    currentPage: 1,
    pageSize: 20,
    sortField: 'amount',
    sortOrder: 'desc'
};

export const FILTER_ACTIONS = {
    SET_ORGANISMOS: 'filters/SET_ORGANISMOS',
    SET_YEARS: 'filters/SET_YEARS',
    SET_AMOUNT_RANGE: 'filters/SET_AMOUNT_RANGE',
    SET_SPENDING_TYPE: 'filters/SET_SPENDING_TYPE',
    SET_PAGINATION: 'filters/SET_PAGINATION',
    SET_SORT: 'filters/SET_SORT',
    RESET_FILTERS: 'filters/RESET_FILTERS'
};

export const filtersReducer = (state = initialState, action) => {
    switch (action.type) {
        case FILTER_ACTIONS.SET_ORGANISMOS:
            return {
                ...state,
                organismos: Set(action.payload)
            };
        
        case FILTER_ACTIONS.SET_YEARS:
            return {
                ...state,
                years: Set(action.payload)
            };
        
        case FILTER_ACTIONS.SET_AMOUNT_RANGE:
            return {
                ...state,
                minAmount: action.payload.min,
                maxAmount: action.payload.max
            };
        
        case FILTER_ACTIONS.SET_PAGINATION:
            return {
                ...state,
                currentPage: action.payload.page || 1,
                pageSize: action.payload.size || 20
            };
        
        case FILTER_ACTIONS.SET_SORT:
            return {
                ...state,
                sortField: action.payload.field,
                sortOrder: action.payload.order
            };
        
        case FILTER_ACTIONS.RESET_FILTERS:
            return initialState;
        
        default:
            return state;
    }
};

// Action creators
export const setOrganismos = (ids) => ({
    type: FILTER_ACTIONS.SET_ORGANISMOS,
    payload: ids
});

export const setYears = (years) => ({
    type: FILTER_ACTIONS.SET_YEARS,
    payload: years
});

export const setAmountRange = (min, max) => ({
    type: FILTER_ACTIONS.SET_AMOUNT_RANGE,
    payload: { min, max }
});

export const setPagination = (page, size) => ({
    type: FILTER_ACTIONS.SET_PAGINATION,
    payload: { page, size }
});

export const setSort = (field, order) => ({
    type: FILTER_ACTIONS.SET_SORT,
    payload: { field, order }
});

export const resetFilters = () => ({
    type: FILTER_ACTIONS.RESET_FILTERS
});

// Selectors
export const selectActiveFilterCount = (state) => {
    let count = 0;
    if (state.organismos.size > 0) count += state.organismos.size;
    if (state.years.size > 0) count += state.years.size;
    if (state.spendingType.size > 0) count += state.spendingType.size;
    return count;
};

export const selectFilterSummary = (state) => ({
    organismos: state.organismos.toArray(),
    years: state.years.toArray(),
    amountRange: { min: state.minAmount, max: state.maxAmount }
});
```

---

## 🎯 6. HELPER DE FORMATO DE DINERO

```jsx
// src/helpers/moneyFormatter.js
export const formatMoney = (value) => {
    if (!value) return '$0';
    return new Intl.NumberFormat('es-UY', {
        style: 'currency',
        currency: 'UYU',
        maximumFractionDigits: 0
    }).format(value);
};

export const formatMoneyWithUnits = (value) => {
    if (!value) return '$0';
    
    const absVal = Math.abs(value);
    let divisor = 1;
    let suffix = '';

    if (absVal >= 1000000000) {
        divisor = 1000000000;
        suffix = ' mil millones';
    } else if (absVal >= 1000000) {
        divisor = 1000000;
        suffix = ' millones';
    } else if (absVal >= 1000) {
        divisor = 1000;
        suffix = ' mil';
    }

    const formatted = (value / divisor).toFixed(1);
    return `$${formatted}${suffix}`;
};

export const formatNumber = (value) => {
    return new Intl.NumberFormat('es-UY').format(value || 0);
};

export const parseMoneyInput = (str) => {
    // Convierte "$1,234.56" → 1234.56
    return parseFloat(
        String(str).replace(/[^\d.-]/g, '')
    );
};
```

---

## 🔠 7. DATAMAPPING - CONSTANTES CENTRALIZADAS

```jsx
// src/dataMapping/organismos.js
export const ORGANISMOS = {
    'mec': { label: 'Ministerio de Educación', abbr: 'MEC' },
    'msp': { label: 'Ministerio de Salud Pública', abbr: 'MSP' },
    'mtop': { label: 'Ministerio de Transporte', abbr: 'MTOP' },
    'ministerio_ambiente': { label: 'Ministerio de Ambiente', abbr: 'MA' },
    'poder_judicial': { label: 'Poder Judicial', abbr: 'PJ' }
};

export const ORGANISMOS_ARRAY = Object.entries(ORGANISMOS).map(([id, data]) => ({
    id,
    ...data
}));

export const SPENDING_TYPES = {
    'operating': { label: 'Gasto Corriente', color: '#1f77b4' },
    'capital': { label: 'Gasto de Inversión', color: '#ff7f0e' },
    'debt': { label: 'Servicio de Deuda', color: '#d62728' },
    'transfers': { label: 'Transferencias', color: '#2ca02c' }
};

export const YEARS = [2020, 2021, 2022, 2023, 2024, 2025];

export const AMOUNT_RANGES = [
    { min: 0, max: 10000, label: '< $10K' },
    { min: 10000, max: 100000, label: '$10K - $100K' },
    { min: 100000, max: 1000000, label: '$100K - $1M' },
    { min: 1000000, max: Infinity, label: '> $1M' }
];
```

---

## 🎬 8. HOOK PERSONALIZADO PARA LLAMADAS API

```jsx
// src/hooks/useApiCall.js
import { useState, useCallback, useRef, useEffect } from 'react';
import { isCancel } from 'axios';

export const useApiCall = (apiFunction, immediate = true) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(immediate);
    const [error, setError] = useState(null);

    const requestRef = useRef(null);

    const execute = useCallback(async (...args) => {
        if (requestRef.current) {
            requestRef.current.cancel('New request initiated');
        }

        setLoading(true);
        setError(null);

        try {
            requestRef.current = apiFunction(...args);
            const response = await requestRef.current.promise;
            setData(response.data);
            return response.data;
        } catch (err) {
            if (!isCancel(err)) {
                setError(err.response?.data?.message || err.message);
            }
            throw err;
        } finally {
            setLoading(false);
        }
    }, [apiFunction]);

    useEffect(() => {
        if (immediate) {
            execute();
        }

        return () => {
            if (requestRef.current) {
                requestRef.current.cancel();
            }
        };
    }, []);

    return { data, loading, error, execute, refetch: execute };
};

// Uso:
// const { data, loading, error } = useApiCall(
//     () => fetchSpendingByYear(2024),
//     true  // immediate = true
// );
```

---

## 🧪 9. TESTS CON JEST + TESTING-LIBRARY

```jsx
// src/components/shared/__tests__/AutocompleteFilterCheckbox.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AutocompleteFilterCheckbox } from '../AuthocompleteFilterCheckbox';

describe('AutocompleteFilterCheckbox', () => {
    const mockItems = [
        { id: '1', label: 'Opción 1', count: 10 },
        { id: '2', label: 'Opción 2', count: 5 },
        { id: '3', label: 'Opción 3', count: 8 }
    ];

    it('renders filter title and search input', () => {
        render(
            <AutocompleteFilterCheckbox
                filterType="Test Filter"
                items={mockItems}
                selectedIds={[]}
                onToggle={jest.fn()}
                onToggleAll={jest.fn()}
            />
        );

        expect(screen.getByText('Test Filter')).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/buscar/i)).toBeInTheDocument();
    });

    it('filters items by search term', () => {
        render(
            <AutocompleteFilterCheckbox
                filterType="Test"
                items={mockItems}
                selectedIds={[]}
                onToggle={jest.fn()}
                onToggleAll={jest.fn()}
            />
        );

        const searchInput = screen.getByPlaceholderText(/buscar/i);
        fireEvent.change(searchInput, { target: { value: 'Opción 1' } });

        expect(screen.getByLabelText(/opción 1/i)).toBeInTheDocument();
        expect(screen.queryByLabelText(/opción 2/i)).not.toBeInTheDocument();
    });

    it('calls onToggle when checkbox is clicked', () => {
        const mockToggle = jest.fn();
        render(
            <AutocompleteFilterCheckbox
                filterType="Test"
                items={mockItems}
                selectedIds={[]}
                onToggle={mockToggle}
                onToggleAll={jest.fn()}
            />
        );

        const checkbox = screen.getAllByRole('checkbox')[0];
        fireEvent.click(checkbox);

        expect(mockToggle).toHaveBeenCalledWith('1', true);
    });

    it('shows select all button', () => {
        render(
            <AutocompleteFilterCheckbox
                filterType="Test"
                items={mockItems}
                selectedIds={[]}
                onToggle={jest.fn()}
                onToggleAll={jest.fn()}
            />
        );

        expect(screen.getByRole('button', { name: /seleccionar todo/i }))
            .toBeInTheDocument();
    });
});
```

---

## 📦 10. CONFIGURACIÓN PACKAGE.JSON

```json
{
  "name": "cuantocuesta-uruguay",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^9.0.0",
    "redux": "^5.0.0",
    "recharts": "^2.10.0",
    "d3": "^7.8.0",
    "d3-sankey": "^0.12.3",
    "d3-hierarchy": "^3.1.2",
    "d3-scale": "^4.0.2",
    "d3-scale-chromatic": "^3.0.0",
    "axios": "^1.6.0",
    "lodash-es": "^4.17.21",
    "react-router-dom": "^6.15.0",
    "immutable": "^4.3.0",
    "prop-types": "^15.8.1",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.4",
    "jest": "^29.7.0",
    "babel-jest": "^29.7.0",
    "@babel/preset-react": "^7.22.0",
    "eslint": "^8.48.0",
    "prettier": "^3.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  }
}
```

