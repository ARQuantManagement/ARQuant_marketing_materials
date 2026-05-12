# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python environment: `GoTrade37_pip` (conda/pip). Scripts are designed to run in Jupyter/IPython (they use `%autoreload` magic at the top).

Key external dependency: data lives in Dropbox at `~/Dropbox/5-Finance/myARQuant/Python/Data/`. The scripts `chdir` into `maindir` before importing local modules, so the working directory matters at runtime.

## Running scripts

Run the main report generation script interactively in Jupyter/IPython:
```
# In Jupyter, open and run ARQUANT_slides_ver_2026_02.py cell by cell
```

Or directly:
```bash
python ARQUANT_slides_ver_2026_02.py
```

The main script will exit early (`sys.exit()`) if the required monthly CSV input files are not present in `histdir`. Check the printed message for which files to download from IBKR.

## Architecture

This project generates periodic investor performance reports for ARQuant/AVESA hedge fund in multiple output formats (website HTML, PowerPoint assets).

**Data flow:**

1. **Input data** — CSV/pickle files in `~/Dropbox/.../Data/ARQuant_history/` and `.../Data/Indexes/`
   - IBKR FTP-delivered monthly return files (e.g. `AVESA_Group_Ltd_<month>_<year>_daily.csv`)
   - Long-term history: `AVESA_Group_Ltd_U3577443_history.csv`
   - Benchmark indexes: HFRI Quant Directional, Eurekahedge, Fama-French factors

2. **Orchestration** — `ARQUANT_slides_ver_2026_02.py`
   - Sets date range (`new_start`, `new_end`) and detects which input files are available
   - Calls analytics functions, then dispatches to output generators
   - Imports `Slides_analytic_function` from `maindir` (Dropbox), not from the repo directly

3. **Analytics library** — `Slides_analytic_function.py`
   - Core functions: return history loading/merging (`update_return_history_v4`), statistics computation, Fama-French regression, ETF data loading via `yfinance` (`ETFs_load`)
   - Intermediate results are saved as pickle files (`Stats.pkl`, `FF3x2.pkl`) in `Presentation_Inputs/`

4. **Output formatting** — `Slides_for_print_function.py`
   - `stats_periods_for_print` / `stats_periods_for_print2`: reshape stats DataFrames into display-ready tables (formats as `%` strings, nulls out YTD rows for annualized metrics)
   - `stat_html`, `camp_html`, `ff_html`: generate HTML table strings for slides
   - Chart/plot functions for matplotlib figures

5. **Output generators:**
   - `ARQUANT_slides_for_website_06_2022.py` → `update_web()` — HTML slides saved to `Website_slides/`
   - `ARQUANT_slides_for_PowerPoint_2025_02.py` → `update_PowerPoint()` — PNG exports and HTML tables saved to `PowerPoint/`

6. **Data update utilities:**
   - `Update_dataset_ARQuant_slides_2025_10.py` — `ARQuant_history_update()` appends new monthly IBKR data to the master history CSV; `update_dataset()` refreshes index data
   - `Benchmark_new_2025.py` — `benchmark_update()` fetches ETF returns via `ETFs_load` and constructs composite benchmark series

## Key conventions

- `new_end` in `ARQUANT_slides_ver_2026_02.py` drives the reporting period — update this for each new report.
- `computer` path variable switches between machines (Moscow MacBook vs Nice MacBook).
- Pickle files in `Presentation_Inputs/` are intermediate caches — regenerate by re-running the analytics section if inputs change.
- Brand color for ARQuant: `#ea6639`; font: Avenir.
