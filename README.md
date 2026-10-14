# Industrial Maintenance BI

> Business Intelligence dashboard for industrial maintenance analysis: find costliest machines, breakdown-prone machines, slowest repairs, MTBF/MTTR, and the machines that should be checked next.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-19-61dafb)
![Chart.js](https://img.shields.io/badge/Chart.js-4-ff6384)
![SQLite](https://img.shields.io/badge/SQLite-3-003b57)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 1. What this project answers

| Question | KPI |
|---|---|
| Which machines cost the most? | `total_cost` |
| Which machines break down the most? | `total_breakdowns` |
| Which machines take longest to repair? | `avg_mttr` |
| How long between breakdowns? | `avg_mtbf` |
| Which machines should be checked? | rank-based score (0–4) |

**Current findings** (100 records, 12 machines, 2026-01 → 2026-09):

| Global | Value |
|---|---|
| Total cost | 76,178.06 |
| Total breakdowns | 334 |
| Avg MTBF | 52.45 h |
| Avg MTTR | 2.81 h |
| Machines to check | **M-05** (score 4), M-11, M-10, M-02 |

---

## 2. Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite | fast dev server, component model |
| Charts | Chart.js + react-chartjs-2 | lightweight, declarative charts |
| Styling | Plain CSS | no framework overhead, easy to read |
| Backend | FastAPI | auto `/docs`, typed routes, async ready |
| ORM | SQLAlchemy | readable models, DB portability |
| Database | SQLite | zero config, single file, perfect for this size |
| Data | CSV + Python `csv` stdlib | no heavy dependencies |
| Validation | custom `etl.py` | transparent rules, printed report |

---

## 3. Architecture

```
mantenimiento_final.csv
        │
        ▼
┌───────────────────┐     ┌──────────────┐
│  ETL (etl.py)     │────▶│  SQLite      │
│  validate + load  │     │ maintenance  │
└───────────────────┘     │ .db          │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  FastAPI     │   /api/overview
                          │  KPI engine  │   /api/machines
                          │  (kpis.py)   │   /api/alerts
                          └──────┬───────┘   /api/timeseries
                                 │
                          ┌──────▼───────┐
                          │  React       │   KPI cards
                          │  + Chart.js  │   charts + alerts
                          └──────────────┘   machine detail
```

---

## 4. User stories

### US-1 — Data ingestion & validation ✅
*As analyst, I load the CSV into the DB so data is clean and trustworthy.*

| # | Subtask | Status |
|---|---------|--------|
| 1.1 | Project scaffold (`backend/`, `data/`) | ✅ |
| 1.2 | Schema: `machines`, `maintenance_records` + CHECK/UNIQUE constraints | ✅ |
| 1.3 | Reader: `utf-8-sig` (BOM-safe), type coercion, date parse | ✅ |
| 1.4 | Validator: NULLs, duplicates, negatives, `breakdowns > 0`, formula drift | ✅ |
| 1.5 | Idempotent load (re-run = no duplicates) | ✅ |

### US-2 — KPI engine ✅
*As manager, I get correct KPIs per machine.*

| # | Subtask | Status |
|---|---------|--------|
| 2.1 | Aggregations: Σcost, Σbreakdowns, avg MTBF, avg MTTR | ✅ |
| 2.2 | Rank-based scoring (worst quartile per KPI → score 0–4) | ✅ |
| 2.3 | Alert rule: score ≥ 2 → priority list | ✅ |

### US-3 — REST API ✅
*As frontend, I consume KPI endpoints.*

| # | Subtask | Status |
|---|---------|--------|
| 3.1 | FastAPI app + CORS + SQLite session | ✅ |
| 3.2–3.6 | `/overview`, `/machines`, `/machines/{id}`, `/alerts`, `/timeseries` | ✅ |
| 3.7 | `curl` verification vs CSV | ✅ |

### US-4 — Dashboard ✅
*As stakeholder, I see everything at a glance.*

| # | Subtask | Status |
|---|---------|--------|
| 4.1 | Vite scaffold, plain CSS, `api.js` fetch wrappers | ✅ |
| 4.2 | KPI cards (cost, breakdowns, MTBF, MTTR) | ✅ |
| 4.3–4.6 | Cost bar, breakdowns bar, MTBF/MTTR bar, monthly trend line | ✅ |
| 4.7 | Alert table (machine, score, reasons) | ✅ |
| 4.8 | Machine detail view (dropdown + monthly chart) | ✅ |

### US-5 — Verification ✅
*As owner, I trust the deliverable.*

| # | Subtask | Status |
|---|---|---|
| 5.1 | Fresh DB rebuild → 100 rows, 0 errors | ✅ |
| 5.2 | Endpoint spot-check vs CSV (M-04, M-08, M-12) | ✅ exact match |
| 5.3 | `npm run build` clean | ✅ |
| 5.4 | README with run commands | ✅ |

---

## 5. Data pipeline

Source: `data/mantenimiento_final.csv` — 100 rows, 12 machines.

**Validation rules** (`backend/app/etl.py`):

1. UTF-8 with BOM handled (`utf-8-sig`)
2. No NULL / empty values in any column
3. No duplicate `IDRegistro`
4. Date matches `YYYY-MM-DD`
5. All numeric columns parse and are ≥ 0
6. `breakdowns > 0` (division safety)
7. **Drift check**: file MTBF/MTTR/CostePorAveria vs recomputed → recompute wins, drift reported

To reload after CSV change:

```bash
cd backend
rm maintenance.db        # full rebuild (optional: keep file for incremental)
python3 -m app.etl
```

---

## 6. KPI definitions

| KPI | Formula | Question |
|---|---|---|
| `total_cost` | `SUM(cost)` | which machines cost most |
| `total_breakdowns` | `SUM(breakdowns)` | which machines break down most |
| `avg_mtbf` | `SUM(hours) / SUM(breakdowns)` | average time between breakdowns |
| `avg_mttr` | `SUM(repair_hours) / SUM(breakdowns)` | average time to repair |
| `avg_cost_per_breakdown` | `SUM(cost) / SUM(breakdowns)` | cost efficiency |

### "Should be checked" rule — no magic thresholds

1. Rank all machines per KPI — cost / breakdowns / MTTR high = bad, MTBF low = bad
2. Flag machines in the **worst quartile**: `ceil(25% × 12) = 3` machines per KPI
3. `score` = number of flags (0–4) → **score ≥ 2 = CHECK**

Works on any dataset size, adapts automatically.

---

## 7. API reference

Base URL: `http://localhost:8000` · Interactive docs: `/docs`

| Endpoint | Returns |
|---|---|
| `GET /api/overview` | global totals + avg MTBF/MTTR |
| `GET /api/machines` | per-machine KPIs, flags, score, priority |
| `GET /api/machines/{id}` | one machine + monthly series |
| `GET /api/alerts` | score ≥ 2 machines, worst first |
| `GET /api/timeseries?metric=cost\|breakdowns\|mtbf\|mttr` | monthly trend |

Example — `GET /api/alerts`:

```json
[
  {
    "machine": "M-05",
    "total_cost": 10371.51,
    "total_breakdowns": 42,
    "avg_mtbf": 45.64,
    "avg_mttr": 3.41,
    "score": 4,
    "priority": "CHECK",
    "flag_reasons": ["major costs", "frequent breakdowns", "slow repairs", "short time between breakdowns"]
  }
]
```

---

## 8. Quick start

```bash
# 1. Clone
git clone https://github.com/Medbdnt21/Industrial-Maintenance-BI.git
cd Industrial-Maintenance-BI

# 2. Backend
python3 -m pip install --user -r backend/requirements.txt
cd backend
python3 -m app.etl                              # validate + load (prints report)
python3 -m uvicorn app.main:app --port 8000     # API on :8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                                     # dashboard on :5173
```

Open **http://localhost:5173** — backend must be running first.

---

## 9. Project structure

```
Industrial-Maintenance-BI/
├── data/
│   └── mantenimiento_final.csv      # source data (Spanish headers)
├── backend/
│   ├── requirements.txt
│   ├── maintenance.db               # created by ETL (not in git)
│   └── app/
│       ├── main.py                  # FastAPI app + CORS
│       ├── db.py                    # SQLite engine + session
│       ├── models.py                # tables + constraints
│       ├── etl.py                   # CSV → validate → load
│       ├── kpis.py                  # KPI + scoring engine (docs inside)
│       ├── series.py                # monthly aggregation
│       ├── schemas.py               # response models
│       └── routers/                 # overview, machines, alerts, timeseries
├── frontend/
│   └── src/
│       ├── api.js                   # fetch wrappers
│       ├── App.jsx                  # layout + data loading
│       └── components/
│           ├── KpiCards.jsx          # global KPI cards
│           ├── CostChart.jsx         # cost by machine
│           ├── BreakdownChart.jsx    # breakdowns by machine
│           ├── MtbfMttrChart.jsx     # MTBF vs MTTR
│           ├── TrendChart.jsx        # monthly cost + breakdowns
│           ├── AlertTable.jsx        # machines to check
│           └── MachineDetail.jsx     # per-machine view
├── README.md
└── .gitignore
```

---

## 10. Verification results

| Check | Result |
|---|---|
| ETL fresh rebuild | 100/100 rows, 0 errors, 0 drift |
| Idempotent re-run | `skipped_existing=100`, no duplicates |
| DB integrity | `PRAGMA integrity_check = ok` |
| API endpoints | all 200; 404 + 422 error cases work |
| KPI vs CSV (M-04, M-08, M-12) | exact match |
| Frontend build | clean, ~401 KB bundle |

---

## 11. Roadmap

- [ ] Auto-refresh dashboard (polling / websockets)
- [ ] Export alerts + KPIs to CSV/PDF
- [ ] Predictive flag: rising cost trend per machine
- [ ] Unit tests (`pytest`) for ETL + KPI engine
- [ ] Swap SQLite → MySQL/Postgres (SQLAlchemy makes this one line)

---

## License

MIT
