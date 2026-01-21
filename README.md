# 💰 ¿Cuánto Cuesta Uruguay?

Una aplicación web moderna para rastrear precios regulados y el costo de vida en Uruguay, con datos oficiales en tiempo real.

## 🌟 Características

- **Precios de Combustibles en Tiempo Real**: Integración con la API oficial de ANCAP a través de catalogodatos.gub.uy
- **Página de Inicio Responsiva**: Hero section moderno con gradientes y animaciones
- **Tarjetas de Precios**: Visualización clara y actualizada de precios de combustibles
- **Comparador de Precios**: Herramienta multi-selección para comparar productos
- **Gráficos Históricos**: Visualización de evolución de precios con Chart.js
- **Estadísticas**: Análisis de precios mínimos, máximos y promedios
- **Diseño Responsivo**: Optimizado para móviles, tablets y escritorio

## 🛠️ Stack Tecnológico

### Frontend (Actual)
- **HTML5**: Estructura semántica
- **CSS3**: Estilos personalizados y animaciones
- **Tailwind CSS**: Framework de utilidades CSS via CDN
- **JavaScript Vanilla**: Lógica de aplicación sin frameworks
- **Chart.js**: Visualización de datos con gráficos interactivos

### Backend (Futuro)
- **Python FastAPI**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos relacional
- **SQLAlchemy**: ORM para Python

## 📊 Fuentes de Datos

- **catalogodatos.gub.uy**: Portal de datos abiertos del gobierno uruguayo
- **ANCAP**: Precios oficiales de combustibles
- **CKAN API**: Interface para acceso a datos estructurados

## 🚀 Uso

### Desarrollo Local

1. Clona el repositorio:
```bash
git clone https://github.com/manusabbath-arch/cuantocuestauruguay.git
cd cuantocuestauruguay
```

2. Abre el archivo `index.html` en tu navegador web:
```bash
# En Linux/Mac
open index.html

# En Windows
start index.html

# O usa un servidor local
python -m http.server 8000
# Luego abre http://localhost:8000
```

### Estructura de Archivos

```
cuantocuestauruguay/
├── index.html          # Página principal con todas las secciones
├── app.js             # Lógica de la aplicación y API calls
└── README.md          # Documentación del proyecto
```

## 📱 Secciones de la Aplicación

### 1. Hero Section
Página de inicio con gradiente atractivo, título destacado y botones de acción.

### 2. Precios de Combustibles
- Tarjetas interactivas con precios actualizados
- Estados de carga y error
- Iconos personalizados por tipo de combustible
- Animaciones suaves

### 3. Comparador de Precios
- Multi-selección de productos
- Gráfico de barras comparativo
- Tabla detallada de comparación
- Actualización en tiempo real

### 4. Análisis Histórico
- Selector de producto individual
- Gráfico de líneas con evolución temporal
- Estadísticas: precio actual, mínimo, máximo y promedio
- Visualización de tendencias

## 🔧 Configuración de la API

La aplicación se conecta automáticamente a:

```javascript
const CKAN_API_BASE = 'https://catalogodatos.gub.uy/api/3/action';
const ANCAP_DATASET_ID = 'precio-de-los-combustibles';
```

Si la API no está disponible, la aplicación utiliza datos de ejemplo para demostración.

## 🎨 Personalización

### Colores
Los colores principales se pueden modificar en el archivo `index.html`:
- Gradiente principal: `#667eea` → `#764ba2`
- Color de acento: Indigo (Tailwind)

### Animaciones
Las animaciones CSS están definidas en el `<style>` del HTML:
- `fadeIn`: Entrada suave de elementos
- `skeleton`: Efecto de carga
- `card-hover`: Hover en tarjetas

## 🌐 Navegación

- **Inicio**: Hero section con información general
- **Precios**: Tarjetas de precios de combustibles
- **Comparar**: Herramienta de comparación multi-producto
- **Histórico**: Análisis de evolución temporal

## 📈 Próximas Funcionalidades

- [ ] Backend con FastAPI
- [ ] Base de datos PostgreSQL
- [ ] Almacenamiento de datos históricos reales
- [ ] Autenticación de usuarios
- [ ] Alertas de cambios de precio
- [ ] Más categorías de productos (alimentos, servicios, etc.)
- [ ] API RESTful propia
- [ ] Dashboard administrativo
- [ ] Exportación de datos (CSV, PDF)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo una licencia de código abierto. Los datos provienen de fuentes oficiales del gobierno uruguayo.

## 👥 Autor

**manusabbath-arch**

## 🙏 Agradecimientos

- Gobierno de Uruguay por proporcionar datos abiertos
- ANCAP por datos de combustibles
- Comunidad de desarrolladores uruguayos

---

**Nota**: Esta es una aplicación de demostración educativa. Los precios mostrados pueden no reflejar los valores actuales del mercado. Siempre verifica los precios oficiales en las fuentes gubernamentales.