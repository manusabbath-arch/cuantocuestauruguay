# Utilities ETL Module - Implementation Guide

This document describes the new utilities ETL module that expands PreciosRegulados.uy beyond combustibles to include public services data.

## Overview

The utilities ETL module (`backend/app/etl/utilities.py`) extracts, transforms, and loads data for:

- **UTE** - Electricity tariffs from URSEA
- **OSE** - Water and sanitation rates from URSEA
- **Antel** - Telecommunications plans (fiber optic, mobile)

## Data Sources

### Primary Sources
- **URSEA** (Unidad Reguladora de Servicios de Energía y Agua)
  - UTE Tariffs: https://www.ursea.gub.uy/inicio/energia-electrica/tarifas/
  - OSE Tariffs: https://www.ursea.gub.uy/inicio/agua-y-saneamiento/tarifas/

- **Antel Official Website**
  - Plans: https://www.antel.com.uy/personas/internet/planes

### Complementary Sources
- **SAG Ingeniería** (https://www.sag.com.uy) - Analysis and cross-reference data

## Products Tracked

### UTE (Electricidad)
- `UTE_RESIDENCIAL_BT1` - Tarifa Residencial BT1
- `UTE_RESIDENCIAL_BT2` - Tarifa Residencial BT2
- `UTE_GENERAL_BT3` - Tarifa General BT3
- `UTE_INDUSTRIAL` - Tarifa Industrial

Unit: $/kWh

### OSE (Agua)
- `OSE_RESIDENCIAL` - Tarifa Residencial
- `OSE_COMERCIAL` - Tarifa Comercial

Unit: $/m³

### Antel (Telecomunicaciones)
- `ANTEL_FIBRA_100` - Fibra Óptica 100 Mbps
- `ANTEL_FIBRA_200` - Fibra Óptica 200 Mbps
- `ANTEL_FIBRA_500` - Fibra Óptica 500 Mbps
- `ANTEL_MOVIL` - Plan Móvil

Unit: $/mes

## API Endpoints

### Run Specific Service ETL
```bash
POST /api/v1/etl/utilities/run?service=ute
POST /api/v1/etl/utilities/run?service=ose
POST /api/v1/etl/utilities/run?service=antel
```

### Run All Utilities ETL
```bash
POST /api/v1/etl/utilities/run
```

### Run All ETL (Combustibles + Utilities)
```bash
POST /api/v1/etl/run-all
```

## Usage Examples

### Manual Execution via API

```bash
# Run UTE ETL
curl -X POST http://localhost:8000/api/v1/etl/utilities/run?service=ute

# Run all utilities
curl -X POST http://localhost:8000/api/v1/etl/utilities/run

# Run everything
curl -X POST http://localhost:8000/api/v1/etl/run-all
```

### Python Usage

```python
from app.etl.utilities import UtilitiesETL
from app.core.database import SessionLocal

db = SessionLocal()
etl = UtilitiesETL(db)

# Run individual service
result_ute = await etl.run_ute()
result_ose = await etl.run_ose()
result_antel = await etl.run_antel()

# Run all
result_all = await etl.run_all()

db.close()
```

## Automated Scheduling

The utilities ETL runs automatically every day:
- **2:00 AM** - Combustibles ETL
- **2:30 AM** - Utilities ETL (UTE, OSE, Antel)

Configure timing in `.env`:
```
ETL_SCHEDULE_HOUR=2
ETL_SCHEDULE_MINUTE=0
```

## PDF Processing

The module is prepared to extract data from URSEA PDF documents using:

- **PyPDF2** - Basic PDF text extraction
- **pdfplumber** - Advanced table extraction
- **tabula-py** - Table data parsing

### Example PDF Extraction (To Implement)

```python
import pdfplumber
import pandas as pd

async def extract_ute_from_pdf(pdf_url: str):
    """Extract UTE tariffs from URSEA PDF"""
    response = requests.get(pdf_url)
    
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        first_page = pdf.pages[0]
        tables = first_page.extract_tables()
        
        # Process tables into DataFrame
        df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
        return df
```

## Web Scraping

For Antel and other web-based sources, use BeautifulSoup4:

```python
from bs4 import BeautifulSoup
import requests

async def scrape_antel_plans():
    """Scrape Antel plans from website"""
    response = requests.get(ANTEL_TARIFAS_URL)
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Extract plan data
    plans = soup.find_all('div', class_='plan-card')
    
    data = []
    for plan in plans:
        price = plan.find('span', class_='price').text
        speed = plan.find('span', class_='speed').text
        data.append({'speed': speed, 'price': price})
    
    return pd.DataFrame(data)
```

## Sample Data

Currently, the module uses sample data for testing. To enable real data extraction:

1. Implement the actual scraping/PDF extraction in:
   - `extract_ute_tarifas()`
   - `extract_ose_tarifas()`
   - `extract_antel_tarifas()`

2. Remove or update the `_get_sample_*_data()` methods

3. Test thoroughly with real data sources

## Testing

Run the utilities ETL tests:

```bash
cd backend
pytest tests/test_utilities_etl.py -v
```

Test coverage includes:
- Data extraction for each service
- Full ETL process
- Product creation
- Database integration

## Database Schema

Products are automatically created with appropriate categories:

- **Category**: `electricidad`, `agua`, `telecomunicaciones`
- **Unit**: `kWh`, `m³`, `mes`
- **Active**: `True` by default

## Error Handling

The ETL includes comprehensive error handling:

- Failed extractions don't stop other services
- Detailed logging for debugging
- Graceful degradation with sample data
- Database rollback on errors

## Future Enhancements

### Immediate (TODO)
- [ ] Implement real PDF extraction for UTE/OSE
- [ ] Implement web scraping for Antel
- [ ] Add historical data backfilling
- [ ] Implement data validation rules

### Medium-term
- [ ] Add more UTE tariff types
- [ ] Include OSE consumption tiers
- [ ] Track Antel promotional offers
- [ ] Cross-reference with SAG data

### Long-term
- [ ] Add other utilities (gas, garbage collection)
- [ ] Implement anomaly detection
- [ ] Add predictive price forecasting
- [ ] Regional price variations

## Configuration

Add to `.env`:

```bash
# Utilities Data Sources
URSEA_UTE_URL=https://www.ursea.gub.uy/inicio/energia-electrica/tarifas/
URSEA_OSE_URL=https://www.ursea.gub.uy/inicio/agua-y-saneamiento/tarifas/
ANTEL_TARIFAS_URL=https://www.antel.com.uy/personas/internet/planes
SAG_URL=https://www.sag.com.uy
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/manusabbath-arch/cuantocuestauruguay/issues
- Documentation: See README.md and API docs at `/docs`

## License

MIT License - See LICENSE file for details
