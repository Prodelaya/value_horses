# Diseño de Base de Datos - ChileSharp

## 1. Visión General

Este documento describe el diseño óptimo de base de datos para el sistema de value betting ChileSharp. El diseño prioriza:

1. **Mínima latencia** en escritura/lectura durante polling activo
2. **Escalabilidad** para múltiples bookmakers y geografías
3. **Simplicidad** para la fase inicial (solo WIN, solo Chile)
4. **Extensibilidad** para futuras funcionalidades (PLACE, otras regiones)

---

## 2. Principios de Diseño

### 2.1 Optimización para Latencia

```
CRÍTICO: El valor del sistema depende de la velocidad
         Scraping → Cálculo → Alerta debe ser < 2 segundos
```

**Decisiones de diseño para latencia:**
- Índices optimizados en campos de búsqueda frecuente
- Snapshots de odds en tabla separada (inserciones rápidas sin locks)
- Caché en memoria de carreras activas (complemento a BD)
- Timestamps UTC para comparaciones rápidas

### 2.2 Multi-Bookmaker desde el Inicio

El diseño soporta múltiples bookmakers (sharps y softs) desde el principio:
- Tabla `bookmakers` centralizada
- Foreign keys en todas las tablas de odds
- Fácil adición de nuevas fuentes sin migración de esquema

### 2.3 Datos Mínimos Necesarios

Siguiendo el principio de simplicidad:
- Solo datos esenciales: caballo, dorsal, cuota
- Sin datos auxiliares (trainer, jockey, form, peso)
- Campos de auditoría solo donde aportan valor

---

## 3. Diagrama de Entidades

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DIAGRAMA ER - CHILESHARP                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                       ┌────────────────────┐              │
│  │  bookmakers  │───────────────────────│   track_aliases    │              │
│  │──────────────│          1:N          │────────────────────│              │
│  │ id (PK)      │                       │ id (PK)            │              │
│  │ code         │  "VERSUS", "TELETRAK" │ canonical_name     │              │
│  │ name         │                       │ alias_name         │              │
│  │ type         │  "SHARP" | "SOFT"     │ bookmaker_id (FK)  │              │
│  │ country      │  "ES", "CL"           │ country            │              │
│  │ is_active    │                       └────────────────────┘              │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│         │ 1:N                                                               │
│         ▼                                                                   │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────────────┐    │
│  │   meetings   │──────▶│    races     │──────▶│       runners        │    │
│  │──────────────│  1:N  │──────────────│  1:N  │──────────────────────│    │
│  │ id (PK)      │       │ id (PK)      │       │ id (PK)              │    │
│  │ country      │       │ meeting_id   │       │ race_id (FK)         │    │
│  │ track        │       │ race_number  │       │ saddle_number        │    │
│  │ race_date    │       │ off_time_utc │       │ name_original        │    │
│  │ source_id    │       │ distance     │       │ name_normalized      │    │
│  │ source_bookie│       │ status       │       │ status               │    │
│  └──────────────┘       └──────┬───────┘       └──────────┬───────────┘    │
│                                │                          │                 │
│                                │                          │                 │
│         ┌──────────────────────┴──────────────────────────┘                 │
│         │                                                                   │
│         │ 1:N                                                               │
│         ▼                                                                   │
│  ┌────────────────────┐     ┌────────────────────┐                         │
│  │   odds_snapshots   │     │    external_ids    │                         │
│  │────────────────────│     │────────────────────│                         │
│  │ id (PK)            │     │ id (PK)            │                         │
│  │ runner_id (FK)     │     │ race_id (FK)       │                         │
│  │ bookmaker_id (FK)  │     │ bookmaker_id (FK)  │                         │
│  │ odds_decimal       │     │ external_race_id   │                         │
│  │ ts_utc             │     │ external_event_id  │                         │
│  │ is_available       │     │ url                │                         │
│  └────────────────────┘     └────────────────────┘                         │
│                                                                             │
│         ┌──────────────────────┐     ┌──────────────────────┐              │
│         │     value_bets       │     │    race_results      │              │
│         │──────────────────────│     │──────────────────────│              │
│         │ id (PK)              │     │ id (PK)              │              │
│         │ race_id (FK)         │     │ race_id (FK)         │              │
│         │ runner_id (FK)       │     │ runner_id (FK)       │              │
│         │ sharp_bookie_id (FK) │     │ finish_position      │              │
│         │ soft_bookie_id (FK)  │     │ status               │              │
│         │ sharp_snapshot_id    │     │ settled_at           │              │
│         │ soft_snapshot_id     │     └──────────────────────┘              │
│         │ p_fair               │                                            │
│         │ o_fair               │                                            │
│         │ o_soft               │                                            │
│         │ edge                 │     "WIN" | "PLACE"                       │
│         │ market_type          │     "PAPER" | "LIVE"                      │
│         │ mode                 │     "PENDING" | "SENT" | "SETTLED"        │
│         │ status               │     "WIN" | "LOSE" | "VOID" | NULL        │
│         │ result               │                                            │
│         │ stake_units          │                                            │
│         │ profit_units         │                                            │
│         │ alert_sent_at        │                                            │
│         │ created_at           │                                            │
│         └──────────────────────┘                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Especificación de Tablas

### 4.1 `bookmakers`

Catálogo de casas de apuestas (sharps y softs).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `code` | VARCHAR(20) | NOT NULL, UNIQUE | Código interno: "VERSUS", "TELETRAK" |
| `name` | VARCHAR(100) | NOT NULL | Nombre display: "Versus.es", "Teletrak.cl" |
| `type` | ENUM | NOT NULL | "SHARP" o "SOFT" |
| `country` | VARCHAR(2) | NOT NULL | Código país ISO: "ES", "CL" |
| `base_url` | VARCHAR(255) | NULL | URL base para scraping |
| `is_active` | BOOLEAN | DEFAULT TRUE | Habilitado para scraping |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_bookmakers_code` en `code`
- `idx_bookmakers_type` en `type`

**Datos iniciales:**
```sql
INSERT INTO bookmakers (code, name, type, country, base_url) VALUES
('TELETRAK', 'Teletrak.cl', 'SHARP', 'CL', 'https://www.teletrak.cl'),
('VERSUS', 'Versus.es', 'SOFT', 'ES', 'https://www.versus.es');
```

---

### 4.2 `meetings`

Agrupación de carreras por hipódromo y fecha.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `country` | VARCHAR(2) | NOT NULL | "CL" para Chile |
| `track` | VARCHAR(100) | NOT NULL | "Hipódromo Chile", "Club Hípico", "Concepción" |
| `race_date` | DATE | NOT NULL | Fecha del meeting |
| `source_bookmaker_id` | INTEGER | FK | Bookmaker de donde se descubrió |
| `source_external_id` | VARCHAR(50) | NULL | ID externo del meeting (ej: "340357") |
| `status` | ENUM | DEFAULT 'SCHEDULED' | SCHEDULED, ACTIVE, FINISHED, CANCELLED |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_meetings_date` en `race_date`
- `idx_meetings_track_date` en (`track`, `race_date`)
- `idx_meetings_status` en `status`

**Constraint único:**
```sql
UNIQUE (track, race_date)
```

---

### 4.3 `track_aliases`

Tabla de normalización para mapear nombres de hipódromos entre diferentes fuentes.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `canonical_name` | VARCHAR(100) | NOT NULL | Nombre canónico del hipódromo |
| `alias_name` | VARCHAR(100) | NOT NULL | Nombre alternativo (como aparece en la fuente) |
| `bookmaker_id` | INTEGER | FK NOT NULL | Bookmaker donde se usa este alias |
| `country` | VARCHAR(2) | NOT NULL | País del hipódromo |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_track_aliases_alias` en (`alias_name`, `bookmaker_id`)
- `idx_track_aliases_canonical` en `canonical_name`

**Constraint único:**
```sql
UNIQUE (alias_name, bookmaker_id)
```

**Datos iniciales (ejemplos reales):**
```sql
-- Mapeo Teletrak → Canónico (bookmaker_id = 1)
INSERT INTO track_aliases (canonical_name, alias_name, bookmaker_id, country) VALUES
('CONCEPCION', 'Club Hípico De Concepción', 1, 'CL'),  -- raceCardId: 302839
('HIPODROMO_CHILE', '01. Hipódromo Chile', 1, 'CL'),
('CLUB_HIPICO', 'Club Hípico de Santiago', 1, 'CL');

-- Mapeo Versus → Canónico (bookmaker_id = 2)
INSERT INTO track_aliases (canonical_name, alias_name, bookmaker_id, country) VALUES
('CONCEPCION', 'Concepcion', 2, 'CL'),  -- meeting_id: 340357
('HIPODROMO_CHILE', 'Hipodromo Chile', 2, 'CL'),
('CLUB_HIPICO', 'Club Hipico', 2, 'CL');
```

> ⚠️ **IMPORTANTE**: Los IDs de meeting/raceCard son **diferentes** entre fuentes.
> Ejemplo real:
> - Versus: `Concepcion` → meeting_id = `340357`
> - Teletrak: `Club Hípico De Concepción` → raceCardId = `302839`
> 
> El matching NO puede hacerse por ID. Se usa: **track normalizado + fecha + hora aproximada**.

**Uso en código:**
```python
def normalize_track_name(alias: str, bookmaker_id: int) -> str:
    """
    Convierte un nombre de hipódromo a su forma canónica.
    Returns canonical_name o el alias original si no hay mapeo.
    """
    result = db.query(TrackAlias).filter(
        TrackAlias.alias_name.ilike(alias),
        TrackAlias.bookmaker_id == bookmaker_id
    ).first()
    return result.canonical_name if result else alias.upper()
```

---

### 4.4 `races`

Carrera individual dentro de un meeting.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `meeting_id` | INTEGER | FK NOT NULL | Referencia al meeting |
| `race_number` | SMALLINT | NOT NULL | Número de carrera (1, 2, 3...) |
| `off_time_utc` | TIMESTAMP | NOT NULL | Hora de salida en UTC |
| `distance` | VARCHAR(20) | NULL | "1200m", "1600m" |
| `surface` | VARCHAR(20) | NULL | "Arena", "Césped" |
| `status` | ENUM | DEFAULT 'SCHEDULED' | SCHEDULED, ACTIVE, FINISHED, CANCELLED |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |
| `updated_at` | TIMESTAMP | NULL | Última actualización |

**Índices:**
- `idx_races_meeting` en `meeting_id`
- `idx_races_off_time` en `off_time_utc` (CRÍTICO para ventana activa)
- `idx_races_status_time` en (`status`, `off_time_utc`)

**Constraint único:**
```sql
UNIQUE (meeting_id, race_number)
```

---

### 4.5 `runners`

Caballo participante en una carrera.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `race_id` | INTEGER | FK NOT NULL | Referencia a la carrera |
| `saddle_number` | SMALLINT | NOT NULL | Número de dorsal |
| `name_original` | VARCHAR(100) | NOT NULL | Nombre original |
| `name_normalized` | VARCHAR(100) | NOT NULL | Nombre normalizado para matching |
| `status` | ENUM | DEFAULT 'ACTIVE' | ACTIVE, SCRATCHED (retirado) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_runners_race` en `race_id`
- `idx_runners_normalized` en (`race_id`, `name_normalized`)
- `idx_runners_saddle` en (`race_id`, `saddle_number`)

**Constraint único:**
```sql
UNIQUE (race_id, saddle_number)
```

---

### 4.6 `external_ids`

Mapeo de IDs externos por bookmaker (para navegación directa).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `race_id` | INTEGER | FK NOT NULL | Referencia a la carrera |
| `bookmaker_id` | INTEGER | FK NOT NULL | Referencia al bookmaker |
| `external_meeting_id` | VARCHAR(50) | NULL | ID del meeting en el bookmaker |
| `external_race_id` | VARCHAR(50) | NOT NULL | ID de la carrera en el bookmaker |
| `url` | VARCHAR(500) | NULL | URL directa a la carrera |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_external_race_bookie` en (`race_id`, `bookmaker_id`)
- `idx_external_lookup` en (`bookmaker_id`, `external_race_id`)

**Constraint único:**
```sql
UNIQUE (race_id, bookmaker_id)
```

---

### 4.7 `odds_snapshots`

Snapshots de cuotas (tabla de alto volumen, optimizada para inserciones).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | BIGSERIAL | PK | Identificador único (BIGINT para volumen) |
| `runner_id` | INTEGER | FK NOT NULL | Referencia al caballo |
| `bookmaker_id` | INTEGER | FK NOT NULL | Referencia al bookmaker |
| `odds_decimal` | DECIMAL(10,4) | NOT NULL | Cuota decimal (ej: 4.5000) |
| `market_type` | ENUM | DEFAULT 'WIN' | WIN, PLACE |
| `is_available` | BOOLEAN | DEFAULT TRUE | Si la cuota está activa |
| `ts_utc` | TIMESTAMP | NOT NULL | Timestamp del snapshot |

**Índices:**
- `idx_snapshots_runner_bookie_ts` en (`runner_id`, `bookmaker_id`, `ts_utc` DESC)
- `idx_snapshots_ts` en `ts_utc` (para limpieza de histórico)

**Notas de rendimiento:**
- Sin `created_at` por duplicar `ts_utc`
- Considerar particionamiento por fecha si volumen > 10M registros
- Considerar TimescaleDB para time-series optimization

---

### 4.8 `value_bets`

Señales de value detectadas.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `race_id` | INTEGER | FK NOT NULL | Referencia a la carrera |
| `runner_id` | INTEGER | FK NOT NULL | Referencia al caballo |
| `sharp_bookmaker_id` | INTEGER | FK NOT NULL | Bookmaker de referencia (Teletrak) |
| `soft_bookmaker_id` | INTEGER | FK NOT NULL | Bookmaker a explotar (Versus) |
| `sharp_snapshot_id` | BIGINT | FK NULL | Snapshot usado del sharp |
| `soft_snapshot_id` | BIGINT | FK NULL | Snapshot usado del soft |
| `p_fair` | DECIMAL(8,6) | NOT NULL | Probabilidad justa (0.xxxxxx) |
| `o_fair` | DECIMAL(10,4) | NOT NULL | Cuota justa calculada |
| `o_soft` | DECIMAL(10,4) | NOT NULL | Cuota del soft al momento |
| `edge` | DECIMAL(8,6) | NOT NULL | Edge calculado (0.15 = 15%) |
| `market_type` | ENUM | DEFAULT 'WIN' | WIN, PLACE |
| `mode` | ENUM | DEFAULT 'PAPER' | PAPER, LIVE |
| `status` | ENUM | DEFAULT 'PENDING' | PENDING, SENT, SETTLED |
| `result` | ENUM | NULL | WIN, LOSE, VOID |
| `stake_units` | DECIMAL(8,4) | DEFAULT 1 | Unidades apostadas |
| `profit_units` | DECIMAL(10,4) | NULL | Profit/loss en unidades |
| `alert_sent_at` | TIMESTAMP | NULL | Cuándo se envió la alerta |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |
| `settled_at` | TIMESTAMP | NULL | Fecha de settlement |

**Índices:**
- `idx_value_bets_race` en `race_id`
- `idx_value_bets_status` en `status`
- `idx_value_bets_mode_status` en (`mode`, `status`)
- `idx_value_bets_created` en `created_at`

---

### 4.9 `race_results`

Resultados oficiales para settlement.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | PK | Identificador único |
| `race_id` | INTEGER | FK NOT NULL | Referencia a la carrera |
| `runner_id` | INTEGER | FK NOT NULL | Referencia al caballo |
| `finish_position` | SMALLINT | NULL | Posición final (1, 2, 3...) |
| `status` | ENUM | NOT NULL | RAN, NR (non-runner), DNF, DQ |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha creación |

**Índices:**
- `idx_results_race` en `race_id`
- `idx_results_position` en (`race_id`, `finish_position`)

**Constraint único:**
```sql
UNIQUE (race_id, runner_id)
```

---

## 5. Enums

```sql
-- Tipos de bookmaker
CREATE TYPE bookmaker_type AS ENUM ('SHARP', 'SOFT');

-- Estado de meeting/carrera
CREATE TYPE event_status AS ENUM ('SCHEDULED', 'ACTIVE', 'FINISHED', 'CANCELLED');

-- Estado del runner
CREATE TYPE runner_status AS ENUM ('ACTIVE', 'SCRATCHED');

-- Tipo de mercado
CREATE TYPE market_type AS ENUM ('WIN', 'PLACE');

-- Modo de apuesta
CREATE TYPE bet_mode AS ENUM ('PAPER', 'LIVE');

-- Estado del value bet
CREATE TYPE bet_status AS ENUM ('PENDING', 'SENT', 'SETTLED');

-- Resultado del bet
CREATE TYPE bet_result AS ENUM ('WIN', 'LOSE', 'VOID');

-- Estado del resultado de carrera
CREATE TYPE result_status AS ENUM ('RAN', 'NR', 'DNF', 'DQ');
```

---

## 6. Queries Críticas Optimizadas

### 6.1 Obtener carreras en ventana activa

```sql
-- Carreras que empiezan en los próximos 10 minutos
SELECT r.id, r.race_number, r.off_time_utc, m.track
FROM races r
JOIN meetings m ON r.meeting_id = m.id
WHERE r.status = 'SCHEDULED'
  AND r.off_time_utc BETWEEN NOW() AND NOW() + INTERVAL '10 minutes'
ORDER BY r.off_time_utc;
```

### 6.2 Último snapshot por runner y bookmaker

```sql
-- Cuotas más recientes para una carrera
SELECT DISTINCT ON (os.runner_id, os.bookmaker_id)
    os.runner_id,
    os.bookmaker_id,
    os.odds_decimal,
    os.ts_utc
FROM odds_snapshots os
JOIN runners ru ON os.runner_id = ru.id
WHERE ru.race_id = $1
ORDER BY os.runner_id, os.bookmaker_id, os.ts_utc DESC;
```

### 6.3 Comparar sharp vs soft para detectar value

```sql
-- Value detection query (para engine)
WITH latest_odds AS (
    SELECT DISTINCT ON (os.runner_id, os.bookmaker_id)
        os.runner_id,
        os.bookmaker_id,
        b.type AS bookie_type,
        os.odds_decimal,
        os.ts_utc,
        os.id AS snapshot_id
    FROM odds_snapshots os
    JOIN bookmakers b ON os.bookmaker_id = b.id
    JOIN runners ru ON os.runner_id = ru.id
    WHERE ru.race_id = $1
      AND os.is_available = TRUE
    ORDER BY os.runner_id, os.bookmaker_id, os.ts_utc DESC
)
SELECT 
    sharp.runner_id,
    sharp.odds_decimal AS sharp_odds,
    soft.odds_decimal AS soft_odds,
    sharp.snapshot_id AS sharp_snapshot_id,
    soft.snapshot_id AS soft_snapshot_id,
    -- Cálculo de edge inline para velocidad
    (1.0 / sharp.odds_decimal) * soft.odds_decimal - 1 AS edge
FROM latest_odds sharp
JOIN latest_odds soft ON sharp.runner_id = soft.runner_id
WHERE sharp.bookie_type = 'SHARP'
  AND soft.bookie_type = 'SOFT'
  AND (1.0 / sharp.odds_decimal) * soft.odds_decimal - 1 >= 0.10;  -- MIN_EDGE
```

---

## 7. Consideraciones de Rendimiento

### 7.1 Volumen Estimado

| Tabla | Registros/día | Registros/mes | Notas |
|-------|---------------|---------------|-------|
| meetings | 5-10 | 150-300 | 1 por hipódromo/día |
| races | 40-60 | 1,200-1,800 | 8-12 por meeting |
| runners | 300-500 | 9,000-15,000 | ~8 por carrera |
| odds_snapshots | 10,000-20,000 | 300,000-600,000 | Alto volumen |
| value_bets | 10-50 | 300-1,500 | Depende del edge |

### 7.2 Estrategias de Optimización

1. **Índices parciales** para carreras activas:
```sql
CREATE INDEX idx_races_active ON races (off_time_utc) 
WHERE status = 'SCHEDULED';
```

2. **Limpieza de snapshots antiguos** (retención 30 días):
```sql
DELETE FROM odds_snapshots 
WHERE ts_utc < NOW() - INTERVAL '30 days';
```

3. **Caché en memoria** (Redis/dict) para carreras activas durante polling

4. **Batch inserts** para snapshots (insertar múltiples en una transacción)

---

## 8. Scripts de Creación

Ver archivo separado: `db/migrations/001_initial_schema.sql`

---

## 9. Extensibilidad Futura

### 9.1 Añadir nuevo bookmaker

```sql
-- Solo insert en bookmakers
INSERT INTO bookmakers (code, name, type, country, base_url)
VALUES ('BETWAY', 'Betway.es', 'SOFT', 'ES', 'https://www.betway.es');
```

### 9.2 Añadir mercado PLACE

```sql
-- Ya soportado via market_type ENUM
-- Solo cambiar DEFAULT si PLACE se vuelve prioritario
INSERT INTO odds_snapshots (runner_id, bookmaker_id, odds_decimal, market_type, ts_utc)
VALUES (123, 1, 1.85, 'PLACE', NOW());
```

### 9.3 Añadir otra geografía

```sql
-- Nuevo meeting con country diferente
INSERT INTO meetings (country, track, race_date, source_bookmaker_id)
VALUES ('MX', 'Hipódromo de las Américas', '2026-02-10', 3);
```

---

*Documento generado: 2026-02-03*
*Versión: 1.0*
