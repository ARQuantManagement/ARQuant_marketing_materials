#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 13:26:07 2021

@author: alexander
"""
from os import listdir, path, makedirs, rename, chdir
import datetime as dt
import pandas as pd

def _rem():
    import platform
    ver = platform.python_version()
    if ver[:-3]<'3.9': return 'M'
    else: return 'ME'

def from_IBKR_YTDreturn(TokenID=506192259300500062118707, QueryID=452838, 
                          datadir='/users/alexander/Dropbox/5-Finance/myARQuant/Python/'):              
        from ib_insync import FlexReport
        FR=FlexReport(token=TokenID, queryId=QueryID)
        df=FR.df(topic='ChangeInNAV')
        return df #cummulated return
# df=from_IBKR_YTDreturn()

# def create_dir(prefix='Data/Presentation_'):
#     #Create a directory
#     '''
#     datadir
#     datadir0
#     year_1
#     month_1
#     '''
    
#     month=dt.date.today().month
#     year=dt.date.today().year
    
#     def last2month(month, year):
#         if month==1 : return (12,11, year-1, year-1)
#         elif month==2 : return (1,12, year, year-1)
#         else: return (month-1, month-2, year, year)
    
#     month_1=last2month(month, year)[0]
#     month_2=last2month(month, year)[1]
#     year_1=last2month(month, year)[2]
#     year_2=last2month(month, year)[3]
    
#     datadir= prefix+str(year_1)+'-'+str(month_1)+'/'
#     makedirs(datadir, exist_ok=True)
#     prefix +str(year_2)+'-'+str(month_2)+'/'
#     datadir0=prefix +str(year_2)+'-'+str(month_2)+'/'
#     return (datadir, datadir0, year_1, month_1)

def update_return_history(datadir, datadir0, year_1, month_1):    
    #Read history from the previous month
    import calendar
    cal = calendar.Calendar()
    weekday_count = 0
    for week in cal.monthdayscalendar(year_1, month_1):
        for i, day in enumerate(week):
            # not this month's day or a weekend
            if day == 0 or i >= 5:
                continue
            # or some other control if desired...
            weekday_count += 1
    # print(weekday_count)
    
    files_update = [f for f in listdir(datadir) 
                    if f.startswith('AVESA_Group_Ltd') 
                    and f.endswith('.csv') 
                    and not f.endswith('_history.csv')
                    ]
    for fn in files_update:
        rename(datadir+fn, datadir+fn[:24]+'_last_month.csv')
    
    #Andrew history
    ret_1=pd.read_csv(datadir0+'AVESA_Group_Ltd_U3577443_history.csv',infer_datetime_format=False)
    ret_1['Date']=pd.to_datetime(ret_1['Date'], 
                                 dayfirst=True,
                                 infer_datetime_format='%d/%m/%Y')
    ret_1.set_index(['Date'], inplace=True)
    #Andrew update
    ret_2=pd.read_csv(datadir+'AVESA_Group_Ltd_U3577443_last_month.csv',infer_datetime_format=False)
    ret_2=ret_2[ret_2.Introduction=='Time Period Performance Statistics']
    ret_2=ret_2[ret_2.Header=='Data']
    ret_2=ret_2[['Name', 'Alias']]
    ret_2.rename(columns={'Name':'Date', 'Alias':'Return'}, inplace=True)
    ret_2['Date']=pd.to_datetime(ret_2['Date'], infer_datetime_format='%m/%d/%Y')
    ret_2.set_index(['Date'], inplace=True)
    ret_2=ret_2.astype('float')/100
    #Andrew - save new history
    andrew_ret=pd.concat([ret_1, ret_2], axis=0)
    andrew_ret.to_csv(datadir+'AVESA_Group_Ltd_U3577443_history.csv')
    return

def update_return_history_v2(datadir, datadir0, year_1, month_1,
                             f_history='AVESA_Group_Ltd_U3577443_history.csv', 
                             f_last_month='AVESA_Group_Ltd_U3577443_last_month.csv'):
    #Read history from the previous month
    # import calendar
    # cal = calendar.Calendar()
    # weekday_count = 0
    # for week in cal.monthdayscalendar(year_1, month_1):
    #     for i, day in enumerate(week):
    #         # not this month's day or a weekend
    #         if day == 0 or i >= 5:
    #             continue
    #         # or some other control if desired...
    #         weekday_count += 1
    # # print(weekday_count)
    
    # files_update = [f for f in listdir(datadir) 
    #                 if f.startswith('AVESA_Group_Ltd') 
    #                 and f.endswith('.csv') 
    #                 and not f.endswith('_history.csv')
    #                 ]
    # for fn in files_update:
    #     rename(datadir+fn, datadir+fn[:24]+'_last_month.csv')
    
    if f_history=='' or f_last_month=='':
        print('\nPlease give file names for update...')
        return
    
    #Andrew history
    ret_1=pd.read_csv(datadir0 + f_history, infer_datetime_format=False)
    ret_1['Date']=pd.to_datetime(ret_1['Date'], 
                                 dayfirst=True,
                                 infer_datetime_format='%d/%m/%Y')
    ret_1.set_index(['Date'], inplace=True)
    ret_1 = ret_1[~ret_1.index.duplicated(keep='first')]
    #Andrew update
    ret_2=pd.read_csv(datadir + f_last_month, infer_datetime_format=False)
    ret_2=ret_2[ret_2.Introduction=='Time Period Performance Statistics']
    ret_2=ret_2[ret_2.Header=='Data']
    ret_2=ret_2[['Name', 'Alias']]
    ret_2.rename(columns={'Name':'Date', 'Alias':'Return'}, inplace=True)
    ret_2['Date']=pd.to_datetime(ret_2['Date'], infer_datetime_format='%m/%d/%Y')
    ret_2.set_index(['Date'], inplace=True)
    ret_2=ret_2.astype('float')/100
    #Andrew - save new history
    
    overlap=ret_1.index.intersection(ret_2.index)
    ret_2=ret_2.drop(overlap)
    
    andrew_ret=pd.concat([ret_1, ret_2], axis=0, join='outer')
    andrew_ret.to_csv(datadir+'AVESA_Group_Ltd_U3577443_history.csv')
    return
# update_return_history_v2()

def update_return_history_v3(f_history='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/'+'AVESA_Group_Ltd_U3577443_history.csv', 
                             f_last_month='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/FTP/'+'AVESA_Group_Ltd_U3577443_July_01_2022_July_28_2022.csv',
                             histdir='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/',
                             isSave = True):

    if f_history=='' or f_last_month=='':
        print('\nPlease give file names for update...')
        return
    
    #Read history
    ret_1=pd.read_csv(f_history, infer_datetime_format=False)
    ret_1['Date']=pd.to_datetime(ret_1['Date'], 
                                 dayfirst=True,
                                 infer_datetime_format='%d/%m/%Y')
    ret_1.set_index(['Date'], inplace=True)
    ret_1 = ret_1[~ret_1.index.duplicated(keep='first')]
    #Read update
    ret_2=pd.read_csv(histdir+f_last_month, 
                      engine='python',
                      header = 0, 
                      usecols = list(range(12)),
                      skiprows = range(1,7), #lambda x: x in  
                      skipfooter = 11,
                      infer_datetime_format=False)
    ret_2=ret_2[ret_2.Introduction=='Time Period Performance Statistics']
    ret_2=ret_2[ret_2.Header=='Data']
    ret_2=ret_2[['Name', 'Alias']]
    ret_2.rename(columns={'Name':'Date', 'Alias':'Return'}, inplace=True)
    ret_2['Date']=pd.to_datetime(ret_2['Date'], infer_datetime_format='%m/%d/%Y')
    ret_2.set_index(['Date'], inplace=True)
    ret_2=ret_2.astype('float')/100
    
    overlap=ret_1.index.intersection(ret_2.index)
    ret_2=ret_2.drop(overlap)
    
    andrew_ret=pd.concat([ret_1, ret_2], axis=0, join='outer')
    if isSave:
        andrew_ret.to_csv(f_history, date_format='%d/%m/%Y')
        return
    else:
        return andrew_ret
# update_return_history_v3()
#%%
def myread_csv(input_file, 
               first_col_name='Introduction', 
               excluded_values = ["Introduction", "Key Statistics", "Risk Measures", 
                                  "Trade Summary","Notes and Disclosure"]
               ):
    import pandas as pd
    from io import StringIO
    import csv
        
    output_lines = []
    header_line = None
    header_found = False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                sample = list(csv.reader([line]))
            except Exception:
                continue  # skip any lines that can't be parsed at all
            if not header_found and sample and 'Introduction' in sample[0]:
                header_found = True
                header_line = line
                output_lines.append(line)
            elif header_found:
                if sample and sample[0] and sample[0][0].strip() not in excluded_values:
                    output_lines.append(line)

    # Filter out lines with unmatched quotes
    def is_valid_csv_line(line, delimiter=','):
        try:
            next(csv.reader([line], delimiter=delimiter))
            return True
        except Exception:
            return False

    valid_lines = [l for l in output_lines if is_valid_csv_line(l)]
    
    data_str = ''.join(valid_lines)
    
    import pandas as pd
    from io import StringIO
    import warnings
    warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)

    df = pd.read_csv(StringIO(data_str), 
                     engine='python', 
                     infer_datetime_format=False,
                     on_bad_lines="skip",   # skip bad lines
                     # warn_bad_lines=False     # suppress warning output
                     )    
    return df

def update_return_history_v4(f_history='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/'+'AVESA_Group_Ltd_U3577443_history.csv', 
                             f_last_month='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/'+'ARQuant_Management_Limited_September_2025_September_2025_daily.csv',
                             # histdir='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/',
                             isSave = True):

    if f_history=='' or f_last_month=='':
        print('\nPlease give file names for update...')
        return
    
    #Read history
    ret_1=pd.read_csv(f_history, infer_datetime_format=False)
    ret_1['Date']=pd.to_datetime(ret_1['Date'], 
                                 dayfirst=True,
                                 infer_datetime_format='%d/%m/%Y')
    ret_1.set_index(['Date'], inplace=True)
    ret_1 = ret_1[~ret_1.index.duplicated(keep='first')]
    #Read update
    ret_2=myread_csv(f_last_month)
    
    ret_2=ret_2[ret_2.Introduction=='Time Period Performance Statistics']
    ret_2=ret_2[ret_2.Header=='Data']
    ret_2=ret_2[['Name', 'Alias']]
    ret_2.rename(columns={'Name':'Date', 'Alias':'Return'}, inplace=True)
    ret_2['Date']=pd.to_datetime(ret_2['Date'], infer_datetime_format='%m/%d/%Y')
    ret_2.set_index(['Date'], inplace=True)
    ret_2=ret_2.astype('float')/100
    
    overlap=ret_1.index.intersection(ret_2.index)
    ret_2=ret_2.drop(overlap)
    
    andrew_ret=pd.concat([ret_1, ret_2], axis=0, join='outer')
    if isSave:
        andrew_ret.to_csv(f_history, date_format='%d/%m/%Y')
        return
    else:
        return andrew_ret
update_return_history_v4() 

#%%
def read_csv(datadir, filename='AVESA_Group_Ltd_U3577443_history.csv'):
    andrew_ret=pd.read_csv(datadir+filename)
    andrew_ret['Date']=pd.to_datetime(andrew_ret['Date'], 
                                  infer_datetime_format='%Y-%m-%d')
    andrew_ret.set_index(['Date'], inplace=True)
    return andrew_ret

#Dictionary with required periods
def period_index(df, period_list):
    from pandas.tseries.offsets import DateOffset, BDay
    import first_and_last_BDays
    from first_and_last_BDays import First_and_Last_BDays_of_year_US
    
    periods={}
    for per in period_list:
        ##for debugging 
        # print(per)
        # z=input('Press any key...')
        if per=='Inception':    
            periods[per]=df.index
        elif per[:6]=='Since ': 
            periods[per]=df.loc[per[6:] : ].index
            end=df.loc[per[6:10]].index[-1].strftime("%Y-%m-%d")
            periods[per[6:]+'_'+ end ] = df.loc[per[6:] : end].index           
        elif per=='MTD':        periods[per]=df.last("1M").index
        elif per=='YTD':        periods[per]=df.loc[str(df.index[-1].year)].index
        elif per[0]=='2':
            first, last = First_and_Last_BDays_of_year_US(per)
            if (first.strftime("%Y-%m-%d") in df.loc[per].index
                ) and (last.strftime("%Y-%m-%d") in df.loc[per].index):
                periods[per]=df.loc[per].index
            if per=='2018': periods[per]=df.loc[per].index
            
        elif per[0]=='L':
            p=int(per[1:-1])
            if isinstance(df.index, pd.PeriodIndex): 
                periods[per]=df.index[-p:]
            else:
                _start = df.index[-1] - DateOffset(months=p)                    
                if df.index[-1].is_month_end:
                    while not _start.is_month_start:
                        _start +=BDay(1)
                while _start not in df.index:
                    _start +=BDay(1)
                periods[per]= df.loc[_start : ].index
        else: continue
    return periods

def var_gaussian2(r, level=5, modified=False):
    """
    Returns the Parametric Gauusian VaR of a Series or DataFrame
    If "modified" is True, then the modified VaR is returned,
    using the Cornish-Fisher modification
    """
    from scipy.stats import norm
    # compute the Z score assuming it was Gaussian
    z = norm.ppf(level/100)
    if modified:
        # modify the Z score based on observed Skewnessness and kurtosis
        from scipy import stats    
        s = stats.skew(r)
        k = stats.kurtosis(r)
        z = (z +
                (z**2 - 1)*s/6 +
                (z**3 -3*z)*(k-3)/24 -
                (2*z**3 - 5*z)*(s**2)/36
            )
    return -(r.mean() + z*r.std(ddof=0))

def cvar_historic2(r, level=5):
    """
    Computes the Conditional VaR of Series or DataFrame
    """
    if isinstance(r, pd.Series):
        is_beyond = r <= -var_historic2(r, level=level)
        return -r[is_beyond].mean()
    elif isinstance(r, pd.DataFrame):
        return r.aggregate(cvar_historic2, level=level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")

def var_historic2(r, level=5):
    """
    Returns the historic Value at Risk at a specified level
    i.e. returns the number such that "level" percent of the returns
    fall below that number, and the (100-level) percent are above
    """
    import numpy as np
    if isinstance(r, pd.DataFrame):
        return r.aggregate(var_historic2, level=level)
    elif isinstance(r, pd.Series):
        return -np.percentile(r, level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")


def summary_stats2(r, riskfree_rate=0.00, periods_per_year=252):
    import numpy as np
    if isinstance(r, pd.Series): r = r.to_frame() 
    rname = r.columns[0]
    
    from quantstats import stats
    #https://github.com/ranaroussi/quantstats/blob/main/quantstats/stats.py
    #FactSheet
    #https://rawcdn.githack.com/ranaroussi/quantstats/main/docs/tearsheet.html
    tr=(1+r).cumprod()
    growth = tr.iloc[-1]-1 #the same as stats.comp(r)[0] 
    ann_vol = stats.volatility(r, periods=periods_per_year)[0]
    ann_sr = stats.sharpe(r, rf= riskfree_rate, periods=periods_per_year)[0]
    ann_r = stats.cagr(r, rf= riskfree_rate)[0]

    dd = stats.max_drawdown(tr)[0]
    ds = stats.to_drawdown_series(r)
    details = stats.drawdown_details(ds)
    # recov = details.iloc[:, details.columns.get_level_values(1)=='days'].max()[0]
    recov = details.iloc[:, details.columns.get_level_values(1)=='days'].describe().values
    
    Skewness = stats.skew(r)[0]
    kurt = stats.kurtosis(r)[0]

    #Edhec_risk_kit
    cf_var5 = r.aggregate(var_gaussian2, modified=True)
    hist_cvar5 = r.aggregate(cvar_historic2)
    # recov[-1]=recov[-1].days #extract days
       
    calmar=stats.calmar(r)[0]
    sortino=stats.sortino(r)[0]
    kelly_criterion = stats.kelly_criterion(r)[0]
    
    #weekly performance
    r1=r.resample("W").apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
    r1.index=r1.index.to_period('W')

    prob_win = ((r1>0).sum()/r1.count())[0]
    mean_ret=r1.mean()
    best = stats.best(r1)[0]
    worst = stats.worst(r1)[0]
    win_rate=stats.win_rate(r1)[0]
    avg_win=stats.avg_win(r1)[0]
    avg_loss=stats.avg_loss(r1)[0]
    
    return pd.DataFrame({
        "Start": r.index[0].strftime('%Y-%m-%d'),
        "End": r.index[-1].strftime('%Y-%m-%d'),
        "Growth": growth,
        "Return annualized": ann_r,
        "Volatility annualized": ann_vol,
        "Sharpe Ratio": round(ann_sr,2),
        "Calmar": calmar,
        "Sortino": sortino,
        'Kelly criterion': kelly_criterion,
        "Skewness": round(Skewness,2),
        "Kurtosis": round(kurt,2),
        "Cornish-Fisher VaR (5%)": cf_var5,
        "Historic CVaR (5%)": hist_cvar5,
        "Max Drawdown": dd,
        "Recovery time (max days)": recov[-1][0],
        "Recovery time(75% cases)": recov[-2][0],        
        "Leverage optimal": np.NAN,
        "Expected growth": np.NAN,
        "Years to increase by 1x Vol": np.NAN,
        "Best Week": best,
        "Worst Week": worst,
        "Mean Return weekly": mean_ret,
        "Average Win weekly": avg_win,
        "Average Loss weekly": avg_loss,
        "Win rate weekly": win_rate,
        "Win Prob. weekly": prob_win
        }, index=[rname]) #[r.name] if Series

def summary_stats_monthly(r, riskfree_rate=0.00, bm=None):
    # from quantstats import stats
    import numpy as np
    if isinstance(r, pd.DataFrame): #r is Series 
        if r.shape[0]>1: r = r.squeeze()
        else: r=pd.Series(r.values[0], index=r.index)
    # rname = r.name
        
    #Growth over period
    growth = (1+r).prod() - 1
    #Geo Avg.Monthly
    if r.shape[0]>1:
        root = lambda x: np.power(x, 1/r.shape[0] )
        geoavg = root( (1+r).prod() ) - 1 
    else: geoavg =r.values
    #Monthly Vol.
    vol_monthly = r.std() if not pd.isna(r.std()) else np.nan
    #Ann.return as CAGR
    ann_r = (1+geoavg)**12 - 1 #CAGR
    #Ann.VOl.
    ann_vol = vol_monthly * np.sqrt(12)

    if isinstance(bm, pd.DataFrame) or isinstance(bm, pd.Series):
        tracking_error_monthly = (r-bm).std() if not pd.isna( (r-bm).std() ) else np.nan
        tracking_error_ann = tracking_error_monthly* np.sqrt(12)
        
        active_return_monthly = r - bm
        active_return_ann= active_return_monthly.mean()*12
        info_ratio_ann= active_return_ann/tracking_error_ann
        
        if tracking_error_ann ==0: info_ratio_ann = np.nan
        # print('Info ratio..',info_ratio_ann)        
        beta = r.cov(bm)/bm.var()
    else: 
        info_ratio_ann = np.nan
        beta = np.nan
        
    #Ann.Sharpe
    def sharpe_ratio(return_series, N, rf):
        mean = return_series.mean() * N - rf
        sigma = return_series.std() * np.sqrt(N)
        return mean / sigma
    ann_sr = sharpe_ratio(r,12,riskfree_rate)
    
    #Sortino ratio
    def sortino_ratio(series, N,rf):
        mean = series.mean() * N - rf
        std_neg = series[series<0].std()*np.sqrt(N)
        return mean/std_neg
    sortino=sortino_ratio(r,12,riskfree_rate)
    #Calmar
    def calmar_ratio(return_series, N):
        def max_drawdown(return_series):
            comp_ret = (return_series+1).cumprod()
            peak = comp_ret.expanding(min_periods=1).max()
            dd = (comp_ret/peak)-1
            return abs(dd.min())
        dd = max_drawdown(return_series)
        if dd > 0 : 
            return return_series.mean()* N / dd
        else: 
            return None
    calmar=calmar_ratio(r, 12)
    
    #High month
    r_monthly_max  = r.max()
    #Low month
    r_monthly_min  = r.min()
    #Win rate
    win_rate = (r>0).sum()/r.count()
    #Max DD
    def _drawdown(return_series):
        wealth_index = 1000*(1+return_series).cumprod()
        previous_peaks = wealth_index.cummax()
        previous_peaks[previous_peaks.values<1000]=1000.
        drawdowns = (wealth_index - previous_peaks)/previous_peaks
        return drawdowns
    def maxDD(return_series):
        drawdowns = _drawdown(return_series)
        return abs(drawdowns.min())    
    dd = maxDD(r) 
    
    #Max Recovery Period
    def _recovery(return_series):     ##1
        drawdowns = _drawdown(return_series)
        prev=drawdowns.iloc[0]
        mask=pd.Series(name='mask', index=return_series.index, dtype='int')
        for i in range(1,len(drawdowns)) :
            if ( (drawdowns.iloc[i]<prev) and (prev==0) ) : 
                mask.iloc[i]=-1
            if ( (drawdowns.iloc[i]>prev) and (drawdowns.iloc[i]==0) ): 
                mask.iloc[i]=1
            prev=drawdowns.iloc[i]
        
        mask=mask[mask!=0]
        if len(mask[mask==1]) == len(mask[mask==-1]):
            recovery =pd.Series(mask[mask==1].index.month - mask[mask==-1].index.month,
                           index=mask[mask==-1].index)
        else: 
            recovery =pd.Series(mask[mask==1].index.month - mask[mask==-1].index[:-1].month,
                           index=mask[mask==-1].index[:-1])
            recovery.loc[mask[mask==-1].index[-1]]= None
        recovery.name='Recovery (months)'      
        return recovery #series
    # _recovery(r) #testing    
    # def maxRecovery(return_series):
    #     recovery= _recovery(return_series)
    #     if pd.isna(recovery.iloc[-1]):
    #         return 'Not recovered'
    #     else:
    #         maxrec = recovery.max()
    #         if maxrec == 1:
    #             return str(maxrec)+' month'
    #         else:
    #             return str(maxrec)+' months'
    # maxrecov = maxRecovery(r)
      
    #Skewness & Kurtosis
    from scipy import stats
    Skewness = stats.skew(r)
    kurt = stats.kurtosis(r)

    #Edhec_risk_kit
    cf_var5 = r.aggregate(var_gaussian2, modified=True)
    hist_cvar5 = r.aggregate(cvar_historic2)
    # recov[-1]=recov[-1].days #extract days

    #Optimal Kelly fraction
    def kelly_ratio(return_series, N, rf):
        mean = return_series.mean() * N - rf
        var = return_series.var(ddof=0) * N if return_series.var(ddof=0)!= 0. else np.nan
        return mean / var
    kelly_fraction = kelly_ratio(r*100, 12, riskfree_rate)
    
    return pd.DataFrame({
        "Start": r.index[0].strftime('%Y-%m'),
        "End": r.index[-1].strftime('%Y-%m'),
        "Growth": growth,
        "Return ann.": ann_r,
        "Volatility ann.": ann_vol,
        'Risk Free Rate': riskfree_rate,
        "Sharpe": ann_sr,
        "Calmar": calmar,
        "Sortino": sortino,
        'Kelly fraction': kelly_fraction,
        "Skewness": Skewness,
        # "Kurtosis": kurt,
        "VaR (5%)": cf_var5,
        # "CVaR (5%)": hist_cvar5,
        "Max Drawdown": dd,
        # "Max Recovery period": maxrecov,
        'Geo.Avg.Monthly': geoavg,
        'Volatility monthly': vol_monthly,
        'High Month': r_monthly_max,
        'Low Month': r_monthly_min,
        'Win rate monthly': win_rate,
        'Beta (to SPY)': beta,
        # 'Tracking Error (SPY)':tracking_error_ann,
        # 'Information Ratio (SPY)':info_ratio_ann,
        }, index=[r.name])

def stats_periods(andrew_ret, periods, librarydir, periods_per_year=252): #, periods_list=['Inception','12M', 'YTD', '3M']):    
    # chdir(librarydir)
    # from edhec_risk_kit import summary_stats
    stats=pd.DataFrame()
    for period in periods.keys():
        print('Creating Stats for {} period...'.format(period) )
        #Actual number of days
        if period in ['L12M', '2018', '2019', '2020', '2021']: Xperiods_per_year=len(periods[period])
        else: Xperiods_per_year = periods_per_year
        # stat=summary_stats(andrew_ret.loc[periods[period]], riskfree_rate=0.00, periods_per_year=Xperiods_per_year)
        stat=summary_stats2(andrew_ret.loc[periods[period]], riskfree_rate=0.00, periods_per_year=Xperiods_per_year)
        stat=stat.rename({stat.index[0]:period})
        # stat=stat.rename({'Return':period})
        stats=stats.append(stat)
    return stats

def stats_periods_monthly(ak_monthly, periods, riskfree_series, bm=None):    
    stats=pd.DataFrame()
    for period in periods.keys():
        print('Creating Stats for {} period...'.format(period) )
        riskfree_rate = riskfree_series.loc[ periods[period] ].mean()
        stat=summary_stats_monthly(ak_monthly.loc[ periods[period] ], 
                                   riskfree_rate=riskfree_rate, bm=bm)
        stat=stat.rename({stat.index[0]:period})
        stats=stats.append(stat)
    return stats

# def spy_vix_qqq(start, end, datadir):
#     '''Monthly returns'''
#     start_=str(start.year)+'_'+str(start.month)+'_'+str(start.day)
#     end_=str(end.year)+'_'+str(end.month)+'_'+str(end.day)
    
#     spy_file='SPY_'+start_+'_'+end_+'.csv'
#     print('Load SPY daily returns...')
#     if not path.isfile(datadir+spy_file):
#         # updating from Yahoo
#         import pandas_datareader as pdr
#         spy=pdr.get_data_yahoo('SPY', start=start, end=end)['Adj Close']
#         spy.to_csv(datadir+spy_file)
#     else:
#         spy=pd.read_csv(datadir+spy_file)
#         spy['Date']=pd.to_datetime(spy['Date'], infer_datetime_format='%Y-%m-%d')
#         spy.set_index('Date', inplace=True)
        
#     if isinstance(spy, pd.DataFrame): spy.columns=['SPY']
#     else: spy.rename('SPY',inplace=True)
#     spy_daily=spy.pct_change()
#     spy_daily.dropna(axis=0,inplace=True)
#     #Spy Daily ->Monthly
#     spy_monthly=spy_daily.resample(_rem).apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
#     spy_monthly.index=spy_monthly.index.to_period('M')
    
#     #VIX ***
#     vix_file='VIX_'+start_+'_'+end_+'.csv'
#     print('Load VIX daily...')
#     if not path.isfile(datadir+vix_file):
#         # updating from Yahoo
#         import pandas_datareader as pdr
#         vix = pdr.DataReader('VIXCLS', 'fred', start=start, end=end).dropna()#.squeeze()
#         vix.index.name ='Date'
#         vix.to_csv(datadir+vix_file)
#     else:
#         vix=pd.read_csv(datadir+vix_file)
#         vix['Date']=pd.to_datetime(vix['Date'], infer_datetime_format='%Y-%m-%d')
#         vix.set_index('Date', inplace=True)
        
#     if isinstance(vix, pd.DataFrame): vix.columns=['VIX']
#     else: vix.rename('VIX',inplace=True)
#     vix_daily=vix.pct_change()
#     vix_daily.dropna(axis=0,inplace=True)
#     #VIX Daily ->Monthly
#     vix_monthly=vix_daily.resample(_rem).apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
#     vix_monthly.index=vix_monthly.index.to_period('M')
    
#     #QQQ - Nasdaq 100 ETF
#     qqq_file='QQQ_'+start_+'_'+end_+'.csv'
#     print('Load Nasdaq 100 ETF daily returns...')
#     if not path.isfile(datadir+qqq_file):
#         # updating from Yahoo
#         import pandas_datareader as pdr
#         qqq=pdr.get_data_yahoo('QQQ', start=start, end=end)['Adj Close']
#         qqq.to_csv(datadir+qqq_file)
#     else:
#         qqq=pd.read_csv(datadir+qqq_file)
#         qqq['Date']=pd.to_datetime(qqq['Date'], infer_datetime_format='%Y-%m-%d')
#         qqq.set_index('Date', inplace=True)
        
#     if isinstance(qqq, pd.DataFrame): qqq.columns=['QQQ']
#     else: qqq.rename('QQQ',inplace=True)
#     qqq_daily=qqq.pct_change()
#     qqq_daily.dropna(axis=0,inplace=True)
#     #QQQ daily->Monthly
#     qqq_monthly=qqq_daily.resample(_rem()).apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
#     qqq_monthly.index=qqq_monthly.index.to_period('M')
#     return spy_monthly, vix_monthly, qqq_monthly

# def spy_vix_qqq_2(datadir, tkr_list=[('SPY', 'yahoo', 'Adj Close'),
#                                      ('VIXCLS', 'fred',''),
#                                      ('QQQ', 'yahoo','Adj Close')], 
#                                       start='2018-02-28'):
#     import pandas_datareader as pdr
#     import yfinance as yf
    
#     for tkr in tkr_list:        
#         print('Loading '+tkr[0]+' daily prices from '+ (tkr[1]).upper() + ' ...')
#         if tkr[1] == 'yahoo': df=yf.download(tkr[0], start=start)    
#         else: df=pdr.DataReader(tkr[0], tkr[1], start=start)
#         if tkr[2]!='': df=df[tkr[2]]
#         if isinstance(df, pd.Series): df=df.to_frame()       
#         df.to_csv(datadir+tkr[0]+'_prices.csv')
        
#         #Daily returns        
#         df1= df.pct_change().rename(columns={'Adj Close':'Return'})
#         df1.dropna(axis=0,inplace=True)
#         df1.to_csv(datadir+tkr[0]+'_returns_Daily.csv')
#         print(tkr[0]+'daily returns calculted and saved')
        
#         #Spy Daily ->Monthly
#         df_monthly=df1.resample(_rem()).apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
#         df_monthly.index=df_monthly.index.to_period('M')
#         df_monthly.to_csv(datadir+tkr[0]+'_returns_Monthly.csv') 
#         print(tkr[0]+'monthly returns calculted and saved')
#     return

# def factor_ETFs_load(datadir, tkr_list=[('IWF', 'tiingo', 'adjClose'), 
#                                         ('IWD', 'tiingo', 'adjClose'),
#                                         ('IWN', 'tiingo', 'adjClose'),
#                                         ('IWO', 'tiingo', 'adjClose'),
#                                         ('MTUM', 'tiingo', 'adjClose'),
#                                         ('VIXM', 'tiingo', 'adjClose')],
#                       start='2018-02-28'):
#     import warnings
#     warnings.simplefilter(action='ignore', category=UserWarning)   
#     import pandas_datareader as pdr
#     for tkr in tkr_list:        
#         print('Load '+tkr[0]+' daily prices from  * '+tkr[1]+' *...')
#         df=pdr.DataReader(tkr[0], tkr[1], start=start)
#         # df=pdr.DataReader('IWF', 'tiingo', start=start)  #testing
#         if tkr[2]!='': df=df[tkr[2]]
#         if isinstance(df, pd.Series): df=df.to_frame()
#         if isinstance(df.index, pd.MultiIndex):
#             df.reset_index(level=0, inplace=True)
#         df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
#         df.index=df.index.tz_localize(None)
#         if 'symbol' in df.columns: df.drop(columns=['symbol'], inplace=True)
#         df.to_csv(datadir+tkr[0]+'_prices.csv')
        
#         #Daily returns        
#         df1= df.pct_change().rename(columns={tkr[2]:'Return'})
#         df1.dropna(axis=0,inplace=True)
#         df1.to_csv(datadir+tkr[0]+'_returns_Daily.csv')
#         print(tkr[0]+' : daily returns calculted and saved')
        
#         #Daily ->Monthly
#         # df1.index=df1.index.replace(tzinfo=None)
#         df_monthly=df1.resample(_rem()).apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
#         df_monthly.index=df_monthly.index.to_period('M')
#         df_monthly.to_csv(datadir+tkr[0]+'_returns_Monthly.csv') 
#         print(tkr[0]+' : monthly returns calculted and saved')
#     return

def VIX_load(datadir, start, isSave=True):
    #VIX index
    # from datetime import date
    # currmonth = date.today().month  
    # currday= date.today().day
    
    # import os
    # currdir = os.getcwd()
    # os.chdir(datadir)
    # file_history='VIXCLS_prices.csv'
    # vix_prices_hist=pd.read_csv(file_history, index_col=[0])['VIXCLS'].squeeze()
    # vix_prices_hist.index=pd.to_datetime(vix_prices_hist.index, format='%Y-%m-%d')
    # lastmonth=vix_prices_hist.index[-1].month
    
    # if  currmonth == lastmonth+1:
    #     print('VIX is actual. Update is not required...')
    # else:        
    import pandas as pd
    import pandas_datareader as pdr
    vix_prices = pdr.DataReader('VIXCLS', 'fred', start=start).dropna().rename(columns={'VIXCLS':'VIX'}).squeeze()
    vix_prices.index.name ='Date'
    vix_prices.index = pd.to_datetime(vix_prices.index, format='%Y-%m-%d')

    #VIX Daily returns        
    vix_returns= vix_prices.pct_change()
    vix_returns.dropna(axis=0,inplace=True)
    
    #Spy Daily ->Monthly
    vix_monthly=vix_returns.resample(_rem()).apply(lambda x: ((x + 1).prod() - 1)).round(4)
    vix_monthly.index=vix_monthly.index.to_period('M')
    
    if isSave:
        vix_prices.to_csv(datadir+'VIXCLS_prices.csv')    
        vix_returns.to_csv(datadir+'VIXCLS_returns_Daily.csv')
        vix_monthly.to_csv(datadir+'VIXCLS_returns_Monthly.csv')
        return
    else:
        return vix_prices, vix_returns, vix_monthly  


    # os.chdir(currdir)

def SP500_load(datadir, start, isSave=True):
    #SP500 index
    # from datetime import date
    # currmonth = date.today().month  
    # currday= date.today().day
    
    # import os
    # currdir = os.getcwd()
    # os.chdir(datadir)
    # file_history='SP500_prices.csv'
    # SP500_prices_hist=pd.read_csv(file_history, index_col=[0])['SP500'].squeeze()
    # SP500_prices_hist.index=pd.to_datetime(SP500_prices_hist.index, format='%Y-%m-%d')
    # lastmonth=SP500_prices_hist.index[-1].month
    
    # if  currmonth == lastmonth+1:
    #     print('SP500 is actual. Update is not required...')
    # else:        
    import pandas as pd
    import pandas_datareader as pdr
    SP500_prices = pdr.DataReader('SP500', 'fred', start=start).dropna()#.squeeze()
    SP500_prices.index.name ='Date'
    SP500_prices.index = pd.to_datetime(SP500_prices.index, format='%Y-%m-%d')

    #SP500 Daily returns        
    SP500_returns= SP500_prices.pct_change() #.rename(columns={'SP500C':'SP500'})
    SP500_returns.dropna(axis=0,inplace=True)

    #Spy Daily ->Monthly
    SP500_monthly=SP500_returns.resample(_rem()).apply(lambda x: ((x + 1).prod() - 1)).round(4)
    SP500_monthly.index=SP500_monthly.index.to_period('M')

    if isSave:
        SP500_prices.to_csv(datadir+'SP500_prices.csv')    
        SP500_returns.to_csv(datadir+'SP500_returns_Daily.csv')
        SP500_monthly.to_csv(datadir+'SP500_returns_Monthly.csv')
        return
    else:
        return SP500_prices, SP500_returns, SP500_monthly  

def TIINGO_load(tkr_list, metric_name='adjClose', startday='2022-05-01', endday=None):
    from tiingo import TiingoClient
    TIINGO_API_key='8a479ccc393e1d1f9f736e5fedbea2af461ee139'
    config = {}
    config['session'] = True
    config['api_key'] = TIINGO_API_key
    client = TiingoClient(config)
    if metric_name == None:
        etfs = client.get_dataframe(tkr_list,
                                    frequency='daily',
                                    startDate=startday,
                                    endDate=endday)   
    else:            
        etfs = client.get_dataframe(tkr_list,
                                    frequency='daily',
                                    metric_name=metric_name, 
                                    startDate=startday,
                                    endDate=endday)
    etfs.index.name ='Date'
    etfs.index=pd.to_datetime(etfs.index, format='%Y-%m-%d')
    return etfs

def ETFs_load(datadir, 
              tkr_list=['SPY', 'QQQ', 'IWF', 'IWD', 'IWN', 'IWO', 'MTUM', 'VIXM'],
              start='2018-02-28', isPrint=True
              ):
    import warnings
    warnings.simplefilter(action='ignore', category=UserWarning)    
    
    etfs = TIINGO_load(tkr_list, metric_name='adjClose', startday=start)
    
    for tkr in etfs.columns:        
        if isPrint: print('*** Load '+tkr +' prices ***')
        df = etfs[[tkr]] #[[.]] for dataframe
        if isinstance(df, pd.Series): df=df.to_frame()
        if isinstance(df.index, pd.MultiIndex):
            df.reset_index(level=0, inplace=True)
        df.index=df.index.tz_localize(None)
        if 'symbol' in df.columns: df.drop(columns=['symbol'], inplace=True)
        df.to_csv(datadir+tkr+'_prices.csv')
        
        #Daily returns        
        df1= df.pct_change() #.rename(columns={tkr:'Return'})
        df1.dropna(axis=0,inplace=True)
        df1.to_csv(datadir+tkr+'_returns_Daily.csv')
        if isPrint: print(tkr+' : daily returns calculted and saved')
        
        #Daily ->Monthly
        # df1.index=df1.index.replace(tzinfo=None)
        df_monthly=df1.resample(_rem()).apply(lambda x: (x + 1).prod() - 1).round(4)
        df_monthly.index=df_monthly.index.to_period('M')
        df_monthly.to_csv(datadir+tkr+'_returns_Monthly.csv') 
        if isPrint: print(tkr+' : monthly returns calculted and saved')
    return

# Load indexes HFR_Equity_Total, HFR_Equity_Mkt_Neutral, HFR_Equity_Quant
# link='https://www.hedgefundresearch.com/download/index-ror-perf-download/2561',
def load_hfr(filename='HFR Equity Total', filetype='csv',
             indexdir='Traders/Data/Indexes/', columnname='HFR Equity Total'):
    
    def p2f(x):
        return float(x.strip('%'))/100

    from os import path
    file=indexdir+filename+'.'+filetype
    Isfile=path.isfile(file) 
    if Isfile :
        df=pd.read_csv(file, header=2, names=['Date', 'Return'], 
                       skipfooter=4, engine='python',converters={'Return':p2f})
        ind_drop=df[df['Date'].str.contains("YTD")].index
        df=df.iloc[df.index.drop(ind_drop)]
        df['Date']=pd.to_datetime(df['Date'], format='%m/%Y')
        df.set_index('Date', inplace=True)
        df.index=df.index.to_period('M')
        df.columns=[filename.rsplit(" ", maxsplit=1)[0]]

        if df.columns != columnname: 
            df.rename(columns={df.columns[0] : columnname}, inplace=True) 

        lastmonth=df.index[-1].month
        lastmonth=df.index[-1].month
    else: 
        print("There is no file"+filename+'.'+filetype)
        return
    from datetime import date
    today = date.today()
    currmonth=today.month
    
    if currmonth > lastmonth+1: print('Please update the file: '+file)
    return df

def ff_approximate(histdir='/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/'
                   ):
    #ETFs from Tiingo - SPY, Value and Growth (iShares Russel indexes)
    '''
    #Large
    IWF	iShares Russell 1000 Growth ETF
    IWD	iShares Russell 1000 Value ETF
    
    #Small
    IWN	iShares Russell 2000 Value ETF
    IWO	iShares Russell 2000 Growth ETF
    '''
    # Download ETFs and save them (prices, daily and monthly returns) to histdir
    benchmarks = ['SPY', 'IWF', 'IWD', 'IWN', 'IWO']
    print('Downloading '+str(benchmarks)+' efts: ...')

    ETFs_load(histdir, tkr_list=benchmarks, isPrint=False)
    
    print('Calculating and saving approximation of French-Fama factors SMB and HML...')
    MKT=pd.read_csv(histdir+ 'SPY_returns_Daily.csv', index_col=[0]).squeeze().rename('MKT')
    MKT.index=pd.to_datetime(MKT.index, format='%Y-%m-%d')
    IWN=pd.read_csv(histdir+ 'IWN_returns_Daily.csv', index_col=[0]).squeeze()
    IWO=pd.read_csv(histdir+ 'IWO_returns_Daily.csv', index_col=[0]).squeeze()
    IWF=pd.read_csv(histdir+ 'IWF_returns_Daily.csv', index_col=[0]).squeeze()
    IWD=pd.read_csv(histdir+ 'IWD_returns_Daily.csv', index_col=[0]).squeeze()
    
    SMB = ((IWN+IWO)/2 - (IWF+IWD)/2).rename('SMB')
    SMB.index=pd.to_datetime(SMB.index, format='%Y-%m-%d')
    
    HML = ((IWN+IWD)/2 - (IWF+IWO)/2).rename('HML')
    HML.index=pd.to_datetime(HML.index, format='%Y-%m-%d')
    
    factors=pd.concat([MKT, SMB, HML], axis=1)
    factors.index.rename(name='Date', inplace=True)
    factors.to_csv(histdir+'French_Fama_approximation.csv')

    return factors

# Alpha and Beta - via French-Fama modelling
def ff_alpha_beta(andrew_ret, periods, datadir, librarydir, 
                  model="FF3x2", subdir='French-Fama/', 
                  groupby ='daily', #or 'weekly', or 'monthly'
                  dataset = 'original' #or 'approximated'
                  ):
    
    chdir(librarydir)
    from edhec_risk_kit import ff_update, beta_test #, annualize_rets
    # import statsmodels.api as sm
    # French-Fama factors loading
    
    if dataset == 'original': 
        ff = ff_update()
    else:  
        ff = ff_approximate() #NOT ready yet => requires to chaged "model" in beta_test() 
    
    # if groupby == 'monthly': 
    #     ff = ff.resample(_rem()).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
    #     ff.index=ff.index.to_period('M')
        
    #     andrew_ret=andrew_ret.resample(_rem()).apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
    #     andrew_ret.index=andrew_ret.index.to_period('M')
        
    #     for period in periods.keys():
    #        periods[period] = periods[period].to_period('M')
        
    # if groupby == 'weekly': 
    #     ff = ff.resample("W").apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
    #     ff.index=ff.index.to_period('W')
        
    #     andrew_ret=andrew_ret.resample("W").apply(lambda x: ((x + 1).cumprod() - 1).last("D"))
    #     andrew_ret.index=andrew_ret.index.to_period('W')
        
    makedirs(datadir+subdir, exist_ok=True)    
    bt_all=pd.DataFrame()
    
    for period in periods.keys():
        if len( periods[period] ) < 3: continue
        beta_test(andrew_ret, ff, period=periods[period], 
                  model=model, print_=True, display_=False, 
                  dirname=datadir+subdir, name=period
                  )
        bt=pd.read_csv(datadir+subdir+period+'_'+model+'.csv', index_col=[0])
        bt_all=pd.concat([bt_all, bt], axis=1)
        
    bt_all.loc['Beta']=bt_all.loc['Mkt-RF']
    bt_all.drop(['Mkt-RF'],inplace=True)
    bt_all.loc['Alpha (p.a.)']= round( (((1+bt_all.loc['alpha'])**252-1)).astype('float'), 3) #.astype(str)+'%'
    bt_all.drop(['alpha'],inplace=True)
    bt_all=bt_all.reindex(['Alpha (p.a.)', 'Beta', 'SMB', 'HML', 'RMW', 'CMA'])
    return bt_all

# Fact Sheet BEFORE and AFTER fees (Return expected for investors)
def after_fees(rm, mfra=1/100, pfr=0.2, hra=5/100, out='nav'):    
    '''
    Calculates monthly NAV after fees based on Geometric means for annual rate
    
    Parameters
    ----------
    nav : Series or DataFrame, dtype=float
        Monthly returns, before fees
    mfra : Number decimal
        Management fee, annual rate.
    pfr : Number decimal
        Performance fee, a proportion of performance above hurtle rate
    hra : Number decimal
        Hurdle, annual rate
    Returns
    -------
    Series, NAV and/or Returns after fees

    '''
    def geom_mean(ret_ann, period=12):
        return (1+ret_ann)**(1/period)-1
    mfrg=geom_mean(mfra)
    hrg=geom_mean(hra)
    
    def compound(ret_geom, period):
        df=pd.Series(np.repeat(ret_geom, period))
        return (1+df).cumprod()
    
    import numpy as np

    #NAV before fees
    if isinstance(rm, pd.DataFrame): rm=rm.squeeze()    #Convert to Series    
    if isinstance(rm, np.float64): rm=pd.Series(rm)
    length=rm.shape[0]
    nav=(1+rm).cumprod()   

    #Management fee accrual
    mf_cumprod=compound(mfrg, length)
    mf_cumprod.index=rm.index
    mf_accrued=mf_cumprod-1.0 # Management fee accrued
    #Hurdle
    h_cumprod=compound(hrg, length)
    h_cumprod.index=rm.index
    #NAV (Performance) above Hurdle
    performance=np.where(nav>h_cumprod, nav - h_cumprod, 0)
    performance=pd.Series(performance,index=rm.index)    
    pf_accrued = performance*pfr #Performance fees accrued
    # ALL fees accrued
    fees_accrued = mf_accrued+pf_accrued 
    #NAV after fees   
    nav_after=nav - fees_accrued
    #Returns after fees
    ret_after=nav_after.copy()
    ret_after.iloc[1:]= nav_after.iloc[1:].values / nav_after.iloc[:-1].values
    ret_after=pd.Series(ret_after-1.0, index=rm.index)
    
    if out.lower()=='both': return nav_after, ret_after
    elif out.lower()=='return': return ret_after
    else: return nav_after        
#test=after_fees(ak_monthly.loc['2020'], output='Return')

def after_fees2(rm, NAV0=100., mfra=1/100, pfr=0.2, hra=3/100, out='nav'):    
    '''
    Calculates monthly NAV after fees based on Geometric means for annual rate
    
    Parameters
    ----------
    nav : Series or DataFrame, dtype=float
        Monthly returns, before fees
    mfra : Number decimal
        Management fee, annual rate.
    pfr : Number decimal
        Performance fee, a proportion of performance above hurtle rate
    hra : Number decimal
        Hurdle, annual rate
    Returns
    -------
    Series, NAV and/or Returns after fees

    '''
    import numpy as np
    if isinstance(rm, pd.DataFrame): rm=rm.squeeze()    #Convert to Series    
    if isinstance(rm, np.float64): rm=pd.Series(rm)
    length=rm.shape[0]

    nav = pd.Series(index=rm.index, dtype='float64', name='NAV(gross)')
    #nav=(1.+rm).cumprod().squeeze().rename('NAV(gross)') #at the and of month
    nav_netto = pd.Series(index=rm.index, dtype='float64', name='NAV(netto)')

    mfm = pd.Series(index=rm.index, dtype='float64', name='Management Fee')
    pfm = pd.Series(index=rm.index, dtype='float64', name='Performance Fee accrued monthly')
    Performance = pd.Series(index=rm.index, dtype='float64', name='Performance accrued monthly')
    NetPerformance = pd.Series(index=rm.index, dtype='float64', name='Net Perfomance accrued monthly')

    hwm_start= pd.Series(index=rm.index, dtype='float64', name='HWM at period start')
    hwm_end= pd.Series(index=rm.index, dtype='float64', name='HWM at period end')
    change = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period start) Changed?')
    change_netto = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period end) Changed?')

    ret_after = pd.Series(index=rm.index, dtype='float64', name='Returns after fees')
    
    for i, per in enumerate(rm.index):
        if i == 0:
            nav.iloc[0] = NAV0*(1+rm.iloc[0])
            hwm_start.iloc[0] = NAV0
            change.iloc[0] = (hwm_start.iloc[0] > NAV0)
            
            mfm.iloc[0] = nav.iloc[0]*(mfra/12)  #at the end of month    
            Performance.iloc[0] = nav.iloc[0] - NAV0
            NetPerformance.iloc[0] = Performance.iloc[0] - NAV0*hra/12
            pfm.iloc[0] = pfr * NetPerformance.iloc[0] #if NetPerformance.iloc[0] > 0 else 0.

            nav_netto.iloc[0] = nav.iloc[0] - mfm.iloc[0] - pfm.iloc[0]            
            hwm_end.iloc[0] = max(hwm_start.iloc[0], nav_netto.iloc[0]) #cristallisation
            change_netto.iloc[0] = (hwm_end.iloc[0] > hwm_start.iloc[0])
            ret_after.iloc[0] = nav_netto.iloc[0] / NAV0 - 1.           
        else:
            nav.iloc[i] = nav_netto.iloc[i-1] * (1.+rm.iloc[i])
            hwm_start.iloc[i] = hwm_end.iloc[i-1]
            change.iloc[i] = (hwm_start.iloc[i] > hwm_start.iloc[i-1])
            
            mfm.iloc[i] = nav.iloc[i]*(mfra/12)  #at the end of month    
            Performance.iloc[i] = nav.iloc[i] - hwm_end.iloc[i-1]
            NetPerformance.iloc[i] = Performance.iloc[i] - hwm_end.iloc[i-1]*hra/12
            
            #ERROR if negative
            pfm.iloc[i] = pfr * NetPerformance.iloc[i] #if NetPerformance.iloc[0] > 0 else 0.

            nav_netto.iloc[i] = nav.iloc[i] - mfm.iloc[i] - pfm.iloc[i]            
            hwm_end.iloc[i] = max(hwm_start.iloc[i], nav_netto.iloc[i])
            change_netto.iloc[i] = (hwm_end.iloc[i] > hwm_start.iloc[i])

            ret_after.iloc[i] = nav_netto.iloc[i]/nav_netto.iloc[i-1] - 1.

    result = pd.concat([nav, hwm_start, change,
                        mfm, Performance, NetPerformance,pfm,
                        nav_netto, hwm_end, change_netto], axis=1)
    
    if out.lower()=='both': return nav_netto, ret_after
    elif out.lower()=='return': return ret_after
    else: return result

def after_fees2m(rm, NAV0=100., mfra=1/100, pfr=0.2, 
                 hra=3/100, hwm0=None, out='nav'):    
    '''
    Calculates monthly NAV after fees based on Geometric means for annual rate
    
    Parameters
    ----------
    nav : Series or DataFrame, dtype=float
        Monthly returns, before fees
    mfra : Number decimal
        Management fee, annual rate.
    pfr : Number decimal
        Performance fee, a proportion of performance above hurtle rate
    hra : Number decimal
        Hurdle, annual rate
    Returns
    -------
    Series, NAV and/or Returns after fees

    '''
    import numpy as np
    if isinstance(rm, pd.DataFrame): rm=rm.squeeze()    #Convert to Series    
    if isinstance(rm, np.float64): rm=pd.Series(rm)
    length=rm.shape[0]
    
    nav_start = pd.Series(index=rm.index, dtype='float64', name='NAV at period start')
    nav = pd.Series(index=rm.index, dtype='float64', name='NAV (before fees) at period end')
    #nav=(1.+rm).cumprod().squeeze().rename('NAV(gross)') #at the and of month
    nav_netto = pd.Series(index=rm.index, dtype='float64', name='NAV (after fees) at period end')

    mfm = pd.Series(index=rm.index, dtype='float64', name='Management Fee')
    pfm = pd.Series(index=rm.index, dtype='float64', name='Performance Fee accrued monthly')
    Performance = pd.Series(index=rm.index, dtype='float64', name='Gross Performance at period end')
    NetPerformance = pd.Series(index=rm.index, dtype='float64', name='Net Perfomance at period end')

    hwm_start= pd.Series(index=rm.index, dtype='float64', name='HWM at period start')
    hwm_end= pd.Series(index=rm.index, dtype='float64', name='HWM at period end')
    change = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period start) Changed?')
    change_netto = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period end) Changed?')

    ret_after = pd.Series(index=rm.index, dtype='float64', name='Returns (after fees)')

    hr_accrual = pd.Series(index=rm.index, dtype='float64', name='HR current period')    
    hr_debt = pd.Series(index=rm.index, dtype='float64', name='HR debt past periods')
    
    for i, per in enumerate(rm.index):
        if i == 0:
            nav_start.iloc[0] = NAV0
            nav.iloc[0] = NAV0*(1+rm.iloc[0])
            hwm_start.iloc[0] = NAV0 if hwm0 == None else hwm0
            change.iloc[0] = (hwm_start.iloc[0] > NAV0)
            
            mfm.iloc[0] = nav.iloc[0]*(mfra/12)  #at the end of month    
            Performance.iloc[0] = nav.iloc[0] - NAV0
            
            hr_accrual.iloc[0] = hra/12*hwm_start.iloc[0]
            hr_debt.iloc[0] = 0.
            NetPerformance.iloc[0] = Performance.iloc[0] - hr_accrual.iloc[0]
            
            pfm.iloc[0] = max(pfr * NetPerformance.iloc[0], 0)

            nav_netto.iloc[0] = nav.iloc[0] - mfm.iloc[0] - pfm.iloc[0]            
            hwm_end.iloc[0] = max(hwm_start.iloc[0], nav_netto.iloc[0]) #cristallisation
            change_netto.iloc[0] = (hwm_end.iloc[0] > hwm_start.iloc[0])
            ret_after.iloc[0] = nav_netto.iloc[0] / NAV0 - 1.           
        else:
            nav_start.iloc[i] = nav_netto.iloc[i-1]
            nav.iloc[i] = nav_netto.iloc[i-1] * (1.+rm.iloc[i])
            hwm_start.iloc[i] = hwm_end.iloc[i-1]
            change.iloc[i] = (hwm_start.iloc[i] > hwm_start.iloc[i-1])
            
            mfm.iloc[i] = nav.iloc[i]*(mfra/12)  #at the end of month    
            Performance.iloc[i] = nav.iloc[i] - hwm_end.iloc[i-1]
            
            hr_accrual.iloc[i] = hra/12 * hwm_start.iloc[i]
                        
            if NetPerformance.iloc[i-1] >= 0:    
                hr_debt.iloc[i] = 0.
            else: #NetPerformance <0
                if Performance.iloc[i-1] > (hr_accrual.iloc[i-1]+hr_debt.iloc[i-1]):
                    hr_debt.iloc[i] = 0.
                else:
                    if Performance.iloc[i-1] > 0: 
                        hr_debt.iloc[i] = (hr_accrual.iloc[i-1]-Performance.iloc[i-1])+hr_debt.iloc[i-1]
                    else:                     
                        hr_debt.iloc[i] = hr_accrual.iloc[i-1]+hr_debt.iloc[i-1]
          
            NetPerformance.iloc[i] = Performance.iloc[i] - (hr_accrual.iloc[i]+hr_debt.iloc[i])
            
            pfm.iloc[i] = max(pfr * NetPerformance.iloc[i], 0)

            nav_netto.iloc[i] = nav.iloc[i] - mfm.iloc[i] - pfm.iloc[i]            
            hwm_end.iloc[i] = max(hwm_start.iloc[i], nav_netto.iloc[i])
            change_netto.iloc[i] = (hwm_end.iloc[i] > hwm_start.iloc[i])

            ret_after.iloc[i] = nav_netto.iloc[i]/nav_netto.iloc[i-1] - 1.
    
    # ret_after.index = rm.index
    result = pd.concat([rm.rename('Returns'),
                        nav_start, nav, mfm, 
                        hwm_start, change,
                        Performance, 
                        hr_accrual, hr_debt,
                        NetPerformance,pfm,
                        nav_netto, hwm_end, change_netto,
                        ret_after], axis=1)
    
    if out.lower()=='both': return nav_netto, ret_after
    elif out.lower()=='details': return result    
    elif out.lower()=='return': return ret_after
    elif out.lower()=='nav_hwm_ret': return nav_netto, hwm_end, ret_after
    else: return result
    
def after_fees2q(rm, NAV0=100., mfra=1/100, pfr=0.2, hra=3/100, out='nav'):    
    '''
    Calculates quarterly NAV after fees based on Geometric means for annual rate
    
    Parameters
    ----------
    nav : Series or DataFrame, dtype=float
        Monthly returns, before fees
    mfra : Number decimal
        Management fee, annual rate.
    pfr : Number decimal
        Performance fee, a proportion of performance above hurtle rate
    hra : Number decimal
        Hurdle, annual rate
    Returns
    -------
    Series, NAV and/or Returns after fees

    '''
    import numpy as np
    if isinstance(rm, pd.DataFrame): rm=rm.squeeze()    #Convert to Series    
    if isinstance(rm, np.float64): rm=pd.Series(rm)
    
    nav = pd.Series(index=rm.index, dtype='float64', name='NAV(gross)')
    nav_netto = pd.Series(index=rm.index, dtype='float64', name='NAV(netto)')

    mfm = pd.Series(index=rm.index, dtype='float64', name='Management Fee')
    pfm = pd.Series(index=rm.index, dtype='float64', name='Performance Fee accrued monthly')
    Performance = pd.Series(index=rm.index, dtype='float64', name='Performance accrued monthly')
    NetPerformance = pd.Series(index=rm.index, dtype='float64', name='Net Perfomance accrued monthly')

    hwm_start= pd.Series(index=rm.index, dtype='float64', name='HWM at period start')
    hwm_end= pd.Series(index=rm.index, dtype='float64', name='HWM at period end')
    change = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period start) Changed?')
    change_netto = pd.Series(index=rm.index, dtype='boolean', name='Is HWM(at period end) Changed?')
    hurdle = pd.Series(index=rm.index, dtype='float64', name='Hurdle rate (/100)')
    rm.rename('Returns before fees monthly', inplace=True)
    ret_after = pd.Series(index=rm.index, dtype='float64', name='Returns after fees monthly')
    
    for i, per in enumerate(rm.index):
        if i == 0: #if 3rd month of quarter
            hwm_start.iloc[0] = NAV0
            change.iloc[0] = (hwm_start.iloc[0] > NAV0)
            hurdle.iloc[0] = hra/12

            nav.iloc[0] = NAV0 * (1+rm.iloc[0])            
            mfm.iloc[0] = nav.iloc[0]*(mfra/12)  #at the end of month                
            
            if per.strftime('%Y-%m')[-2:] in ['03', '06', '09', '12']:
                Performance.iloc[0] = nav.iloc[0] - hwm_start.iloc[0]
                NetPerformance.iloc[0] = Performance.iloc[0] - hwm_start.iloc[0]*hurdle.iloc[0]
                pfm.iloc[0] = max(pfr * NetPerformance.iloc[0], 0.)
                
                nav_netto.iloc[0] = nav.iloc[0] - mfm.iloc[0] - pfm.iloc[0]            
                hwm_end.iloc[0] = max(hwm_start.iloc[0], nav_netto.iloc[0]) #cristallisation
                change_netto.iloc[0] = (hwm_end.iloc[0] > hwm_start.iloc[0])
            else:
                Performance.iloc[0] = 0.
                NetPerformance.iloc[0] = 0.
                pfm.iloc[0] = 0.
                
                nav_netto.iloc[0] = nav.iloc[0] - mfm.iloc[0] - pfm.iloc[0]            
                hwm_end.iloc[0] = hwm_start.iloc[0] #cristallisation
                change_netto.iloc[0] = (hwm_end.iloc[0] > hwm_start.iloc[0])

            ret_after.iloc[0] = nav_netto.iloc[0] / NAV0 - 1.
            
        elif i == 1: #if 2nd month of quarter
            hwm_start.iloc[1] = hwm_end.iloc[0]
            change.iloc[1] = (hwm_start.iloc[1] > hwm_start.iloc[0])                
            hurdle.iloc[1] = hra/12*2

            nav.iloc[1] = nav_netto.iloc[0] * (1.+rm.iloc[1])            
            mfm.iloc[1] = nav.iloc[1]*(mfra/12)  #at the end of month    
                
            if per.strftime('%Y-%m')[-2:] in ['03', '06', '09', '12']:
                Performance.iloc[1] = nav.iloc[1] - hwm_start.iloc[1]
                NetPerformance.iloc[1] = Performance.iloc[1] - hwm_start.iloc[i]*hurdle.iloc[1]
                pfm.iloc[1] = max( pfr * NetPerformance.iloc[1], 0. )
                
                nav_netto.iloc[1] = nav.iloc[1] - mfm.iloc[1] - pfm.iloc[1]            
                hwm_end.iloc[1] = max(hwm_start.iloc[1], nav_netto.iloc[1]) #cristallisation
                change_netto.iloc[1] = (hwm_end.iloc[1] > hwm_start.iloc[1])
            else:
                Performance.iloc[1] = 0.
                NetPerformance.iloc[1] = 0.
                pfm.iloc[1] = 0.
                
                nav_netto.iloc[1] = nav.iloc[1] - mfm.iloc[1] - pfm.iloc[1]            
                hwm_end.iloc[1] = hwm_start.iloc[1]#cristallisation
                change_netto.iloc[1] = (hwm_end.iloc[1] > hwm_start.iloc[1])

            ret_after.iloc[1] = nav_netto.iloc[1] / nav_netto.iloc[0]- 1.            
        
        else: #i>=2
            hwm_start.iloc[i] = hwm_end.iloc[i-1]
            change.iloc[i] = (hwm_start.iloc[i] > hwm_start.iloc[i-1])
            
            occur = (hwm_start == hwm_start.iloc[i]).sum()
            hurdle.iloc[i] = hra/12*occur
            
            nav.iloc[i] = nav_netto.iloc[i-1] * (1.+rm.iloc[i])            
            mfm.iloc[i] = nav.iloc[i]*(mfra/12)  #at the end of month    
            
            if per.strftime('%Y-%m')[-2:] in ['03', '06', '09', '12']:           
                Performance.iloc[i] = nav.iloc[i] - hwm_start.iloc[i]
                NetPerformance.iloc[i] = Performance.iloc[i] - hwm_start.iloc[i]*hurdle.iloc[i]
 
                pfm.iloc[i] = max(pfr * NetPerformance.iloc[i], 0)
    
                nav_netto.iloc[i] = nav.iloc[i] - mfm.iloc[i] - pfm.iloc[i]            
                hwm_end.iloc[i] = max(hwm_start.iloc[i], nav_netto.iloc[i])
                change_netto.iloc[i] = (hwm_end.iloc[i] > hwm_start.iloc[i])
            else:
                Performance.iloc[i] = 0.
                NetPerformance.iloc[i] = 0.
                pfm.iloc[i] = 0.
                
                nav_netto.iloc[i] = nav.iloc[i] - mfm.iloc[i] - pfm.iloc[i]            
                hwm_end.iloc[i] = hwm_start.iloc[i]#cristallisation
                change_netto.iloc[i] = (hwm_end.iloc[i] > hwm_start.iloc[i])
                
            ret_after.iloc[i] = nav_netto.iloc[i]/nav_netto.iloc[i-1] - 1.

    result = pd.concat([nav, hwm_start, #change,
                        mfm, Performance, NetPerformance,
                        hurdle, pfm,
                        nav_netto, hwm_end, #change_netto,
                        rm, ret_after], axis=1)
    result.to_csv('/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/Returns after fees monthly.csv')
    
    if out.lower()=='both': return nav_netto, ret_after
    elif out.lower()=='return': return ret_after
    else: return result
    
def factsheet(ak_ret, years=['2018', '2019', '2020', '2021', '2022'], 
              decim=2, output='before fees', af_func=after_fees, 
              **kwargs):
    '''
    ak_net is monthly returns, after fees (net)
    '''
    import numpy as np
    fs=pd.DataFrame(columns=years, dtype=np.float32,
                    index=['Jan','Feb','Mar','Apr','May','Jun', 'Jul',
                             'Aug','Sep','Oct', 'Nov', 'Dec'])

    # ak_cum=(1+ak_net).cumprod() #series with cumulative trend    
    # nav_start=1.0
    YTD=[]
    for y in fs.columns:
        if y not in ak_ret.index: 
            YTD.append(None)
            continue
        
        if output.lower() == 'after fees':
            if af_func == None:
                ak_cum = (1+ak_ret.loc[y]).cumprod().squeeze() #series with cumulative trend        
                ak_ret1 = ak_ret.loc[y]
            else:                
                ak_cum, ak_ret1 = af_func(ak_ret.loc[y], **kwargs)
                ak_cum.index=ak_ret.loc[y].index
                ak_ret1.index=ak_ret.loc[y].index
        else: 
            ak_cum=(1+ak_ret.loc[y]).cumprod().squeeze() #series with cumulative trend        
            ak_ret1=ak_ret.copy()
        #Print for debugging
        # print('Type of ak_cum is', type(ak_cum))
        # print(ak_cum)
        if isinstance(ak_cum, np.float64): YTD.append(ak_cum-1)
        else: YTD.append(ak_cum.iloc[-1]-1)
        
        for m in fs.index:
            current=y+'-'+m
            # period=dt.datetime.strptime(y+'-'+m, '%Y-%b')
            #Debugging
            # print('Type of ak_ret1 is', type(ak_ret1))
            if current not in ak_ret1.index: continue
            ret=ak_ret1.loc[current]
            if isinstance(ret, pd.Series): fs.loc[m,y]=ret[0]
            else: fs.loc[m,y]=ret
        
    fs.loc['YTD']=YTD
    fs=fs.astype(float).round(decim)
    # fs= fs.where(fs.isnull()==True, (fs*100).astype(str)+'%' ) 
    # fs.fillna('',inplace=True)
    return fs.T
#%%
