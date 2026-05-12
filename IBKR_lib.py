#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 18:11:06 2023

@author: alexander
"""


def parse_flexreport(name,
                     section = ['Time Period Performance Statistics',
                                'Cumulative Performance Statistics',
                                	'Performance by Symbol']
                     ):
    import pandas as pd
    rows=pd.read_csv(name,
                     names = ['Section','Field'],
                     usecols = [0,1]
                     )
    dic = dict()
    for _key in section:   
        idx=rows[rows.Section == _key ].index
        if len(idx)==0: print('\n*** Place a correct "Monthly factsheet" in ARQuant_history')
        dic[_key] = pd.read_csv(name,
                                header = idx[1],
                                nrows = len(idx[2:])
                                )
    return dic

def render (dic, output = 'both'):
    import pandas as pd
    for key, df in dic.items():
        df=df.drop(df.columns[[0, 1,]], axis=1)
        if 'Date' in df.columns and 'Performance' in key:
            if 'Time Period' in key: ret= df.copy()
            if 'Cumulative' in key:  ret['Cum Return'] = df['Return']
        if 'Performance by Symbol' in key:
            idx = df[df.Description.isnull()].index
            contrib=df.drop(idx, axis=0)
            contrib.rename(columns={'FinancialInstrument':'Instrument'}, inplace=True)
            # contrib = contrib [['Symbol', 'Description', 'Instrument', ]]
    if output == 'both':
        return ret, contrib
    elif 'ret' in output:
        return ret
    else:
        return contrib

def contrib_selection(contrib, 
                      select = ['Symbol', 'Description', 'Instrument', 'Contribution'],
                      criteria = 'Contribution',
                      ntop=None, isUSD=True):  
    import pandas as pd      
    if not isUSD: contrib1 = contrib.drop(contrib[contrib.Symbol=='USD'].index, axis=0)
    else: contrib1=contrib.copy()
    # contrib2 = contrib1.drop(columns=['Sector', 'AvgWeight','Return', 'Unrealized_P&L', 'Realized_P&L', 'Open'], axis=1)
    contrib2=contrib1[select]
    contrib2 = contrib2.sort_values(by=criteria, ascending=False, ignore_index = True)
    if ntop != None:
        if contrib2.shape[0]> 2*ntop:
            contrib3 = pd.concat([contrib2.iloc[:ntop],
                                  contrib2.iloc[-ntop:]])
        else: contrib3 = contrib2.copy()
    else: contrib3 = contrib2.copy()    
    contrib3[criteria]=contrib3[criteria].apply("{:.2f}%".format)
    return contrib3

# contrib_selection(contrib1, ntop=10)
    