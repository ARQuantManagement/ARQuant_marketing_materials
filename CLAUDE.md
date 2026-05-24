# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python environment: `ARQuant37_pip` (conda env at `/Users/alexander/opt/anaconda3/envs/ARQuant37_pip`, Python 3.7). Required external packages: `pandas_datareader` (FRED API), `yfinance` (ETFs), `weasyprint` (HTML→PDF for factsheet), `matplotlib`, `pandas`. Scripts use `%autoreload` magic and are designed to run in Jupyter/IPython but also work as standalone Python.

Run with explicit interpreter to avoid env mismatches:
```bash
/Users/alexander/opt/anaconda3/envs/ARQuant37_pip/bin/python <script>.py
```

## Path conventions

All scripts use `script_dir = os.path.dirname(os.path.abspath(__file__))` as `maindir`, making the project **location-independent**. **Exception:** `AMC_EUR_hedged_simulation_2026_05.py` sets `maindir = os.path.dirname(script_dir)` (the parent of the project dir) to preserve legacy `maindir + datadir + ...` path patterns. Data is expected one level above the project root:

- Project: `.../Python/ARQuant marketing materials/`
- Data: `.../Python/Data/ARQuant_history/`, `.../Python/Data/Indexes/`
- Outputs: `.../Python/Data/Factsheet_<period>/`, `.../Python/Data/Presentation_<period>/`

**Always use `os.path.join()`** for path construction, never string concatenation (e.g., `maindir + datadir` produces broken paths). The `datadir` variable is a relative path starting with `'..'`:
```python
datadir = os.path.join('..', 'Data', 'Factsheet_' + _period)
```

## Monthly workflow checklist

Each period, make exactly these edits before running:

| Script | Variable to change | Format |
|---|---|---|
| `ARQUANT_slides_ver_2026_05.py` | `new_end` (~line 44) | `'YYYY-MM-DD'` (last calendar day) |
| `ARQUANT_factsheet_2026_05.py` | `new_end` (~line 44) | `'YYYY-MM-DD'` |
| `AMC_EUR_hedged_simulation_2026_05.py` | `period_end` (~line 35) | `'YYYY-MM'` |

Also download the two IBKR FlexReport CSVs for the new month into `../Data/ARQuant_history/` before running the slides/factsheet scripts — they `sys.exit()` immediately if the files are missing, printing the exact filenames needed.

See `USAGE.md` for full step-by-step operational instructions and a common-issues table.

## Running scripts

The two main entry-point scripts are:
- `ARQUANT_slides_ver_2026_05.py` — generates slides for website/PowerPoint
- `ARQUANT_factsheet_2026_05.py` — generates monthly investor factsheet (PDF/HTML)

Both will `sys.exit()` if the required monthly IBKR CSV input files are missing in `histdir` — check the printed message for which files to download.

Standalone simulation script (separate from the monthly pipeline):
- `AMC_EUR_hedged_simulation_2026_05.py` — EUR-hedged AMC backtest. Reads `arquant_spy_raw_inputs.xlsx` (sheet `Q2Update`) from `../Data/ETI_EUR_hedged/`, pulls EUR/USD spot (`DEXUSEU`, resampled to **end-of-month**) and 1-month rates (USD T-Bill via FRED `DGS1MO`, EUR Euribor via ECB Data Portal) from external APIs, writes outputs to `../Data/ETI_EUR_hedged/<period_end>/`. Reporting window is driven by `period_start` / `period_end` near the top, not `new_end`.

Additional AMC inputs:
- **USD net monthly returns** — `../Data/EUR_hedge/AVESA_Group_Ltd_U3577443_history_mothly_net_2025_04.csv` (line ~337). When a newer FTP-delivered file is available, update the filename in the `pd.read_csv()` call.
- **iShares EUR-hedged ETF benchmark** (`IBCF.DE`) — fetched via Financial Modeling Prep in `SP500_EUR_HDG_load()`. The free-tier API key is hardcoded as `_FMP_API_KEY` (~line 234); free tier allows 250 req/day which is sufficient for monthly runs.

### EUR-hedged return formula (critical)

The hedge calc uses covered interest parity. **The formula must apply the spot at the start of month t (= end of t-1) and the forward locked in at t-1**, not same-month spot/forward — otherwise the carry-direction inverts and EUR-hedged returns are systematically overstated by ≈ (r_USD − r_EUR)/12 per month. Correct form:

```python
R_EUR_hedged[t] = (1 + R_USD[t]) * spot.shift(1) / forward.shift(1) - 1
                ≈ R_USD[t] - (r_USD[t-1] - r_EUR[t-1]) / 12
```

Equivalently from rates: `(1+R_USD) * (1+r_EUR.shift(1)/12) / (1+r_USD.shift(1)/12) - 1`. The script includes a sanity-check print that compares the realised monthly carry drag against the rate differential and warns if signs diverge. **Don't remove that check** — it's the guardrail against re-inverting the formula. The pre-fix tag `v2026.05-pre-hedge-fix` marks the last commit with the buggy direction.

### Euribor missing-month handling

ECB publishes Euribor 1M monthly averages only after the month closes, so the reporting month is typically missing on first fetch. `AMC_EUR_hedged_simulation_2026_05.py` resolves this automatically: any trailing-NaN month is **carry-forwarded from the previous month's value** (cascades across multiple missing months). The dict `_EURIBOR_OVERRIDES = {'YYYY-MM': value_in_percent}` near the top is an **optional** explicit override — use it when you have an authoritative value better than carry-forward (e.g. from EMMI daily fixing). Each resolution is printed to console: `Euribor 1M [YYYY-MM]: X.XXX% (manual override | ECB not yet published; carried forward)`.

### ETI landing-page update

As its final step, `AMC_EUR_hedged_simulation_2026_05.py` calls `update_eti_landing_page()` to refresh the multilingual landing page. The **current target is `ARQuant_ETI_Landing_Page_multilang_with_fees.html` in the project root** (`script_dir`) — the legacy `ARQuant_ETI_Landing_Page_multilang.html` is kept on disk but is no longer written to. The function replaces `const PERF`, `const SP500_HDG`, `const METRICS` JS literals, the four `hero-stat-val` numbers, and rewrites the period-end date string in EN/FR/DE/IT. ETI inception ("May 2026") and the Base Prospectus date ("3 April 2025") are shielded from generic date replacement via the `_ETI_PROTECT_PATTERNS` placeholder mechanism. A `<!-- ARQUANT_DATA_END: YYYY-MM -->` marker inside `<head>` records the last-written period so subsequent runs know which old dates to overwrite; a timestamped `.bak.<ts>` copy is saved alongside the file on each run.

## Version suffix convention

Most scripts share a unified `2026_05` suffix that should be updated together when bumping versions. **Exception:** `Benchmark_new_2025.py` keeps its `2025` suffix and is imported as `from Benchmark_new_2025 import ...`.

## Architecture

This project generates periodic investor performance reports for ARQuant/AVESA hedge fund in multiple output formats (website HTML, PowerPoint assets, monthly factsheet).

**Data flow:**

1. **Input data**
   - `../Data/ARQuant_history/` — IBKR FTP-delivered monthly FlexReport CSVs (e.g. `ARQuant_Management_Limited_<Month_YYYY>_<Month_YYYY>_daily.csv`) and long-term history `AVESA_Group_Ltd_U3577443_history.csv`
   - `../Data/Indexes/` — Eurekahedge, Fama-French factors, SPY, VIX cached
   - `../Data/ETI_EUR_hedged/` — AMC simulation inputs (`arquant_spy_raw_inputs.xlsx`) and outputs
   - `../Data/EUR_hedge/` — USD net monthly returns CSV for AMC simulation; filename must be updated when a new FTP file arrives

2. **Orchestration scripts:**
   - `ARQUANT_slides_ver_2026_05.py` — slides pipeline; calls analytics then dispatches to website/PowerPoint generators
   - `ARQUANT_factsheet_2026_05.py` — factsheet pipeline; parses IBKR FlexReport via `IBKR_lib`, builds plots, renders HTML/PDF

3. **Analytics library** — `Slides_analytic_function.py`
   - Return history loading/merging (`update_return_history_v3/v4`, both take `histdir` as parameter)
   - Statistics computation, Fama-French regression, ETF data loading via `yfinance` (`ETFs_load`)
   - FRED fetchers (`VIX_load`, `SP500_load`, RFR via `pandas_datareader`)
   - Intermediate results saved as pickles in `Presentation_Inputs/`

4. **IBKR parsing** — `IBKR_lib.py`
   - `parse_flexreport()` extracts sections from IBKR FlexReport CSV (Time Period Performance, Cumulative Performance, Performance by Symbol)
   - `render()` shapes raw sections into returns + contributors dataframes
   - `contrib_selection()` filters/sorts top-N contributors and detractors

5. **Output formatting** — `Slides_for_print_function.py`
   - `stats_periods_for_print` / `stats_periods_for_print2`: reshape stats into display tables
   - `stat_html`, `camp_html`, `ff_html`, `factsheet_html`: HTML table/page generators (factsheet uses `weasyprint`)
   - Chart/plot functions for matplotlib figures

6. **Output generators:**
   - `ARQUANT_slides_for_website_2026_05.py` → `update_web()` — HTML slides → `Website_slides/`
   - `ARQUANT_slides_for_PowerPoint_2026_05.py` → `update_PowerPoint()` — PNG/HTML tables → `PowerPoint/`

7. **Data update utilities:**
   - `Update_dataset_ARQuant_slides_2026_05.py` — `ARQuant_history_update()` appends new monthly IBKR data; `update_dataset()` refreshes index data via FRED
   - `Benchmark_new_2025.py` — `benchmark_update()` fetches ETF returns via `ETFs_load` and constructs composite benchmark

## Network error handling

FRED (`fred.stlouisfed.org`) is prone to read timeouts. Wrap any direct FRED call in try-except with a sensible fallback or "continue with existing data" message — see `update_dataset()` call site and `RFR_load()` in `ARQUANT_factsheet_2026_05.py` for the pattern.

## Key conventions

- `new_end` in the main scripts drives the reporting period — update this for each new report.
- Pickle files in `Presentation_Inputs/` are intermediate caches — regenerate by re-running the analytics section if inputs change.
- Brand color for ARQuant: `#ea6639`; font: Avenir.
- `.gitignore` covers `__pycache__/`, `.DS_Store`, `.ipynb_checkpoints/`, `.vscode/`, `.idea/`, `*.py[cod]`, `*.so`, `.Python`, `*.egg-info/`, `*.swp` — don't re-track these.
- Stats table current-year column: in `PP_pages_stat` (and similar period selectors) use the literal `'YTD'` for the current year, not the year string (e.g. `'2026'`). `Stats.pkl` contains both rows with identical data, but `stats_periods_for_print2` only blanks out the YTD-incompatible rows (Return ann., Volatility ann., Risk Free Rate, Sharpe/Calmar/Sortino, Kelly, Skewness, Kurtosis, VaR/CVaR) when the index label is exactly `'YTD'`. The rendered column header comes from the period label, so `'YTD'` also gives the right caption.
