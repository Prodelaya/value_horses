# Roadmap Detallado - ChileSharp

## Índice

1. [Visión General](#1-visión-general)
2. [Fase 0: Validación](#2-fase-0-validación)
3. [Fase 1: Implementación Paper](#3-fase-1-implementación-paper)
4. [Fase 2: Análisis y Calibración](#4-fase-2-análisis-y-calibración)
5. [Fase 3: Producción Limitada](#5-fase-3-producción-limitada)
6. [Fase 4: Escalado](#6-fase-4-escalado)
7. [Dependencias entre Fases](#7-dependencias-entre-fases)
8. [Criterios de Éxito](#8-criterios-de-éxito)

---

## 1. Visión General

### 1.1 Objetivo del Sistema

ChileSharp es un sistema automatizado de detección de value bets en carreras de caballos chilenas. El sistema explota la asimetría de información entre:

- **Sharp (Referencia)**: Teletrak.cl - Pool parimutuel con dinero de insiders chilenos
- **Soft (Explotación)**: Versus.es - Casa española con cuotas fijas menos eficientes

### 1.2 Métrica Crítica de Éxito

```
LATENCIA MÁXIMA ACEPTABLE: < 2 segundos
Desde: Captura de cuota en Teletrak + Versus
Hasta: Envío de alerta de value bet
```

### 1.3 Timeline Estimado

| Fase | Duración | Estado |
|------|----------|--------|
| Fase 0 | 1-2 semanas | 🟡 En progreso |
| Fase 1 | 3-4 semanas | ⚪ Pendiente |
| Fase 2 | 2-4 semanas | ⚪ Pendiente |
| Fase 3 | 2-4 semanas | ⚪ Pendiente |
| Fase 4 | Ongoing | ⚪ Pendiente |

---

## 2. Fase 0: Validación

### 2.1 Objetivo de la Fase

Confirmar que el scraping es viable, que las fuentes de datos están disponibles y que existe cobertura suficiente de carreras chilenas en Versus.

**Duración estimada**: 1-2 semanas

**Criterio de éxito**: Todos los puntos de validación confirmados positivamente.

---

### 2.2 Tareas de la Fase

#### 2.2.1 Validación de Acceso a Teletrak

**Descripción**: Confirmar que Teletrak.cl muestra las cuotas del pool (campo "Prob") sin requerir login, y que la estructura del DOM es parseable.

**Información para el equipo técnico**:
- Teletrak.cl es la fuente sharp (referencia)
- El campo "Prob" representa la cuota decimal del pool WIN
- Se debe poder extraer: lista de caballos, dorsales, cuotas
- Verificar si requiere JavaScript (Playwright) o si HTML estático es suficiente (BeautifulSoup)

**Entregables**:
1. Documento confirmando acceso público a cuotas
2. Captura de pantalla del DOM mostrando estructura
3. Lista de selectores CSS/XPath para datos clave
4. Decisión: Playwright vs requests+BS4

**Riesgos a evaluar**:
- Geobloqueo (si aplica, evaluar VPN)
- Cambios frecuentes de DOM
- Rate limiting

---

#### 2.2.2 Validación de Estructura DOM de Teletrak

**Descripción**: Documentar la estructura exacta del DOM de Teletrak para el scraper de odds.

**Información para el equipo técnico**:
- Identificar los elementos que contienen cada caballo
- Mapear campos: nombre, dorsal, cuota Prob, total pool
- Verificar si hay paginación o lazy loading
- Documentar la URL pattern de cada carrera

**Entregables**:
1. Diagrama/esquema de estructura DOM
2. Selectores CSS definitivos para cada campo
3. Script de prueba que extrae datos de una carrera de ejemplo

---

#### 2.2.3 Validación de Carreras Chilenas en Versus

**Descripción**: Confirmar que Versus.es lista las carreras de los hipódromos chilenos y que las cuotas están disponibles.

**Información para el equipo técnico**:
- Versus agrupa carreras bajo "Chilean Horse Racing"
- La estructura es SPA (Single Page Application) - requiere Playwright
- URLs identificadas:
  - Lista de meetings: `/apuestas/sports/horse_racing/meetings/today`
  - Detalle de carrera: `/meetings/{meeting_id}/races/{race_id}`
- Datos a extraer: caballo, dorsal, cuota WIN

**Entregables**:
1. Confirmación de que aparece "Chilean Horse Racing" en meetings
2. Lista de hipódromos chilenos detectados (Hipódromo Chile, Club Hípico, Concepción)
3. Volumen de carreras/día típico
4. Selectores CSS para extracción de cuotas

**Notas importantes**:
- Versus usa clases con prefijo `ta-` (ej: `.ta-SelectionButtonView`)
- Los IDs de carrera están embebidos en clases CSS
- Ver documento PLAN_SCRAPING.md para detalles técnicos

---

#### 2.2.4 Validación de Fuente de Resultados Oficiales

**Descripción**: Identificar fuente fiable para obtener resultados oficiales y cerrar los bets (settlement).

**Información para el equipo técnico**:
- Opciones prioritarias:
  1. Sección "Resultados" de cada hipódromo
  2. Teletrak.cl post-carrera
  3. Versus.es (si muestra resultados)
- Datos necesarios: posición final, status (corrió/retirado)
- Preferir HTML estructurado sobre PDFs

**Entregables**:
1. URL de fuente de resultados elegida
2. Formato de datos disponible (HTML/PDF/API)
3. Horario de disponibilidad post-carrera
4. Script de prueba de extracción

---

#### 2.2.5 Medición de Volumen Real

**Descripción**: Cuantificar el volumen real de carreras chilenas disponibles.

**Información para el equipo técnico**:
- Medir durante 1 semana completa
- Registrar por día: número de meetings, número de carreras, horarios
- Confirmar ventana horaria (17:00-23:00 CET estimado)

**Entregables**:
1. Tabla con volumen por día de la semana
2. Horarios de inicio/fin típicos
3. Confirmación de que hay suficiente volumen para paper trading

---

### 2.3 Checklist de Validación

- [ ] Teletrak: Acceso público confirmado
- [ ] Teletrak: Selectores DOM documentados
- [ ] Versus: Carreras chilenas visibles
- [ ] Versus: Selectores DOM documentados
- [ ] Versus: IDs de carrera extraíbles
- [ ] Resultados: Fuente identificada
- [ ] Volumen: Medición de 1 semana completa

---

## 3. Fase 1: Implementación Paper

### 3.1 Objetivo de la Fase

Construir el sistema completo de detección de value bets en modo paper trading (sin dinero real), con alertas funcionales.

**Duración estimada**: 3-4 semanas

**Criterio de éxito**: Sistema funcionando end-to-end, generando alertas de value que se registran en BD y se envían vía Telegram.

---

### 3.2 Tareas de la Fase

#### 3.2.1 Configuración de Infraestructura

**Descripción**: Preparar el entorno de desarrollo y producción.

**Información para el equipo técnico**:
- Hardware: MiniPC con Ubuntu Server (ya disponible)
- Base de datos: PostgreSQL 15+
- Python 3.11+ con virtualenv
- Playwright instalado con browsers

**Subtareas**:
1. Instalar PostgreSQL y crear base de datos `chilesharp`
2. Crear usuario de BD con permisos apropiados
3. Configurar Python venv con dependencias
4. Instalar Playwright y browsers headless
5. Configurar variables de entorno (.env)

**Entregables**:
1. Script de setup automatizado
2. Archivo requirements.txt actualizado
3. Archivo .env.example con variables necesarias

---

#### 3.2.2 Implementación de Modelo de Datos

**Descripción**: Crear las tablas de la base de datos según el diseño documentado.

**Información para el equipo técnico**:
- Ver documento DISENO_BD.md para esquema completo
- Usar SQLAlchemy 2.0 como ORM
- Usar Alembic para migrations
- Priorizar tablas en orden de dependencia

**Orden de creación**:
1. `bookmakers` (catálogo, datos iniciales)
2. `meetings` (agrupación de carreras)
3. `races` (carreras individuales)
4. `runners` (caballos participantes)
5. `external_ids` (mapeo de IDs por bookmaker)
6. `odds_snapshots` (tabla de alto volumen)
7. `value_bets` (señales generadas)
8. `race_results` (para settlement)

**Entregables**:
1. Archivo `db/models.py` con todos los modelos
2. Migrations en `db/migrations/`
3. Script de seed con datos iniciales de bookmakers

---

#### 3.2.3 Implementación de Scraper de Programa Diario (Teletrak)

**Descripción**: Scraper que descarga el programa de carreras del día desde Teletrak.

**Información para el equipo técnico**:
- Frecuencia: 1 vez/día (mañana, antes de primera carrera)
- Objetivo: Obtener lista de carreras y caballos
- Insertar en: `meetings`, `races`, `runners`
- Crear mapeo en `external_ids` para Teletrak

**Lógica de negocio**:
1. Navegar a página de programa del día
2. Extraer cada carrera: hipódromo, número, hora
3. Por cada carrera, extraer lista de caballos: nombre, dorsal
4. Normalizar nombres para matching futuro
5. Insertar en BD (upsert para evitar duplicados)

**Entregables**:
1. `scrapers/teletrak_program.py`
2. Tests unitarios de parsing
3. Logs estructurados

---

#### 3.2.4 Implementación de Scraper de Odds (Teletrak)

**Descripción**: Scraper que hace polling de las cuotas del pool en Teletrak durante ventana activa.

**Información para el equipo técnico**:
- Frecuencia: Cada 10-15 segundos durante ventana activa
- Ventana activa: T-10 a T-1 minutos antes del off
- Objetivo: Capturar snapshots de cuotas para cálculo de p_fair
- Insertar en: `odds_snapshots`

**Lógica de negocio**:
1. Identificar carreras en ventana activa (query a BD)
2. Para cada carrera activa, navegar a URL de Teletrak
3. Extraer cuota "Prob" de cada caballo
4. Insertar snapshot con timestamp UTC
5. Emitir evento para trigger inmediato del engine

**Optimizaciones para latencia**:
- Browser persistente (no crear/cerrar por request)
- Múltiples tabs/pages para carreras paralelas
- Caché de URLs de carrera

**Entregables**:
1. `scrapers/teletrak_odds.py`
2. Tests de extracción
3. Métricas de latencia por scraping

---

#### 3.2.5 Implementación de Scraper de Discovery (Versus)

**Descripción**: Scraper que descubre las carreras chilenas disponibles en Versus.

**Información para el equipo técnico**:
- Frecuencia: 1 vez/día (mañana)
- Objetivo: Obtener meeting_id y race_id de carreras chilenas
- URL: `/apuestas/sports/horse_racing/meetings/today`
- Filtrar: Solo "Chilean Horse Racing"

**Lógica de negocio**:
1. Navegar a página de meetings de hoy
2. Esperar carga completa del DOM
3. Localizar sección "Chilean Horse Racing"
4. Extraer cada meeting: nombre del hipódromo, IDs de carreras
5. Crear/actualizar `external_ids` con mapeo Versus

**Entregables**:
1. `scrapers/versus_discovery.py`
2. Tests de parsing de meetings
3. Lógica de matching meeting Versus ↔ meeting Teletrak

---

#### 3.2.6 Implementación de Scraper de Odds (Versus)

**Descripción**: Scraper que hace polling de las cuotas fijas en Versus durante ventana activa.

**Información para el equipo técnico**:
- Frecuencia: Cada 15-20 segundos durante ventana activa
- Requiere: Playwright (es SPA)
- URL directa: `/meetings/{meeting_id}/races/{race_id}`
- Datos: caballo, dorsal, cuota WIN

**Lógica de negocio**:
1. Identificar carreras con external_id de Versus en ventana activa
2. Navegar directamente a URL de carrera
3. Esperar carga de cuotas (`.ta-SelectionButtonView`)
4. Extraer por cada caballo: dorsal, nombre, cuota
5. Hacer matching con runner existente (por nombre normalizado)
6. Insertar snapshot con bookmaker_id de Versus
7. Trigger inmediato al engine

**Manejo de errores**:
- Cuota "SP" (sin precio): marcar caballo como no disponible
- Carrera no encontrada: marcar como CANCELLED
- Timeout: retry con backoff

**Entregables**:
1. `scrapers/versus_odds.py`
2. Tests de extracción con mocks de Playwright
3. Logs de latencia y errores

---

#### 3.2.7 Implementación de Engine de Matching

**Descripción**: Módulo que normaliza y empareja nombres de caballos entre fuentes.

**Información para el equipo técnico**:
- Los nombres pueden variar entre Teletrak y Versus
- Diferencias comunes: acentos, sufijos (CHI), números romanos (II, III)
- Matching primario: nombre normalizado + race + dorsal
- Matching secundario: nombre normalizado + race (sin dorsal)

**Función de normalización**:
```
ENTRADA: "GRAN PRÍNCIPE (CHI)"
SALIDA:  "GRAN PRINCIPE"

Transformaciones:
1. Mayúsculas
2. Eliminar sufijos: (CHI), (ARG), II, III, 2, 3
3. Eliminar acentos (á→a, é→e, etc.)
4. Normalizar espacios múltiples
5. Eliminar caracteres especiales
```

**Entregables**:
1. `engine/matching.py`
2. `utils/normalization.py`
3. Tests exhaustivos con casos edge
4. Tabla de correcciones manuales (si aplica)

---

#### 3.2.8 Implementación de Engine de Pricing

**Descripción**: Módulo que calcula probabilidades justas, cuotas fair y edge.

**Información para el equipo técnico**:
- Input: Snapshots de odds de Teletrak y Versus
- Output: p_fair, o_fair, edge por caballo

**Fórmulas (ver PROJECT.md para detalle)**:
```
1. Probabilidad implícita: p̃_i = 1 / D_i (cuota Teletrak)
2. Normalización: p_i = p̃_i / Σ(p̃_j)
3. Cuota justa: O_fair = 1 / p_i
4. Edge: edge = p_i × O_soft - 1
```

**Lógica de negocio**:
1. Obtener últimos snapshots de Teletrak para la carrera
2. Calcular probabilidades normalizadas (quitar vig del pool)
3. Obtener últimos snapshots de Versus para la carrera
4. Por cada caballo con datos en ambas fuentes:
   - Calcular O_fair
   - Calcular edge vs cuota Versus
5. Retornar lista de (runner, p_fair, o_fair, o_soft, edge)

**Entregables**:
1. `engine/pricing.py`
2. Tests con casos conocidos
3. Logging de cálculos para auditoría

---

#### 3.2.9 Implementación de Engine de Señales

**Descripción**: Módulo que evalúa condiciones de value y genera alertas.

**Información para el equipo técnico**:
- Condiciones de value (configurables):
  - `edge >= MIN_EDGE` (10% paper, 15% producción)
  - `O_soft >= O_fair × (1 + DELTA)` (delta = 0.10-0.20)
  - Runner activo (no SCRATCHED)
  - Cuota disponible (no SP)

**Lógica de negocio**:
1. Recibir resultados de pricing
2. Filtrar por edge mínimo
3. Filtrar por delta soft/fair
4. Generar record en `value_bets` con status PENDING
5. Seleccionar primary pick (mayor edge)
6. Enviar alerta inmediata

**Entregables**:
1. `engine/signals.py`
2. `config/settings.py` con umbrales configurables
3. Tests de filtrado
4. Integración con sistema de alertas

---

#### 3.2.10 Implementación de Sistema de Alertas

**Descripción**: Módulo que envía alertas de value bet vía Telegram.

**Información para el equipo técnico**:
- Canal de notificación: Telegram Bot
- Latencia crítica: Alerta debe salir en < 500ms tras detección
- Contenido de alerta:
  - Hipódromo, hora, número de carrera
  - Caballo, dorsal
  - Cuota Versus
  - Edge calculado

**Formato de alerta sugerido**:
```
🏇 VALUE DETECTADO

📍 Club Hípico - Carrera 5
⏰ 18:30 CET (Off en 8 min)

🐎 GRAN PRINCIPE (#4)
💰 Cuota Versus: 5.50
📊 Edge: +18.2%

⚡ Apuesta recomendada: 1 unidad
```

**Entregables**:
1. `utils/telegram.py`
2. Configuración de bot en .env
3. Test de envío de mensajes
4. Rate limiting (evitar spam)

---

#### 3.2.11 Implementación de Scraper de Resultados

**Descripción**: Scraper que descarga resultados oficiales post-carrera.

**Información para el equipo técnico**:
- Frecuencia: 1 vez/día (noche, post-jornada)
- Fuente: Definida en Fase 0
- Datos: Posición final, status (corrió/NR/DNF)

**Lógica de negocio**:
1. Identificar carreras FINISHED sin resultados
2. Navegar a fuente de resultados
3. Extraer posición de cada caballo
4. Insertar en `race_results`
5. Trigger de settlement

**Entregables**:
1. `settlement/results_scraper.py`
2. Parser robusto con fallbacks
3. Logging de carreras sin resultados

---

#### 3.2.12 Implementación de Settlement Automático

**Descripción**: Módulo que cierra los value bets basándose en resultados.

**Información para el equipo técnico**:
- Ejecutar después de obtener resultados
- Actualizar `value_bets` con resultado y profit

**Lógica de settlement**:
```
SI posición = 1:
    result = WIN
    profit = stake × (o_soft - 1)
SI posición > 1 Y status = RAN:
    result = LOSE
    profit = -stake
SI status = NR:
    result = VOID
    profit = 0
```

**Entregables**:
1. `settlement/settle_paper.py`
2. Tests con casos edge (NR, DNF, DQ)
3. Logs de P&L

---

#### 3.2.13 Implementación de Orquestador

**Descripción**: Scripts que coordinan la ejecución de todos los componentes.

**Información para el equipo técnico**:
- `run_scrapers_loop.py`: Orquesta scrapers de odds en ventana activa
- `run_engine_loop.py`: Orquesta engine de pricing/signals
- `run_settlement.py`: Ejecuta settlement diario

**Configuración de scheduling**:
```cron
# Ejemplo crontab
0 9 * * * /path/to/run_discovery.sh      # Discovery AM
* 17-23 * * * /path/to/run_odds.sh       # Odds polling
0 0 * * * /path/to/run_settlement.sh     # Settlement nocturno
```

**Entregables**:
1. `scripts/run_scrapers_loop.py`
2. `scripts/run_engine_loop.py`
3. `scripts/run_settlement.py`
4. Scripts bash wrapper
5. Archivos systemd/cron para scheduling

---

### 3.3 Checklist de Fase 1

- [ ] Infraestructura configurada (PostgreSQL, Python, Playwright)
- [ ] Modelo de datos implementado con migrations
- [ ] Scraper programa Teletrak funcionando
- [ ] Scraper odds Teletrak funcionando
- [ ] Scraper discovery Versus funcionando
- [ ] Scraper odds Versus funcionando
- [ ] Engine de matching funcionando
- [ ] Engine de pricing funcionando
- [ ] Engine de signals funcionando
- [ ] Alertas Telegram funcionando
- [ ] Scraper de resultados funcionando
- [ ] Settlement automático funcionando
- [ ] Orquestación con cron/systemd configurada
- [ ] Sistema corriendo end-to-end durante 1 semana sin intervención

---

## 4. Fase 2: Análisis y Calibración

### 4.1 Objetivo de la Fase

Acumular datos suficientes para validar estadísticamente que el sistema genera value real.

**Duración estimada**: 2-4 semanas (depende del volumen)

**Criterio de éxito**: 200-300 picks acumulados, yield > 5%, CLV positivo.

---

### 4.2 Tareas de la Fase

#### 4.2.1 Acumulación de Datos

**Descripción**: Dejar el sistema en paper trading activo durante 2-4 semanas.

**Información para el equipo técnico**:
- Objetivo: 200-300 picks totales
- Monitoreo diario de errores y uptime
- No ajustar parámetros durante acumulación (evitar overfitting)

**Métricas a trackear diariamente**:
- Número de picks generados
- Edge medio
- Hit rate (% ganadores)
- Errores de scraping

**Entregables**:
1. Dashboard simple (queries SQL o notebook)
2. Export de datos para análisis

---

#### 4.2.2 Análisis de Yield por Bucket de Edge

**Descripción**: Segmentar picks por rango de edge y calcular yield real.

**Información para el equipo técnico**:
- Buckets sugeridos: 10-15%, 15-20%, 20-30%, >30%
- Por cada bucket calcular:
  - Número de picks
  - Yield (profit/stake)
  - Hit rate

**Pregunta a responder**: ¿Mayor edge correlaciona con mayor yield real?

**Entregables**:
1. Query/script de análisis
2. Tabla de resultados por bucket
3. Recomendación de ajuste de MIN_EDGE si aplica

---

#### 4.2.3 Análisis de CLV (Closing Line Value)

**Descripción**: Comparar cuota de entrada vs cuota de cierre.

**Información para el equipo técnico**:
- CLV = (cuota_entrada - cuota_cierre) / cuota_cierre
- CLV positivo = compraste antes de que el mercado se moviera
- Indicador predictivo de edge sostenible

**Cálculo**:
1. Por cada value bet, obtener cuota Versus al momento de alerta
2. Obtener último snapshot de Versus antes del off
3. Calcular CLV

**Entregables**:
1. Query de cálculo de CLV
2. Distribución de CLV (% positivo, media)
3. Análisis de correlación CLV ↔ resultado

---

#### 4.2.4 Análisis de Drawdown

**Descripción**: Evaluar riesgo de pérdida máxima.

**Información para el equipo técnico**:
- Calcular racha perdedora más larga
- Calcular máximo drawdown sobre banca simulada
- Evaluar si stakes deben ajustarse

**Entregables**:
1. Gráfico de evolución de bankroll
2. Métrica de max drawdown
3. Recomendación de bankroll mínimo para producción

---

#### 4.2.5 Calibración de Umbrales

**Descripción**: Ajustar parámetros basándose en resultados.

**Información para el equipo técnico**:
- Parámetros a evaluar:
  - MIN_EDGE (10% → 12%? 15%?)
  - DELTA_SOFT_FAIR (0.10 → 0.15?)
  - Ventana temporal (T-10 → T-8?)
- Solo ajustar si hay evidencia estadística clara

**Entregables**:
1. Documento de calibración con justificación
2. Actualización de `config/settings.py`
3. A/B test si aplica (mantener ambas configuraciones)

---

### 4.3 Checklist de Fase 2

- [ ] 200+ picks acumulados
- [ ] Yield global calculado (target: > 5%)
- [ ] Análisis por bucket de edge completado
- [ ] CLV calculado (target: > 50% positivo)
- [ ] Drawdown máximo evaluado
- [ ] Umbrales calibrados si necesario
- [ ] Documento de análisis final con recomendación GO/NO-GO

---

## 5. Fase 3: Producción Limitada

### 5.1 Objetivo de la Fase

Comenzar apuestas con dinero real, con stakes pequeños y monitoreo exhaustivo.

**Duración estimada**: 2-4 semanas

**Criterio de éxito**: P&L positivo, sistema estable, sin limitación de cuenta.

---

### 5.2 Tareas de la Fase

#### 5.2.1 Configuración de Cuenta Versus

**Descripción**: Preparar cuenta real de Versus para apuestas.

**Información para el equipo técnico**:
- Verificación de cuenta completada
- Fondos depositados
- Límites de apuesta conocidos
- Segunda cuenta (backup) recomendada

**Entregables**:
1. Cuenta verificada y fondeada
2. Documentación de límites

---

#### 5.2.2 Activación de Modo LIVE

**Descripción**: Cambiar sistema de PAPER a LIVE.

**Información para el equipo técnico**:
- Cambio en config: `MODE = 'LIVE'`
- MIN_EDGE aumentado a 15%
- Stakes conservadores (1-2% de bankroll)
- Alertas ahora son instrucciones de apuesta real

**Entregables**:
1. Config de producción
2. Proceso de apuesta manual documentado (si no hay automatización)

---

#### 5.2.3 Monitoreo de Performance Real

**Descripción**: Tracking exhaustivo de resultados reales.

**Información para el equipo técnico**:
- Comparar P&L real vs P&L paper del mismo período
- Detectar discrepancias (slippage, rechazos)
- Monitorear señales de limitación de cuenta

**Señales de alerta**:
- Apuestas rechazadas
- Stakes máximos reducidos
- Cuotas peores que las mostradas

**Entregables**:
1. Dashboard de P&L real
2. Alertas de anomalías
3. Decisión de escalar o pausar

---

#### 5.2.4 Integración de Notificaciones Avanzadas

**Descripción**: Mejorar sistema de alertas para operación real.

**Información para el equipo técnico**:
- Confirmación de apuesta colocada
- Resultados en tiempo real
- Resumen diario de P&L
- Alertas de errores críticos

**Entregables**:
1. Nuevos formatos de mensaje Telegram
2. Resumen diario automatizado

---

### 5.3 Checklist de Fase 3

- [ ] Cuenta Versus configurada
- [ ] Modo LIVE activado
- [ ] Stakes conservadores definidos
- [ ] 2 semanas de operación real
- [ ] P&L real vs paper comparado
- [ ] Sin señales de limitación
- [ ] Decisión de escalar documentada

---

## 6. Fase 4: Escalado

### 6.1 Objetivo de la Fase

Aumentar volumen, añadir más fuentes y optimizar arquitectura.

**Duración estimada**: Ongoing

---

### 6.2 Tareas de la Fase

#### 6.2.1 Arquitectura Event-Driven

**Descripción**: Migrar de polling a arquitectura event-driven para máxima latencia.

**Información para el equipo técnico**:
- Reemplazar polling con streams de eventos
- Opciones: Redis Streams, RabbitMQ, Kafka
- Pricing engine en memoria, recalcula por evento
- Sub-segundo de latencia objetivo

**Arquitectura objetivo**:
```
[Ingestors] → [Message Queue] → [Pricing Engine] → [Alerter]
     ↓                               ↓
   [DB]                           [DB]
```

**Entregables**:
1. POC de arquitectura event-driven
2. Migración gradual
3. Métricas de latencia antes/después

---

#### 6.2.2 Añadir Otras Softs Españolas

**Descripción**: Integrar más bookmakers españoles para arbitrar.

**Información para el equipo técnico**:
- Candidatas: Betway, Codere, Luckia, Sportium
- El diseño de BD ya soporta múltiples bookmakers
- Requiere nuevo scraper por cada soft
- Comparar cuotas de múltiples softs por cada carrera

**Entregables por cada soft**:
1. Scraper de discovery
2. Scraper de odds
3. Tests de integración

---

#### 6.2.3 Añadir Otros Mercados Sharp

**Descripción**: Incorporar pools de otros países como referencia.

**Información para el equipo técnico**:
- Candidatas: México (Hipódromo de las Américas), Panamá
- Evaluar eficiencia del pool (dinero informado)
- Requiere scrapers específicos por fuente

**Entregables**:
1. Estudio de viabilidad por país
2. Scrapers según prioridad

---

#### 6.2.4 Mercados PLACE

**Descripción**: Extender sistema a mercado de colocado.

**Información para el equipo técnico**:
- Modelo de datos ya soporta `market_type = 'PLACE'`
- Requiere lógica de settlement diferente (top 2 o 3 paga)
- Evaluar edge típico en PLACE vs WIN

**Entregables**:
1. Lógica de pricing para PLACE
2. Settlement para PLACE
3. Análisis de yield PLACE

---

#### 6.2.5 API y Dashboard

**Descripción**: Crear interfaz web para monitoreo y operación.

**Información para el equipo técnico**:
- Framework: FastAPI para backend
- Dashboard: Simple HTML/JS o Streamlit
- Funcionalidades:
  - Ver carreras activas
  - Historial de bets
  - P&L en tiempo real
  - Configuración de umbrales

**Entregables**:
1. API REST con endpoints básicos
2. Dashboard de monitoreo
3. Autenticación básica

---

### 6.3 Checklist de Fase 4

- [ ] Arquitectura event-driven implementada
- [ ] Al menos 1 soft adicional integrada
- [ ] Latencia < 500ms confirmada
- [ ] Mercado PLACE evaluado
- [ ] Dashboard de monitoreo disponible

---

## 7. Dependencias entre Fases

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIAGRAMA DE DEPENDENCIAS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FASE 0                    FASE 1                               │
│  ┌─────────────┐           ┌─────────────────────┐             │
│  │ Validación  │ ────────▶ │ Modelo de datos     │             │
│  │ Teletrak    │           └──────────┬──────────┘             │
│  └─────────────┘                      │                        │
│  ┌─────────────┐                      ▼                        │
│  │ Validación  │           ┌─────────────────────┐             │
│  │ Versus      │ ────────▶ │ Scrapers            │             │
│  └─────────────┘           └──────────┬──────────┘             │
│  ┌─────────────┐                      │                        │
│  │ Validación  │                      ▼                        │
│  │ Resultados  │           ┌─────────────────────┐             │
│  └──────┬──────┘           │ Engine              │             │
│         │                  └──────────┬──────────┘             │
│         │                             │                        │
│         │                             ▼                        │
│         │                  ┌─────────────────────┐             │
│         └────────────────▶ │ Settlement          │             │
│                            └──────────┬──────────┘             │
│                                       │                        │
│                                       ▼                        │
│  FASE 2                    ┌─────────────────────┐  FASE 3     │
│  ┌─────────────┐           │ Orquestación        │             │
│  │ Acumulación │ ◀─────────┴─────────────────────┘             │
│  │ 200+ picks  │                                               │
│  └──────┬──────┘                                               │
│         │                                                      │
│         ▼                                                      │
│  ┌─────────────┐           ┌─────────────────────┐             │
│  │ Análisis    │ ────────▶ │ Producción LIVE     │             │
│  │ GO/NO-GO    │           └──────────┬──────────┘             │
│  └─────────────┘                      │                        │
│                                       ▼                        │
│                            FASE 4                              │
│                            ┌─────────────────────┐             │
│                            │ Escalado            │             │
│                            └─────────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Criterios de Éxito

### 8.1 Métricas Técnicas

| Métrica | Target | Crítico |
|---------|--------|---------|
| Latencia scraping→alerta | < 2s | ✅ |
| Uptime de scrapers | > 99% | ✅ |
| Tasa de matching de caballos | > 95% | ✅ |
| Errores de scraping/día | < 10 | |

### 8.2 Métricas de Negocio

| Métrica | Target | Fase |
|---------|--------|------|
| Yield (ROI) | > 5% | Fase 2+ |
| CLV positivo | > 50% picks | Fase 2+ |
| Edge medio | > 10% | Fase 1+ |
| Picks/semana | > 20 | Fase 1+ |

### 8.3 Criterios GO/NO-GO

**Para pasar de Fase 2 a Fase 3**:
- [ ] Yield > 5% con 200+ picks
- [ ] CLV positivo en >50% de picks
- [ ] Edge correlaciona con yield
- [ ] Max drawdown < 25% bankroll simulado
- [ ] Sin errores sistemáticos de scraping

---

*Documento generado: 2026-02-03*
*Versión: 1.0*
