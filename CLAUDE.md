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

## Running scripts

The two main entry-point scripts are:
- `ARQUANT_slides_ver_2026_05.py` — generates slides for website/PowerPoint
- `ARQUANT_factsheet_2026_05.py` — generates monthly investor factsheet (PDF/HTML)

Both will `sys.exit()` if the required monthly IBKR CSV input files are missing in `histdir` — check the printed message for which files to download.

Standalone simulation script (separate from the monthly pipeline):
- `AMC_EUR_hedged_simulation_2026_05.py` — EUR-hedged AMC backtest. Reads `arquant_spy_raw_inputs.xlsx` (sheet `Q2Update`) from `../Data/ETI_EUR_hedged/`, pulls EUR/USD spot (`DEXUSEU`) and 1-month rates (USD T-Bill, EUR Euribor) from FRED, writes outputs to `../Data/ETI_EUR_hedged/<period_end>/`. Reporting window is driven by `period_start` / `period_end` near the top, not `new_end`.

## Version suffix convention

Most scripts share a unified `2026_05` suffix that should be updated together when bumping versions. **Exception:** `Benchmark_new_2025.py` keeps its `2025` suffix and is imported as `from Benchmark_new_2025 import ...`.

## Architecture

This project generates periodic investor performance reports for ARQuant/AVESA hedge fund in multiple output formats (website HTML, PowerPoint assets, monthly factsheet).

**Data flow:**

1. **Input data** — CSVs in `../Data/ARQuant_history/` and `../Data/Indexes/`
   - IBKR FTP-delivered monthly return files (e.g. `ARQuant_Management_Limited_<month>_<year>_daily.csv`)
   - Long-term history: `AVESA_Group_Ltd_U3577443_history.csv`
   - Benchmark indexes: Eurekahedge, Fama-French factors, SPY, VIX cached

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
