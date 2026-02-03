# ChileSharp: Sistema de Value Betting en Carreras de Caballos Chilenas

## Resumen Ejecutivo

**ChileSharp** es un sistema automatizado de detección de value bets en carreras de caballos chilenas. Explota la asimetría de información entre el pool local chileno (Teletrak) —donde apuestan insiders— y las casas de apuestas españolas (Versus.es inicialmente) que ofrecen cuotas fijas menos ajustadas al mercado local.

---

## 1. Modelo de Negocio

### 1.1 Concepto

| Rol | Fuente | Características |
|-----|--------|-----------------|
| **Sharp (referencia)** | Teletrak.cl | Pool parimutuel local con dinero de insiders chilenos (propietarios, entrenadores, tipsters) |
| **Soft (explotación)** | Versus.es | Casa española con cuotas fijas; mercado chileno es secundario, actualización lenta |

**Edge**: Cuando el pool de Teletrak indica una probabilidad real significativamente mayor que la implícita en la cuota de Versus → value bet.

### 1.2 Fases del Proyecto

| Fase | Objetivo | Entregable |
|------|----------|------------|
| **Fase 0** | Validación de acceso y cobertura | Confirmar scraping viable, estructura de datos |
| **Fase 1** | Paper trading | Sistema completo sin dinero real; registro en BD |
| **Fase 2** | Análisis estadístico | 200-300 picks, validación de KPIs |
| **Fase 3** | Producción limitada | Apuestas reales con stake pequeño |
| **Fase 4** | Escalado | Event-driven, múltiples softs, otros mercados sharp |

---

## 2. Fuentes de Datos

### 2.1 Hipódromos Cubiertos

- **Hipódromo Chile** (Santiago)
- **Club Hípico de Santiago**
- **Club Hípico de Concepción**

**Volumen estimado**: 4-6 jornadas/semana, 8-12 carreras/jornada.

**Horario**: 17:00-23:00 CET (13:00-19:00 hora Chile).

### 2.2 Teletrak (Sharp)

**Datos obtenidos por carrera**:
- Lista de caballos: dorsal, nombre
- Columna `Prob`: cuota decimal del pool WIN (ej: 4.5, 18.7)
- Total apostado ganador (pool total WIN)

**Acceso**: Scraping HTTP/HTML (sin API pública documentada).

**Formato Prob**: Número decimal interpretable como "paga X por 1 unidad apostada".

### 2.3 Versus.es (Soft)

**Datos obtenidos por carrera**:
- Lista de caballos
- Cuota fija WIN decimal

**Acceso**: Scraping web (requests/BS4, Playwright si requiere JS).

### 2.4 Resultados Oficiales

**Fuentes**:
- Hipódromo Chile: sección "Resultados por Reunión"
- Club Hípico Santiago: "Programa y Resultados por carrera"
- Club Hípico Concepción: sección de resultados

**Estrategia**: Priorizar HTML estructurado; fallback a parseo de PDFs.

---

## 3. Modelo Matemático

### 3.1 Cálculo de Probabilidad Fair

Sea $D_i$ la cuota `Prob` del caballo $i$ en Teletrak:

**Probabilidad implícita con vig**:
$$\tilde{p}_i = \frac{1}{D_i}$$

**Normalización (quitar comisión del pool)**:
$$Z = \sum_{j} \tilde{p}_j$$
$$p_i = \frac{\tilde{p}_i}{Z}$$

**Cuota justa (fair odds)**:
$$O_{fair,i} = \frac{1}{p_i}$$

### 3.2 Cálculo de Edge

**Edge frente a la soft**:
$$edge_i = p_i \cdot O_{soft,i} - 1$$

**Interpretación**: `edge = 0.15` → +15% de valor esperado por unidad apostada.

### 3.3 Condición Alternativa (Soft vs Fair)

$$O_{soft,i} \geq O_{fair,i} \cdot (1 + \delta)$$

Con $\delta$ en rango 0.10–0.20.

### 3.4 Steam Detection (Opcional)

$$steam\_pct = \frac{D_{apertura} - D_{mínimo}}{D_{apertura}}$$

Filtrar caballos con `steam_pct ≥ 20%` (fuertemente apoyados en Teletrak).

---

## 4. Reglas de Filtrado

### 4.1 Filtros Principales

| Filtro | Valor Inicial | Notas |
|--------|---------------|-------|
| Edge mínimo | ≥ 10% | Subir a 15% en producción |
| Distancia soft/fair | $O_{soft} \geq O_{fair} \times 1.10$ | δ configurable 0.10-0.20 |
| Ventana temporal | T-10 a T-1 minutos | Antes: ruido; después: riesgo de no ejecutar |
| Liquidez mínima | Por definir | Descartar pools muy pequeños |

### 4.2 Filtros Opcionales

- **Stability check**: Comparar última $p_i$ con media de últimos 3-5 snapshots
- **Steam filter**: Solo caballos con steam_pct ≥ 20%

### 4.3 Picks por Carrera

- **Operativo**: Máximo 1 pick por carrera (mayor edge que cumpla filtros)
- **Análisis interno**: Registrar todos los value bets con flag `primary_pick`

---

## 5. Modelo de Datos

### 5.1 Diagrama de Tablas

```
┌─────────────────┐
│     races       │
│─────────────────│
│ id (PK)         │
│ country         │
│ track           │
│ race_date       │
│ race_number     │
│ off_time_utc    │
│ surface         │
│ distance        │
│ race_type       │
│ status          │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────────┐
│    runners      │       │   teletrak_races    │
│─────────────────│       │─────────────────────│
│ id (PK)         │       │ race_id (FK)        │
│ race_id (FK)    │       │ racecard_id         │
│ saddle_number   │       │ teletrak_race_id    │
│ name_original   │       │ url                 │
│ name_normalized │       └─────────────────────┘
│ status          │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌───────────────────────┐     ┌───────────────────────┐
│  teletrak_snapshots   │     │  versus_odds_snapshots│
│───────────────────────│     │───────────────────────│
│ id (PK)               │     │ id (PK)               │
│ race_id (FK)          │     │ race_id (FK)          │
│ runner_id (FK)        │     │ runner_id (FK)        │
│ ts_utc                │     │ ts_utc                │
│ prob_dec              │     │ odds_dec              │
│ total_pool_win        │     │ versus_event_id       │
└───────────────────────┘     └───────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│   versus_events     │       │   versus_runners    │
│─────────────────────│       │─────────────────────│
│ id (PK)             │       │ id (PK)             │
│ race_id (FK)        │       │ versus_event_id(FK) │
│ versus_event_id_ext │       │ runner_id (FK)      │
│ event_name          │       │ name_versus         │
│ scheduled_time      │       │ saddle_number       │
└─────────────────────┘       └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│    value_bets       │       │   race_results      │
│─────────────────────│       │─────────────────────│
│ id (PK)             │       │ id (PK)             │
│ race_id (FK)        │       │ race_id (FK)        │
│ runner_id (FK)      │       │ runner_id (FK)      │
│ teletrak_snap_id    │       │ finish_position     │
│ versus_snap_id      │       │ status (RAN/NR/etc) │
│ p_fair              │       │ official_time       │
│ o_fair              │       └─────────────────────┘
│ o_soft              │
│ edge                │
│ stake_units         │
│ mode (PAPER/LIVE)   │
│ primary_pick        │
│ status              │
│ result (WIN/LOSE/NR)│
│ profit_units        │
│ created_at          │
└─────────────────────┘
```

### 5.2 Descripción de Tablas

| Tabla | Propósito |
|-------|-----------|
| `races` | Carrera canónica (hipódromo + fecha + número) |
| `runners` | Caballo participante en una carrera |
| `teletrak_races` | Mapeo de `races` a identificadores de Teletrak |
| `teletrak_snapshots` | Snapshots del pool (prob, total apostado) |
| `versus_events` | Carreras según Versus |
| `versus_runners` | Caballos de Versus mapeados a `runners` |
| `versus_odds_snapshots` | Snapshots de cuotas fijas de Versus |
| `value_bets` | Señales generadas (paper o live) |
| `race_results` | Resultados oficiales para settlement |

---

## 6. Arquitectura

### 6.1 Fase Paper (Monolito Modular)

```
┌──────────────────────────────────────────────────────────────┐
│                     SERVIDOR (MiniPC i9)                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ teletrak_       │  │ teletrak_       │                   │
│  │ program.py      │  │ odds.py         │                   │
│  │ (cron: 1x/día)  │  │ (polling 10-15s)│                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           ▼                    ▼                             │
│  ┌─────────────────────────────────────────┐                │
│  │              PostgreSQL                  │                │
│  │  races | runners | snapshots | bets     │                │
│  └─────────────────────────────────────────┘                │
│           ▲                    ▲                             │
│           │                    │                             │
│  ┌────────┴────────┐  ┌────────┴────────┐                   │
│  │ versus_odds.py  │  │ engine/         │                   │
│  │ (polling 15-20s)│  │ pricing.py      │                   │
│  └─────────────────┘  │ signals.py      │                   │
│                       │ matching.py     │                   │
│                       └────────┬────────┘                   │
│                                │                             │
│                       ┌────────┴────────┐                   │
│                       │ settlement/     │                   │
│                       │ results.py      │                   │
│                       │ settle_paper.py │                   │
│                       └─────────────────┘                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Módulos Python

```
horses/
├── scrapers/
│   ├── teletrak_program.py    # Descarga programa diario
│   ├── teletrak_odds.py       # Polling de Prob en ventana activa
│   └── versus_odds.py         # Polling de cuotas Versus
├── engine/
│   ├── matching.py            # Normalización y mapeo de nombres
│   ├── pricing.py             # Cálculo p_fair, O_fair, edge
│   └── signals.py             # Generación de value_bets
├── settlement/
│   ├── results_scraper.py     # Descarga resultados oficiales
│   └── settle_paper.py        # Cierre de picks (profit/loss)
├── db/
│   ├── models.py              # SQLAlchemy models
│   └── migrations/            # Alembic migrations
├── utils/
│   ├── normalization.py       # Normalización de nombres
│   └── timezone.py            # Conversiones CLT ↔ UTC ↔ CET
├── config/
│   └── settings.py            # Configuración (umbrales, polling)
└── scripts/
    ├── run_scrapers_loop.py   # Orquestador de scrapers
    ├── run_engine_loop.py     # Orquestador de engine
    └── run_settlement.py      # Settlement diario
```

### 6.3 Orquestación (Fase Paper)

| Job | Frecuencia | Descripción |
|-----|------------|-------------|
| `teletrak_program` | 1x/día (mañana) | Descarga carreras del día |
| `teletrak_odds` | Cada 10-15s en ventana | Snapshots del pool |
| `versus_odds` | Cada 15-20s en ventana | Snapshots de cuotas |
| `engine_signals` | Cada 15-30s en ventana | Evalúa y genera picks |
| `settlement` | 1x/día (noche) | Descarga resultados, cierra picks |

**Ventana activa**: T-10 a T-1 minutos antes del off.

### 6.4 Fase Producción (Event-Driven)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │ teletrak-    │    │ versus-      │                          │
│  │ ingestor     │    │ ingestor     │                          │
│  └──────┬───────┘    └──────┬───────┘                          │
│         │                   │                                   │
│         ▼                   ▼                                   │
│  ┌─────────────────────────────────────┐                       │
│  │         Redis Streams / RabbitMQ    │                       │
│  │    (teletrak_snapshot, versus_snap) │                       │
│  └──────────────────┬──────────────────┘                       │
│                     │                                           │
│                     ▼                                           │
│  ┌─────────────────────────────────────┐                       │
│  │         pricing-engine              │                       │
│  │   (estado en memoria, recalcula     │                       │
│  │    en caliente por evento)          │                       │
│  └──────────────────┬──────────────────┘                       │
│                     │                                           │
│         ┌───────────┼───────────┐                              │
│         ▼           ▼           ▼                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ notifier │ │ PostgreSQL│ │ bet-     │                       │
│  │ telegram │ │ (histórico)│ │ executor │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Matching de Caballos

### 7.1 Estrategia de Normalización

```python
def normalize_name(name: str) -> str:
    """
    Normaliza nombre de caballo para matching.

    Transformaciones:
    1. Mayúsculas
    2. Strip sufijos: (CHI), (ARG), II, III, 2, 3
    3. Eliminar acentos
    4. Normalizar espacios
    5. Eliminar caracteres especiales
    """
    pass
```

### 7.2 Criterios de Match

1. **Match primario**: `name_normalized` + `race_id` + `saddle_number`
2. **Match secundario**: `name_normalized` + `race_id` (sin dorsal)
3. **Corrección manual**: Tabla de mapeo para casos conflictivos

### 7.3 Logging de No-Matches

Instrumentar logs para detectar fallos de matching y afinar reglas.

---

## 8. Gestión de Zonas Horarias

### 8.1 Estrategia

| Fuente | Zona Original | Almacenamiento |
|--------|---------------|----------------|
| Hipódromos Chile | CLT/CLST | UTC |
| Teletrak | CLT/CLST | UTC |
| Versus | CET/CEST | UTC |

### 8.2 Implementación

```python
# Todas las horas se guardan en UTC
off_time_utc = parse_chile_time(raw_time).astimezone(pytz.UTC)

# Conversión para display
off_time_cet = off_time_utc.astimezone(pytz.timezone('Europe/Madrid'))
```

---

## 9. Staking

### 9.1 Fase Paper

- **Stake fijo**: 1 unidad abstracta por pick
- Sin Kelly ni ajustes por edge

### 9.2 Fase Producción (Futuro)

- Evaluar Kelly fraccional basado en edge y bankroll
- Requiere edge estable demostrado en paper

---

## 10. Settlement

### 10.1 Proceso

1. Scraper descarga resultados oficiales (post-jornada)
2. Inserta en `race_results` (posición, status)
3. `settle_paper.py` actualiza `value_bets`:
   - **WIN**: `profit = stake * (o_soft - 1)`
   - **LOSE**: `profit = -stake`
   - **NR/Void**: `profit = 0`

### 10.2 Datos Guardados

| Campo | Uso |
|-------|-----|
| `finish_position` | Posición exacta (1, 2, 3...) |
| `status` | RAN, NR, DNF, etc. |

Permite evolucionar a mercados PLACE en el futuro.

---

## 11. KPIs y Métricas

### 11.1 Métricas Principales

| KPI | Fórmula | Target |
|-----|---------|--------|
| **Yield (ROI)** | $\sum profit / \sum stake$ | > 5% |
| **Edge medio** | Media de `edge` en picks | ≥ 10-15% |
| **CLV** | % de picks donde cuota baja después | > 50% |
| **Hit rate** | % de picks ganadores | Variable por odds |

### 11.2 Análisis Adicional

- Distribución de yield por buckets de edge (10-15%, 15-20%, 20-30%, >30%)
- Longitud de peor racha perdedora
- Máximo drawdown sobre banca ficticia
- Correlación edge teórico → yield real

### 11.3 Validación de Modelo

En Fase 2, con 200-300 picks:
- Yield real > 5% con edge medio ≥ 10-15%
- CLV positivo consistente
- Coherencia entre edge predicho y yield observado

---

## 12. Infraestructura

### 12.1 Hardware (Fase Paper)

**MiniPC BMAX B9 Power**:
- CPU: Intel Core i9-12900H (14 cores, max 5.0GHz)
- RAM: 24GB
- Storage: 1TB SSD
- OS: Ubuntu Server
- Conectividad: WiFi 6, Bluetooth 5.2

### 12.2 Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.11+ |
| Base de datos | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| HTTP Client | requests, httpx |
| HTML Parser | BeautifulSoup4 |
| Browser Automation | Playwright (si necesario) |
| Scheduling | cron, systemd timers |
| API (futuro) | FastAPI |
| Contenedores | Docker, docker-compose |

---

## 13. Configuración

### 13.1 Parámetros Configurables

```python
# config/settings.py

# Umbrales de edge
MIN_EDGE = 0.10  # 10%
MIN_EDGE_PRODUCTION = 0.15  # 15%

# Distancia soft vs fair
DELTA_SOFT_FAIR = 0.10  # O_soft >= O_fair * 1.10

# Ventana temporal (minutos antes del off)
WINDOW_START_MINUTES = 10
WINDOW_END_MINUTES = 1

# Polling intervals (segundos)
TELETRAK_POLL_INTERVAL = 15
VERSUS_POLL_INTERVAL = 20
ENGINE_EVAL_INTERVAL = 15

# Steam detection (opcional)
ENABLE_STEAM_FILTER = False
MIN_STEAM_PCT = 0.20  # 20%

# Liquidez mínima (CLP)
MIN_POOL_WIN = None  # Por definir
```

---

## 14. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cambio estructura DOM Teletrak | Media | Alto | Monitoreo de errores, alertas, parsers resilientes |
| Geobloqueo Teletrak/Versus | Baja | Alto | VPN como fallback |
| Matching fallido de caballos | Media | Medio | Logs detallados, tabla de correcciones manuales |
| Edge no se materializa | Media | Alto | Fase paper extensa, análisis estadístico riguroso |
| Limitación de cuenta en Versus | Alta (largo plazo) | Alto | Múltiples softs, stakes conservadores |
| Latencia insuficiente | Baja (paper) | Bajo | Arquitectura event-driven en producción |

---

## 15. Roadmap

### Fase 0: Validación (1-2 semanas)
- [ ] Confirmar acceso a Teletrak (Prob visible sin login)
- [ ] Confirmar estructura DOM de Teletrak
- [ ] Confirmar carreras chilenas en Versus.es
- [ ] Confirmar fuente de resultados oficiales
- [ ] Medir volumen real de carreras/semana

### Fase 1: Implementación Paper (3-4 semanas)
- [ ] Modelo de datos + migraciones
- [ ] Scraper programa Teletrak
- [ ] Scraper odds Teletrak
- [ ] Scraper odds Versus
- [ ] Engine de matching
- [ ] Engine de pricing y señales
- [ ] Scraper de resultados
- [ ] Settlement automático
- [ ] Orquestación con cron/systemd

### Fase 2: Análisis (2-4 semanas)
- [ ] Acumular 200-300 picks
- [ ] Dashboard/queries de KPIs
- [ ] Validar yield, edge, CLV
- [ ] Ajustar umbrales si necesario

### Fase 3: Producción Limitada
- [ ] Integración con Telegram para notificaciones
- [ ] Mode LIVE con stakes pequeños
- [ ] Monitoreo de performance real

### Fase 4: Escalado
- [ ] Arquitectura event-driven
- [ ] Añadir otras softs españolas
- [ ] Añadir otros mercados sharp (México, Panamá)
- [ ] Mercados PLACE

---

## 16. Glosario

| Término | Definición |
|---------|------------|
| **Sharp** | Fuente de cuotas/probabilidades considerada eficiente (dinero informado) |
| **Soft** | Casa de apuestas con cuotas menos eficientes, explotables |
| **Edge** | Ventaja matemática esperada sobre la casa |
| **Value bet** | Apuesta con valor esperado positivo |
| **Prob** | Cuota del pool parimutuel en Teletrak |
| **Fair odds** | Cuota teórica sin margen, basada en probabilidad real |
| **CLV** | Closing Line Value: comparación de cuota de entrada vs cuota de cierre |
| **Yield/ROI** | Retorno sobre inversión: beneficio / total apostado |
| **Pool** | Sistema de apuestas mutuas donde los apostantes compiten entre sí |
| **Parimutuel** | Sistema de pool donde la casa toma comisión fija |
| **Steam** | Movimiento brusco de dinero que hace bajar la cuota de un caballo |
| **NR** | Non-runner: caballo retirado que no participa |

---

*Documento generado: 2025-12-11*
*Versión: 1.0*
