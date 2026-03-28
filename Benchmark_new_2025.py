#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 10:29:40 2025

@author: alexander
"""

#%%
def benchmark_update(etf_list=[
                              'BTAL',
                              'CLSE',
                              # 'EHLS', launched in mid-2024
                              'FFLS',
                              'LBAY',
                              'LSEQ',
                              'EQLS'
                              ],
                    startday = '2018-02-28',
                    maindir='/Users/alexander/Dropbox/5-Finance/myARQuant/Python/',
                    histdir='/Users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/',
                    datadir='/Users/alexander/Dropbox/5-Finance/myARQuant/Python/Data/Benchmark/',
                    ):
    import pandas as pd
    from os import chdir
    chdir(maindir)
    from Slides_analytic_function import ETFs_load

    #Settings
    ETFs_load(histdir, tkr_list=etf_list, start=startday, isPrint=False)  

    etf_df=pd.DataFrame()
    for tkr in etf_list:
        etf_df[tkr] = pd.read_csv(histdir+tkr+'_returns_daily.csv',                   
                              index_col=[0], infer_datetime_format=True).squeeze()

    etf_df.index=pd.to_datetime(etf_df.index, format='%Y-%m-%d')
    
    _coeff=pd.Series([0., 0.25623894, 0.1947488, 0.29173207, 0., 0.],
                     index=['BTAL','CLSE','FFLS','LBAY', 'LSEQ', 'EQLS'], 
                     dtype='float64')
    bm1= etf_df.dot(_coeff).rename('3 ETFs weighted')
    
    bm2= etf_df.mean(axis=1).rename('6 ETFs equally')
    
    _coeff3=pd.Series([0., 0.33333, 0.33333, 0.33333, 0., 0.],
                     index=['BTAL','CLSE','FFLS','LBAY', 'LSEQ', 'EQLS'], 
                     dtype='float64')
    bm3= etf_df.dot(_coeff3).rename('3 ETFs equally')

    etf_df['New bechmark-2 (7 ETF equally)'] = bm2    
    etf_df['New bechmark-1 (3 ETF weighted)'] = bm1
    etf_df['New bechmark-3 (3 ETF equally)'] = bm3
    
    return etf_df

#%%
# Only runs if the script is executed directly, not on import
if __name__ == '__main__':
    
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
    
    computer = '/Users/alexander/' #Moscow Macbook
    # computer= '/Users/alexander/Library/CloudStorage/' #Nice Macbook
    
    maindir= computer + 'Dropbox/5-Finance/myARQuant/Python/'
    librarydir= computer +'Dropbox/0-ML/Python/GoTrader/'
    histdir= computer + 'Dropbox/5-Finance/myARQuant/Python/Data/ARQuant_history/'
    indexdir = computer +'Dropbox/5-Finance/myARQuant/Python/Data/Indexes/'
    
    datadir = computer + 'Dropbox/5-Finance/myARQuant/Python/Data/Benchmark/'
    #%%
    
    etf_df= benchmark_update()
    
    etf_df_monthly=etf_df.loc['2024':].resample("M").apply(lambda x: ((x + 1).prod() - 1))
    etf_df_monthly.index=etf_df_monthly.index.to_period('M')
    
    etf_df.loc['2024':].to_csv(datadir+"New benchmark and its components (daily, from 2024-01).csv")
    etf_df_monthly.to_csv(datadir+"New benchmark and its components (monthly, from 2024-01).csv")
    # etf_df[['New bechmark-1 (3 ETF weighted)','New bechmark-3 (3 ETF equally)']].loc['2024':].corr()
    
    #%%
    startyear='2025'
    bm_df=etf_df.loc[startyear:, etf_df.columns[-3:]
                                # 'New bechmark-1 (3 ETF weighted)',
                                # 'New bechmark-2 (7 ETF equally)',
                                # 'New bechmark-3 (3 ETF equally)',
                                # 'CLSE','FFLS','LBAY',
                                ]
    
    bm_df.to_csv(histdir+"New benchmark and its components (daily, from 2024-01).csv")
    
    bm_df_monthly=bm_df.resample("M").apply(lambda x: ((x + 1).prod() - 1))
    bm_df_monthly.index=bm_df_monthly.index.to_period('M')
    bm_df_monthly.to_csv(histdir+"New benchmark and its components (monthly, from 2024-01).csv")
    
    bm_df_wealth = (1+bm_df_monthly).cumprod()*100
    new_col_order=bm_df_wealth.iloc[-1].sort_values(ascending=False).index
    bm_df_wealth = bm_df_wealth[new_col_order]
    #Plot cummulative returna
    bm_both=pd.concat([pd.DataFrame([ [100.,] * bm_df_wealth.shape[1] ], columns=bm_df_wealth.columns),
                        bm_df_wealth],axis=0)
    bm_both.plot()
    
    #%%
    ##Pareto optimal
    
    from New_robot_release_functions import Pareto, PCA_stats_uniqueness
    
    dfp_sorted, objectives, pareto_optimal_indices, dominated_indices, stats = Pareto(etf_df_monthly, period=None, method='paretoset')
    dfsave=dfp_sorted.loc[pareto_optimal_indices, objectives]
    dfsave.to_csv(datadir+' Pareto optimal variants.csv')
    stats.T.to_csv(datadir+' Metrics for variants.csv')    
    etf_df_monthly.to_csv(datadir+'ETFs monthly returns.csv')
    
    #%%
    #Sharpe optimisation
    def portfolio_return(weights, returns):
        """
        Computes the return on a portfolio from constituent returns and weights
        weights are a numpy array or Nx1 matrix and returns are a numpy array or Nx1 matrix
        """
        return weights.T @ returns
    
    
    def portfolio_vol(weights, covmat):
        """
        Computes the vol of a portfolio from a covariance matrix and constituent weights
        weights are a numpy array or N x 1 maxtrix and covmat is an N x N matrix
        """
        vol = (weights.T @ covmat @ weights)**0.5
        return vol 
    
    def msr(riskfree_rate, er, cov, _bounds=(-1.0, 1.0) ):
        """
        Returns the weights of the portfolio that gives you the maximum sharpe ratio
        given the riskfree rate and expected returns and a covariance matrix
        """
        from scipy.optimize import minimize    
    
        n = cov.shape[0] # initially it was er.shape[0]
        init_guess = np.repeat(1/n, n)
        bounds = (_bounds,) * n # an N-tuple of 2-tuples!
        weights_sum_to_1 = {'type': 'eq',
                            'fun': lambda weights: np.sum(weights) - 1
                            }
        def neg_sharpe(weights, riskfree_rate, er, cov):
            """
            Returns the negative of the sharpe ratio
            of the given portfolio
            """
            r = portfolio_return(weights, er)
            vol = portfolio_vol(weights, cov)
            return -(r - riskfree_rate)/vol
        
        weights = minimize(neg_sharpe, init_guess,
                           args=(riskfree_rate, er, cov), 
                           method='SLSQP',
                           options={'disp': False},
                           constraints=(weights_sum_to_1,),
                           bounds=bounds)
        return pd.Series(weights.x, index=cov.index)
    
    #GACR - This method is more suitable when returns are volatile. More reliable for long-term returns.
    dfr=etf_df.loc['2024':,['BTAL', 'CLSE', 'FFLS', 'LBAY', 'LSEQ', 'EQLS']]
    root = lambda x: np.power(x, 1/dfr.shape[0])
    er_geo = ( root( (1+dfr).prod() )-1 ).values 
    
    from sklearn.covariance import LedoitWolf
    lw = LedoitWolf()
    cov_shrinkage = lw.fit(dfr).covariance_
    cov_shrinkage_df = pd.DataFrame(cov_shrinkage, index=dfr.columns, columns=dfr.columns)
    
    weights_geo=msr(4.5/100, er_geo, cov_shrinkage_df, _bounds=(0., 1.0) ).rename('ER CAGR')
    print(weights_geo.round(2))
