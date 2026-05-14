#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Initial settings
from IPython import get_ipython
ipython = get_ipython()
if '__IPYTHON__' in globals():
    ipython.magic('load_ext autoreload')
    ipython.magic('autoreload 2')
# get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")
# get_ipython().run_line_magic('matplotlib', 'inline')
    
import os
import re
import shutil
import numpy as np
import pandas as pd
from os import chdir, listdir, path, rename, makedirs, getcwd
from os import stat as os_stat
import datetime as dt
from importlib import reload

# Location-independent paths: derive from this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
maindir = os.path.dirname(script_dir)  # parent of project = .../Python/

# All input/output for this script lives in ETI_EUR_hedged
eti_dir = os.path.join(maindir, 'Data', 'ETI_EUR_hedged')

# Legacy dataset roots used elsewhere in the script
#histdir = os.path.join(maindir, 'Data', 'ARQuant_history')
datadir = os.path.join('Data', 'ETI_EUR_hedged')  # kept for legacy maindir+datadir+... patterns

period_start = '2018-03'
period_end = '2026-04'

# Optional explicit overrides for Euribor 1M monthly average (value in percent,
# e.g. 1.897 = 1.897%). Use when you have an authoritative value better than
# simple carry-forward (e.g. from EMMI daily fixing or an internal estimate).
# Missing months are otherwise filled automatically from the previous month —
# see the resolver below.
_EURIBOR_OVERRIDES = {
    # '2026-05': 1.897,
}

subdir = os.path.join(eti_dir, period_end)
makedirs(subdir, exist_ok=True)

#%%
# Parse daily returns from the raw inputs workbook : Backtest of current release + 30% SPY

# Source: arquant_spy_raw_inputs.xlsx, sheet 'Q2Update'.
# Column D ("Adjusted") header is at D17, data starts at D18; dates in column A.
_raw_xlsx = os.path.join(eti_dir, 'arquant_spy_raw_inputs.xlsx')
_daily = pd.read_excel(_raw_xlsx, sheet_name='Q2Update', header=None,
                       usecols=[0, 3], skiprows=17, names=['Date', 'Adjusted'])
_daily = _daily.dropna(subset=['Date'])
_daily['Date'] = pd.to_datetime(_daily['Date'])
_daily.set_index('Date', inplace=True)
_daily = _daily.loc[period_start:period_end]
_daily.reset_index().to_csv(os.path.join(eti_dir, 'arquant_spy_returns_daily.csv'), index=False)

_monthly = _daily.resample("M").apply(lambda x: ((x + 1).prod() - 1))
_monthly.index = _monthly.index.to_period('M')
_monthly.to_csv(os.path.join(eti_dir, 'arquant_spy_returns_monthly.csv'), index=True)
#Upload ARQuant Simulation = Backtest of current release + 30% SPY
arq_m=pd.read_csv(os.path.join(eti_dir, 'arquant_spy_returns_monthly.csv'),
                       infer_datetime_format=False)
arq_m['Date']=pd.to_datetime(arq_m['Date'], dayfirst=True,
                                  infer_datetime_format='%d/%m/%Y')#correct parse dates
arq_m.set_index(['Date'], inplace=True) #setting index
arq_m.index=pd.to_datetime(arq_m.index, format='%Y-%m-%d')

arq_m = arq_m.loc[period_start : period_end]

arq_m.rename(columns={'Adjusted':'Return_USD'}, inplace=True)

arq_m.index=arq_m.index.to_period('M')

#%%
def FX_load(rate='DEXUSEU',start='2018-02-28', isDaily=True):
    import pandas_datareader as pdr
    eur_usd=pdr.DataReader(rate, 'fred', start)
    if isinstance(eur_usd, pd.DataFrame):
        eur_usd=eur_usd.squeeze()
        eur_usd.name = 'USD per EUR (spot)'
    if isDaily:
        return eur_usd
    else:
        # Month-end spot: the relevant point for valuing positions and for
        # entering rolling 1-month FX hedges at the start of the next month.
        fx_monthly = eur_usd.resample('M').last()
        fx_monthly.index=fx_monthly.index.to_period('M')
        return fx_monthly

eur_usd_mo_eom = FX_load(rate='DEXUSEU',start='2018-02-01',isDaily=False)


#Unhedged performance: EUR_NAV[t]/EUR_NAV[t-1] = (1+R_USD)*S[t-1]/S[t]
fx_coef = (eur_usd_mo_eom.shift(1)/eur_usd_mo_eom).dropna(axis=0)
ret_eur_unhedged=(1+arq_m.squeeze())*fx_coef-1

dfr_all = pd.concat([arq_m,eur_usd_mo_eom], axis=1, join='outer')
eur_usd_mo_eom = eur_usd_mo_eom.iloc[1:] #Remove Feb-2018

dfr_all.loc[arq_m.index,'Return_EUR (unhedged)'] = ret_eur_unhedged

dfr_all.to_csv(os.path.join(subdir, '_ARQuant_monthly_EUR_simulation.csv'), index=True)

#%%
#EURUSD forwards simulation by the difference between USD and EUR interest rate
##EURIBOR is the functional and practical equivalent of 1-month T-Bill 

def USD_1m_load(start='2018-02-28', isDaily=True): # 1-month T-Bill
    import pandas_datareader as pdr
    # Market yield on U.S. Treasury securities, 1-Month Constant Maturity
    print("Downloading data from FRED...")

    try:
        usd_1m = pdr.DataReader("DGS1MO", "fred", start)        
        usd_1m.columns = ['USD 1-month']
        usd_1m.index.name='Date'
        if isinstance(usd_1m, pd.DataFrame): 
            usd_1m=usd_1m.squeeze()
    except Exception as e:
        print(f"1-month USD rates: {e}")
    if isDaily:
        return usd_1m
    else:        
        # Resample to monthly average
        usd_monthly = usd_1m.resample('M').mean()
        usd_monthly.index=usd_monthly.index.to_period('M')
        return usd_monthly

def EUR_1m_load(start='2018-02-28'): # 1-month Euribor monthly average

    import time
    import requests
    from io import StringIO

    # ECB Data Portal (replaces the retired sdw-wsrest.ecb.europa.eu host).
    # Dataflow FM, series M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA = Euribor 1-month, monthly average.
    url = "https://data-api.ecb.europa.eu/service/data/FM/M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA"
    headers = {"Accept": "text/csv"}
    params = {"format": "csvdata", "startPeriod": str(start)[:7]}

    # Local cache used when the ECB API is unavailable (transient 500s, timeouts, DNS).
    cache_path = os.path.join(eti_dir, 'EUR_1m_euribor_cache.csv')

    print("Fetching data from ECB Data Portal (this can take ~1 min on a cold call)...")
    csv_text = None
    last_err = None
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params,
                                    timeout=(15, 90))
            if response.status_code == 200 and response.text.strip():
                csv_text = response.text
                # Refresh local cache on every successful fetch.
                try:
                    with open(cache_path, 'w') as f:
                        f.write(csv_text)
                except OSError:
                    pass
                break
            last_err = f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            last_err = f"{type(e).__name__}: {e}"
        print(f"  attempt {attempt+1} failed: {last_err}; retrying...")
        time.sleep(2 * (attempt + 1))

    if csv_text is None:
        if os.path.exists(cache_path):
            print(f"  ECB API unavailable ({last_err}); falling back to local cache: {cache_path}")
            with open(cache_path) as f:
                csv_text = f.read()
        else:
            raise Exception(
                f"Failed to fetch data from ECB Data Portal: {last_err}. "
                f"No local cache at {cache_path}; retry later or place a previously "
                f"saved CSV (same SDMX schema, columns TIME_PERIOD & OBS_VALUE) there."
            )

    df = pd.read_csv(StringIO(csv_text))
    
    # Keep only key columns for readability
    columns_to_keep = ["TIME_PERIOD", "OBS_VALUE"]
    df = df[columns_to_keep]
    
    # Convert TIME_PERIOD to datetime and sort
    df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
    df = df.sort_values("TIME_PERIOD").reset_index(drop=True)
    
    df.columns = ['Date','EUR 1-month']
    df=df.set_index('Date')
    df=df.loc[start:]
    df.index=df.index.to_period('M')
    return df
    
#%%
#EUR 1-month rates history
eur_1mo=EUR_1m_load(start='2018-03-01')

dfr_all['1MO_EUR_interest_rate']=eur_1mo

# Resolve trailing months that ECB hasn't published yet. Priority:
#   1) explicit value from _EURIBOR_OVERRIDES (authoritative)
#   2) carry-forward of the previous month's value (automatic fallback)
# Cascades correctly across multiple missing trailing months.
_last_valid = dfr_all['1MO_EUR_interest_rate'].last_valid_index()
if _last_valid is None:
    raise ValueError("Euribor 1M series is empty — check ECB API connection.")
for _p in dfr_all.loc[dfr_all.index > _last_valid].index:
    _p_str = str(_p)
    if _p_str in _EURIBOR_OVERRIDES:
        _val, _src = _EURIBOR_OVERRIDES[_p_str], 'manual override'
    else:
        _val = dfr_all['1MO_EUR_interest_rate'].dropna().iloc[-1]
        _src = 'ECB not yet published; carried forward'
    dfr_all.loc[_p, '1MO_EUR_interest_rate'] = _val
    print(f"Euribor 1M [{_p_str}]: {_val:.3f}% ({_src})")
eur_1mo = dfr_all['1MO_EUR_interest_rate'].iloc[1:]

#USD 1-month rates history
usd_1mo=USD_1m_load(start='2018-03-01',isDaily=False)

dfr_all['1MO_USD_interest_rate']=usd_1mo

#%%
# iShares S&P 500 EUR Hedged UCITS ETF — monthly returns since Mar-2018.
# Source: Financial Modeling Prep, daily adj-close, compounded into months.
# Default ticker IBCF.DE matches the benchmark named on the landing page
# (iShares S&P 500 EUR Hedged UCITS ETF Acc, ISIN IE00B3ZW0K18, Xetra).
_FMP_API_KEY = 'db413ca4aade59bea7ca7e22c3f88f10'

def SP500_EUR_HDG_load(ticker='IBCF.DE', start='2018-02-01', end=None,
                       api_key=_FMP_API_KEY):
    """Monthly returns of the iShares S&P 500 EUR Hedged UCITS ETF.

    Fetches daily adjusted-close prices from Financial Modeling Prep and
    compounds daily returns into monthly returns. Returns a pd.Series of
    monthly returns (decimal) indexed by PeriodIndex 'M'.
    """
    import requests
    url = (f'https://financialmodelingprep.com/api/v3/'
           f'historical-price-full/{ticker}')
    params = {'from': start, 'apikey': api_key}
    if end is not None:
        params['to'] = end
    print(f"Downloading {ticker} daily prices from Financial Modeling Prep...")
    r = requests.get(url, params=params, timeout=(15, 90))
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, dict) or not payload.get('historical'):
        raise RuntimeError(
            f"FMP returned no historical data for {ticker}: {str(payload)[:200]}"
        )
    df = pd.DataFrame(payload['historical'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')
    close = df['adjClose']
    daily_ret = close.pct_change().dropna()
    monthly_ret = daily_ret.resample('M').apply(lambda x: (1 + x).prod() - 1)
    monthly_ret.index = monthly_ret.index.to_period('M')
    monthly_ret.name = f'{ticker}_return'
    return monthly_ret

# Trim to the simulation window so the benchmark line aligns with PERF
# (Mar-2018 through period_end, partial months dropped at both ends).
sp500_hdg_ret = SP500_EUR_HDG_load(ticker='IBCF.DE', start='2018-02-01')
sp500_hdg_ret = sp500_hdg_ret.loc[period_start:period_end]
dfr_all['sp500_eur_hdg_return'] = sp500_hdg_ret

# Indexed performance from Mar-2018 = 100; missing months treated as 0 return.
sp500_hdg_indexed = 100 * (1 + dfr_all['sp500_eur_hdg_return']
                           .loc['2018-03':].fillna(0)).cumprod()
dfr_all['sp500_eur_hdg_indexed'] = sp500_hdg_indexed


# Covered interest parity (USD per EUR convention, with USD as "domestic"):
#   F = S * (1 + r_USD) / (1 + r_EUR)
# When r_USD > r_EUR, the forward sells EUR at a premium (more USD per EUR
# in the future), i.e. the higher-rate currency trades at a forward discount.

eur_usd_spot = eur_usd_mo_eom.squeeze()
eur_usd_forward_calc = eur_usd_spot * (1+usd_1mo.values/100/12)/(1+eur_1mo.values/100/12)

dfr_all['USD per EUR (1mo forward)']=eur_usd_forward_calc
dfr_all.to_csv(os.path.join(subdir, '_ARQuant_monthly_EUR_simulation.csv')) #https://fred.stlouisfed.org/series/DEXUSEU

# Hedging USD exposure with a rolling 1-month FX forward.
# The forward applied to month t is locked in at end of month t-1, using rates
# observable at t-1. Same for spot used to convert the principal at start of t.
#   R_EUR_hedged(t) = (1 + R_USD(t)) * S(t-1) / F(t-1 -> t) - 1
#                  ≈ R_USD(t) - (r_USD(t-1) - r_EUR(t-1)) / 12
# The EUR investor gives up the (usually positive) USD-EUR rate differential,
# so EUR-hedged returns are typically lower than USD returns by that carry.
dfr_all['eur_returns_hedged']= (
    (1 + dfr_all['Return_USD'])
    * dfr_all['USD per EUR (spot)'].shift(1)
    / dfr_all['USD per EUR (1mo forward)'].shift(1)
    - 1
)

# Sanity check: the realised carry drag (R_USD - R_EUR_hedged) should be
# positive on average when USD rates exceed EUR rates, and roughly equal to
# the average rate differential. A sign mismatch means the formula direction
# is wrong (e.g. forward/spot vs spot/forward inverted).
_carry_actual_m = (dfr_all['Return_USD'] - dfr_all['eur_returns_hedged']).dropna().mean()
_carry_implied_m = ((dfr_all['1MO_USD_interest_rate'] - dfr_all['1MO_EUR_interest_rate'])
                    .dropna().mean()) / 100 / 12
print(f"Hedge sanity check: realised monthly carry drag = {_carry_actual_m*100:+.3f}%, "
      f"rate-implied = {_carry_implied_m*100:+.3f}% "
      f"(both should match in sign when USD rates exceed EUR rates).")
if _carry_actual_m * _carry_implied_m < 0:
    print("  WARNING: hedge return moves opposite to rate differential — check formula sign.")

#%%
#Return in EUR after AMC fees (excl. entry fee and block issue fee)
chdir(maindir)
from Slides_analytic_function import after_fees2m, factsheet

pfee = 20/100
mfee = (1.25+0.20+0.05)/100
eur_nav_net, eur_hwm_net, eur_ret_net = after_fees2m(dfr_all['eur_returns_hedged'].dropna(axis=0), 
                                                     NAV0=1-0.54/100, 
                                                     mfra=mfee, 
                                                     pfr=pfee, 
                                                     hra=0., 
                                                     out='nav_hwm_ret'
                                                     )
dfr_all['eur_returns_hedged_net']=eur_ret_net
dfr_all.to_csv(os.path.join(subdir, '_ARQuant_monthly_EUR_simulation.csv')) 


#Upload USD returns after fees
arq_monthly_net=pd.read_csv(os.path.join(maindir, 'Data', 'EUR_hedge',
                                         'AVESA_Group_Ltd_U3577443_history_mothly_net_2025_04.csv'),
                        infer_datetime_format=False)
arq_monthly_net['Date']=pd.to_datetime(arq_monthly_net['Date'], dayfirst=True,
                                  infer_datetime_format='%Y-%m')#correct parse dates
arq_monthly_net.set_index(['Date'], inplace=True) #setting index
arq_monthly_net.index=arq_monthly_net.index.to_period('M')
arq_monthly_net=arq_monthly_net.squeeze()

dfr_all['usd_returns_net']=arq_monthly_net

dfr_all.to_csv(os.path.join(subdir, '_ARQuant_monthly_EUR_simulation.csv'))


#Formatting EUR returns after fees.
#Year list runs from inception year through period_end's year so the current
#reporting year (and any future year that ends up in the data) is always shown.
_fs_years = [str(y) for y in range(int(period_start.split('-')[0]),
                                   int(period_end.split('-')[0]) + 1)]
eur_ret_fs_net=factsheet(eur_ret_net,
                         years=_fs_years,
                         output='after fees', af_func=None, #None if net returns, otherwise after_fees or after_fees2m or after_fees2q
                         decim=4
                         )
# eur_ret_fs_net.index.name='(in %)'
(eur_ret_fs_net*100).to_csv(os.path.join(subdir, '_EUR_simulation_Fact_sheet.csv'))

chdir(maindir)
from Slides_for_print_function import f_fsnet, factsheet_html
imaps_color = '#{:02x}{:02x}{:02x};'.format(173, 157, 116)

factsheet_html(f_fsnet(eur_ret_fs_net, pct=''), 
               os.path.join(subdir, '_EUR_simulation_Fact_sheet'),
               resolution = 300, isLastRow = False, isWriteHTML = False,
               table_width = '7.2cm;', 
               # col_formatter =['6.5%']+(['7%',]*12)+['9.5%'], 
               row_height = '0.618cm;',
               col_width = ('7.00%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;',
                            '7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.30%;'), 
               width= '40.0;', #'24.95cm;', # 24.95/7*8=28.5
               height = '6.1cm;', #height is 0.91 per row
               bcolor = imaps_color,
               ) 

#%%
#Plot for AMC factsheet

# 1) Prepeare data for plot
df1=dfr_all['eur_returns_hedged_net'].loc['2020-12':]
df1.iloc[0]=0.
df1=df1.to_frame()

# Index the cumulative hedged EUR returns to 100 (starting at first valid value)
df1['indexed_performance'] = 100 * (1 + df1['eur_returns_hedged_net'].fillna(0)).cumprod()

# Benchmark: iShares S&P 500 EUR Hedged — indexed from the same Dec-2020 base
# so both lines share a common starting value of 100.
df_bench = dfr_all['sp500_eur_hdg_return'].loc['2020-12':].copy()
df_bench.iloc[0] = 0.
df_bench = df_bench.to_frame()
df_bench['indexed_bench'] = 100 * (1 + df_bench['sp500_eur_hdg_return'].fillna(0)).cumprod()


# Extract annual performance by compounding monthly returns
years  = df1.index.year.unique()[1:].astype('str')
tick_positions = []
for year in years:
    year_len = df1.loc[year].shape[0]
    if year_len == 12: 
        tick_positions.append(pd.to_datetime(f"{year}-07"))
    else:
        midpoint = int(1+year_len/2)
        tick_positions.append(pd.to_datetime(f"{year}-0{midpoint}"))

annual_returns=pd.Series(index=years,dtype='float')
for i,y in enumerate(annual_returns.index):
    annual_returns.loc[y] = (1+df1.loc[y,'eur_returns_hedged_net']).prod()-1
annual_returns = annual_returns.round(4)*100

#%%
#Perpare samples for metrics table
ret=dfr_all.loc['2018-03':, 'eur_returns_hedged_net']
rfr=dfr_all.loc['2018-03':, '1MO_EUR_interest_rate']/100

samples={#montly returns
         "Since Inception (Mar'18)": ret.loc['2018-03':],
         "Since Jan-2021": ret.loc['2021-01':],
         }
rfr_mean ={#montly returns
         "Since Inception (Mar'18)": rfr.loc['2018-03':].mean(),
         "Since Jan-2021": rfr.loc['2021-01':].mean(),
         }

for per in [60,36,12]:
    samples[f'L{per}M']=ret.iloc[-per:]
    rfr_mean[f'L{per}M']=rfr.iloc[-per:].mean()

col_list = ['Return ann.', 'Volatility ann.', 'Risk Free Rate','Sharpe','Max Drawdown']

metrics_df = pd.DataFrame(dtype='float')

from Slides_analytic_function import summary_stats_monthly

for i,per in enumerate(samples.keys()):
    print(f'Calculate metrics for {per}')
    ret_m = samples[per]
    metrics=summary_stats_monthly(ret_m, riskfree_rate = rfr_mean[per])
    metrics=metrics[col_list].squeeze()
    for col in col_list:
        metrics[col]=round(metrics[col]*100,2) if col !='Sharpe' else round(metrics[col],2)
    metrics.name=per
        
    metrics_df=pd.concat([metrics_df, metrics],axis=1)

#%%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def rgb_to_matplotlib(r, g, b):
    """Convert 0-255 RGB values to Matplotlib format (0-1)"""
    return (r/255.0, g/255.0, b/255.0)

# --- Create the plot ---
fig, ax1 = plt.subplots(figsize=(12, 6))

# Ensure left Y-axis starts at 100
left_min = min(df1['indexed_performance'].min(), df_bench['indexed_bench'].min())
left_max = max(df1['indexed_performance'].max(), df_bench['indexed_bench'].max())

# top_limit = max(left_max, annual_returns.max())+15

ax1.set_ylim(left_min*0.95, left_max*1.05)  # start at left_min

# Plot indexed performance (left y-axis)
ax1.plot(df1.index.to_timestamp(), df1['indexed_performance'],
         color=rgb_to_matplotlib (11,52,105), #Alternative is rgb_to_matplotlib (13,46,93)
         linewidth=2, label='Indexed performance')

# Plot iShares S&P 500 EUR Hedged benchmark (orange dashed, matches HTML chart)
ax1.plot(df_bench.index.to_timestamp(), df_bench['indexed_bench'],
         color=rgb_to_matplotlib(234, 102, 57),
         linewidth=1.8, linestyle='--',
         label='iShares S&P 500 EUR Hedged')

ax1.set_ylabel('Indexed performance', color='black')
ax1.tick_params(axis='y', labelcolor='black')

# Left Y-axis ticks: only min, max, and 100
ax1.set_yticks([100,
                # round(left_min, 0),
                round(left_max, 0)])
ax1.grid(True, linestyle='--', alpha=0.7)

# Plot annual performance bars (right y-axis) without ticks
ax2 = ax1.twinx()
bars = ax2.bar(tick_positions, annual_returns.values, 
               color=imaps_color[:-1], # Alternative is rgb_to_matplotlib(173,157,116), 
               alpha=0.7, width=100, label='Annual return (%)')
ax2.set_yticks([])  # Remove ticks
ax2.set_yticklabels([])  # Remove labels
ax2.spines['right'].set_visible(False)

# Add annual return values on top of bars
for bar, value in zip(bars, annual_returns.values):
    ax2.text(bar.get_x() + bar.get_width()/2, value, #+/-0.25 
             f'{value:.2f}%', ha='center', va='bottom', fontsize=9)

# X-axis setup
ax1.set_xticks(tick_positions)
ax1.set_xticklabels([str(year) for year in years])

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
fig.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)

# Title and source
fig.suptitle('Performance (EUR-simulated)', fontsize=14)
fig.text(0.5, -0.1, 'EUR hedge simulated on the basis of month-end data / Source: ARQuant Management', ha='center', fontsize=10)

# --- Table data (transposed) ---

row_labels = metrics_df.index
row_values = metrics_df.values

metrics_df.index.name='(%p.a.)'
table_df=metrics_df.reset_index()

# Make first column wider (e.g., 1.5x wider)
num_cols = len(table_df.columns)
table_width = 1 # adjust 0.1 until the width feels right
first_col_width = 0.15  # first column width
second_col_width = 0.25  # first column width
remaining_width = table_width - first_col_width -second_col_width
other_col_width = remaining_width / (num_cols - 2)

# Create the list of widths
col_widths = [first_col_width] + [second_col_width] + [other_col_width] * (num_cols - 2)

# Create transposed table below plot
table = plt.table(cellText=table_df.values,
                  colLabels=table_df.columns,
                  # rowLabels=table_df.index,
                  cellLoc='center',
                  rowLoc='center',
                  loc='bottom right',
                  bbox=[0, -0.41, table_width, 0.33],  # align right side
                  colWidths=col_widths)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

# Adjust layout
# plt.subplots_adjust(bottom=0.4)
# plt.savefig(os.path.join(os.path.join(subdir, '_AMC_simulated_past_performance_plot.png')), 
#             dpi=300, pad_inches=0.0)

plt.subplots_adjust(left=0.1, right=0.9, top=0.92, bottom=0.23)
plt.savefig(os.path.join(subdir, '_AMC_simulated_past_performance_plot.png'), 
            dpi=300, bbox_inches='tight', pad_inches=0.05)

plt.show()
plt.close()

#%%
# Monthly update of the ARQuant ETI multilang landing page (OneDrive)
# Replaces the embedded PERF / METRICS JS literals, the 4 hero-stat values,
# and rewrites the simulation period-end date string in EN/FR/DE/IT.
# ETI inception ("May 2026") and the Base Prospectus date ("3 April 2025")
# are preserved via placeholder protection.

_ETI_MONTHS = {
    'en_short': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    'en_long' : ['January','February','March','April','May','June','July','August','September','October','November','December'],
    'fr_long_l': ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
    'fr_long_u': ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
    'de_short': ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'],
    'de_long' : ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
    'it_short': ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
    'it_long_l': ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],
}

# Anchored contexts whose embedded date must NOT be replaced (ETI inception + prospectus date).
_ETI_PROTECT_PATTERNS = [
    re.compile(r'ETI launched (\w+ \d{4})'),
    re.compile(r'ETI lancé en (\w+ \d{4})'),
    re.compile(r'ETI-Start (\w+ \d{4})'),
    re.compile(r'ETI lanciato a (\w+ \d{4})'),
    re.compile(r'incepted in (\w+ \d{4})'),
    re.compile(r'a été lancé en (\w+ \d{4})'),
    re.compile(r'wurde im (\w+ \d{4}) aufgelegt'),
    re.compile(r'è stato lanciato a (\w+ \d{4})'),
    re.compile(r'<div class="fact-val">(\w+ \d{4})</div>'),
    re.compile(r'(?:Base Prospectus|Prospectus de Base|Basisprospekt|Prospetto di Base) (?:dated|daté du|vom|datato) (\d+\.? \w+ \d{4})'),
]

def _eti_end_period_strings(yyyymm):
    """Return language-specific representations of a YYYY-MM end period."""
    y, m = yyyymm.split('-')
    y = int(y); i = int(m) - 1
    return {
        k: f'{_ETI_MONTHS[k][i]} {y}' if k != 'it_short_dot' else f'{_ETI_MONTHS["it_short"][i]}. {y}'
        for k in ('en_short','en_long','fr_long_l','fr_long_u',
                  'de_short','de_long','it_long_l','it_short_dot')
    }

def _eti_protect_dates(html):
    """Swap protected date strings (inception, prospectus) for unique placeholders.
    Returns (html, list of (placeholder, original))."""
    placeholders = []
    def _replacer(m):
        date_str = m.group(1)
        start, end = m.start(1) - m.start(), m.end(1) - m.start()
        full = m.group(0)
        ph = f'\x00PROTECTED_{len(placeholders)}\x00'
        placeholders.append((ph, date_str))
        return full[:start] + ph + full[end:]
    for pat in _ETI_PROTECT_PATTERNS:
        html = pat.sub(_replacer, html)
    return html, placeholders

def _eti_unprotect_dates(html, placeholders):
    for ph, original in placeholders:
        html = html.replace(ph, original)
    return html

def _eti_format_perf_js(returns):
    """Build the body of the `const PERF = { ... };` JS object.
    Input: pd.Series of EUR monthly net returns (decimal), PeriodIndex 'M'."""
    pct = returns * 100
    by_year = {}
    for prd, val in pct.items():
        if not hasattr(prd, 'year'):
            prd = pd.Period(prd, freq='M')
        if prd.year not in by_year:
            by_year[prd.year] = [None] * 12
        by_year[prd.year][prd.month - 1] = None if pd.isna(val) else float(val)
    rows = []
    for y in sorted(by_year):
        cells = ['null' if v is None else f'{v:.2f}' for v in by_year[y]]
        rows.append(f'  {y}: [{", ".join(cells)}],')
    return '\n' + '\n'.join(rows) + '\n'

def _eti_format_metrics_js(metrics_df):
    """Build the body of the `const METRICS = [ ... ];` JS array.
    Columns must already be in order Inception / Since-Jan2021 / L60M / L36M / L12M."""
    rows = []
    for col in metrics_df.columns:
        r = metrics_df[col]
        rows.append(
            '  {{ ret: {ret:.2f}, vol: {vol:.2f}, rfr: {rfr:.2f}, '
            'sharpe: {sh:.2f}, dd: {dd:.2f} }},'.format(
                ret=float(r['Return ann.']),
                vol=float(r['Volatility ann.']),
                rfr=float(r['Risk Free Rate']),
                sh=float(r['Sharpe']),
                dd=abs(float(r['Max Drawdown'])),
            )
        )
    return '\n' + '\n'.join(rows) + '\n'

def update_eti_landing_page(html_path, monthly_returns_eur, metrics_df,
                            period_end_str, previous_period_end=None,
                            sp500_hdg_returns=None, backup=True):
    """Refresh the ARQuant ETI multilang landing page with the latest EUR-hedged
    simulation data.

    Replaces the embedded PERF / METRICS JS literals, the 4 hero-stat values
    (annualised return, Sharpe, max drawdown, cumulative return), and rewrites
    the simulation period-end date string across EN/FR/DE/IT. ETI inception
    ("May 2026") and the Base Prospectus date are preserved.

    A `<!-- ARQUANT_DATA_END: YYYY-MM -->` marker is maintained inside <head>
    so subsequent runs know which previous date to overwrite.

    Parameters
    ----------
    html_path : str
        Absolute path to ARQuant_ETI_Landing_Page_multilang.html.
    monthly_returns_eur : pd.Series
        EUR net returns indexed by PeriodIndex 'M' (decimal, e.g. 0.0312).
    metrics_df : pd.DataFrame
        Risk/return metrics; columns in order (Inception, Since Jan-2021,
        L60M, L36M, L12M); rows: 'Return ann.', 'Volatility ann.',
        'Risk Free Rate', 'Sharpe', 'Max Drawdown' (all in percent except Sharpe).
    period_end_str : str
        New simulation end period as 'YYYY-MM'.
    previous_period_end : str, optional
        Override for the previous end period when the marker is absent.
    backup : bool
        Save a timestamped .bak.<ts> copy before overwriting.
    """
    if not os.path.exists(html_path):
        raise FileNotFoundError(f'ETI landing page not found: {html_path}')
    if metrics_df.shape[1] < 5:
        raise ValueError(f'metrics_df must have 5 period columns; got {metrics_df.shape[1]}')

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    marker_re = re.compile(r'<!-- ARQUANT_DATA_END: (\d{4}-\d{2}) -->')
    mk = marker_re.search(html)
    prev_end = mk.group(1) if mk else (previous_period_end or '2026-04')

    if backup:
        ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2(html_path, f'{html_path}.bak.{ts}')

    # Protect ETI inception / prospectus dates from generic date replacement.
    html, protected = _eti_protect_dates(html)

    # ── 1. Replace PERF block ────────────────────────────────────────
    perf_body = _eti_format_perf_js(monthly_returns_eur.dropna())
    perf_re = re.compile(r'const PERF = \{[^}]*\};', re.DOTALL)
    if not perf_re.search(html):
        raise ValueError("Couldn't locate `const PERF = {...};` in HTML.")
    html = perf_re.sub(f'const PERF = {{{perf_body}}};', html, count=1)

    # ── 1b. Replace SP500_HDG block (iShares S&P 500 EUR Hedged) ─────
    if sp500_hdg_returns is not None and len(sp500_hdg_returns.dropna()):
        sp500_body = _eti_format_perf_js(sp500_hdg_returns.dropna())
        sp500_re = re.compile(r'const SP500_HDG = \{[^}]*\};', re.DOTALL)
        if sp500_re.search(html):
            html = sp500_re.sub(f'const SP500_HDG = {{{sp500_body}}};', html, count=1)
        else:
            # Insert right after the PERF block if the literal isn't present yet.
            html = perf_re.sub(
                lambda m: m.group(0) + f'\nconst SP500_HDG = {{{sp500_body}}};',
                html, count=1)

    # ── 2. Replace METRICS block ─────────────────────────────────────
    metrics_body = _eti_format_metrics_js(metrics_df)
    metrics_re = re.compile(r'const METRICS = \[[^\]]*\];', re.DOTALL)
    if not metrics_re.search(html):
        raise ValueError("Couldn't locate `const METRICS = [...];` in HTML.")
    html = metrics_re.sub(f'const METRICS = [{metrics_body}];', html, count=1)

    # ── 3. Hero stat values ──────────────────────────────────────────
    inc = metrics_df.iloc[:, 0]
    ann_ret = float(inc['Return ann.'])
    sharpe  = float(inc['Sharpe'])
    dd      = abs(float(inc['Max Drawdown']))
    cum_ret = float(((1 + monthly_returns_eur.dropna()).prod() - 1) * 100)

    html = re.sub(
        r'(<div class="hero-stat-val">)[+\-\d.]+%(\s*</div>\s*<div class="hero-stat-label" data-i18n="hero_stat1_label">)',
        rf'\g<1>{ann_ret:.2f}%\g<2>', html, count=1)
    html = re.sub(
        r'(<div class="hero-stat-val orange">)[+\-\d.]+(\s*</div>\s*<div class="hero-stat-label" data-i18n="hero_stat2_label">)',
        rf'\g<1>{sharpe:.2f}\g<2>', html, count=1)
    html = re.sub(
        r'(<div class="hero-stat-val">)[+\-\d.]+%(\s*</div>\s*<div class="hero-stat-label" data-i18n="hero_stat3_label">)',
        rf'\g<1>{dd:.2f}%\g<2>', html, count=1)
    html = re.sub(
        r'(<div class="hero-stat-val orange">)[+\-\d.]+%(\s*</div>\s*<div class="hero-stat-label" data-i18n="hero_stat4_label">)',
        rf'\g<1>{cum_ret:+.0f}%\g<2>', html, count=1)

    # ── 4. Period-end date strings (EN/FR/DE/IT) ─────────────────────
    if prev_end != period_end_str:
        old_s = _eti_end_period_strings(prev_end)
        new_s = _eti_end_period_strings(period_end_str)
        # Longer keys first so e.g. "April 2026" is replaced before "Apr 2026".
        for key in sorted(old_s, key=lambda k: -len(old_s[k])):
            if old_s[key] != new_s[key]:
                html = html.replace(old_s[key], new_s[key])

    # Restore protected dates (inception, prospectus).
    html = _eti_unprotect_dates(html, protected)

    # ── 5. Update / insert the data-end marker in <head> ─────────────
    new_marker = f'<!-- ARQUANT_DATA_END: {period_end_str} -->'
    if mk:
        html = marker_re.sub(new_marker, html, count=1)
    else:
        html = html.replace('<head>', f'<head>\n{new_marker}', 1)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'ETI landing page updated: {html_path}')
    print(f'  Data window: {prev_end} -> {period_end_str}')
    print(f'  Hero stats : ret={ann_ret:.2f}%  vol={float(inc["Volatility ann."]):.2f}%  '
          f'sharpe={sharpe:.2f}  dd={dd:.2f}%  cum={cum_ret:+.0f}%')


#%%
# Push the freshly computed simulation into the landing page
_eti_html_path = os.path.expanduser(
    '~/Library/CloudStorage/OneDrive-ARQUANTMANAGEMENTLIMITED/'
    'ARQuant Main Site - Documents/4- Marketing/AMC/_Marketing materials/'
    'ARQuant_ETI_Landing_Page_multilang.html'
)
try:
    update_eti_landing_page(
        html_path=_eti_html_path,
        monthly_returns_eur=dfr_all['eur_returns_hedged_net'].dropna(),
        metrics_df=metrics_df,
        period_end_str=period_end,
        sp500_hdg_returns=dfr_all['sp500_eur_hdg_return'].dropna(),
    )
except Exception as _e:
    print(f'ETI landing page update skipped: {type(_e).__name__}: {_e}')

