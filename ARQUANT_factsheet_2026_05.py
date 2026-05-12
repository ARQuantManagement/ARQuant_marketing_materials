#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified on feb 08, 2026
@author: alexander

Env: GoTrade37_pip

Updates compared to the previous version:
    - Adjustments on the Y2026 start    
"""

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
from os import chdir, listdir, path, rename, makedirs, remove
from os import stat as os_stat
import datetime as dt
from importlib import reload

script_dir = os.path.dirname(os.path.abspath(__file__))
maindir = script_dir
librarydir = os.path.join(os.path.expanduser('~'), 'Dropbox/0-ML/Python/GoTrader/')
histdir = os.path.join(script_dir, '..', 'Data', 'ARQuant_history')
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
#YTD
sstart = dt.date(int(new_end[:4]),1,1).strftime('%B_%Y_') 
# #L12M
# from datetime import date
# from dateutil.relativedelta import relativedelta
# sstart_ = dt.datetime.strptime(new_end, '%Y-%m-%d').date() + relativedelta(months=-12,day=31)+relativedelta(months=1,day=1)
# sstart = sstart_.strftime('%B_%Y_')

report_list1= ['AVESA_Group_Ltd_'+ eend + eend+'daily.csv',
              'AVESA_Group_Ltd_'+ sstart+eend+'monthly.csv'
              ]
report_list2= ['ARQuant_Management_Limited_'+ eend + eend+'daily.csv',
               'ARQuant_Management_Limited_'+ sstart +eend+'monthly.csv'
               # 'ARQuant_Management_Limited_September_2025_February_2026_monthly.csv' #!!! CHANGE
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
    
if isinstance(new_start, str):
    year, month, day = map(int, new_start.split('-'))
    new_start= dt.date(year, month, day)
    
if isinstance(new_end, str):
    year, month, day = map(int, new_end.split('-'))
    new_end= dt.date(year, month, day)
    
if isinstance(new_end, dt.datetime):
    new_end= new_end.date()
#%%
# isTrue=True
List_of_files=[
    os.path.join(histdir, 'AVESA_Group_Ltd_U3577443_history.csv'),
    # os.path.join(indexdir, 'bm_newI_Quant_Directional.csv'),
    os.path.join(indexdir, 'Eurekahedge North America Long Short Equities HF Index.csv'),
    os.path.join(histdir, 'French_Fama_approximation.csv'),
    os.path.join(histdir, 'Frecn_Fama_daily.csv'),
    os.path.join(histdir, 'Frecn_Fama_monthly.csv'),
    os.path.join(histdir, 'Risk_Free_Rate_monthly.csv')
    ]

# List_of_time_modified=[]
# for i, path_to_file in enumerate(List_of_files):
#     stat_result = os_stat(path_to_file)
#     List_of_time_modified.append(dt.datetime.fromtimestamp(stat_result.st_mtime, 
#                                                            tz=dt.timezone.utc).date())

# if min(List_of_time_modified).month < dt.datetime.today().month :
#     #Update ARQuant, bm_newI and EurekaHedge indexes
#     from Update_dataset_ARQuant_slides_11_2022 import update_dataset
#     update_dataset(report_list[0])

List_of_last_months=[]
from dateutil import parser
for i, path_to_file in enumerate(List_of_files):
    csv = pd.read_csv(path_to_file,infer_datetime_format=False)
    last = csv.iloc[-1,0]
    last_dt = parser.parse(last)
    List_of_last_months.append(last_dt)
    
last_update_month = min(List_of_last_months).month
condition1 = (last_update_month+1 < dt.datetime.today().month) and (last_update_month<=11)
condition2 = (dt.datetime.today().month ==1) and (last_update_month==11) #now Jan, last update in Nov
condition3 = (dt.datetime.today().month ==2) and (last_update_month==12) #now Jan, last update in Nov

# if condition1 or condition2 or condition3:
#     #Update ARQuant, bm_newI and EurekaHedge indexes

from Update_dataset_ARQuant_slides_2026_05 import *
ARQuant_history_update(report_list[0])
try:
    update_dataset()
except Exception as e:
    print(f'Warning: Failed to update dataset: {type(e).__name__}: {e}')
    print('Continuing with existing data...')

#%%    
#print('Loading daily return history of ARquant startegy...')    
andrew_ret=pd.read_csv(os.path.join(histdir, 'AVESA_Group_Ltd_U3577443_history.csv'), 
                       infer_datetime_format=False)
andrew_ret['Date']=pd.to_datetime(andrew_ret['Date'], dayfirst=True,
                                  infer_datetime_format='%d/%m/%Y')#correct parse dates
andrew_ret.set_index(['Date'], inplace=True) #setting index
andrew_ret.index=pd.to_datetime(andrew_ret.index, format='%Y-%m-%d') #change formate of dates

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
if new_start.strftime("%Y-%m-%d")=='2018-03-01':
    _period='Inception_'        
    # if new_end==offset.rollforward(new_end):
    #     _period += new_end.strftime('%Y-%m')
    # else: 
    _period += new_end.strftime('%Y-%m-%d')
else:
    _period=new_start.strftime('%Y-%m-%d')+'_'+new_end.strftime('%Y-%m-%d')
        
datadir = os.path.join('..', 'Data', 'Factsheet_' + _period)
makedirs(os.path.join(maindir, datadir), exist_ok=True)

#%%    
# Returns daily->monthly
ak_monthly=andrew_ret[new_start:new_end].resample("M").apply(lambda x: ((x + 1).cumprod() - 1).last("D")).squeeze()
ak_monthly.index=ak_monthly.index.to_period('M')
ak_monthly.rename('ARQuant (gross)', inplace = True)
# ak_monthly.to_csv(os.path.join(maindir, datadir, 'AVESA_Group_Ltd_U3577443_monthly.csv'))

# #%%
# #Fact sheet BEFORE fees
# ak_fs_gross=factsheet(ak_monthly, output='before fees', decim=3)
# ak_fs_gross.to_csv(datadir+intdir+'Fact Sheet (before fees).csv')

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
ak_net_monthly2 = ak_net_monthly2.rename('ARQuant (net of fees)')

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
#Merging all periods
ak_net_monthly = pd.concat([ak_net_monthly1,
                            ak_net_monthly2,
                            ak_net_monthly3], axis=0)
ak_net_monthly.rename('ARQuant (net of fees)', inplace=True)
ak_net_monthly.index=ak_monthly.index
 
#factsheet as CSV
feestring=str(round(mfee1*100,2))+'-'+str(round(pfee1*100,1))+'-'+str(round(hurdle1*100,1))
# kwargs={'NAV0' : NAV0, 'mfra' : mfee, 'pfr' : pfee, 'hra' : hurdle, 'out' : 'both'}
years_list=['2018', '2019', '2020', '2021', '2022', '2023', '2024','2025','2026']
ak_fs_net=factsheet(ak_net_monthly, 
                    years=years_list,
                    output='after fees', af_func=None, #None if net returns, otherwise after_fees or after_fees2m or after_fees2q
                    decim=4, 
                    # **kwargs
                    )
    
#%%#Render factsheet as HTML and PGN
chdir(maindir)
from Slides_for_print_function import f_fsnet, factsheet_html #,factsheet_html_v2
#Newsletter
height1 = 6.45#cm
rh1=height1/(len(years_list)+1)-len(years_list)*0.01
# rh1=.48
factsheet_html(f_fsnet(ak_fs_net, pct=''),
               os.path.join(maindir, datadir, '_nl 1- Fact sheet (after_fees' + feestring + ')'),
               resolution = 300, isLastRow = False, isWriteHTML = False,
               table_width = '7.25cm;', 
               # col_formatter =['6.5%']+(['7%',]*12)+['9.5%'], 
               col_width = ('7.00%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;',
                            '7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.15%;','7.30%;'), 
                width= '40;', #'24.95cm;', # 24.95/7*8=28.5
               row_height = str(rh1)+'cm;',
               height = str(height1)+'cm;',
               font_size='15px',
               ) 

#Factsheet
height2 = 8.8#cm
rh2=height2/len(years_list)-0.16
factsheet_html(f_fsnet(ak_fs_net, pct=''),
               os.path.join(maindir, datadir, '_fs 1- Fact sheet (after_fees' + feestring + ')'),
               resolution = 300, isLastRow = False, isWriteHTML = False,
               table_width = '14.7cm;', #if add row increase by 1.142857 420px
               # col_formatter =['6.5%']+(['7%',]*12)+['9.5%'], 
               col_width = ('7.2%;','7.4%;','7.0%;'), 
               width='28.57cm;', # width = 25/7.7 (3.24675) of height
               row_height = str(rh2)+'cm;', # 7 rows from Y2018 to Y2023;row_height = '36px;', 
               height = str(height2)+'cm;', #height is 1.1 per row
               font_size='18px',
               ) 

#%%    
## ======== Last Month ========
#Dictionary with colors
dicclrs={'arquant':'#ea6639',   # '#dc6d45'
      'benchmark1':'#43884e',
      'benchmark2':'#6b6c6d',
      'benchmark3': '#b5583c',
      'background':'#edb6a2', # '#f2d1c6'
      'dates': '#afb1b2',    # '#d6d7d8'
      'plotname': 'black'}
clist=[] #Colors from ARQuant presentation
for key, value in dicclrs.items():
    temp = value
    clist.append(temp)
from matplotlib.cm import get_cmap
clist=clist[:3]

#%%
from os import chdir

chdir(maindir)
from Slides_for_print_function import plot_bar_line, stat_html
from IBKR_lib import parse_flexreport, render, contrib_selection

for i, report in enumerate(report_list):
    print("Report : ", report)    
    #Extract selected sections from IB Report 1118496 as raw dataframe
    dic = parse_flexreport(os.path.join(histdir, report),
                           section = ['Time Period Performance Statistics',
                                      'Cumulative Performance Statistics',
                                      'Performance by Symbol'])       
    # Get Returns and Contributors as dataframes
    ret, contrib = render(dic, output = 'both')
    
    #remove extra columns
    contrib = contrib.drop(columns=['Sector', 'AvgWeight','Return', 'Unrealized_P&L', 'Realized_P&L', 'Open'], 
                           axis=1)
    # contrib = contrib_selection(contrib,
    #                             select = ['Symbol', 'Description', 'Instrument', 'Contribution'],
    #                             criteria = 'Contribution',
    #                             ntop=None, isUSD=True
    #                             )
    if ret.shape[1]>4  or contrib.shape[1]>4:
        print(report+"    is damaged and to be replaced !!!")
        print('ret.shape[1] = ',ret.shape[1])
        print('contrib.shape[1] = ',contrib.shape[1])

    ##Make a Bar+Line plot for Returns
    ret.set_index(['Date'], inplace=True) #setting index
    ret.index=pd.to_datetime(ret.index)
    ret=ret.drop(columns=['Account'])

    if report == report_list[0]:
        ret.rename(columns={'Return':'Daily', 'Cum Return':'Cumulative'}, inplace=True)
        periodcontrib = ret.index[-1].strftime('%B')
        per = 'Last Month '
        # height = (15.59+0.7)/18 * (1+contrib.shape[0])
    if report == report_list[1]:
        ret.rename(columns={'Return':'Monthly', 'Cum Return':'Cumulative'}, inplace = True)
        periodcontrib = ret.index[-1].strftime('%Y')+' YTD'
        per = 'YTD '
        # height = 19.65
   
    #for Newsletter
    plot_bar_line(ret,
                  dicclrs,
                  # datadir= maindir+'Data/Factsheet_Inception_2022-04-30/',
                  datadir=os.path.join(maindir, datadir), 
                  plotname='_nl '+str(i+2)+'- Plot '+per+ret.columns[0]+' and '+ret.columns[1]+' Returns',
                  yscale = 'linear', base =1,
                  ytext = "Return (%)",
                  figsize=(10,6), show = False, subtitle=False, isGrid = True,
                  c=clist)
    #for Factsheet
    plot_bar_line(ret,
                  dicclrs,
                  # datadir= maindir+'Data/Factsheet_Inception_2022-04-30/',
                  datadir=os.path.join(maindir, datadir),
                  plotname='_fs '+str(i+2)+'- Plot '+per+ret.columns[0]+' and '+ret.columns[1]+' Returns',
                  yscale = 'linear', base =1,
                  ytext = "Return (%)",
                  figsize=(12.5,6), show = False, subtitle=False, isGrid = True,
                  c=clist)
#%%
    ##Make a table as picture for Contributors
    # contrib = contrib.drop(contrib[contrib.Symbol=='USD'].index, axis=0)
    try:
        contrib = contrib.set_index('Symbol').drop('USD',axis=0).reset_index()        
    except:
        print('USD is not found')
        
    contrib = contrib.sort_values(by='Contribution', ascending=False, ignore_index = True)
    if contrib.shape[0]>20:
        contrib=contrib.iloc[:10].append(contrib.iloc[-10:])

    step =(15.59+0.7)/18 
    height = step * (1+contrib.shape[0])

    if report == report_list[0]: 
        contrib_LM = contrib.set_index('Symbol')
        contrib_LM.to_csv(os.path.join(maindir, datadir, 'Contributors_' + eend[:-1] + '.csv'))
        contrib_list = contrib['Symbol'].to_list()
    contrib.Contribution = contrib.Contribution.apply("{:.3f}%".format)
    
    #for Newsletter
    filename = '_nl '+str(i+2)+'- Contributors ' + periodcontrib    
    if per == "YTD ": coef = 1.22 #1.25 by default
    else: coef = 1.55 #1.5 by default
    
    stat_html(contrib.set_index('Symbol'),
              os.path.join(maindir, datadir, filename), 
              # maindir+datadir,
              resolution = 200, isLastRow = False, isWriteHTML = False,
              table_width = '100%', row_height = "100%;",
              col_space = '20px', #Minimum space of column
              col_formatter =['13%', '47%', '20%', '20%'],
              size ='width:'+str(height*coef)+'cm; height: '+str(height+0.1)+'cm;'
              )
    
    #for FactSheet
    if contrib.shape[0]>10: 
        contrib20=contrib.iloc[:10].append(contrib.iloc[-10:])
    else: 
        contrib20 = contrib
    contrib20 = contrib20.drop(columns=['Instrument'], axis=1)
    height = step * (1+contrib20.shape[0])
    filename = '_fs '+str(i+2)+'- Contributors ' + periodcontrib    
    stat_html(contrib20.set_index('Symbol'),
              os.path.join(maindir, datadir, filename), 
              # maindir+datadir,
              resolution = 200, isLastRow = False, isWriteHTML = False,
              table_width = '100%', row_height = '29px;',
              col_space = '20px', #Minimum space of column
              col_formatter =['17%', '58%', '25%'],
              size ='width: 12.75cm; height: '+str(height-step*1.76)+'cm;') #width 13.0 by default


    if report == report_list[0]: #Last Month
        remove(os.path.join(maindir, datadir, '_fs 2- Contributors ')+ periodcontrib +'.png')
    
#%%
## ======= YTD Section ========
# New index -monthly returns
from Benchmark_new_2025 import benchmark_update
etf_df= benchmark_update(startday = '2024-01-01')

bm_df=etf_df.loc['2024':new_end, ['New bechmark-1 (3 ETF weighted)', 'New bechmark-3 (3 ETF equally)']]

bm_new_daily=pd.concat([bm_df.loc['2024':'2025-02', 'New bechmark-1 (3 ETF weighted)'],
                        bm_df.loc['2025-03':, 'New bechmark-3 (3 ETF equally)']
                        ],axis=0)

bm_new_daily = bm_new_daily.rename('New bechmark (ETF basket)')
bm_new = bm_new_daily.resample("M").apply(lambda x: ((x + 1).prod() - 1))
bm_new.index=bm_new.index.to_period('M')

# From 'Eurekahedge North America Long Short Equities HF Index.csv' - mothly returns
print('Loading Eureka Hedge Index monthly returns...')
erk = pd.read_csv(os.path.join(indexdir, 'Eurekahedge North America Long Short Equities HF Index.csv'), 
                  index_col=[0], infer_datetime_format=True)['Return']
erk.index= pd.to_datetime(erk.index).to_period('M')
erk.rename('Old benchmark (EurekaHedge N.America)', inplace=True)
erk=erk.loc[:'2024-12']

# Load SPY - monthly returns
print('Loading SPY monthly returns...')
spy= pd.read_csv(os.path.join(histdir, 'SPY_returns_Monthly.csv'), 
                 index_col=[0], infer_datetime_format=True).squeeze()
spy.index=pd.to_datetime(spy.index).to_period('M')
spy.rename('S&P500 (SPY)', inplace=True)
spy=spy.loc[:new_end.strftime('%Y-%m')]

def ret_compare(arq, spy, bm_new, erk, periods=[-1,-3,-6,-12]):
    res=pd.DataFrame(columns=['ARQuant net', 'SPY', 'bm_new', 'EurekaHedge'])
    for per in periods:
        res.loc[per]=[((1+arq.iloc[per:]).prod()-1)*100,
                      ((1+spy.iloc[per:]).prod()-1)*100,
                      ((1+bm_new.iloc[per:]).prod()-1)*100,
                      ((1+erk.iloc[per:]).prod()-1)*100]
    return res.round(2)
res=ret_compare(ak_monthly, spy, bm_new, erk)

print('\nSPY : {:.2f}%'.format(spy.iloc[-1]*100), ' for ', spy.index[-1])
print('SPY : {:.2f}%'.format(((1+spy.loc[str(new_end.year)]).prod()-1)*100), ' for YTD '+str(new_end.year))

print('\nbm_new : {:.2f}%'.format(bm_new.iloc[-1]*100), ' for ', bm_new.index[-1])
print('bm_new : {:.2f}%'.format(((1+bm_new.loc[str(new_end.year)]).prod()-1)*100), ' for YTD '+str(new_end.year))

# print('\nEurekaHedge : {:.2f}%'.format(erk.iloc[-1]*100), ' for ', erk.index[-1])
# try:
#     print('EurekaHedge : {:.2f}%'.format(((1+erk.loc[str(new_end.year)]).prod()-1)*100), ' for YTD'+str(new_end.year))
# except:
#     print('!!! EurekaHedge is missing for :', str(new_end) )
    
print('\nARQuant net: {:.2f}%'.format(ak_net_monthly.iloc[-1]*100), ' for ', ak_net_monthly.index[-1])
print('ARQuant net: {:.2f}%'.format(((1+ak_net_monthly.loc[str(new_end.year)]).prod()-1)*100), ' for YTD '+str(new_end.year))

print('\nARQuant gross: {:.2f}%'.format(ak_monthly.iloc[-1]*100), ' for ', ak_net_monthly.index[-1])
print('ARQuant gross: {:.2f}%'.format(((1+ak_monthly.loc[str(new_end.year)]).prod()-1)*100), ' for YTD '+str(new_end.year))

# print('bm_newI : {:.2f}%'.format(((1+bm_new.iloc[-3:]).prod()-1)*100), ' for ', bm_new.index[-3:])
# print('ErekaHedge : {:.2f}%'.format(((1+erk.iloc[-3:]).prod()-1)*100), ' for ', erk.index[-3:])

# print('ARQuant net: {:.2f}%'.format(((1+ak_net_monthly.iloc[-6:]).prod()-1)*100), ' for ', erk.index[-6:])
# print('bm_newI : {:.2f}%'.format(((1+bm_new.iloc[-6:]).prod()-1)*100), ' for ', bm_new.index[-6:])
# print('ErekaHedge : {:.2f}%'.format(((1+erk.iloc[-6:]).prod()-1)*100), ' for ', erk.index[-6:])

# print('ARQuant net: {:.2f}%'.format(((1+ak_net_monthly.iloc[-3:]).prod()-1)*100), ' for ', erk.index[-3:])
# print('ARQuant net: {:.2f}%'.format(((1+ak_net_monthly.iloc[-6:]).prod()-1)*100), ' for ', erk.index[-6:])

bm_new.to_csv(os.path.join(maindir, datadir, 'New benchmark (ETF basket).csv'))
erk.to_csv(os.path.join(maindir, datadir, 'Old benchmark (EurekaHedge N.America).csv'))

#%%
# Align dates for ARQuant and benchmarks, then save
ak_monthly.rename('ARQuant (before fees)', inplace = True)
# dfs1=[ak_monthly, ak_net_monthly, spy]
dfs1=[ak_net_monthly, spy]
dfs1=pd.concat(dfs1, axis=1, join='inner').reset_index().set_index(['Date'])
dfs2=[dfs1, 
      bm_new, 
      erk]
dfs2=pd.concat(dfs2, axis=1, join='outer')
dfs2=dfs2.loc[dfs1.index]
dfs2.to_csv(os.path.join(maindir, datadir, 'ARQuant vs Benchmarks.csv'))

dfs3=dfs2.copy()

print('Plotting monthly performance of ', dfs2.columns.tolist())
chdir(maindir)        
from Slides_for_print_function import plot_for_print
    
if len(dfs2.columns) > len(clist) :
    d=len(dfs2.columns) - len(clist)
    cmap = get_cmap('Paired') #RuOr Accent
    for i in range(d):
        clist.append(cmap(1/d))

dfs_wealth = (1+dfs2).cumprod()
dfs_wealth['New bechmark (ETF basket)'].loc['2023-12']=1.
multiple=dfs_wealth['Old benchmark (EurekaHedge N.America)'].loc['2023-12']
dfs_wealth['New bechmark (ETF basket)'].loc['2023-12':]=dfs_wealth['New bechmark (ETF basket)'].loc['2023-12':]*multiple

#for Newsletter
plot_for_print(dfs_wealth, 
               dicclrs,
               datadir=os.path.join(maindir, datadir), 
               yscale = 'log', base =100,
               marker=[None,None,None,None,None],
               ytext = "Net Return Index (Log scale)",
               plotname='_nl 4- ARQuant_vs_Benchmarks_since_Inception',
               subtitle = False,
               figsize=(10,6), show = False, isGrid = True,
               c=clist)
#for Factsheet
plot_for_print(dfs_wealth, 
               dicclrs,
               datadir=os.path.join(maindir, datadir), 
               yscale = 'log', base =100,
               marker=[None,None,None,None,None],
               ytext = "Net Return Index (Log scale)",
               plotname='_fs 4- ARQuant_vs_Benchmarks_since_Inception',
               subtitle = False,
               figsize=(12,6), show = False, isGrid = True,
               c=clist)

#%%

# from Slides_for_print_function import plot_distribution
# model4 = 'Return_Distribution_since_inception'
# savefig4=maindir+datadir+model4+'.png'

# plot_distribution(dfs2, 
#                   dicclrs,
#                   figsize=(10, 6), #(8.5, 5.5)
#                   fontname='Avenir Next', grayscale=False, ylabel=True,
#                   subtitle=True, compounded=False,
#                   savefig=savefig4, 
#                   show=True,
#                   ytext = "Monthly Return")
#%%
# Returns
##Testing formulas mine vs quantstats
# dfs2=ak_monthly for testing
# import quantstats as qs
# qs.reports.basic(andrew_ret.squeeze())

calyears=dfs2.shape[0]//12

index=['1 Month','3 Month','6 Month','12 Month']
for y in range(2,calyears+1):
    m=12*y
    index.append(str(y)+' Year Ann.')
index.append('Since Inception')

returns=pd.DataFrame(index=index, columns=dfs2.columns, dtype='float32')

returns.loc['1 Month'] = dfs2.iloc[-1:].values
returns.loc['3 Month'] = ( (1+dfs2.iloc[-3:]).prod()-1 ).values
returns.loc['6 Month']= ( (1+dfs2.iloc[-6:]).prod()-1 ).values
returns.loc['12 Month']=( (1+dfs2.iloc[-12:]).prod()-1 ).values
for y in range(2,calyears+1):
    m=12*y
    root = lambda x: np.power(x, 1./y)
    returns.loc[str(y)+' Year Ann.']=( root( (1+dfs2.iloc[-m:]).prod() )-1 ).values

root = lambda x: np.power(x, 12/dfs2.shape[0])
returns.loc['Since Inception']= ( root( (1+dfs2).prod() )-1 ).values

returns.loc[returns.index[4:],'New bechmark (ETF basket)']=np.nan
returns.loc[returns.index[0:4],'Old benchmark (EurekaHedge N.America)']=np.nan

returns.index.rename('Returns (%)', inplace=True)
(returns *100).astype(float).round(2).to_csv(os.path.join(maindir, datadir, 'Returns summary.csv'))

#%%
# Risk/Return
dfs3=dfs2.copy()
dfs3.loc[:'2025-01','Benchmark (New+Old combined)']=dfs3.loc[:'2025-01', 'Old benchmark (EurekaHedge N.America)']
dfs3.loc['2025-01':,'Benchmark (New+Old combined)']=dfs3.loc['2025-01':, 'New bechmark (ETF basket)']
dfs3=dfs3.drop(columns=['Old benchmark (EurekaHedge N.America)', 'New bechmark (ETF basket)'])

stats=pd.DataFrame(columns=dfs3.columns, dtype='float32')
# import quantstats.stats as _stats

#Geo.Avg.Monthly
root = lambda x: np.power(x, 1/dfs3.shape[0])
stats.loc['Geo.Avg.Monthly'] = ( root( (1+dfs3).prod() )-1 ).values 
#Std.Deviation
stats.loc['Std.Deviation'] = dfs3.std().values 
#High Month
stats.loc['High Month'] = dfs3.max().values 
#High Month
stats.loc['Low Month'] = dfs3.min().values 
#Annualized Return
root12 = lambda x: np.power(x, 12/dfs3.shape[0])
stats.loc['Annualized Return']= ( root12( (1+dfs3).prod() )-1 ).values
#Annualized Stdev
stats.loc['Annualized Stdev'] = stats.loc['Std.Deviation']*np.sqrt(12)

#Risk Free Rate
def RFR_load(tBill='TB3MS', fallback=0.0425): # 3-month T-Bill as of month start
    try:
        import pandas_datareader as pdr
        z=pdr.DataReader(tBill, 'fred')
        if isinstance(z, pd.DataFrame): z=z.squeeze()
        return z.iloc[-1]/100
    except Exception as e:
        print(f'Warning: Failed to fetch RFR from FRED ({type(e).__name__}). Using fallback={fallback:.2%}')
        return fallback

#Sharpe Ratio
stats.loc['Risk Free Rate'] = [ RFR_load(),]*stats.shape[1]
stats.loc['Sharpe Ratio'] = (stats.loc['Annualized Return'] - stats.loc['Risk Free Rate']
                             ) / stats.loc['Annualized Stdev']
stats.loc['Sharpe Ratio'] = stats.loc['Sharpe Ratio'].round(2)

# % of Winning Months
stats.loc['% of Winning Months'] = (dfs3>0).sum() / dfs3.shape[0]

#Max Drawdown
def maxDD(return_series):
    wealth_index = 1000*(1+return_series).cumprod()
    previous_peaks = wealth_index.cummax()
    previous_peaks[previous_peaks.values<1000]=1000.
    drawdown = (wealth_index - previous_peaks)/previous_peaks
    return drawdown.min()  
stats.loc['Max Drawdown (%)'] = maxDD(dfs3) *(-1.)

stats.loc[~stats.index.isin(['Sharpe Ratio'])] = (stats.loc[~stats.index.isin(['Sharpe Ratio'])] *100).round(2)

stats.index.rename('Risk/Return', inplace=True)
stats.to_csv(os.path.join(maindir, datadir, 'Risk vs Return since incepton.csv'))

#%%
# #for ARQ fund newsletter
# afund=(returns.T *100).round(1)
# ytd=str(dfs2.index[-1].year)
# afund['YTD']=(((1+dfs2.loc[ytd]).prod()-1).values*100).round(1)
# afund['Ann.Vol.']= stats.loc['Annualized Stdev'].round(1)

# afund.drop(['3 Month', '2 Year Ann.', '4 Year Ann.'], axis=1, inplace=True)
# afund=afund.reindex(columns=['Since Inception', 'Ann.Vol.',  '3 Year Ann.', '1 Year', 
#                        'YTD', '6 Month', '1 Month'])
# afund.to_csv(os.path.join(maindir, datadir, 'ARQ fund vs benchmarks.csv'))

#%%
from os import chdir
chdir(maindir)
from Slides_for_print_function import stat_html

##Make a picture for Risk/Return
#for Newsletter
stat_html(stats, 
          os.path.join(maindir, datadir, '_nl 4- Risk_Return'), 
          resolution = 200,isLastRow = False, isWriteHTML = False,
          table_width = '100%;', 
          row_height = '23.1px;',
           col_formatter =['31%', '23%', '23%','23%'],
           # col_formatter =['29%', '19%', '14%','17%', '21%'], #if HRI
          col_space = '20px', #Minimum space of column
          size ='width: 23cm; height: 8.5cm;')
#for Factsheet
stat_html(stats, 
          os.path.join(maindir, datadir, '_fs 4- Risk_Return'), 
          resolution = 200,isLastRow = False, isWriteHTML = False,
          table_width = '100%;', 
          row_height = '38.7px;', #change here
           col_formatter =['31%', '23%', '23%','23%'],
           # col_formatter =['29%', '19%', '14%','17%', '21%'], #if HRI
          col_space = '20px', #Minimum space of column
          size ='width: 17.0cm; height: 12.65cm;') #DON'T change without HRI
          # size ='width: 17.0cm; height: 13.3cm;') #DON'T change if HRI
          
#%%
##Make a picture for Return Summary
returns1=(returns *100).astype(float).round(2)
returns2=returns1.fillna("-")
returns3=returns2.drop(['7 Year Ann.','8 Year Ann.'], axis=0)

#for Newsletter
stat_html(returns3, 
          os.path.join(maindir, datadir, '_nl 4- Returns summary'), 
          resolution = 200, isLastRow = False, isWriteHTML = False,
          table_width = '100%;', 
           row_height = '22px;',
          # col_formatter =['31%', '23%', '23%','23%'],
           col_formatter =['29%', '19%', '14%','17%', '21%'], #if HRI
          col_space = '20px', #Minimum space of column
          size ='width: 23cm; height: 8.425cm;')
#for Factsheet
stat_html(returns3, 
          os.path.join(maindir, datadir, '_fs 4- Returns summary'), 
          resolution = 200, isLastRow = False, isWriteHTML = False,
          table_width = '100%;', 
          row_height = '26px;',
          # col_formatter =['31%', '23%', '23%','23%'],
           col_formatter =['29%', '19%', '14%','17%', '21%'], #if bm_newI
          col_space = '20px', #Minimum space of column
          size ='width: 17.0cm; height: 9.85cm;') #DON'T change without bm_newI
          # size ='width: 17.0cm; height: 10.6cm;') #DON'T change if bm_newI

#%%
from Slides_analytic_function import summary_stats2
ak_stats_LM = summary_stats2(andrew_ret.loc[new_end.strftime('%Y-%m')],
                          riskfree_rate=RFR_load(), 
                          periods_per_year=252
                          )
# from Slides_for_print_function import stats_periods_for_print
# ak_stats_LM_for_print=stats_periods_for_print(ak_stats_LM.squeeze())
ak_stats_LM.T.to_csv(os.path.join(maindir, datadir, 'Stats Last month.csv'))

#%%
#VIX weekly volatility
# Load datasets ****
vix_daily=pd.read_csv(os.path.join(histdir, 'VIXCLS_prices.csv'))
vix_daily=vix_daily.set_index('Date')
vix_daily.index=pd.to_datetime(vix_daily.index)
vix_daily=vix_daily.loc[new_start:new_end]

#Last Month
lastmonth=vix_daily.index[-1].month
lastyear=vix_daily.index[-1].year
vix_daily_LM=vix_daily.loc[f'{lastyear}-{lastmonth}'].squeeze()

#Weekly
vix_w=vix_daily_LM.resample("W-Fri").mean().rename('VIX Weekly Average')
vix_w_hl=vix_daily_LM.resample("W-Fri").apply(np.ptp).rename('VIX Weekly HL')

pd.concat([vix_w,vix_w_hl],axis=1).to_csv(os.path.join(maindir, datadir, 'VIX weekly volatility.csv'))

#%%
'''
#Momentum streignth in Last month
from pandas.tseries.offsets import DateOffset, BDay
startday= andrew_ret.loc[year_month].index[0]-BDay(29)
endday= andrew_ret.loc[year_month].index[-1]

timeperiod = 14

chdir(maindir)
from Slides_analytic_function import TIINGO_load
from talib import ADX, MFI

adx_df = pd.DataFrame(index= andrew_ret.loc[startday:endday].index)
mfi_df = pd.DataFrame(index= andrew_ret.loc[startday:endday].index)

for tkr in contrib_list:
    print(tkr)
    stock= TIINGO_load(tkr,
                       metric_name=None,
                       startday= startday,
                       endday= endday)
    stock.index = stock.index.tz_convert(None)
   
    adx = ADX(stock.high, stock.low, stock.close, timeperiod = timeperiod).rename(tkr)
    adx_df=pd.concat([adx_df, adx], axis=1, join = 'inner')

    mfi = MFI(stock.high, stock.low, stock.close, stock.volume, timeperiod = timeperiod).rename(tkr)
    mfi_df=pd.concat([mfi_df, mfi], axis=1, join = 'inner')

adx_df=adx_df.loc[year_month]
adx_df.to_csv(os.path.join(histdir, 'Contributors_ADX_daily.csv'))
#%%
spyd = TIINGO_load('SPY',
                  metric_name=None,
                  startday= '2022-05-31',
                  endday= new_end.strftime('%Y-%m-%d')
                  )
spyd.index = spyd.index.tz_convert(None)

spyd = spyd['close'].pct_change().rename('Return').to_frame()
spyd.dropna(axis=0,inplace=True)
spyd['TR'] = (1+spyd['Return']).cumprod()

import quantstats.stats as _stats
sharpe = _stats.sharpe(spyd.Return)

spy_dd = _stats.to_drawdown_series(spyd.Return.fillna(0))
spy_dddf = _stats.drawdown_details(spy_dd)
spy_maxDD = spy_dddf.sort_values(by='days', ascending=False, 
                              kind='mergesort')[:5]
#%%
ak = andrew_ret.loc[year_month].copy()
ak['TR'] = (1+ak['Return']).cumprod()

# print( ((ak-spy)*100).iloc[-1].apply("{:.2f}%".format) )
pd.concat([ak.TR.rename('ARQuant'),spyd.TR.rename('SPY')],axis=1).plot()

ak_dd = _stats.to_drawdown_series(ak.Return.fillna(0))
ak_dddf = _stats.drawdown_details(ak_dd)
ak_maxDD = ak_dddf.sort_values(by='days', ascending=False, 
                              kind='mergesort')[:5]
#%%

# '''
# adx_strong = (adx_df[adx_df>30.].count() / adx_df.count() *100).apply("{:.2f}%".format)
# adx_strong.rename('ADX>30 freq(%)', inplace = True)
# dependence = pd.concat([adx_strong.sort_index(ascending=True),
#                         contrib_LM['Contribution'].sort_index(ascending=True)],
#                        axis=1)
# adx_df['NVDA'].hist()

# 1. if profit, RSI or ADX should have a strong pattern. Otherwise, if loss, no pattern. 
# 2. If RSI high or low, what does it mean?
# 3. How to calculate momentum for month? - as daily average? or histogram?
# '''
#%%
# data = andrew_ret.loc[year_month].copy()
# data ['TR'] = (1+data['Return']).cumprod()

# #Filtering ARQuant
# chdir('/users/alexander/Dropbox/0-ML/Python/GoTrader')
# import Prinston_finlib as pf

# lv=0.025   #Play with  Lambda
# pf.filter_plot(data ,lambda_value=lv, regime_num=0, TR_num=1, labels=['Days','Daily Return (%)'])
# betas=pf.trend_filtering(data ['Return'].values,lambda_value=lv)

# #Regime switching
# threshold=1e-4

# pf.plot_regime_color(data , lambda_value=lv, log_TR=True,
#                       regime_num=0, 
#                       TR_num=1, 
#                       threshold=threshold,
#                       labels=['Days', 'ARQuant Log-scale'],
#                       title='Regime Plot of ARQuant')
# #Selecting turning points using the threshold
# ini_points, regime = pf.regime_switch(betas,threshold, include=True)
# regime=pd.DataFrame(data=regime, index=data.index, columns=['Regime'])

# idx=pd.DataFrame(columns=['Start', 'End'], index=range(len(ini_points)-1) )
# for i,k in enumerate(ini_points[:-1]):
#     idx['Start'].iloc[i]=data.index[ini_points[i]]
#     idx['End'].iloc[i]=data.index[ini_points[i+1]-1]
    
# #%%
# regime_adx=[]
# for i in idx.index:
#     _start = idx['Start'].iloc[i]
#     _end = idx['Start'].iloc[i]
#     _df = adx_df.loc[_start:_end]
#     # regime_adx.append( _df.mean.apply("{:.2f}".format))
#     regime_adx.append( (_df[_df>30.].count() / _df.count() *100).apply("{:.1f}%".format))

# #%%
# p9m=pd.Series(index=ak_monthly.index[9:])
# for i in range(len(ak_monthly)-9):
#     p9m.iloc[i]=all(ak_monthly.iloc[i:i+9]>0.)