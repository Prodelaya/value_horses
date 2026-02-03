# Plan de Scraping - ChileSharp

## Índice

- [Parte A: Versus.es (Soft)](#parte-a-versuses-soft)
- [Parte B: Teletrak.cl (Sharp)](#parte-b-teletrakcel-sharp)
- [Parte C: Matching de Carreras](#parte-c-matching-de-carreras)

---

## Resumen Ejecutivo

Este documento detalla la estrategia de scraping para obtener las cuotas de carreras de caballos chilenas desde ambas fuentes:

| Fuente | Rol | Datos Objetivo |
|--------|-----|----------------|
| **Versus.es** | Soft (explotación) | Cuotas fijas WIN |
| **Teletrak.cl** | Sharp (referencia) | Cuotas de pool Prob |

**Prioridad crítica**: Mínima latencia entre scraping → cálculo → alerta.

---

# Parte A: Versus.es (Soft)

## A.1 Estructura de URLs

### A.1.1 URLs Identificadas

| Tipo | URL Pattern | Propósito |
|------|-------------|-----------|
| Carreras de Hoy | `/apuestas/sports/horse_racing/meetings/today` | Lista de meetings del día |
| Carreras de Mañana | `/apuestas/sports/horse_racing/meetings/tomorrow` | Lista de meetings de mañana |
| Detalle de Carrera | `/apuestas/sports/horse_racing/meetings/{meeting_id}/races/{race_id}` | Cuotas individuales |

### A.1.2 Ejemplos Reales

```
https://www.versus.es/apuestas/sports/horse_racing/meetings/today
https://www.versus.es/apuestas/sports/horse_racing/meetings/tomorrow
https://www.versus.es/apuestas/sports/horse_racing/meetings/340357/races/25929231
https://www.versus.es/apuestas/sports/horse_racing/meetings/340357/races/25929233
```

---

## A.2 Estructura de Páginas

### A.2.1 Página de Meetings (today/tomorrow)

**Contenido visible:**
- Agrupación por país (Chilean Horse Racing, Irlanda, Italia, etc.)
- Nombre del hipódromo/meeting (ej: Concepcion, Club Hipico)
- Condición de pista (ej: "Tipo pista: FAST")
- Grid de botones con horarios de cada carrera

**Identificación de Carreras Chilenas:**

> ⚠️ **IMPORTANTE**: No filtrar solo por texto "Chilean Horse Racing". 
> Versus puede mostrar carreras chilenas con diferentes etiquetas.
> **Usar la bandera de Chile para identificar:**

```html
<img src="https://sportswidget-cdn.versus.es/images/country-flags/chile.svg" 
     alt="Bandera de Chile" 
     class="ta-Image-img_tag">
```

**Selector recomendado:**
```python
# Buscar por imagen de bandera chilena
chile_flags = await page.query_selector_all('img[src*="chile.svg"]')
# Navegar al padre para obtener el meeting completo
```

**Elementos DOM clave:**
- Botones de carrera: `.ta-RaceMeetingCoupon-raceButton`
- IDs embebidos en clases: `ta-{race_id}`

**Características técnicas:**
- ⚠️ **SPA (Single Page Application)**: Contenido dinámico cargado por JavaScript
- ⚠️ **IDs no visibles directamente**: Los meeting_id y race_id se manejan via eventos JS
- ✅ **No requiere autenticación**: Datos públicamente accesibles

### A.2.2 Página de Detalle de Carrera

**Contenido visible:**
- Header: Nombre del hipódromo, hora, distancia, superficie
- Selector de carreras: Navegación horizontal entre carreras del mismo meeting
- Tabs de mercados: "Ganador o colocado", "Gemela"
- Tabla de participantes con cuotas

**Datos por caballo (solo necesarios):**
| Campo | Ubicación | Selector estimado |
|-------|-----------|-------------------|
| Dorsal | Columna izquierda | `.ta-SelectionButtonView` area |
| Nombre | Centro de fila | Texto del participante |
| Cuota WIN | Botón derecho | `.ta-SelectionButtonView` |

**Elementos DOM clave:**
- Botones de cuotas: `.ta-SelectionButtonView`
- Selector de carrera: `.ta-MenuRowItem`
- Tabs de mercado: `.ta-MenuItem`

---

## A.3 Estrategia de Scraping Versus

### A.3.1 Flujo General

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE SCRAPING VERSUS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  DISCOVERY  │────▶│   FILTER    │────▶│   POLLING   │           │
│  │ (1x/día AM) │     │   CHILE     │     │ (cada 15-20s)│           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                  │                  │
│  Obtener lista       Filtrar por                Scrapear cuotas    │
│  de meetings         bandera Chile              de carreras en     │
│  del día             (chile.svg)                ventana activa     │
│                                                  │                  │
│                                                  ▼                  │
│                                          ┌─────────────┐           │
│                                          │    STORE    │           │
│                                          │   (BD/RAM)  │           │
│                                          └─────────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### A.3.2 Fase 1: Discovery (Descubrimiento)

**Frecuencia**: 1 vez al día (mañana, antes de primera carrera)

**Objetivo**: Obtener lista de meetings y races chilenas del día

**Pasos**:
1. Navegar a `/meetings/today`
2. Esperar carga completa del DOM (2-3 segundos)
3. Buscar todas las imágenes con `src*="chile.svg"`
4. Por cada bandera, navegar al contenedor padre para obtener meeting info
5. Extraer meeting_id y race_ids de los botones de carrera
6. Guardar en BD con normalización de nombre de track

**Técnica recomendada**: Playwright (contenido JS-heavy)

### A.3.3 Fase 2: Polling de Cuotas

**Frecuencia**: Cada 15-20 segundos durante ventana activa

**Ventana activa**: T-10 a T-1 minutos antes de cada carrera

**Objetivo**: Capturar snapshots de cuotas para cálculo de value

**Pasos**:
1. Identificar carreras en ventana activa
2. Navegar directamente a URL de carrera: `/meetings/{meeting_id}/races/{race_id}`
3. Esperar carga de cuotas (1-2 segundos)
4. Extraer por cada caballo:
   - Dorsal (saddle_number)
   - Nombre
   - Cuota WIN decimal
5. Guardar snapshot en `odds_snapshots` con `bookmaker_id = VERSUS`
6. Trigger inmediato al engine de value detection

---

## A.4 Implementación Técnica Versus

### A.4.1 Herramienta Recomendada

| Opción | Pros | Contras |
|--------|------|---------|
| **Playwright** ✅ | Maneja JS/SPA, headless, robusto | Mayor consumo recursos |
| Requests + BS4 | Ligero, rápido | No ejecuta JS, fallará |
| Selenium | Conocido, robusto | Más lento que Playwright |

**Decisión**: **Playwright** es obligatorio dado que Versus es una SPA.

### A.4.2 Optimizaciones para Latencia

```python
# Estrategias de mínima latencia

# 1. Browser persistente (no crear/cerrar por cada request)
browser = await playwright.chromium.launch(headless=True)
context = await browser.new_context()

# 2. Caché de páginas abiertas por carrera
open_pages = {}  # race_id -> Page

# 3. Navegación directa (skip discovery en polling)
page.goto(f"/meetings/{meeting_id}/races/{race_id}")

# 4. Wait específico solo para cuotas
await page.wait_for_selector('.ta-SelectionButtonView')

# 5. Extracción paralela de múltiples carreras
await asyncio.gather(*[scrape_race(r) for r in active_races])
```

### A.4.3 Extracción de Datos

```python
# Pseudocódigo de extracción
async def extract_versus_odds(page) -> list[dict]:
    """
    Extrae cuotas de la página de carrera de Versus.
    
    Returns:
        Lista de {saddle_number, name, odds_decimal}
    """
    runners = []
    
    # Esperar a que carguen las cuotas
    await page.wait_for_selector('.ta-SelectionButtonView')
    
    # Extraer cada participante
    # NOTA: Selectores exactos a confirmar tras pruebas
    participant_rows = await page.query_selector_all('[data-participant-row]')
    
    for row in participant_rows:
        saddle = await row.query_selector('.saddle-number')
        name = await row.query_selector('.horse-name')
        odds_btn = await row.query_selector('.ta-SelectionButtonView')
        
        runners.append({
            'saddle_number': int(await saddle.inner_text()),
            'name': await name.inner_text(),
            'odds_decimal': float(await odds_btn.inner_text())
        })
    
    return runners
```

### A.4.4 Intercepción de API (Alternativa Avanzada)

Versus probablemente hace llamadas XHR/Fetch a su backend. Interceptar estas llamadas puede ser más eficiente:

```python
# Interceptar llamadas de red para obtener JSON directamente
async def intercept_api(page):
    responses = []
    
    async def handle_response(response):
        if 'api' in response.url and 'race' in response.url:
            data = await response.json()
            responses.append(data)
    
    page.on('response', handle_response)
    await page.goto(race_url)
    
    return responses
```

**Ventaja**: JSON estructurado, sin parseo de DOM
**Riesgo**: Endpoint puede cambiar sin aviso

---

# Parte B: Teletrak.cl (Sharp)

## B.1 Estructura de URLs

### B.1.1 URLs Identificadas

| Tipo | URL Pattern | Propósito |
|------|-------------|-----------|
| Página Principal | `/wager` | Lista de meetings y carreras del día |
| Carrera Específica | `/wager?raceCardId={raceCardId}&raceId={raceId}` | Cuotas de una carrera |

### B.1.2 Ejemplos Reales

```
https://apuestas.teletrak.cl/wager
https://apuestas.teletrak.cl/wager?raceCardId=302839&raceId=2200648
```

### B.1.3 Parámetros de URL

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `raceCardId` | ID del meeting/jornada | 302839 |
| `raceId` | ID de la carrera específica | 2200648 |

---

## B.2 Estructura de la Página

### B.2.1 Componentes Principales

```
┌────────────────────────────────────────────────────────────────────┐
│                         TELETRAK WAGER                              │
├──────────────────┬─────────────────────────────────────────────────┤
│                  │                                                  │
│   SIDEBAR        │              CONTENIDO PRINCIPAL                │
│   (Jornadas)     │                                                  │
│                  │  ┌─────────────────────────────────────────┐    │
│  ┌────────────┐  │  │  HEADER: Nombre meeting + Live signal   │    │
│  │ 1. UK      │  │  └─────────────────────────────────────────┘    │
│  │ 🇬🇧        │  │                                                  │
│  ├────────────┤  │  ┌─────────────────────────────────────────┐    │
│  │ Concepción │  │  │  TABS: [1] [2] [3] [4] [5] ... carreras │    │
│  │ 🇨🇱        │  │  └─────────────────────────────────────────┘    │
│  ├────────────┤  │                                                  │
│  │ Hipódromo  │  │  ┌─────────────────────────────────────────┐    │
│  │ Chile 🇨🇱  │  │  │  VIEWS: Apuesta | Programa | Probables  │    │
│  └────────────┘  │  └─────────────────────────────────────────┘    │
│                  │                                                  │
│                  │  ┌─────────────────────────────────────────┐    │
│                  │  │           TABLA DE CABALLOS             │    │
│                  │  │  No. | Caballo | PP | ... | Prob | ...  │    │
│                  │  │   1  | Ferrata |  3 | ... | 6,0  | ...  │    │
│                  │  │   2  | Storm   |  1 | ... | 2,7  | ...  │    │
│                  │  └─────────────────────────────────────────┘    │
│                  │                                                  │
└──────────────────┴─────────────────────────────────────────────────┘
```

### B.2.2 Sidebar - Lista de Jornadas

**Contenido visible:**
- Lista de meetings activos del día
- Nombre del hipódromo
- Bandera del país (identificador clave para Chile)
- Número de carrera actual
- Pool total
- Hora de próxima carrera (MTP)

**Identificación de Carreras Chilenas:**

> ⚠️ **IMPORTANTE**: Filtrar por bandera chilena usando la clase CSS

```html
<div class="icon-flag flag sprite default-flag_small cl-flag"></div>
```

**Selector CSS para bandera chilena:**
```css
.cl-flag
```

**Elementos DOM del sidebar:**
```css
/* Fila de meeting */
.upcoming-row.event-row

/* Nombre del hipódromo */
h4.event-row-event-name

/* O el texto truncado */
h4.event-row-event-name .truncate-text

/* Número de carrera */
h3.race-number-cell

/* Pool total */
h3.pool-amount-cell .currency,
.currency.pools-total__currency /* Selector alternativo en detalle */

/* Hora */
h3.mtp-cell
```

**Ejemplo de nombres de track en Teletrak:**
- `Club Hípico De Concepción`
- `01. Hipódromo Chile`
- `Club Hípico de Santiago`

### B.2.3 Tabla de Caballos

**Columnas relevantes:**

| Columna | Contenido | Selector |
|---------|-----------|----------|
| No. | Número de dorsal | Primera columna numérica |
| Caballo | Nombre del caballo | `h2` dentro de la fila |
| **Prob** | Cuota decimal del pool | Columna "Prob" (9ª posición) |

**Características del campo Prob:**
- Formato: Decimal con coma como separador (`6,0` no `6.0`)
- Puede incluir etiqueta "FAV" para el favorito
- Representa la cuota del pool parimutuel

**Conversión de formato:**
```python
def parse_teletrak_odds(odds_str: str) -> float:
    """
    Convierte cuota de Teletrak a decimal.
    
    Args:
        odds_str: "6,0" o "2,7 FAV"
    
    Returns:
        float: 6.0 o 2.7
    """
    # Quitar "FAV" si existe
    clean = odds_str.replace('FAV', '').strip()
    # Reemplazar coma por punto
    return float(clean.replace(',', '.'))
```

### B.2.4 Navegación entre Carreras

**Tabs de carrera:**
- Números 1, 2, 3... en la parte superior
- Clase: `.races-switch-tab`
- Clic cambia la carrera sin recargar página

**Views/Pestañas:**
- "Apuesta" (default) - Contiene columna Prob ✅
- "Programa de carreras" - Información de forma
- "Probables" - Proyecciones (no usar)

---

## B.3 Estrategia de Scraping Teletrak

### B.3.1 Flujo General

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE SCRAPING TELETRAK                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  DISCOVERY  │────▶│   FILTER    │────▶│   POLLING   │           │
│  │ (1x/día AM) │     │  .cl-flag   │     │ (cada 10-15s)│           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                  │                  │
│  Navegar a         Filtrar meetings             Scrapear cuotas    │
│  /wager            con bandera                  Prob en tab        │
│                    chilena                      "Apuesta"          │
│                                                  │                  │
│                                                  ▼                  │
│                                          ┌─────────────┐           │
│                                          │    STORE    │           │
│                                          │   (BD/RAM)  │           │
│                                          └─────────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### B.3.2 Fase 1: Discovery (Descubrimiento)

**Frecuencia**: 1 vez al día (mañana, hora Chile ~10:00 CLT)

**Objetivo**: Obtener lista de meetings chilenos y sus raceCardId/raceId

**Pasos**:
1. Navegar a `https://apuestas.teletrak.cl/wager`
2. Esperar carga completa del sidebar (2-3 segundos)
3. Buscar todos los meetings con `.cl-flag` (bandera chilena)
4. Por cada meeting chileno:
   - Extraer nombre del hipódromo
   - Hacer clic para cargar sus carreras
   - Capturar raceCardId de la URL
   - Iterar por tabs de carrera para obtener cada raceId
5. Normalizar nombre de track usando tabla `track_aliases`
6. Guardar en BD: `meetings`, `races`, `external_ids`

**Extracción de IDs de URL:**
```python
def extract_teletrak_ids(url: str) -> tuple[str, str]:
    """
    Extrae raceCardId y raceId de la URL de Teletrak.
    
    Args:
        url: "https://apuestas.teletrak.cl/wager?raceCardId=302839&raceId=2200648"
    
    Returns:
        tuple: ("302839", "2200648")
    """
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('raceCardId', [None])[0], params.get('raceId', [None])[0]
```

### B.3.3 Fase 2: Polling de Cuotas

**Frecuencia**: Cada 10-15 segundos durante ventana activa

**Ventana activa**: T-10 a T-1 minutos antes de cada carrera

**Objetivo**: Capturar snapshots de cuotas Prob para cálculo de p_fair

**Pasos**:
1. Identificar carreras en ventana activa (query a BD)
2. Navegar directamente a URL: `/wager?raceCardId={id}&raceId={id}`
3. Esperar carga de tabla de caballos
4. Asegurar estar en tab "Apuesta" (default)
5. Extraer por cada caballo:
   - Dorsal (No.)
   - Nombre del caballo
   - Cuota Prob (convertir coma a punto)
6. Guardar snapshot en `odds_snapshots` con `bookmaker_id = TELETRAK`
7. Trigger al engine para comparación inmediata con Versus

---

## B.4 Implementación Técnica Teletrak

### B.4.1 Herramienta Recomendada

| Opción | Pros | Contras |
|--------|------|---------|
| **Playwright** ✅ | Consistencia con Versus, maneja SPA | Mayor consumo recursos |
| Requests + BS4 | Más ligero | Teletrak también usa JS dinámico |

**Decisión**: **Playwright** para mantener consistencia y manejar contenido dinámico.

### B.4.2 Extracción de Datos

```python
async def extract_teletrak_odds(page) -> list[dict]:
    """
    Extrae cuotas de la página de carrera de Teletrak.
    
    Returns:
        Lista de {saddle_number, name, odds_decimal}
    """
    runners = []
    
    # Esperar a que cargue la tabla de caballos
    await page.wait_for_selector('.wager-sidebar__horses')
    
    # Extraer cada fila de caballo
    horse_rows = await page.query_selector_all('.horse-row')  # Ajustar selector
    
    for row in horse_rows:
        # Número de dorsal (columna No.)
        saddle_el = await row.query_selector('.saddle-number')
        saddle = int(await saddle_el.inner_text())
        
        # Nombre del caballo (h2)
        name_el = await row.query_selector('h2')
        name = await name_el.inner_text()
        
        # Cuota Prob (9ª columna o buscar por posición)
        prob_el = await row.query_selector('.prob-column')  # Ajustar selector
        prob_text = await prob_el.inner_text()
        
        # Convertir formato: "6,0" -> 6.0, "2,7 FAV" -> 2.7
        odds = parse_teletrak_odds(prob_text)
        
        runners.append({
            'saddle_number': saddle,
            'name': name.strip(),
            'odds_decimal': odds
        })
    
    return runners


def parse_teletrak_odds(odds_str: str) -> float:
    """Convierte cuota Teletrak a decimal."""
    clean = odds_str.replace('FAV', '').strip()
    return float(clean.replace(',', '.'))
```

### B.4.3 Selectores CSS Identificados

```python
# Configuración de selectores Teletrak
TELETRAK_SELECTORS = {
    # Sidebar
    'meeting_rows': '.upcoming-row.event-row',
    'chile_flag': '.cl-flag',
    'track_name': 'h4.event-row-event-name .truncate-text',
    'race_number': 'h3.race-number-cell',
    'pool_amount': 'h3.pool-amount-cell .currency',
    'mtp_time': 'h3.mtp-cell',
    
    # Tabs de carrera
    'race_tabs': '.races-switch-tab',
    
    # Tabla de caballos
    'horse_table': '.wager-sidebar__horses',  # Verificar
    'horse_row': '.horse-row',  # Verificar
    'horse_name': 'h2',
    'horse_trainer': 'h6',  # Info adicional, no necesaria
    
    # Columnas específicas - A CONFIRMAR
    'saddle_column': 'td:nth-child(1)',  # Posición estimada
    'prob_column': 'td:nth-child(9)',     # Posición estimada
}
```

> ⚠️ **NOTA**: Los selectores de tabla deben confirmarse con pruebas reales.
> La estructura exacta de la tabla puede variar.

---

# Parte C: Matching de Carreras

## C.1 Problema de Matching

Las carreras en Versus y Teletrak no usan los mismos identificadores ni nombres:

| Versus | Teletrak |
|--------|----------|
| `Concepcion` | `Club Hípico De Concepción` |
| `Hipodromo Chile` | `01. Hipódromo Chile` |
| Meeting ID: 340357 | raceCardId: 302839 |

## C.2 Estrategia de Matching

### C.2.1 Matching por Track + Fecha + Hora

```python
def match_race(versus_race, teletrak_races) -> Optional[TeletrakRace]:
    """
    Encuentra la carrera equivalente en Teletrak.
    
    Criterios de match:
    1. Mismo track (normalizado)
    2. Misma fecha
    3. Hora similar (±5 minutos de tolerancia)
    """
    versus_track = normalize_track_name(versus_race.track, VERSUS_ID)
    
    for t_race in teletrak_races:
        t_track = normalize_track_name(t_race.track, TELETRAK_ID)
        
        if versus_track != t_track:
            continue
        
        if versus_race.date != t_race.date:
            continue
        
        time_diff = abs(versus_race.off_time - t_race.off_time)
        if time_diff <= timedelta(minutes=5):
            return t_race
    
    return None
```

### C.2.2 Tabla track_aliases

Ver diseño en `docs/DISENO_BD.md` - Sección 4.3

```sql
-- Ejemplo de uso
SELECT canonical_name 
FROM track_aliases 
WHERE alias_name ILIKE 'Club Hípico De Concepción' 
  AND bookmaker_id = 1;  -- TELETRAK

-- Retorna: 'CONCEPCION'
```

### C.2.3 Flujo de Discovery Coordinado

```
┌────────────────────────────────────────────────────────────────────┐
│                    DISCOVERY COORDINADO                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    TELETRAK                         VERSUS                         │
│    ─────────                        ──────                         │
│         │                              │                            │
│         ▼                              ▼                            │
│  ┌─────────────┐               ┌─────────────┐                     │
│  │ Scrape      │               │ Scrape      │                     │
│  │ meetings    │               │ meetings    │                     │
│  │ con .cl-flag│               │ chile.svg   │                     │
│  └──────┬──────┘               └──────┬──────┘                     │
│         │                              │                            │
│         ▼                              ▼                            │
│  ┌─────────────┐               ┌─────────────┐                     │
│  │ Normalizar  │               │ Normalizar  │                     │
│  │ track names │               │ track names │                     │
│  └──────┬──────┘               └──────┬──────┘                     │
│         │                              │                            │
│         └──────────────┬───────────────┘                           │
│                        │                                            │
│                        ▼                                            │
│               ┌─────────────────┐                                  │
│               │     MATCH       │                                  │
│               │ track + fecha   │                                  │
│               │ + hora          │                                  │
│               └────────┬────────┘                                  │
│                        │                                            │
│                        ▼                                            │
│               ┌─────────────────┐                                  │
│               │   Crear race    │                                  │
│               │ con external_ids│                                  │
│               │ de ambas fuentes│                                  │
│               └─────────────────┘                                  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Configuración Recomendada

```python
# config/settings.py

# ═══════════════════════════════════════════════════════════════════
# VERSUS (SOFT)
# ═══════════════════════════════════════════════════════════════════
VERSUS_BASE_URL = "https://www.versus.es/apuestas/sports/horse_racing"
VERSUS_POLL_INTERVAL_SECONDS = 15
VERSUS_PAGE_LOAD_TIMEOUT_MS = 5000
VERSUS_ODDS_SELECTOR_TIMEOUT_MS = 3000
VERSUS_DISCOVERY_TIME = "09:00"  # CET
VERSUS_CHILE_FLAG_SELECTOR = 'img[src*="chile.svg"]'

# ═══════════════════════════════════════════════════════════════════
# TELETRAK (SHARP)
# ═══════════════════════════════════════════════════════════════════
TELETRAK_BASE_URL = "https://apuestas.teletrak.cl"
TELETRAK_POLL_INTERVAL_SECONDS = 10  # Más frecuente (es la referencia)
TELETRAK_PAGE_LOAD_TIMEOUT_MS = 5000
TELETRAK_DISCOVERY_TIME = "10:00"  # CLT (Chile)
TELETRAK_CHILE_FLAG_SELECTOR = ".cl-flag"

# ═══════════════════════════════════════════════════════════════════
# COMMON
# ═══════════════════════════════════════════════════════════════════
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_BROWSER = "chromium"

# Ventana de scraping activo
WINDOW_START_MINUTES = 10  # T-10
WINDOW_END_MINUTES = 1     # T-1

# Matching
RACE_TIME_TOLERANCE_MINUTES = 5
```

---

## Manejo de Errores

### Errores Comunes

| Error | Fuente | Causa | Mitigación |
|-------|--------|-------|------------|
| Timeout | Ambas | Página lenta | Retry con backoff exponencial |
| Elemento no encontrado | Ambas | Cambio de DOM | Logging + alerta, fallback selectores |
| Cuota "SP" | Versus | Sin precio fijo | Ignorar caballo en ese poll |
| Formato cuota inválido | Teletrak | Texto inesperado | Try/except, loguear y skip |
| Race no matched | Matching | Diferencia de horarios | Aumentar tolerancia, log warning |
| Track no encontrado | Matching | Nuevo track sin alias | Alerta para añadir a track_aliases |

### Logging Estructurado

```python
logger.info("teletrak_scrape_complete", extra={
    "race_id": race_id,
    "raceCardId": race_card_id,
    "runners_count": len(runners),
    "latency_ms": elapsed_ms,
    "ts_utc": datetime.utcnow().isoformat()
})

logger.warning("track_alias_not_found", extra={
    "track_name": original_name,
    "bookmaker": "TELETRAK",
    "action": "using_original_uppercase"
})
```

---

## Métricas de Monitoreo

| Métrica | Descripción | Alerta si |
|---------|-------------|-----------|
| `teletrak_scrape_latency_ms` | Tiempo de scraping Teletrak | > 2000ms |
| `versus_scrape_latency_ms` | Tiempo de scraping Versus | > 3000ms |
| `scrape_success_rate` | % de scrapings exitosos | < 95% |
| `race_match_rate` | % de carreras matcheadas | < 90% |
| `odds_stale_seconds` | Antigüedad del último snapshot | > 20s (Teletrak), > 30s (Versus) |

---

## Próximos Pasos

1. [ ] **Validar selectores Teletrak**: Confirmar selectores de tabla de caballos
2. [ ] **Implementar scraper Teletrak**: `scrapers/teletrak_odds.py`
3. [ ] **Implementar discovery Teletrak**: `scrapers/teletrak_discovery.py`
4. [ ] **Crear tabla track_aliases**: Datos iniciales de hipódromos chilenos
5. [ ] **Implementar matching**: `engine/matching.py` para carreras
6. [ ] **Pruebas de latencia**: Medir tiempos reales end-to-end
7. [ ] **Evaluar intercepción API Versus**: Investigar endpoints JSON

---

*Documento actualizado: 2026-02-03*
*Basado en exploración de: versus.es y apuestas.teletrak.cl*

