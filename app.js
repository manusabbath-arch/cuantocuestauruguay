// Global state
let fuelData = [];
let comparisonChart = null;
let historicalChart = null;

// ANCAP API Configuration
const CKAN_API_BASE = 'https://catalogodatos.gub.uy/api/3/action';
const ANCAP_DATASET_ID = 'precio-de-los-combustibles';

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando aplicación...');
    loadFuelPrices();
    initializeCharts();
});

// Fetch fuel prices from ANCAP via CKAN API
async function loadFuelPrices() {
    console.log('📡 Cargando precios de combustibles...');
    
    const loadingDiv = document.getElementById('loading-prices');
    const errorDiv = document.getElementById('error-prices');
    const pricesDiv = document.getElementById('fuel-prices');
    
    loadingDiv.classList.remove('hidden');
    errorDiv.classList.add('hidden');
    pricesDiv.classList.add('hidden');
    
    try {
        // First, get dataset metadata to find the resource
        const datasetResponse = await fetch(`${CKAN_API_BASE}/package_show?id=${ANCAP_DATASET_ID}`);
        const datasetData = await datasetResponse.json();
        
        if (!datasetData.success) {
            throw new Error('No se pudo obtener información del dataset');
        }
        
        // Get the first CSV resource
        const resources = datasetData.result.resources;
        const csvResource = resources.find(r => r.format === 'CSV' || r.format === 'csv');
        
        if (!csvResource) {
            throw new Error('No se encontró recurso CSV en el dataset');
        }
        
        console.log('📦 Recurso encontrado:', csvResource.name);
        
        // Fetch the actual data using datastore_search
        const dataResponse = await fetch(`${CKAN_API_BASE}/datastore_search?resource_id=${csvResource.id}&limit=100`);
        const data = await dataResponse.json();
        
        if (!data.success) {
            throw new Error('No se pudieron obtener los datos');
        }
        
        fuelData = data.result.records;
        console.log('✅ Datos cargados:', fuelData.length, 'registros');
        
        // Process and display fuel prices
        displayFuelPrices(fuelData);
        
        // Initialize comparison tool
        initializeComparison(fuelData);
        
        // Initialize historical data
        initializeHistorical(fuelData);
        
        loadingDiv.classList.add('hidden');
        pricesDiv.classList.remove('hidden');
        
    } catch (error) {
        console.error('❌ Error cargando precios:', error);
        loadingDiv.classList.add('hidden');
        errorDiv.classList.remove('hidden');
        document.getElementById('error-message').textContent = error.message;
        
        // Use mock data for demonstration
        console.log('🔄 Usando datos de ejemplo...');
        useMockData();
    }
}

// Use mock data if API fails
function useMockData() {
    const mockData = [
        { producto: 'Gasolina Super 95', precio: '72.50', unidad: '$/litro', fecha: '2026-01-15' },
        { producto: 'Gasolina Premium 97', precio: '79.30', unidad: '$/litro', fecha: '2026-01-15' },
        { producto: 'Gasoil', precio: '56.80', unidad: '$/litro', fecha: '2026-01-15' },
        { producto: 'Gasoil Premium', precio: '62.40', unidad: '$/litro', fecha: '2026-01-15' },
        { producto: 'Supergas', precio: '48.20', unidad: '$/litro', fecha: '2026-01-15' },
        { producto: 'GNC', precio: '38.90', unidad: '$/m³', fecha: '2026-01-15' }
    ];
    
    fuelData = mockData;
    
    displayFuelPrices(mockData);
    initializeComparison(mockData);
    initializeHistorical(mockData);
    
    document.getElementById('loading-prices').classList.add('hidden');
    document.getElementById('fuel-prices').classList.remove('hidden');
}

// Display fuel price cards
function displayFuelPrices(data) {
    const container = document.getElementById('fuel-prices');
    container.innerHTML = '';
    
    // Get unique products (latest prices)
    const products = getLatestPrices(data);
    
    products.forEach((item, index) => {
        const card = createFuelCard(item, index);
        container.appendChild(card);
    });
}

// Get latest prices for each product
function getLatestPrices(data) {
    const productMap = new Map();
    
    data.forEach(item => {
        const productName = item.producto || item.Producto || item.PRODUCTO || 'Producto';
        const price = item.precio || item.Precio || item.PRECIO || item.price || '0';
        const unit = item.unidad || item.Unidad || item.UNIDAD || item.unit || '$/litro';
        const date = item.fecha || item.Fecha || item.FECHA || item.date || new Date().toISOString();
        
        if (!productMap.has(productName)) {
            productMap.set(productName, {
                producto: productName,
                precio: parseFloat(price),
                unidad: unit,
                fecha: date
            });
        }
    });
    
    return Array.from(productMap.values());
}

// Create fuel price card
function createFuelCard(item, index) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md p-6 card-hover fade-in';
    card.style.animationDelay = `${index * 0.1}s`;
    
    const icon = getFuelIcon(item.producto);
    
    card.innerHTML = `
        <div class="flex items-center justify-between mb-4">
            <div class="text-3xl">${icon}</div>
            <span class="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">Actualizado</span>
        </div>
        <h4 class="text-lg font-semibold text-gray-900 mb-2">${item.producto}</h4>
        <div class="flex items-baseline justify-between">
            <div>
                <span class="text-3xl font-bold text-indigo-600">$${item.precio.toFixed(2)}</span>
                <span class="text-sm text-gray-500 ml-2">${item.unidad}</span>
            </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-200">
            <button onclick="showProductDetail('${item.producto}')" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                Ver detalles →
            </button>
        </div>
    `;
    
    return card;
}

// Get appropriate icon for fuel type
function getFuelIcon(productName) {
    const name = productName.toLowerCase();
    if (name.includes('gasolina') || name.includes('nafta')) return '⛽';
    if (name.includes('gasoil') || name.includes('diesel')) return '🚛';
    if (name.includes('gas') || name.includes('gnc')) return '🔥';
    if (name.includes('super')) return '🚗';
    return '⛽';
}

// Initialize comparison tool
function initializeComparison(data) {
    const products = getLatestPrices(data);
    const selector = document.getElementById('product-selector');
    selector.innerHTML = '';
    
    products.forEach((item, index) => {
        const checkbox = document.createElement('div');
        checkbox.className = 'flex items-center';
        checkbox.innerHTML = `
            <input type="checkbox" id="product-${index}" value="${item.producto}" 
                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                   onchange="updateComparison()">
            <label for="product-${index}" class="ml-2 text-sm text-gray-700">
                ${item.producto}
            </label>
        `;
        selector.appendChild(checkbox);
    });
}

// Update comparison chart and table
function updateComparison() {
    const checkboxes = document.querySelectorAll('#product-selector input[type="checkbox"]:checked');
    const selectedProducts = Array.from(checkboxes).map(cb => cb.value);
    
    if (selectedProducts.length === 0) {
        document.getElementById('comparison-table-container').classList.add('hidden');
        if (comparisonChart) {
            comparisonChart.data.labels = [];
            comparisonChart.data.datasets[0].data = [];
            comparisonChart.update();
        }
        return;
    }
    
    const products = getLatestPrices(fuelData);
    const selectedData = products.filter(p => selectedProducts.includes(p.producto));
    
    // Update chart
    const labels = selectedData.map(p => p.producto);
    const prices = selectedData.map(p => p.precio);
    
    if (comparisonChart) {
        comparisonChart.data.labels = labels;
        comparisonChart.data.datasets[0].data = prices;
        comparisonChart.update();
    }
    
    // Update table
    const tableBody = document.getElementById('comparison-table');
    tableBody.innerHTML = '';
    
    selectedData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item.producto}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">$${item.precio.toFixed(2)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.unidad}</td>
        `;
        tableBody.appendChild(row);
    });
    
    document.getElementById('comparison-table-container').classList.remove('hidden');
}

// Initialize historical data selector
function initializeHistorical(data) {
    const products = getLatestPrices(data);
    const selector = document.getElementById('historical-product-selector');
    selector.innerHTML = '<option value="">Selecciona un producto...</option>';
    
    products.forEach(item => {
        const option = document.createElement('option');
        option.value = item.producto;
        option.textContent = item.producto;
        selector.appendChild(option);
    });
    
    selector.addEventListener('change', function() {
        if (this.value) {
            updateHistoricalChart(this.value);
        }
    });
}

// Update historical chart
function updateHistoricalChart(productName) {
    // Generate mock historical data (6 months)
    const historicalData = generateHistoricalData(productName);
    
    if (historicalChart) {
        historicalChart.data.labels = historicalData.labels;
        historicalChart.data.datasets[0].data = historicalData.prices;
        historicalChart.update();
    }
    
    // Update statistics
    const prices = historicalData.prices;
    const currentPrice = prices[prices.length - 1];
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
    
    document.getElementById('stat-current').textContent = `$${currentPrice.toFixed(2)}`;
    document.getElementById('stat-min').textContent = `$${minPrice.toFixed(2)}`;
    document.getElementById('stat-max').textContent = `$${maxPrice.toFixed(2)}`;
    document.getElementById('stat-avg').textContent = `$${avgPrice.toFixed(2)}`;
    
    document.getElementById('statistics').classList.remove('hidden');
}

// Generate mock historical data
function generateHistoricalData(productName) {
    const products = getLatestPrices(fuelData);
    const product = products.find(p => p.producto === productName);
    const basePrice = product ? product.precio : 50;
    
    const labels = [];
    const prices = [];
    const months = ['Ago', 'Sep', 'Oct', 'Nov', 'Dic', 'Ene'];
    
    for (let i = 0; i < 6; i++) {
        labels.push(months[i]);
        // Generate realistic price variation (±5%)
        const variation = (Math.random() - 0.5) * 0.1;
        const price = basePrice * (1 + variation);
        prices.push(parseFloat(price.toFixed(2)));
    }
    
    return { labels, prices };
}

// Initialize Chart.js charts
function initializeCharts() {
    // Comparison Chart
    const comparisonCtx = document.getElementById('comparison-chart').getContext('2d');
    comparisonChart = new Chart(comparisonCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Precio ($/unidad)',
                data: [],
                backgroundColor: 'rgba(99, 102, 241, 0.8)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Comparación de Precios'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
    
    // Historical Chart
    const historicalCtx = document.getElementById('historical-chart').getContext('2d');
    historicalChart = new Chart(historicalCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Precio',
                data: [],
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Evolución Histórica de Precios'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

// Show product detail (placeholder for future implementation)
function showProductDetail(productName) {
    const products = getLatestPrices(fuelData);
    const product = products.find(p => p.producto === productName);
    
    if (product) {
        alert(`Detalles de ${productName}\n\nPrecio: $${product.precio.toFixed(2)} ${product.unidad}\n\nEn una versión futura, aquí se mostrará información detallada del producto incluyendo su historial completo, estadísticas y comparaciones.`);
    }
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

console.log('✅ Aplicación inicializada');
