# ChileSharp - Value Betting Automation System

<p align="center">
  <strong>Sistema automatizado de detección de value bets en carreras de caballos chilenas</strong>
</p>

---

## 📋 Descripción

ChileSharp es un sistema que explota la asimetría de información entre el pool parimutuel de **Teletrak.cl** (donde apuestan insiders chilenos) y las casas de apuestas españolas como **Versus.es** (con cuotas fijas menos eficientes).

El sistema detecta automáticamente cuándo las cuotas de Versus ofrecen valor positivo respecto a las probabilidades "reales" derivadas del pool de Teletrak, y envía alertas en tiempo real.

```
🏇 VALUE DETECTADO

📍 Club Hípico - Carrera 5
⏰ 18:30 CET (Off en 8 min)

🐎 GRAN PRINCIPE (#4)
💰 Cuota Versus: 5.50
📊 Edge: +18.2%
```

---

## 🎯 Propuesta de Valor

| Sharp (Referencia) | Soft (Explotación) |
|--------------------|-------------------|
| **Teletrak.cl** | **Versus.es** |
| Pool parimutuel con dinero de insiders | Cuotas fijas, mercado chileno secundario |
| Refleja probabilidades "reales" | Actualización lenta → oportunidad |

**Edge**: Cuando `P_fair × O_soft > 1.10` → Value Bet

---

## 📚 Documentación

### Documentos Principales

| Documento | Propósito |
|-----------|-----------|
| [PROJECT.md](./PROJECT.md) | Especificación completa del proyecto |
| [CLAUDE.md](./CLAUDE.md) | Guía rápida para desarrollo |

### Documentación Técnica (docs/)

| Documento | Propósito |
|-----------|-----------|
| [ROADMAP.md](./docs/ROADMAP.md) | Fases del proyecto con tareas detalladas |
| [DISENO_BD.md](./docs/DISENO_BD.md) | Diseño de base de datos optimizado |
| [PLAN_SCRAPING.md](./docs/PLAN_SCRAPING.md) | Estrategia de scraping de Versus |

---

## 🏗️ Arquitectura

```
horses/
├── config/           # Configuración (umbrales, polling)
├── db/               # Modelos SQLAlchemy y migrations
├── engine/           # Matching, pricing y señales
├── scrapers/         # Scrapers de Teletrak y Versus
├── scripts/          # Orquestadores y utilidades
├── settlement/       # Resultados y cierre de bets
├── utils/            # Normalización, timezone, etc.
└── docs/             # Documentación técnica
```

---

## 🚀 Fases del Proyecto

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 0** | 🟡 En progreso | Validación de acceso y cobertura |
| **Fase 1** | ⚪ Pendiente | Paper trading completo |
| **Fase 2** | ⚪ Pendiente | Análisis estadístico (200+ picks) |
| **Fase 3** | ⚪ Pendiente | Producción limitada |
| **Fase 4** | ⚪ Pendiente | Escalado (múltiples softs, event-driven) |

Ver [ROADMAP.md](./docs/ROADMAP.md) para detalle de cada fase.

---

## ⚡ Métrica Crítica

```
LATENCIA MÁXIMA: < 2 segundos
Scraping → Cálculo de Value → Envío de Alerta
```

El valor del sistema depende de la velocidad. El diseño prioriza latencia mínima en todas las decisiones.

---

## 📊 Modelo Matemático

### Cálculo de Probabilidad Fair

```
p̃_i = 1 / D_i           # Prob implícita con vig
p_i = p̃_i / Σ(p̃_j)      # Normalizada (sin comisión)
O_fair = 1 / p_i         # Cuota justa
```

### Cálculo de Edge

```
edge = p_i × O_soft - 1
```

**Ejemplo**: Si `p_fair = 0.22` (22%) y `O_soft = 5.50`:
```
edge = 0.22 × 5.50 - 1 = 0.21 = +21% de valor esperado
```

---

## 🛠️ Tech Stack

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.11+ |
| Base de datos | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Browser Automation | Playwright |
| HTTP | requests, httpx |
| Parsing | BeautifulSoup4 |
| Scheduling | cron, systemd |
| Alertas | Telegram Bot |

---

## 📈 KPIs Target

| KPI | Target |
|-----|--------|
| Yield (ROI) | > 5% |
| Edge medio | ≥ 10-15% |
| CLV positivo | > 50% picks |
| Uptime scrapers | > 99% |

---

## 🔧 Configuración

Parámetros principales en `config/settings.py`:

```python
MIN_EDGE = 0.10                    # 10% (paper)
MIN_EDGE_PRODUCTION = 0.15         # 15% (live)
DELTA_SOFT_FAIR = 0.10             # O_soft >= O_fair × 1.10
WINDOW_START_MINUTES = 10          # Ventana: T-10
WINDOW_END_MINUTES = 1             # Hasta: T-1
TELETRAK_POLL_INTERVAL = 15        # Segundos
VERSUS_POLL_INTERVAL = 20          # Segundos
```

---

## 📖 Referencias de Decisiones

### Decisiones de Diseño

1. **Multi-bookmaker desde el inicio**: El modelo de BD soporta múltiples sharps y softs sin migración.
   - Ver: [DISENO_BD.md](./docs/DISENO_BD.md#22-multi-bookmaker-desde-el-inicio)

2. **Playwright obligatorio para Versus**: Versus es una SPA que requiere ejecución de JavaScript.
   - Ver: [PLAN_SCRAPING.md](./docs/PLAN_SCRAPING.md#51-herramienta-recomendada)

3. **Solo WIN inicialmente**: Mercado PLACE preparado pero no activo.
   - Ver: [DISENO_BD.md](./docs/DISENO_BD.md#92-añadir-mercado-place)

4. **Datos mínimos**: Solo caballo, dorsal y cuota. Sin trainer, jockey, form.
   - Ver: [DISENO_BD.md](./docs/DISENO_BD.md#23-datos-mínimos-necesarios)

### Documentos de Referencia

- **Especificación completa**: [PROJECT.md](./PROJECT.md)
- **Modelo de datos**: [PROJECT.md → Sección 5](./PROJECT.md#5-modelo-de-datos)
- **Fórmulas matemáticas**: [PROJECT.md → Sección 3](./PROJECT.md#3-modelo-matemático)
- **Riesgos y mitigaciones**: [PROJECT.md → Sección 14](./PROJECT.md#14-riesgos-y-mitigaciones)

---

## 🚦 Estado Actual

**Fase**: 0 - Validación

**Progreso**:
- [x] Estructura de proyecto creada
- [x] Documentación base (CLAUDE.md, PROJECT.md)
- [x] Exploración de Versus.es completada
- [ ] Validación de Teletrak.cl
- [ ] Validación de fuente de resultados
- [ ] Medición de volumen de carreras

---

## 📞 Contacto

*Proyecto privado - Value betting automation*

---

*Última actualización: 2026-02-03*
