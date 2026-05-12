#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 12:06:40 2021

@author: alexander
GoTrader37_pip
"""
def ARQuant_history_update(arq_append):
    import os 
    import pandas as pd
    # from importlib import reload
    # import IBKR_FTP_delivery
    # from os import chdir, listdir #, rename
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maindir = script_dir
    histdir = os.path.join(script_dir, '..', 'Data', 'ARQuant_history')
    ftpdir = os.path.join(script_dir, '..', 'Data', 'FTP')
    strategydir ='Strategy Summary/Inputs/' 
    
    #Update History of Daily Returns
    os.chdir(maindir)
    from Slides_analytic_function import update_return_history_v4
    
    update_return_history_v4(f_history =os.path.join(histdir, 'AVESA_Group_Ltd_U3577443_history.csv'),
                             f_last_month=os.path.join(histdir, arq_append))
    return print('\n*** ARQuant history has been updated ***')

#ARQuant_history_update
    #%%
def update_dataset(indexdir = None):
        
    import os 
    import pandas as pd
    # from importlib import reload
    # import IBKR_FTP_delivery
    # from os import chdir, listdir #, rename
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maindir = script_dir
    histdir = os.path.join(script_dir, '..', 'Data', 'ARQuant_history')
    ftpdir = os.path.join(script_dir, '..', 'Data', 'FTP')
    strategydir ='Strategy Summary/Inputs/' 
    
    if indexdir is None:
        indexdir = os.path.join(script_dir, '..', 'Data', 'Indexes')
    
    start = "2018-02-28"
    currdir =os.getcwd()
    # indexdir = '/users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/Indexes/'
    
    from datetime import date
    currmonth = date.today().month  
    currday= date.today().day
    
    # #HFR updates - NOT IN USE
    # os.chdir(indexdir)
    # file_history='HFRI_Quant_Directional.csv'
    # hfr=pd.read_csv(file_history, index_col=[0]).squeeze()
    # hfr.index=pd.to_datetime(hfr.index, format='%Y-%m-%d')
    # lastmonth=hfr.index[-1].month
    
    # if  currmonth == lastmonth+1:
    #     print('HFR indexes are actual. Update is not required...')
    # else:
    #     print('Downloading updates for HFR indexes from hfr.com...')
    #     os.chdir('/users/alexander/Dropbox/5-Finance/myARQuant/Python/')
    #     from HFR_download import HFR_indexies_update
    #     HFR_indexies_update(site_url='https://www.hfr.com/my-account/login/#login',
    #                         isPrint=True, 
    #                         isReturn=False,
    #                         indexdir=indexdir,
    #                         file_history=file_history)
 
    # #EurekaHedge updates   
    # os.chdir(indexdir)
    # file_history='Eurekahedge North America Long Short Equities HF Index.csv'
    # eri=pd.read_csv(file_history, index_col=[0])['Return'].squeeze()
    # eri.index=pd.to_datetime(eri.index, format='%Y-%m')
    # lastmonth=eri.index[-1].month
    
    # if  currmonth == lastmonth+1:
    #     print('EurekaHedge index is actual. Update is not required...')
    # else:
    #     print('Downloading updates for EurekaHedge index...')
    #     os.chdir('/Users/alexander/Dropbox/5-Finance/myARQuant/Python/')
    #     from HFR_download import ERI_indexies_download_and_process
    #     ERI_indexies_download_and_process()        
    
    os.chdir(currdir)
    
    # index_update()
    
    #%%
    #Download VIX and update file with VIX
    # file_history='VIXCLS_returns_Daily.csv'
    # vix=pd.read_csv(histdir+file_history, index_col=[0])
    # vix.index=pd.to_datetime(vix.index, format='%Y-%m')
    # lastday=vix.index[-1].month
    
    # if  lastmonth+1>=currmonth:
    #     print('VIX is actual. Update is not required...')
    # else:
    #     print('Downloading updates for VIX...')
        
    
    
    print('\nDownloading VIX, SPY and other benchmarks...')
    
    os.chdir('/users/alexander/Dropbox/5-Finance/myARQuant/Python/')
    from Slides_analytic_function import VIX_load
    VIX_load(histdir, start)
    
    #%%
    #ETFs from Tiingo - SPY, QQQ, Momentum, Value and Growth (iShares Russel indexes)
    '''
    #Large
    IWF	iShares Russell 1000 Growth ETF
    IWD	iShares Russell 1000 Value ETF
    
    #Small
    IWN	iShares Russell 2000 Value ETF
    IWO	iShares Russell 2000 Growth ETF
    '''
    
    benchmarks = ['SPY', 'QQQ', 'IWF', 'IWD', 'IWN', 'IWO', 'MTUM', 'VIXM']
    os.chdir('/users/alexander/Dropbox/5-Finance/myARQuant/Python/')
    from Slides_analytic_function import ETFs_load
    ETFs_load(histdir, tkr_list=benchmarks, start='2003-01-01', isPrint=False)
    
    #%%
    print('\nCalculating and saving approximation of French-Fama factors SMB and HML...')
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

    #%%
    # #French Fama factors downloads
    # print('\nDownloading original French-Fama factors...')
    # os.chdir('/users/alexander/Dropbox/0-ML/Python/GoTrader')
    # from edhec_risk_kit import ff_update
    # #daily
    # ff=ff_update()
    # ff=ff.loc['2018-03-01':]
    # ff.index=pd.to_datetime(ff.index, format='%Y-%m-%d')
    # ff.to_csv(histdir+'Frecn_Fama_daily.csv')
    # #monthly
    # def ff_monthly_update():
    #     header=2 
    #     link='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip'
    #     raw = pd.read_csv(link, header=header, sep=',')
    #     names=raw.columns.tolist()
    #     names[0] = 'Date'
    #     raw.columns = names
    #     if isinstance(raw['Date'].iloc[-1], str) :
    #         raw = raw.iloc[:-1]
        
    #     yearstart = raw.index[pd.isna(raw['Date'])].values[0]
    #     ff_monthly =raw.loc[:yearstart-2].dropna(axis=0, how='all')
    #     # ff_yearly = raw.loc[yearstart+1:].dropna(axis=0, how='all')
    
    #     format_='%Y%m' 
    #     ff_monthly['Date']=pd.to_datetime(ff_monthly['Date'], format=format_)
    #     ff_monthly.set_index('Date', inplace=True)
    #     # ff_monthly.index=ff_monthly.index.tz_localize(None)
    #     ff_monthly=ff_monthly.astype(float)/100
    #     return ff_monthly #, ff_yearly
    
    # ff= ff_monthly_update()
    # ff=ff.loc['2003-01':]
    # ff.index=pd.to_datetime(ff.index, format='%Y-%m')
    # ff.to_csv(histdir+'Frecn_Fama_monthly.csv')
    
    #%%
    '''
    #Study correlation between actual and approximated French-Fama factors
    print('Correlation between:')
    print("ff['Mkt-RF'] vs MKT_aprox = ", 
          pd.concat([MKT, ff['Mkt-RF']], axis=1).dropna(axis=0).corr().iloc[1,0].round(4)
          )
    print("ff['SMB'] vs SMB_aprox = ", 
          pd.concat([SMB, ff['SMB']], axis=1).dropna(axis=0).corr().iloc[1,0].round(4)
          )
    print("ff['HML'] vs HML_aprox = ", 
          pd.concat([HML, ff['HML']], axis=1).dropna(axis=0).corr().iloc[1,0].round(4)
          )
    '''
    #%%
    print('\nUpdating Risk Free Rate and S&P 500 from Fred portal...')
        # def RFR_load(tBill='TB3MS'): # 3-month T-Bill as of month start
        #     import pandas_datareader as pdr
        #     z=pdr.DataReader(tBill, 'fred')
        #     if isinstance(z, pd.DataFrame): z=z.squeeze()
        #     return z.iloc[-1]/100
        
    import pandas_datareader as pdr
    rfr=pdr.DataReader('TB3MS', 'fred', start= '2003-01-01')
    rfr.index=pd.to_datetime(rfr.index, format='%Y-%m-%d')
    if isinstance(rfr, pd.DataFrame): rfr=rfr.squeeze()
    rfr.index.name = 'Date'
    rfr.name = 'RF'
    rfr=rfr/100
    lm=rfr.index[-1]
    from os import path
    if path.isfile(histdir+'Risk_Free_Rate_monthly.csv'):
        rfr_existing = pd.read_csv(histdir+'Risk_Free_Rate_monthly.csv', infer_datetime_format=False)
        rfr_existing['Date']=pd.to_datetime(rfr_existing['Date'], dayfirst=True,
                                            infer_datetime_format='%Y-%m-%d')#correct parse dates
        rfr_existing.set_index(['Date'], inplace=True)#setting index
        lm_existing = rfr_existing.index[-1]
    else:
        from datetime import datetime
        lm_existing = datetime(2003, 1, 1, 0, 0, 0)
    
    if lm_existing < lm:
        rfr.to_csv(histdir+'Risk_Free_Rate_monthly.csv')
        print('*** Risk Free Rate has been updated ***')
    else:
        print("*** Risk Free Rate in the existing file is up to date so the history hasn't been updated ***")
    
    tkr= 'SP500'
    sp500_price=pdr.DataReader(tkr, 'fred', start = start) #start= '2018-02-28'
    if isinstance(sp500_price, pd.DataFrame): sp500_price=sp500_price.squeeze()
    sp500_price.index.name = 'Date'
    sp500_price.name = 'SP500'
    sp500_price.to_csv(histdir+tkr+'_prices.csv')   
    #Daily returns        
    sp500_ret= sp500_price.pct_change() #.rename(columns={tkr:'Return'})
    sp500_ret.dropna(axis=0,inplace=True)
    sp500_ret.to_csv(histdir+tkr+'_returns_Daily.csv')
        
    #Daily ->Monthly
    sp500_ret_monthly=sp500_ret.resample("M").apply(lambda x: ((x + 1).cumprod() - 1).last("D")).round(4)
    sp500_ret_monthly.index=sp500_ret_monthly.index.to_period('M')
    sp500_ret_monthly.to_csv(histdir+tkr+'_returns_Monthly.csv') 
       
    return     print('\n*** Updating has finished successfully ***')
# update_dataset()
