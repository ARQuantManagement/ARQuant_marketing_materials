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
def FX_load(rate='DEXUSEU',start='2018-02-28', isDaily=True): # 3-month T-Bill as of month start
    import pandas_datareader as pdr
    eur_usd=pdr.DataReader(rate, 'fred', start)
    if isinstance(eur_usd, pd.DataFrame): 
        eur_usd=eur_usd.squeeze()
        eur_usd.name = 'USD per EUR (spot)'
    if isDaily:
        return eur_usd
    else: 
        # Resample to monthly average
        fx_monthly = eur_usd.resample('M').mean()
        fx_monthly.index=fx_monthly.index.to_period('M')
        return fx_monthly

eur_usd_mo_mean = FX_load(rate='DEXUSEU',start='2018-02-01',isDaily=False)


#Unhedged performance
fx_coef = (eur_usd_mo_mean.shift(1)/eur_usd_mo_mean).dropna(axis=0)
ret_eur_unhedged=(1+arq_m.squeeze())*fx_coef-1

dfr_all = pd.concat([arq_m,eur_usd_mo_mean], axis=1, join='outer')
eur_usd_mo_mean = eur_usd_mo_mean.iloc[1:] #Remove Feb-2018

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
dfr_all['1MO_EUR_interest_rate'].iloc[-1] = 1.897 #Manually add current month average
eur_1mo = dfr_all['1MO_EUR_interest_rate'].iloc[1:]

#USD 1-month rates history
usd_1mo=USD_1m_load(start='2018-03-01',isDaily=False)

dfr_all['1MO_USD_interest_rate']=usd_1mo


# usd_eur_rate => EUR in USD
# eur_usd_rate => USD in EUR
#spot rate x (1 + domestic interest rate) / (1 + foreign interest rate)
#Simulated 1-month forward rates: forward_usd_eur_rate (i.e. EUR_per_USD) = usd_eur_rate * (1 + 0.0175/12)/(1+ 0.01/12)), assuming USD interest rate = 1.75%, EUR = 1%.

eur_usd_spot = eur_usd_mo_mean.squeeze()
eur_usd_forward_calc = eur_usd_spot * (1+usd_1mo.values/100/12)/(1+eur_1mo.values/100/12)
eur_usd_forward_apply = eur_usd_forward_calc.shift(1).dropna().squeeze()

dfr_all['USD per EUR (1mo forward)']=eur_usd_forward_calc
dfr_all.to_csv(os.path.join(subdir, '_ARQuant_monthly_EUR_simulation.csv')) #https://fred.stlouisfed.org/series/DEXUSEU

#Hedging USD exposure using a 1-month FX forward (rolling monthly hedge), 
# funded by USD and EUR deposits — a common currency-hedged return calculation.
dfr_all['eur_returns_hedged']= (1+dfr_all['Return_USD']) * dfr_all['USD per EUR (1mo forward)']/dfr_all['USD per EUR (spot)'] - 1

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


#Formatting EUR returns after fees
eur_ret_fs_net=factsheet(eur_ret_net, 
                         years=['2018', '2019', '2020', '2021', '2022', '2023', '2024','2025'],
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
left_min, left_max = df1['indexed_performance'].min(), df1['indexed_performance'].max()

# top_limit = max(left_max, annual_returns.max())+15

ax1.set_ylim(left_min*0.95, left_max*1.05)  # start at left_min

# Plot indexed performance (left y-axis)
ax1.plot(df1.index.to_timestamp(), df1['indexed_performance'],
         color=rgb_to_matplotlib (11,52,105), #Alternative is rgb_to_matplotlib (13,46,93)
         linewidth=2, label='Indexed performance')
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
fig.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

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

