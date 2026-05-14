# ARQuant Marketing Materials — User Guide

How to run the monthly reporting pipeline that produces the website slides,
the investor factsheet, and the AMC EUR-hedged simulation (which also
refreshes the ETI landing page on OneDrive).

The three entry-point scripts are:

| Script | Purpose |
|---|---|
| `ARQUANT_slides_ver_2026_05.py` | Slides for the website and PowerPoint |
| `ARQUANT_factsheet_2026_05.py` | Monthly investor factsheet (HTML + PDF) |
| `AMC_EUR_hedged_simulation_2026_05.py` | EUR-hedged AMC backtest + ETI landing-page update |

---

## 1. Prerequisites

### Python environment

Conda env `ARQuant37_pip` (Python 3.7), located at
`/Users/alexander/opt/anaconda3/envs/ARQuant37_pip`.

Always run with the **explicit interpreter** to avoid env mismatches:

```bash
/Users/alexander/opt/anaconda3/envs/ARQuant37_pip/bin/python <script>.py
```

The scripts also work inside Jupyter / IPython (they use `%autoreload`).

### Folder layout

The project is **location-independent**: each script derives its paths
from its own file location. Data must live **one directory above** the
project root:

```
Python/
├── ARQuant marketing materials/      ← this repo (scripts)
└── Data/                             ← all inputs/outputs
    ├── ARQuant_history/              ← IBKR FlexReport CSVs (manual download)
    ├── Indexes/                      ← Eurekahedge / Fama-French / cached SPY, VIX
    ├── ETI_EUR_hedged/               ← AMC simulation inputs/outputs
    ├── EUR_hedge/                    ← USD net monthly returns (input to AMC sim)
    ├── Presentation_<YYYY-MM>/       ← slides outputs (auto-created)
    └── Factsheet_<YYYY-MM>/          ← factsheet outputs (auto-created)
```

---

## 2. Monthly workflow at a glance

Each month:

1. **Download two IBKR FlexReport CSVs** for the relevant entity
   (`ARQuant_Management_Limited` or `AVESA_Group_Ltd`) into
   `../Data/ARQuant_history/`:
   - `<entity>_<Month_YYYY>_<Month_YYYY>_daily.csv`
   - `<entity>_<January_YYYY>_<Month_YYYY>_monthly.csv` (YTD)
2. **Edit `new_end`** at the top of the script you want to run, e.g.
   `'2026-05-31'` (last calendar day of the reporting month).
3. Run the script.

If the expected CSVs are missing, the script prints the exact filenames it
needs and calls `sys.exit()` — no partial run.

---

## 3. Slides — `ARQUANT_slides_ver_2026_05.py`

Generates HTML slides for the **website** and PNG/HTML assets for
**PowerPoint**.

**What to edit:**

- Line ~44 — `new_end = 'YYYY-MM-DD'` (last calendar day of the reporting month)
- `params['PP_pages_stat']` (around line ~128) — selects which periods appear
  on the three PowerPoint stat-table pages. **Use the literal string `'YTD'`**
  (not the year number) for the current-year column.

**Inputs:**

- IBKR FlexReports in `../Data/ARQuant_history/`
- Cached benchmark indexes and Fama-French factors in `../Data/Indexes/`

**Outputs** (in `../Data/Presentation_<YYYY-MM>/`):

- `Website_slides/` — HTML slides via `update_web()`
- `PowerPoint/` — PNGs and HTML tables via `update_PowerPoint()`
- Pickled intermediate results in `Presentation_Inputs/`

**Run:**

```bash
/Users/alexander/opt/anaconda3/envs/ARQuant37_pip/bin/python ARQUANT_slides_ver_2026_05.py
```

---

## 4. Factsheet — `ARQUANT_factsheet_2026_05.py`

Generates the monthly investor factsheet as HTML and PDF.

**What to edit:**

- Line ~44 — `new_end = 'YYYY-MM-DD'`

**Inputs:**

- Same IBKR FlexReports as the slides pipeline
- Benchmark indexes & Fama-French caches in `../Data/Indexes/`
- Risk-free rate pulled live from FRED (with retry/fallback)

**Outputs** (in `../Data/Factsheet_<YYYY-MM>/`):

- HTML factsheet
- PDF factsheet (rendered with `weasyprint`)

**Run:**

```bash
/Users/alexander/opt/anaconda3/envs/ARQuant37_pip/bin/python ARQUANT_factsheet_2026_05.py
```

If FRED times out, you will see a warning but the run continues using the
last-known risk-free rate.

---

## 5. AMC EUR-hedged simulation — `AMC_EUR_hedged_simulation_2026_05.py`

Runs the EUR-hedged backtest of the ARQuant strategy + 30% SPY overlay,
and (at the end) pushes the latest figures into the ARQuant ETI multilang
landing page on OneDrive.

**What to edit:**

- Line ~34–35:
  - `period_start` — usually `'2018-03'` (strategy inception)
  - `period_end` — e.g. `'2026-05'` (the new end of the simulation window)
- Line ~42 — `_EURIBOR_OVERRIDES` (optional): pin Euribor 1M for a specific
  `'YYYY-MM'` to a value in percent when you have something more authoritative
  than carry-forward (e.g. EMMI daily fixing or an internal estimate). If
  empty, missing trailing months are automatically filled from the previous
  month — no manual edits required.

> Note: this script uses **`period_start` / `period_end`** in `YYYY-MM`
> format, not `new_end` like the other two.

**Inputs:**

- `../Data/ETI_EUR_hedged/arquant_spy_raw_inputs.xlsx`, sheet `Q2Update`
  (daily strategy + 30% SPY returns)
- `../Data/EUR_hedge/AVESA_Group_Ltd_U3577443_history_mothly_net_2025_04.csv`
  (USD net monthly returns — replace with a newer file when available)
- FRED: EUR/USD spot (`DEXUSEU`) and 1-month USD T-Bill (`DGS1MO`)
- ECB Data Portal: Euribor 1-month
  (`FM/M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA`).
  A local CSV cache (`EUR_1m_euribor_cache.csv`) is used automatically when
  the ECB API is unavailable.
- Financial Modeling Prep: daily prices of `IBCF.DE`
  (iShares S&P 500 EUR Hedged UCITS ETF Acc, Xetra, EUR, ISIN IE00B3ZW0K18).
  Daily prices are compounded into monthly returns and indexed to 100 at
  Mar-2018 for the benchmark line on the landing-page chart. API key is
  hardcoded in `SP500_EUR_HDG_load()`; free tier (250 req/day) is enough.

**Outputs** (in `../Data/ETI_EUR_hedged/<period_end>/`):

- `_ARQuant_monthly_EUR_simulation.csv` — full simulation dataframe
- `_EUR_simulation_Fact_sheet.csv` and `.html` — formatted yearly returns
- `_AMC_simulated_past_performance_plot.png` — performance chart with
  inline metrics table

**Run:**

```bash
/Users/alexander/opt/anaconda3/envs/ARQuant37_pip/bin/python AMC_EUR_hedged_simulation_2026_05.py
```

### 5.0 Hedge methodology

The EUR-hedged return is computed via covered interest parity using **end-of-month** EUR/USD spot and **start-of-month** rates (i.e. the forward locked in at end of the previous month):

```
R_EUR_hedged[t] = (1 + R_USD[t]) * spot[t-1] / forward[t-1 → t] - 1
                ≈ R_USD[t] - (r_USD[t-1] - r_EUR[t-1]) / 12
```

The EUR investor gives up the (typically positive) USD-EUR rate differential, so EUR-hedged returns are normally **lower** than USD returns by that monthly carry. The script prints a sanity check on each run:

```
Hedge sanity check: realised monthly carry drag = +X.XXX%, rate-implied = +X.XXX%
```

Both numbers should have the same sign. If you see `WARNING: hedge return moves opposite to rate differential`, the formula direction has regressed — restore from tag `v2026.05-pre-hedge-fix`'s parent or re-apply the correct `spot.shift(1)/forward.shift(1)` form.

FX is resampled to end-of-month (`resample('M').last()`), not monthly average — month-end spot is the relevant valuation point and aligns with how the rolling 1-month hedge is actually entered.

### 5.1 Automatic update of the ETI landing page

After the simulation finishes, the script overwrites this file on OneDrive:

```
~/Library/CloudStorage/OneDrive-ARQUANTMANAGEMENTLIMITED/
ARQuant Main Site - Documents/4- Marketing/AMC/_Marketing materials/
ARQuant_ETI_Landing_Page_multilang.html
```

A timestamped backup (`<file>.bak.YYYYMMDD_HHMMSS`) is saved alongside the
original before each write.

**What is refreshed automatically:**

- Monthly returns heatmap (`PERF` JS object)
- iShares S&P 500 EUR Hedged monthly returns (`SP500_HDG` JS object) —
  drives the benchmark line on the indexed-performance chart
- The five risk/return metric cards (`METRICS` JS array) for
  Inception / Since-Jan-2021 / L60M / L36M / L12M
- The four hero stats: annualised return, Sharpe, max drawdown,
  cumulative return
- Simulation period-end date string across EN / FR / DE / IT
  (e.g. `Apr 2026` → `May 2026`, `avril 2026` → `mai 2026`, etc.)

**What is preserved (never replaced):**

- ETI inception date `May 2026` and its translations
- Base Prospectus date `3 April 2025` and its translations

**Idempotency:** the previous end date is tracked via the marker
`<!-- ARQUANT_DATA_END: YYYY-MM -->` inside `<head>`, so re-running the
script repeatedly is safe.

If the OneDrive path is unreachable or the file has been edited in a way
that breaks the embedded `PERF` / `METRICS` blocks, the HTML update step
is skipped with a printed warning. The simulation itself still completes
and writes all CSV / PNG outputs.

---

## 6. Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Script exits with "No update for YTD…" | IBKR FlexReport CSVs missing | Download the filenames printed by the script into `../Data/ARQuant_history/` |
| FRED read timeout | Transient FRED outage | Re-run; risk-free rate falls back to the last cached value |
| ECB API 500 / DNS error | ECB downtime | Local cache `EUR_1m_euribor_cache.csv` is used automatically |
| `ETI landing page update skipped` | OneDrive path missing or HTML structure changed | Verify the path exists; the simulation step still completes |
| `weasyprint` errors during PDF render | Missing native libs in the conda env | Reinstall `weasyprint` in `ARQuant37_pip` |
| Broken paths from concatenation | Code uses `maindir + datadir` instead of `os.path.join` | Use `os.path.join()` everywhere; `datadir` starts with `..` and must not be string-glued |
| `Euribor 1M [YYYY-MM]: X.XXX% (ECB not yet published; carried forward)` | Reporting month not yet published by ECB | Informational only — script auto-fills from the previous month. Optionally pin a more accurate value via `_EURIBOR_OVERRIDES` |
| `WARNING: hedge return moves opposite to rate differential` | Hedge formula direction inverted (regression) | Restore correct form: `(1+R_USD) * spot.shift(1) / forward.shift(1) - 1`. See §5.0 |

---

## 7. Bumping the version suffix

Most scripts share the suffix `2026_05`. When bumping to a new period
(e.g. `2026_06`), rename and update imports together in:

- `ARQUANT_slides_ver_2026_05.py`
- `ARQUANT_factsheet_2026_05.py`
- `AMC_EUR_hedged_simulation_2026_05.py`
- `Update_dataset_ARQuant_slides_2026_05.py`
- `ARQUANT_slides_for_website_2026_05.py`
- `ARQUANT_slides_for_PowerPoint_2026_05.py`

**Exception:** `Benchmark_new_2025.py` keeps the `_2025` suffix on purpose
and is imported as `from Benchmark_new_2025 import ...`.

---

## 8. Brand conventions

- ARQuant brand color: `#ea6639`
- Font: Avenir
