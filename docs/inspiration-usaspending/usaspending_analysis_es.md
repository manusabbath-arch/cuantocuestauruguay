# Análisis: USAspending Website Repository
## Patrones reutilizables para un proyecto similar en Uruguay

---

## 📋 Resumen Ejecutivo

El repositorio `fedspendingtransparency/usaspending-website` implementa una plataforma de transparencia fiscal **altamente inspirativa** para un proyecto uruguayo. Usa React 18 + Redux + SCSS con patrones modernos y reutilizables.

---

## 🏗️ 1. COMPONENTES REACT REUTILIZABLES

### 1.1 Estructura organizacional

```
src/js/
├── components/
│   ├── sharedComponents/          ← Componentes genéricos reutilizables
│   ├── search/                    ← Búsqueda avanzada
│   ├── agency/                    ← Perfiles de agencias
│   ├── recipient/                 ← Perfiles de beneficiarios
│   ├── award/                     ← Detalles de premios/grants
│   └── covid19/                   ← Módulos temáticos especializados
└── containers/                    ← Smart components (Redux connected)
```

### 1.2 Componentes genéricos evidenciados

#### **Checkbox & Filtros**
```jsx
// Patrón: Base reutilizable para filtros
- CheckboxItem               → Checkbox individual con búsqueda
- CheckboxTree              → Árbol jerárquico de checkboxes
- AutocompleteWithCheckboxList → Búsqueda + checkbox combinados
- ListCheckbox              → Lista simple de checkboxes
- PrimaryCheckboxType       → Wrapper tipado
```

**Implementación**: Todos siguen patrón de props:
- `selectedFilters` (Set/Array)
- `singleFilterChange(selection)` callback
- `searchString` para filtrado en tiempo real
- `bulkFilterChange()` para seleccionar/deseleccionar todo

#### **Iconografía modular**
```jsx
// src/js/components/sharedComponents/icons/Icons.jsx
// Exporta 40+ íconos como componentes pequeños
export const AngleDown = ({ iconName, iconClass, alt }) => ...
export const Award = ({ iconName, iconClass, alt }) => ...
export const BudgetFunction = ({ iconName, iconClass, alt }) => ...
// Pattern: Todos wrappean BaseIcon con valores por defecto
```

**Ventaja para Uruguay**: Crear `<CedulaIcon />`, `<EntidadIcon />`, etc normalizados

#### **Tooltips & Mensajes**
```jsx
- Tooltip                    → Tooltip posicionado dinámicamente
- TooltipWrapper (data-transparency-ui) → Wrapper accesible
- Alert                      → Alertas tipo info/error/warning/success
- Note                       → Notas informativas
- ChartNoResults             → Mensaje vacío reutilizable
- ChartLoadingMessage        → Loading spinner consistente
- ChartError                 → Error handling genérico
```

#### **Buttons & Controles**
```jsx
- Button (data-transparency-ui)  → Button con variantes
- ShareIcon508               → Compartir accesible
- DownloadButton508          → Descargar accesible
- RoundedToggle              → Toggle redondeado
- CheckboxChevron            → Chevron interactivo
```

#### **Layouts**
```jsx
- PageWrapper                → Layout general con meta tags
- FlexGridRow, FlexGridCol   → Grid responsive (data-transparency-ui)
- FilterSidebar              → Sidebar con filtros acordeón
- SectionWrapper             → Wrapper para secciones
```

### 1.3 Patrones de props y state

```jsx
// Patrón consistente para filtros
const propTypes = {
    selectedFilters: PropTypes.array,      // valores seleccionados
    filters: PropTypes.array,              // opciones disponibles
    singleFilterChange: PropTypes.func,    // callback cambio individual
    bulkFilterChange: PropTypes.func,      // callback cambio múltiple
    searchString: PropTypes.string,        // término de búsqueda
    loading: PropTypes.bool,
    error: PropTypes.bool,
    noResults: PropTypes.bool
};

// Patrón de hooks para manejo de estado
const [selectedFilters, setSelectedFilters] = useState([]);
const [searchString, setSearchString] = useState('');
const [loading, setLoading] = useState(false);
```

---

## 📊 2. VISUALIZACIÓN DE DATOS DE GASTO

### 2.1 Librerías y tecnologías

| Librería | Uso | Observación |
|----------|-----|-------------|
| **D3.js** | Gráficos custom avanzados | Para diagramas Sankey, treemaps, paths |
| **Recharts** | Gráficos simples React-friendly | BarChart, LineChart (componentes) |
| **Lodash** | Transformaciones de datos | Agregaciones, ordenamientos |
| **data-transparency-ui** | Componentes UI preconstruidos | InformationBoxes, LoadingMessage |

### 2.2 Patrones de visualización

#### **A. Gráficos de serie temporal**
```jsx
// Patrón: Reciben data formateada
BarChartTrendline
├── Props: data, height, width, padding, xSeries, ySeries, zSeries
├── SVG custom con D3 scales: scaleLinear()
├── Tooltip dinámico al hover
└── Manejo de responsive (calculateWidth)

TimeVisualizationChart (nuevo con Recharts)
├── <BarChart>
├── <XAxis> con CustomXTick
├── <Tooltip> personalizado
└── <ReferenceLine> para referencias
```

#### **B. Diagramas Sankey (flujos de presupuesto)**
```jsx
SankeyVisualization (familia)
├── SankeyVisualizationVertical    → Layout vertical (móvil)
├── SankeyVisualizationHorizontal  → Layout horizontal (desktop)
└── Nodos: Budget Authority → Obligated/Unobligated → Outlays

// Props para nodos:
{
    name: '_totalBudgetAuthority',
    label: 'Total Budgetary Resources',
    color: '#AAC6E2',
    glossary: URL,
    textWidth: 140,
    textHeight: 31
}
```

#### **C. Treemaps (distribución jerárquica)**
```jsx
AwardBreakdownTreeMap
├── Usa hierarchy() y treemap() de d3-hierarchy
├── Props: awardBreakdown[], totalAmount, toggleState
├── Tooltip al hover muestra detalles
└── ColorScale: scaleQuantize() por rango de montos

// Data esperada:
[
    { label: 'Category', value: 1000000, color: '#' },
    { children: [...] }
]
```

#### **D. Gráficos de obligaciones por tipo de premio**
```jsx
ObligationsByAwardType
├── Gráfico circular (Sunburst) con D3
├── Categorías: Contracts, IDVs, Grants, Loans, etc.
├── Permite drill-down interactivo
└── Props: outer[], inner[], fiscalYear, isMobile
```

### 2.3 Estructura de datos para visualización

```js
// Patrón general: normalización antes de visualizar
const chartData = {
    groups: ['Q1 FY2024', 'Q2 FY2024'],  // etiquetas X
    xSeries: ['Oct 2023', 'Nov 2023'],   // tooltips
    ySeries: [150000000, 250000000],     // valores Y
    zSeries: [10, 15],                   // valores secundarios
    rawLabels: ['Award count']
};

// Para agregaciones
const aggregated = {
    category: 'Contracts',
    aggregated_amount: 5000000000,
    count: 1250
};
```

### 2.4 Manejo de tooltips personalizado

```jsx
// Patrón: Componente tooltip contenedor + callback
<TooltipWrapper
    content={<CustomTooltip data={data} />}
    closeTooltip={() => setShowTooltip(false)}
    showInfoTooltip={showTooltip === 'custom'} />

// En el gráfico:
onMouseEnter={() => displayTooltip(position, data)}
onMouseLeave={() => hideTooltip()}
```

---

## 🔌 3. PATRONES DE ETL/API

### 3.1 Estructura de integración API

```
src/js/apis/
├── apiRequest.js              ← Wrapper Axios con configuración global
├── disaster.js                ← Endpoints COVID-19
├── agency.js                  ← Endpoints de agencias
├── account.js                 ← Endpoints de cuentas federales
├── award.js                   ← Endpoints de premios
├── search.js                  ← Endpoints de búsqueda avanzada
└── recipient.js               ← Endpoints de beneficiarios
```

### 3.2 Wrapper de API base

```jsx
// helpers/apiRequest.js - Configuración centralizada
export const apiRequest = (axiosParams = {}) => {
    const defaultHeaders = { 'X-Requested-With': 'USASpendingFrontend' };
    const cancelToken = CancelToken.source();
    
    const defaultParams = {
        baseURL: getBaseUrl(axiosParams),  // URL según ENV
        cancelToken: cancelToken.token
    };
    
    return {
        promise: axios(params(axiosParams)),
        cancel: () => cancelToken.cancel()  // Para cleanup
    };
};
```

### 3.3 Endpoints específicos

```jsx
// apis/disaster.js - COVID-19 example
export const fetchOverview = (defCodes) => apiRequest({
    url: defCodes 
        ? `v2/disaster/overview/?def_codes=${defCodeQueryString(defCodes)}`
        : 'v2/disaster/overview/'
});

export const fetchAgencySpending = (params) => apiRequest({
    url: 'v2/disaster/agency/spending/',
    method: 'post',
    data: params  // POST para queries complejas
});

// apis/agency.js
export const fetchSubagencySpendingList = (code, fy, type, params) => 
    apiRequest({
        url: `v2/agency/${code}/sub_agency/${fy ? `?fiscal_year=${fy}` : ''}`,
        params
    });
```

### 3.4 Patrón de paginación

```js
// Request
{
    limit: 20,           // por página
    page: 1,             // número de página
    sort: 'field_name',  // campo para ordenar
    order: 'asc'         // asc | desc
}

// Response
{
    results: [...],
    page_metadata: {
        total: 950,      // total de registros
        page: 1,
        page_size: 20,
        total_pages: 48
    }
}
```

### 3.5 Manejo de solicitudes en containers

```jsx
// Patrón: useCallback + useRef para cancel
const fetchSpendingByAgencyCallback = useCallback(() => {
    if (request.current) {
        request.current.cancel();  // Cancela anterior
    }
    
    setLoading(true);
    setError(false);
    
    const params = {
        filter: { ... },
        pagination: { limit: 20, page: currentPage, sort, order }
    };
    
    request.current = fetchAwardSpendingByAgency(params);
    
    request.current.promise
        .then((res) => {
            setResults(res.data.results);
            setTotalItems(res.data.page_metadata.total);
            setLoading(false);
        })
        .catch((err) => {
            if (!isCancel(err)) {
                setError(true);
            }
            setLoading(false);
        });
}, [currentPage, sort, order]);
```

### 3.6 Transformación de datos (ETL)

```jsx
// helpers/searchHelper.js - Ejemplo transformación
export const performSpendingByCategorySearch = (params) => apiRequest({
    url: 'v2/search/spending_by_category/${params.category}',
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    data: params
});

// Luego en container: parseRows(res.data.results)
const parseRows = (data) => data.map(item => ({
    id: item.id,
    name: item.agency_name || item.recipient_name,
    amount: formatMoneyWithUnits(item.obligated_amount),  // Formatea en frontend
    count: item.award_count
}));
```

### 3.7 Almacenamiento en caché (hash URL)

```jsx
// Patrón: Guardar estado filtros en URL hash
export const generateUrlHash = (data) => apiRequest({
    url: 'v2/search_filters/hash/',
    method: 'post',
    data
});

// Uso:
const tempHash = generateUrlHash(filters);
tempHash.promise
    .then((results) => {
        window.history.pushState(null, null, `?hash=${results.data.hash}`);
    });
```

---

## 📦 4. ESTRUCTURA DE DATOS

### 4.1 Modelo de datos centralizado

```jsx
// dataMapping/ - Constantes y mapeos
dataMapping/
├── search/
│   ├── awardType.js           ← Tipos de premios
│   ├── contractFields.js       ← Campos de contratos
│   ├── recipientType.js        ← Tipos de beneficiarios
│   ├── searchFilterCategories.jsx
│   └── awardTableColumns.jsx   ← Configuración de columnas
├── covid19/
│   ├── covid19.js              ← Constantes COVID
│   ├── amountsVisualization.js
│   └── recipient/map/map.js    ← Mapeo de filtros geográficos
└── shared/
    ├── mobileBreakpoints.js
    └── stickyHeader.js
```

### 4.2 Definición de tipos de premios

```js
// dataMapping/search/awardType.js
export const awardTypeGroups = {
    contracts: ['IDV_B', 'IDV_C', ...],
    grants: ['02', '03', ...],
    direct_payments: ['05', '06', ...],
    loans: ['07', '08', ...],
    other: ['09', '10', ...]
};

export const awardTypeLabels = {
    'contracts': 'Contracts',
    'IDV_B': 'Indefinite Delivery / Blanket Purchase Agreement',
    ...
};
```

### 4.3 Definición de filtros

```js
// Patrón: Cada filtro tiene definición + mapeo
export const extentCompetedDefinitions = [
    { 
        name: 'Full and Open Competition',
        value: 'F'
    },
    { 
        name: 'Not Competed',
        value: 'D'
    }
];

export const extentCompetedTypeMapping = {
    'F': 'Full and Open',
    'D': 'Not Competed'
};
```

### 4.4 Configuración de tabla

```js
// dataMapping/search/awardTableColumns.jsx
export const awardTableColumns = [
    {
        title: 'Recipient Name',
        displayName: 'Recipient',
        customWidth: customWidth30
    },
    {
        title: 'Action Date',
        displayName: 'Date',
        subtitle: '(Action)',
        customWidth: customWidth20
    },
    {
        title: 'Award Amount',
        displayName: 'Award Amount',
        customWidth: customWidth25,
        right: true  // Alineado a derecha
    }
];
```

### 4.5 Redux state structure

```js
// redux/reducers/search/searchFiltersReducer.js
const initialState = {
    // Filtros básicos
    selectedAwardingAgencies: Set(),
    selectedFundingAgencies: Set(),
    selectedRecipients: Map(),      // Inmutable.js Order Map
    selectedLocations: Set(),
    
    // Filtros temporales
    timePeriodFY: Set(),
    time_period: Set(),
    
    // Filtros categorías
    awardType: Set(),
    awardDescription: '',
    awardAmounts: Map(),
    selectedCFDA: Map(),
    
    // Filtros avanzados
    recipientType: Set(),
    extentCompeted: Set(),
    setAside: Set(),
    pricingType: Set(),
    defCode: CheckboxTreeSelections(),
    
    // Búsqueda
    searchTerm: ''
};

// CheckboxTreeSelections es estructura personalizada para árboles
class CheckboxTreeSelections {
    constructor({ require = [], exclude = [], counts = [] }) {
        this.require = require;      // Nodos explícitamente seleccionados
        this.exclude = exclude;      // Nodos explícitamente no seleccionados
        this.counts = counts;        // Metadata de conteos
    }
}
```

### 4.6 Modelo de respuesta API

```js
// Estructuras de datos esperadas del backend

// 1. Overview (agregados de alto nivel)
{
    funding: [
        { def_code: 'L', amount: 7410000000 },
        { def_code: 'M', amount: 11230000000 }
    ],
    total_budget_authority: 2300000000000,
    spending: {
        award_obligations: 866700000000,
        award_outlays: 413100000000,
        total_obligations: 963000000000,
        total_outlays: 459000000000
    }
}

// 2. Detalle de gasto por categoría
{
    results: [
        {
            group: 'Department of Defense',
            aggregated_amount: 500000000,
            percentage: 15.5
        }
    ],
    page_metadata: { total: 120, page: 1 }
}

// 3. Serie temporal
{
    groups: ['Q1 FY2024', 'Q2 FY2024'],
    series: [
        { month: 'Oct 2023', amount: 150000000, awards: 10 },
        { month: 'Nov 2023', amount: 250000000, awards: 15 }
    ]
}
```

---

## 🔍 5. FILTRADO AVANZADO

### 5.1 Arquitectura de filtros

```
search/
├── filters/                      ← Componentes para cada filtro
│   ├── awardType/AwardType.jsx
│   ├── agency/Agency.jsx
│   ├── recipient/RecipientSearchContainer.jsx
│   ├── location/LocationSection.jsx
│   ├── keyword/Keyword.jsx
│   ├── naics/NAICSCheckboxTree.jsx
│   ├── psc/PSCCheckboxTreeContainer.jsx
│   ├── defc/DEFCheckboxTreeContainer.jsx (COVID)
│   ├── ExtentCompeted.jsx
│   ├── SetAside.jsx
│   └── PricingType.jsx
├── collapsibleSidebar/
│   ├── SidebarContentFilters.jsx
│   └── SidebarContentFilterAccordion.jsx
└── topFilterBar/
    ├── TopFilterBar.jsx          ← Display de filtros activos
    └── filterGroups/
        ├── LocationFilterGroup.jsx
        ├── RecipientFilterGroup.jsx
        └── [40+ más]
```

### 5.2 Componente genérico de búsqueda

```jsx
// AutocompleteWithCheckboxList - Patrón reutilizable
<AutocompleteWithCheckboxList
    filterType="Recipients"
    handleTextInputChange={handleTextInputChange}
    onSearchClear={handleSearchClear}
    onClearAll={handleClearAll}
    searchString={searchString}
    filters={recipientList}          // Opciones con label/value
    selectedFilters={selectedRecipients}
    toggleSingleFilter={toggleRecipient}
    toggleAll={toggleAll}
    noResults={noResults}
    errorMessage={errorMessage}
    isLoading={isLoading}
    limit={500} />

// Props esperadas en filters:
const filters = [
    {
        id: 'recipient_1',
        name: 'Company ABC Inc',
        label: 'Company ABC Inc (DUNS: 123456789)',
        children: []  // Si es jerárquico
    }
];
```

### 5.3 Filtro de búsqueda jerárquica (Checkbox Tree)

```jsx
// Patrón: Para filtros con múltiples niveles
<LegacyCheckboxTree
    data={hierarchicalData}
    isLoading={loading}
    isError={error}
    errorMessage="Error cargando datos"
    noResults={noResults}
    shouldExpandAll={expandAll}
    sortOrder="alphabetical"
    selectedNodes={selectedNodes}
    onNodeToggle={toggleNode}
    onBulkSelect={bulkSelectNodes}
    searchInput={searchString} />

// Data esperada:
[
    {
        label: 'Year 2024',
        value: '2024',
        children: [
            {
                label: 'Q1',
                value: 'Q1',
                count: 450,
                children: [...]
            }
        ]
    }
]
```

### 5.4 Filtro de rango

```jsx
// Patrón: Para montos, fechas, cantidades
<AwardAmountSearch />
// Internamente:
<input type="range" min="0" max="1000000000" step="1000000" />
<input type="text" placeholder="Min" value={minAmount} onChange={() => {...}} />
<input type="text" placeholder="Max" value={maxAmount} onChange={() => {...}} />
```

### 5.5 Filtro de ubicación (especial)

```jsx
// Componente multiníivel: País -> Estado -> Condado
<LocationSection />
├── Tabs: [Domestic, Foreign]
├── EntityDropdown (search + autocomplete)
└── Caché de selecciones previas en localStorage
```

### 5.6 Manejo de filtros en Redux

```jsx
// Container patrón: Conecta filter component a Redux
const CFDASearchContainer = () => {
    const [searchString, setSearchString] = useState('');
    const selectedCFDA = useSelector(state => state.filters.selectedCFDA);
    const dispatch = useDispatch();
    
    const toggleCFDA = useCallback((selection) => {
        dispatch(updateSelectedCFDA(selection));
    }, [dispatch]);
    
    const handleTextInputChange = (e) => {
        setSearchString(e.target.value);
        getCFDAFromSearchString(e.target.value);
    };
    
    return (
        <AutocompleteWithCheckboxList
            searchString={searchString}
            filters={autocompleteCFDA}
            selectedFilters={selectedCFDA}
            toggleSingleFilter={toggleCFDA}
            toggleAll={toggleAll}
        />
    );
};
```

### 5.7 Persistencia de filtros

```jsx
// Patrón: Guardar en URL + localStorage
export const generateUrlHash = (filters) => {
    // POST al backend que almacena y devuelve hash
};

// Recuperar:
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('hash')) {
    dispatch(restoreHashedFilters(urlParams.get('hash')));
}

// En Redux actions:
export const restoreHashedFilters = (hash) => (dispatch) => {
    apiRequest({
        url: `v2/search_filters/hash/${hash}/`
    }).then(res => {
        dispatch(setFilters(res.data.filters));
    });
};
```

### 5.8 Count/Validación de filtros

```jsx
// Patrón: Mostrar cantidad disponible por filtro
export const getFilterCount = (filters) => {
    
 const counts = {
        'Time Period': filters.timePeriodFY.size,
        'Location': filters.selectedLocations.size,
        'Agency': filters.selectedAwardingAgencies.size + 
                  filters.selectedFundingAgencies.size,
        'Award Type': excludeIDVBandNewFCodes(filters.awardType),
        'Recipient': filters.selectedRecipients.size,
        'Recipient Type': filters.recipientType.size,
        'NAICS': generateCount(filters.naicsCodes),
        'Assistance Listing': filters.selectedCFDA.size,
        'Extent Competed': filters.extentCompeted.size
    };
    
    const totalCount = Object.values(counts).reduce((a, b) => a + b, 0);
    return { counts, totalCount };
};

// Mostrar: "23 Active Filters:"
```

---

## 🎯 PATRONES CLAVE ADAPTABLES A URUGUAY

| Patrón | Uso en USAspending | Adaptación para CuántoCuestaUruguay |
|--------|-------------------|-------------------------------------|
| **Checkbox Tree** | Dominios (NAICS, PSC) | Clasificadores de gasto, ministerios |
| **Sankey Diagram** | Flujo presupuesto | Flujo de fondos público → privado |
| **Time Series** | Obligaciones por trimestre | Gasto trimestral por departamento |
| **Treemap** | Desglose por categoría | Desglose por sector + organismo |
| **API Wrapper** | axiós + cancelToken | Reutilización HTTP genérica |
| **Redux Filters** | Immutable.js Sets | State management consistente |
| **Paginación** | limit/page/sort | Eficiencia en grandes datasets |
| **Hash URL** | Persistencia filtros | Compartibilidad de análisis |

---

## 💡 RECOMENDACIONES PARA TU PROYECTO

### Stack recomendado (idéntico a USAspending)
```json
{
    "react": "^18.x",
    "redux": "^5.x",
    "react-redux": "^9.x",
    "recharts": "^2.x",
    "d3": "^7.x",
    "axios": "^1.x",
    "tailwindcss": "para estilos (tu preferencia)",
    "lodash-es": "para transformaciones"
}
```

### Jerarquía de carpetas propuesta
```
src/
├── components/
│   ├── shared/        ← Todos los reutilizables
│   ├── layouts/       ← PageWrapper, Sidebars
│   ├── filters/       ← Componentes filtrado
│   ├── charts/        ← Visualizaciones
│   └── pages/         ← Páginas completas
├── containers/        ← Redux connected
├── hooks/             ← Custom hooks (USAspending usa varios)
├── apis/              ← Endpoints como functions
├── redux/             ← Store, reducers, actions
├── helpers/           ← Utilidades (formatting, dates)
├── dataMapping/       ← Constantes (NO cambiar en runtime)
└── styles/            ← SCSS global + Tailwind
```

### Patrones a implementar desde inicio

1. **API Wrapper centralizado** (`helpers/apiRequest.js`)
   - Configuración global en un lugar
   - Cancel tokens para cleanup
   - Error handling estándar

2. **Modelos de datos** (`dataMapping/`)
   - Evita "magic strings" en componentes
   - Facilita cambios en fuente única

3. **Redux con Immutable.js**
   - Para Sets/Maps de filtros
   - Mais predictable que mutaciones

4. **Componentes "dumb" + Containers "smart"**
   - Componentes reutilizables sin lógica
   - Containers manejan estado y side effects

5. **PropTypes obligatorios**
   - Menos overhead que TypeScript
   - Validación en desarrollo adecuada

---

## 📚 Referencias en el código

- **Storybook**: https://fedspendingtransparency.github.io/usaspending-website/docs/
- **API Docs**: https://api.usaspending.gov/
- **GitHub**: https://github.com/fedspendingtransparency/usaspending-website
- **Live**: https://www.usaspending.gov/

