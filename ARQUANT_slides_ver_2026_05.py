#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified on Aug 29, 2021
@author: alexander

Env: GoTrade37_pip
"""

from IPython import get_ipython
ipython = get_ipython()
if '__IPYTHON__' in globals():
    ipython.magic('load_ext autoreload')
    ipython.magic('autoreload 2')
# get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")
# get_ipython().run_line_magic('matplotlib', 'inline')
    
import numpy as np
import pandas as pd
from os import chdir, listdir, path, rename, makedirs
from os import stat as os_stat
import datetime as dt
from importlib import reload
import os

computer = '/Users/alexander/' #Moscow Macbook
# computer= '/Users/alexander/Library/CloudStorage/' #Nice Macbook

script_dir = os.path.dirname(os.path.abspath(__file__))
maindir = script_dir
librarydir= computer +'Dropbox/0-ML/Python/GoTrader/'
histdir= os.path.join(script_dir, '..', 'Data', 'ARQuant_history')
indexdir = os.path.join(script_dir, '..', 'Data', 'Indexes')

arsenydir = 'Presentation_Inputs/'
intdir = 'Internal_Use/'

chdir(maindir)
import Slides_analytic_function 
from Slides_analytic_function import *    

#%%
new_start='2018-03-01'
new_end = '2026-04-30' #+manually change for Q1 _monthly

year_month = dt.datetime.strptime(new_end, '%Y-%m-%d').strftime('%Y-%m')
eend = dt.datetime.strptime(new_end, '%Y-%m-%d').strftime('%B_%Y_')
sstart = dt.date(int(new_end[:4]),1,1).strftime('%B_%Y_')

report_list1= ['AVESA_Group_Ltd_'+ eend + eend+'daily.csv',
              'AVESA_Group_Ltd_'+ sstart+eend+'monthly.csv'
              ]
report_list2= ['ARQuant_Management_Limited_'+ eend + eend+'daily.csv',
               'ARQuant_Management_Limited_'+ sstart +eend+'monthly.csv' #hide for Q1
              # 'ARQuant_Management_Limited_December_2024_February_2025_monthly.csv' #!!! Change L3M
              # 'ARQuant_Management_Limited_March_2023_February_2024_monthly.csv' #!!! CHANGE if L12M
              ]

files_list = listdir(histdir)
def is_daily_monthly_exist(report_list2, files_list):
    check = True
    for _, val in enumerate(report_list2):
        check = check * (val in files_list)
    return True if check == 1 else False

if is_daily_monthly_exist(report_list1, files_list): report_list = report_list1
elif is_daily_monthly_exist(report_list2, files_list): report_list = report_list2  
else: 
    print ("No update for YTD and/or last month...")
    print('Please download '+' '.join(report_list2)+ ' to directory '+histdir)
    import sys
    sys.exit()  
    
List_of_files=[
    os.path.join(histdir, 'AVESA_Group_Ltd_U3577443_history.csv'),
    os.path.join(indexdir, 'HFRI_Quant_Directional.csv'),
    os.path.join(indexdir, 'Eurekahedge North America Long Short Equities HF Index.csv'),
    os.path.join(histdir, 'French_Fama_approximation.csv'),
    os.path.join(histdir, 'Frecn_Fama_daily.csv'),
    os.path.join(histdir, 'Frecn_Fama_monthly.csv'),
    os.path.join(histdir, 'Risk_Free_Rate_monthly.csv'),
    ]

List_of_last_months=[]
List_of_las_modified =[]
from dateutil import parser
for i, path_to_file in enumerate(List_of_files):
    csv = pd.read_csv(path_to_file,infer_datetime_format=False)
    last = csv.iloc[-1,0]
    last_dt = parser.parse(last)
    List_of_last_months.append(last_dt)
    List_of_las_modified.append(dt.datetime.fromtimestamp(path.getmtime(path_to_file)))
    
last_update_month = min(List_of_last_months).month
condition1 = (last_update_month+1 < dt.datetime.today().month) and (last_update_month<=11)
condition2 = (dt.datetime.today().month ==1) and (last_update_month==11) #now Jan, last update in Nov
condition3 = (dt.datetime.today().month ==2) and (last_update_month==12) #now Jan, last update in Nov


# if condition1 or condition2 or condition3:
  # Update ARQuant, HFRI and EurekaHedge indexes

from Update_dataset_ARQuant_slides_2026_05 import * #HFR and French-Fama updates - NOT IN USE
ARQuant_history_update(report_list[0])
try:
    update_dataset()
except Exception as e:
    print(f"\n⚠️ Warning: Could not update dataset from FRED (timeout/network issue)")
    print(f"Error: {type(e).__name__}: {str(e)[:100]}")
    print("Continuing with existing data...\n")

#%%

# Inputs for monthly updating slides
params={
        # 'new_start': '2018-03-01', 
        # 'new_end' : '2022-10-31',
        'inception' : '2018-03-01',
        'fs_years' : ['2018', '2019', '2020', '2021', '2022', '2023', '2024','2025','2026'],
        'file_returns' : 'AVESA_Group_Ltd_U3577443_history.csv',
        'analytic_periods_stats' : ['Inception', '2018', '2019', '2020', '2021', '2022', '2023','L12M', 'YTD', 'L3M'] ,
        'analytic_periods_ff' : ['Inception','2018','2019','2020','2021','2022','2023','L12M','YTD'] ,
        'analytic_periods_plot' : ['Inception','L36M',],
        'investor_periods_stats' : ['Inception','L36M',
                                    'L12M','YTD',
                                    '2018','2019','2020','2021','2022','2023','2024','2025','2026'] , #YTD
        'investor_periods_ff' : ['Inception','L36M','2018','2019','2020','2021','2022','2023','L12M'] ,
        'investor_periods_plot' : ['Inception'] ,
        'isForWeb' : True ,
        'isForPP' : True,
        'PP_pages_stat' : {'P1':['Inception',
                                 '2024',
                                  '2025','YTD',
                                 ],
                           'P2':['2021', '2022', '2023'],
                           'P3':['2018', '2019', '2020']
                           } ,
        'PP_pages_ff': {'P1':['Inception', 'L36M', 'L12M'],
                        'P2':['2021', '2022', '2023'],
                        'P3':['2018', '2019', '2020']
                        }  
        }

#%%
# def update_statistics(params):
# Assign variables
# new_start=params['new_start'] 
# new_end = params['new_end']
inception = params['inception']
analytic_periods_stats = params[ 'analytic_periods_stats']
analytic_periods_ff = params[ 'analytic_periods_ff']
analytic_periods_plot = params[ 'analytic_periods_plot']
investor_periods_stats = params[ 'investor_periods_stats']
investor_periods_ff = params[ 'investor_periods_ff']
investor_periods_plot = params[ 'investor_periods_plot']
isForWeb = params[ 'isForWeb']
isForPP = params[ 'isForPP']

#%%  
if isinstance(new_start, str):
    year, month, day = map(int, new_start.split('-'))
    new_start= dt.date(year, month, day)
    
if isinstance(new_end, str):
    year, month, day = map(int, new_end.split('-'))
    new_end= dt.date(year, month, day)
    
if isinstance(new_end, dt.datetime):
    new_end= new_end.date()
    
#%%
#print('Loading daily return history of ARquant startegy...')
andrew_ret=pd.read_csv(os.path.join(histdir, params['file_returns']), 
                       infer_datetime_format=False)
andrew_ret['Date']=pd.to_datetime(andrew_ret['Date'], dayfirst=True,
                                  infer_datetime_format='%d/%m/%Y')#correct parse dates
andrew_ret.set_index(['Date'], inplace=True) #setting index
# andrew_ret.index=pd.to_datetime(andrew_ret.index, format='%Y-%m-%d') #change formate of dates
if isinstance(andrew_ret, pd.DataFrame) and len(andrew_ret.columns)>1:
    andrew_ret = andrew_ret[andrew_ret.columns[0]]
    
#Align the requested last day with the actual last day
actual_end = andrew_ret.index[-1].date() #initially it was datestamp
if new_end > actual_end: 
    print("=> Requested end of the period is beyond actual range. Adjuested to the actual end:", actual_end)
    new_end = actual_end

#Align the requested first day with the actual first day
actual_start = andrew_ret.index[0].date()
if new_start < actual_start: 
    print("=> Requested start of the period is beyond actual range. Adjuested to the actual start:", actual_start)
    new_start = actual_start
    
#Building a name for folder with outputs    
# from pandas.tseries.offsets import BMonthEnd
# offset = BMonthEnd()
if new_start.strftime("%Y-%m-%d")==inception:
    _period='Inception_'        
    # if new_end==offset.rollforward(new_end):
    #     _period += new_end.strftime('%Y-%m')
    # else: 
    _period += new_end.strftime('%Y-%m-%d')
else:
    _period=new_start.strftime('%Y-%m-%d')+'_'+new_end.strftime('%Y-%m-%d')
        
datadir = os.path.join('..', 'Data', 'Presentation_' + _period)
makedirs(os.path.join(maindir, datadir), exist_ok=True)
makedirs(os.path.join(maindir, datadir, intdir), exist_ok=True)
makedirs(os.path.join(maindir, datadir, arsenydir), exist_ok=True)
makedirs(os.path.join(maindir, datadir, arsenydir, 'CSV'), exist_ok=True)

# andrew_ret=andrew_ret.loc[ new_start.strftime("%Y-%m-%d") : new_end.strftime("%Y-%m-%d")] #for selecting other dates
andrew_ret=andrew_ret.loc[ new_start : new_end] #for selecting other dates

#%%    
print('\n Saving returns...')    
# andrew_ret.to_csv(maindir+datadir+intdir+'Returns.csv')
# andrew_ret.to_pickle(maindir+datadir+arsenydir+'Returns.pkl')
# andrew_ret.to_csv(maindir+datadir+arsenydir+'CSV/Returns.csv')

# Returns daily->monthly
ak_monthly=andrew_ret.resample("M").apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
ak_monthly.index=ak_monthly.index.to_period('M')
ak_monthly.to_csv(os.path.join(histdir, params['file_returns'][:-4]+'_mothly.csv'))
ak_monthly.to_csv(os.path.join(maindir, datadir, params['file_returns'][:-4]+'_mothly.csv'))

def _drawdown(return_series):
    wealth_index = 1000*(1+return_series).cumprod()
    previous_peaks = wealth_index.cummax()
    previous_peaks[previous_peaks.values<1000]=1000.
    drawdowns = (wealth_index - previous_peaks)/previous_peaks
    return drawdowns
dd = _drawdown(ak_monthly.squeeze())
dd.to_csv(os.path.join(maindir, datadir, 'DrawDowns_monthly.csv'))    

#%%
#Selecting possible periods from all_periods_stats
def possible_periods_monthly(ak_monthly, #returns
                     new_start, #start date
                     wanted_list #the list we are looking for
                     #period_index #function of building indexes
                     ):
    year_idx = ak_monthly.index.year.unique()
    month_idx = ak_monthly.index.unique()
    possible_list = []
    if new_start.strftime("%Y-%m-%d")==inception: 
        possible_list=['Inception']
    else: 
        possible_list =['Since '+ new_start.strftime("%Y-%m-%d")]
        
    for period in wanted_list[1:]: #all_periods_stats is given as argument
        if period[0] == 'L' and len(month_idx)>= int(period[1:-1]) :
            possible_list.append(period)
        elif period == 'YTD': possible_list.append(period)
        elif period == 'MTD': possible_list.append(period)
        else:
            if int(period) in year_idx:
                possible_list.append(period)
    return possible_list 

def period_index_monthly(df, period_list):
    
    if not isinstance(df.index, pd.PeriodIndex): 
        return print('Index should be PeriodIndex !!!')

    periods={}
    for per in period_list:
        ##for debugging 
        # print(per)
        # z=input('Press any key...')
        if per=='Inception':    
            periods[per]=df.index
        elif per[:6]=='Since ':
            #Since and till present
            periods[per]=df.loc[per[6:13] : ].index
            #Since and till the end of that year                
            end=df.loc[per[6:10]].index[-1].strftime('%Y-%m')
            periods[per[6:]+'_'+ end ] = df.loc[per[6:13] : end].index           
        elif per=='MTD':        periods[per]=df.index[-1]
        elif per=='YTD':        
            year= df.index.year.unique()[-1]
            periods[per]=df.loc[str(year)].index
        elif per[0]=='2': 
            periods[per]=df.loc[per].index
        elif per[0]=='L':
            p=int(per[1:-1])
            periods[per]=df.index[-p:]
        else: continue
    return periods
# periods = period_index_monthly(df, possible_periods)  #testing

#%%
## Statistics
#Risk Free Rate - RF
rfr_monthly = pd.read_csv(os.path.join(histdir, 'Risk_Free_Rate_monthly.csv'), index_col=[0],
                          infer_datetime_format=True).squeeze()
rfr_monthly.index=pd.to_datetime(rfr_monthly.index, format='%Y-%m-%d')
rfr_monthly.index=rfr_monthly.index.to_period('M')
print('Last month for Risk Free rate : ', rfr_monthly.index[-1])

chdir(maindir)
### Statistics of ARQuant strategy (Return gross, before fees)
print('\n*** Preparing and saving statistics ***')

# #Analytic (for internal use only)
print('    for internal use')
periods = period_index_monthly(ak_monthly, 
                                possible_periods_monthly(ak_monthly, new_start, 
                                                         analytic_periods_stats)
                                )
from Slides_analytic_function import stats_periods_monthly

ak_stats_internal=stats_periods_monthly(ak_monthly, periods, rfr_monthly)

from Slides_for_print_function import stats_periods_for_print2
ak_stats_internal_for_print=stats_periods_for_print2(ak_stats_internal)
ak_stats_internal_for_print.index.rename('Risk/Return (before fees)', inplace=True)
ak_stats_internal_for_print.to_csv(os.path.join(maindir, datadir, intdir, 'Stats_internal_for_print.csv'))

#For presentation (investors)
print('    for investors (presentation)')
periods = period_index_monthly(ak_monthly,
                               possible_periods_monthly(ak_monthly, new_start, investor_periods_stats)
                               )
ak_stats_investor=stats_periods_monthly(ak_monthly, periods, rfr_monthly)
ak_stats_investor.to_pickle(os.path.join(maindir, datadir, arsenydir, 'Stats.pkl')) #keeps index and data type
ak_stats_investor.index.rename('Risk/Return', inplace=True)
ak_stats_investor.to_csv(os.path.join(maindir, datadir, arsenydir, 'CSV', 'Stats.csv'))

#%%    
### Factsheet before and after fees
chdir(maindir)
reload(Slides_analytic_function)
from Slides_analytic_function import factsheet
# Set years and moths
print('Preparing Fact sheet (before and after fees)...')

#Fact sheet BEFORE fees
ak_fs_gross=factsheet(ak_monthly, 
                      years=params['fs_years'],
                      output='before fees', decim=3)
ak_fs_gross.to_csv(os.path.join(datadir, intdir, 'Fact Sheet (before fees).csv'))

###Fact sheet AFTER fees
NAV0=100.
#Until Dec-2022
mfee=0.85/100
pfee=18.5/100
hurdle= 3./100
print('Until Dec-2022   Mtm fee: {0:.2%},  Pfm fee: {1:.1%}, Hurdle: {2:.2%}'.format(mfee, pfee, hurdle))

#Until Sep-2022 cash basis, i.e. PF is calculated when paid at the quarter end (cash basis)
ak_net_monthly1 = after_fees2q(ak_monthly.loc[:'2022-09'], NAV0=NAV0, 
                               mfra=mfee, pfr=pfee, 
                               hra=hurdle, out='return'
                               ).rename('ARQuant (net of fees)')

#From October 2022 accraul basis, i.e. PF is calculated on monthly basis (accual method)
nav_monthly2, hwm_monthly2, ak_net_monthly2 = after_fees2m(ak_monthly.loc['2022-10':'2022-12'], 
                                                           NAV0=NAV0, 
                                                           mfra=mfee, pfr=pfee, 
                                                           hra=hurdle, out='nav_hwm_ret'
                                                           )
ak_net_monthly2 .rename('ARQuant (net of fees)')

#Saving details of accuals until Dec-2022
after_fees2m(ak_monthly.loc['2022-10':], NAV0=nav_monthly2.iloc[-1],
             mfra=mfee, pfr=pfee,
             hra=hurdle, out='details').T.to_csv(os.path.join(maindir, datadir, 'Details of fees accuals until Dec-2022.csv'))

#Since Jan-2023 new MF and PF rates (2nd band, ie 1-3 mln)
mfee1=0.9/100
pfee1=23/100
hurdle1= 3./100
#Take nav_netto and hwm from the proevious period
print('Since Jan-2023   Mtm fee: {0:.2%},  Pfm fee: {1:.1%}, Hurdle: {2:.2%}'. format(mfee1,pfee1, hurdle1))
ak_net_monthly3 = after_fees2m(ak_monthly.loc['2023-01':], 
                               NAV0=nav_monthly2.iloc[-1],
                               hwm0=hwm_monthly2.iloc[-1],
                               mfra=mfee1, pfr=pfee1, 
                               hra=hurdle1, out='return'
                               ).rename('ARQuant (net of fees)')
#Saving details of accuals since Jan-2022
after_fees2m(ak_monthly.loc['2023-01':],
             NAV0=nav_monthly2.iloc[-1],
             hwm0=hwm_monthly2.iloc[-1],
             mfra=mfee1, pfr=pfee1,
             hra=hurdle1, out='details').T.to_csv(os.path.join(maindir, datadir, 'Details of fees accuals since Jan-2023.csv'))

#Merging all periods
ak_net_monthly = pd.concat([ak_net_monthly1,
                            ak_net_monthly2,
                            ak_net_monthly3], axis=0)
ak_net_monthly.rename('ARQuant (net of fees)', inplace=True)
ak_net_monthly.index=ak_monthly.index
 
ak_net_monthly.to_csv(os.path.join(maindir, datadir, params['file_returns'][:-4]+'_mothly_net.csv'))

#factsheet as CSV
feestring=str(round(mfee1*100,2))+'-'+str(int(pfee1*100))+'-'+str(round(hurdle1*100,1))
# kwargs={'NAV0' : NAV0, 'mfra' : mfee, 'pfr' : pfee, 'hra' : hurdle, 'out' : 'both'}
ak_fs_net=factsheet(ak_net_monthly, 
                    years=params['fs_years'],
                    output='after fees', af_func=None, #None if net returns, otherwise after_fees or after_fees2m or after_fees2q
                    decim=4, 
                    # **kwargs
                    )
ak_fs_net.to_csv(os.path.join(datadir, intdir, 'Fact Sheet (after fees '+feestring+').csv'))
ak_fs_net.to_csv(os.path.join(datadir, arsenydir, 'Fact_Sheet_after_fees.csv'))

#%%    
### French-Fama
print('Calculating French-Fama loadings for different periods...')

ff_monthly = pd.read_csv(os.path.join(histdir, 'Frecn_Fama_monthly.csv'), 
                 index_col=[0], infer_datetime_format=True)
ff_monthly.index=pd.to_datetime(ff_monthly.index, format='%Y-%m-%d')
ff_monthly.index=ff_monthly.index.to_period('M')

#Change risk-free - as TB3MS (3M T-bills)
ff_monthly['RF']=rfr_monthly

#FF 3
ff_monthly = ff_monthly.drop(['CMA','RMW'], axis=1)

#Only SPY - CAMP
spy= pd.read_csv(os.path.join(histdir, 'SPY_returns_Monthly.csv'),
                  index_col=[0], infer_datetime_format=True).squeeze()
spy.index=pd.to_datetime(spy.index).to_period('M')
spy.rename('SPY', inplace=True)

ff_monthly['Mkt-RF'] = spy-rfr_monthly
ff_monthly = ff_monthly.drop(['SMB', 'HML'], axis=1)
    
def ff_alpha_beta2(ak_monthly, ff_monthly, periods, 
                   datadir, librarydir, subdir='French-Fama/',
                   display_=True, print_=True, rnd=4): 
    
    from os import chdir, getcwd, makedirs
    
    makedirs(os.path.join(datadir, subdir), exist_ok=True)    
    cd = getcwd()
    chdir(librarydir)
    
    def FF3x2(ak_monthly, ff_monthly, dirname='', 
              display_= display_, print_= print_, rnd=rnd, name=''):
        # import warnings
        # warnings.warn("deprecated", DeprecationWarning)
        
        # name = ak_monthly.name if isinstance(ak_monthly, pd.Series) else ak_monthly.columns[0] 
 
        exp_var_ff = ff_monthly.drop(['RF'],axis=1)
        exp_var_ff['alpha'] = 1
        y_excess = pd.Series(data=(ak_monthly.squeeze() - ff_monthly['RF']), name=name)
                   
        import statsmodels.api as sm
        lm = sm.OLS(y_excess, exp_var_ff).fit()
        GT_res_ff =pd.to_numeric(lm.params).round(rnd)
        GT_res_ff.name = name
        if display_ : print(lm.summary())
        if print_ :
            sample = open(dirname+name+'_FF3x2.txt', 'w') 
            print(lm.summary(), file = sample) 
            sample.close()     
            GT_res_ff.to_csv(dirname+name+'_FF3x2.csv') 
        return #GT_res_ff
    
    bt_all=pd.DataFrame()        
    for period in periods.keys():
        if len( periods[period] ) < 8: continue
        
        idx_common = ff_monthly.index.intersection(ak_monthly.loc[periods[period]].index)
        ff_monthly2 = ff_monthly.loc[idx_common]
        ak_monthly2 = ak_monthly.loc[idx_common]
        
        FF3x2(ak_monthly2, ff_monthly2,
              print_=True, display_=False,
              dirname=os.path.join(datadir, subdir), rnd=rnd, name=period)
        bt=pd.read_csv(os.path.join(datadir, subdir, period+'_FF3x2.csv'), index_col=[0])
        bt_all=pd.concat([bt_all, bt], axis=1)
        
    bt_all.loc['Beta (S&P500)']=bt_all.loc['Mkt-RF']
    bt_all.drop(['Mkt-RF'],inplace=True)
    # bt_all.loc['Alpha(month)']= bt_all.loc['alpha']
    bt_all.loc['Alpha (p.a.)']= bt_all.loc['alpha']*12
    bt_all.drop(['alpha'],inplace=True)
    # bt_all=bt_all.reindex(['Alpha(month)', 'Beta', 'SMB', 'HML', 'RMW', 'CMA'])
    bt_all=bt_all.reindex(['Alpha (p.a.)', 'Beta (S&P500)'])
    
    chdir(cd)
    return bt_all

#Analytic (for internal use only)
print('    for internal use')
periods = period_index_monthly(ak_monthly, 
                               possible_periods_monthly(ak_monthly, new_start, analytic_periods_ff)
                               )
bt_all_internal=ff_alpha_beta2(ak_monthly, ff_monthly, periods,
                               os.path.join(maindir, datadir, intdir), librarydir,
                               subdir='French-Fama/', display_=False,
                               print_=True, rnd=4)

bt_all_internal.to_csv(os.path.join(maindir, datadir, intdir, 'FF3x2_internal.csv'))

#For investors
print('    for investors (presentation)')
periods = period_index_monthly(ak_monthly, 
                               possible_periods_monthly(ak_monthly, new_start, investor_periods_ff)
                               )
 
bt_all= ff_alpha_beta2(ak_monthly, ff_monthly, periods,
                       os.path.join(maindir, datadir, arsenydir), librarydir,
                       subdir='French-Fama/', display_=False,
                       print_=True, rnd=4)

bt_all.to_pickle(os.path.join(maindir, datadir, arsenydir, 'FF3x2.pkl'))
bt_all.to_csv(os.path.join(maindir, datadir, arsenydir, 'CSV', 'FF3x2.csv'))
    
#%%  
#ETF basket
from Benchmark_new_2025 import benchmark_update
etf_df= benchmark_update(startday = '2024-01-01')

bm_df=etf_df.loc['2024':new_end, ['New bechmark-1 (3 ETF weighted)', 'New bechmark-3 (3 ETF equally)']]

bm_new_daily=pd.concat([bm_df.loc['2024':'2025-02', 'New bechmark-1 (3 ETF weighted)'],
                        bm_df.loc['2025-03':, 'New bechmark-3 (3 ETF equally)']
                        ],axis=0)

bm_new_daily = bm_new_daily.rename('New bechmark (ETF basket)')
bm_new = bm_new_daily.resample("M").apply(lambda x: ((x + 1).prod() - 1))
bm_new.index=bm_new.index.to_period('M')

#Old Eureka index
erk = pd.read_csv(os.path.join(indexdir, 'Eurekahedge North America Long Short Equities HF Index.csv'), 
                  index_col=[0], infer_datetime_format=True)['Return']
erk.index= pd.to_datetime(erk.index).to_period('M')
erk.rename('Old benchmark (EurekaHedge N.America)', inplace=True)
erk=erk.loc[new_start.strftime('%Y-%m'):new_end.strftime('%Y-%m')]

# bm_compare=pd.concat([erk,bm_new],axis=1).loc['2024']
# ax=(bm_compare*100).plot(ylabel='Monthly returns (%)', xlabel="", )
# ax.xaxis.set_major_formatter('{x:.0%}')
# plt.show()
#%%
    
#Merge into one dataframe
dfs1=[ak_net_monthly, bm_new, erk]
dfs1=pd.concat(dfs1, axis=1, join='outer').reset_index().set_index(['Date'])


#%%
# Load SPY - monthly returns
print('Loading SPY monthly returns...')
spy= pd.read_csv(os.path.join(histdir, 'SPY_returns_Monthly.csv'),
                 index_col=[0], infer_datetime_format=True).squeeze()
spy.index=pd.to_datetime(spy.index).to_period('M')
spy.rename('S&P500 (SPY)', inplace=True)

##IF GROSS MONTHLY RETURNS    
# ak_monthly.rename(columns={'Return':'ARQuant'}, inplace=True)
# dfs1=[ak_monthly, spy_monthly, qqq_monthly]

# , HFR_Equity_Total]
dfs2=pd.concat([dfs1, spy], axis=1, join='inner')
dfs2=dfs2.loc[dfs1.index]

dfs2.to_csv(os.path.join(maindir, datadir, intdir, 'ARQuant vs Benchmarks.csv'))
dfs2.to_pickle(os.path.join(maindir, datadir, arsenydir, 'ARQuant vs Benchmarks.pkl'))
dfs2.to_csv(os.path.join(maindir, datadir, arsenydir, 'CSV', 'ARQuant vs Benchmarks.csv'))


#%%
#Plot - for Internal Use
plotdir='Plots/'
periods = period_index_monthly(ak_monthly, 
                              possible_periods_monthly(ak_monthly, new_start, analytic_periods_plot)
                              )
   
print('Creating Drawdown Period Plot...')
chdir(maindir)
# from Slides_analytic_function import drawdown_details_monthly
from Slides_for_print_function import plot_longest_drawdowns
makedirs(os.path.join(maindir, datadir, intdir, plotdir), exist_ok=True)

dicclrs={'arquant':'#ea6639',   # '#dc6d45'
      'benchmark1':'#43884e',
      'benchmark2':'#6b6c6d',
      'benchmark3': '#b5583c',
      'background':'#edb6a2', # '#f2d1c6'
      'dates': '#afb1b2',    # '#d6d7d8'
      'plotname': 'black'}
for period in periods.keys():
    print('Period: ', period)    
    model3 = 'Drawdoans_Periods_'
    savefig3=os.path.join(maindir, datadir, intdir, plotdir, model3+period+'.png')
    save_dd=os.path.join(maindir, datadir, intdir, plotdir, model3+period+'.csv')
    # logret = np.log(1 + andrew_ret.loc[periods[period]] )

    ret = ak_net_monthly.loc[periods[period]]
    ret.index=ret.index.to_timestamp('M')

    # ret = andrew_ret.loc[str(periods[period][0]):str(periods[period][-1])]
    plot_longest_drawdowns(ret.squeeze() if ret.shape[0]>1 else pd.Series(ret.values[0],index=ret.index), 
                           dicclrs,
                           criteria = 'days',
                           periods=5, lw=1.5,
                           yscale = 'linear',
                           ytext = "Cumulative Net Return",
                           savefig=savefig3, save_dd=save_dd,
                           grayscale=False, 
                           show=False, figsize=(8.5, 5.5),
                           isOffset = True #to change the 1st day of the month to the last day of the previous one
                           )
#%%
print('Plotting monthly performance of ARQuant vs SPY, QQQ and EH indexes...')
chdir(maindir)        
from Slides_for_print_function import plot_for_print
    
#Dictionary with colors
clist=[] #Colors from ARQuant presentation
for key, value in dicclrs.items():
    temp = value
    clist.append(temp)
from matplotlib.cm import get_cmap
clist=clist[:3]
if len(dfs2.columns) > len(clist) :
    d=len(dfs2.columns) - len(clist)
    cmap = get_cmap('Paired') #RuOr Accent
    for i in range(d):
        clist.append(cmap(1/d))
  
def possible_periods_m(ret, new_start, wanted_list):
    year_idx=ret.index.year.unique()
    month_idx=ret.index
    possible_list = []
    if new_start.strftime("%Y-%m-%d")==inception: 
        possible_list=['Inception']
    else: 
        possible_list =['Since '+ new_start.strftime("%Y-%m-%d")]
    for period in wanted_list[1:]: #all_periods_stats is given as argument
        if period in year_idx:
            possible_list.append(period)
        if period[0] == 'L' and len(month_idx)>= int(period[1:-1]) :
            possible_list.append(period)
        if period == 'YTD': possible_list.append(period)
        if period == 'MTD': possible_list.append(period)
    return period_index(ret, possible_list)    

periods=possible_periods_m(dfs2, new_start, analytic_periods_plot)  
    
for period in periods.keys():
    print('Period: ', period)    
    dfs_wealth = (1+dfs2.loc[periods[period]]).cumprod()
    dfs_wealth['New bechmark (ETF basket)'].loc['2023-12']=1.
    multiple=dfs_wealth['Old benchmark (EurekaHedge N.America)'].loc['2023-12']
    dfs_wealth['New bechmark (ETF basket)'].loc['2023-12':]=dfs_wealth['New bechmark (ETF basket)'].loc['2023-12':]*multiple
    plot_for_print(dfs_wealth,
                   dicclrs,
                   datadir=os.path.join(maindir, datadir, intdir, plotdir), 
                   yscale = 'log', base =100,
                   marker=[None,None,None,None,None],
                   ytext = "Net Return Index (Log scale)",
                   plotname='ARQuant_vs_Benchmarks_'+period,
                   figsize=(9,6), show = False, 
                   c=clist)
    
#%%
#Table and plot for PowerPoint (if manual)
# datadir = 'Data/Presentation_Inception_2022-03-31/'
if isForPP:
    chdir(maindir)
    from ARQUANT_slides_for_PowerPoint_2026_05 import update_PowerPoint
    update_PowerPoint(maindir, datadir, arsenydir,
                      pages_stat=params['PP_pages_stat'],
                      pages_ff = params['PP_pages_ff'],
                      wsize_stat = {'P1':'18cm;', 'P2':'18cm;', 'P3':'18cm;'}, #P1 was 16.5
                      wsize_ff = {'P1':'10cm;', 'P2':'12cm;', 'P3':'12cm;'},
                      resolution = 200,
                      drop_list = ['Beta (to SPY)'],
                      )
    
print('*** Preparation for investor slides is completed ***')
print('\n')
#%%
# Create a folder for web slides 
if isForWeb:
    # import ARQUANT_slides_for_website_v2
    if new_start.strftime("%Y-%m-%d")==inception: 
        chdir(maindir)
        from ARQUANT_slides_for_website_2026_05 import update_web
        update_web(maindir, datadir, arsenydir, intdir,
                   filename = 'Fact Sheet (after fees '+feestring+').csv',
                   isAlpha=False)
    else: 
        from termcolor import colored, cprint    
        cprint('\n!!! Because Start Date is not the Inception, tables and slides for website is not preparing !!!', 'red', attrs=['blink'])
# return
# update_statistics(params)