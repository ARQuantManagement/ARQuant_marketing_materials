#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified on 6-April, 2021
@author: alexander

Env GoTrader37_pip
"""

def update_web(maindir, datadir, arsenydir, intdir, filename ='', isAlpha=True):
    print('\n')  
    print('*** Preparing tables and plots for print and website ***')
    
    from os import chdir, makedirs
    import pandas as pd 
    
    webdir='Website_slides/'
    makedirs(maindir+datadir+webdir, exist_ok=True)

    ## PRINTING and PLOTING for Slides 5, 6, 7, 8, 9
    chdir(maindir)
    import Slides_for_print_function
    
    # specify the custom font to use
    import matplotlib.pyplot as plt
    plt.rcParams['font.family']= 'Avenir'
    # to check all fonts available
    # import matplotlib.font_manager
    # matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    # plt.rcParams['font.Avenir'] = 'Avenir'
    
    dicclrs={'arquant':'#ea6639',   # '#dc6d45'
             'benchmark1':'#43884e',
             'benchmark2':'#6b6c6d',
             'benchmark3': '#b5583c',
             'background':'#edb6a2', # '#f2d1c6'
             'dates': '#afb1b2',    # '#d6d7d8'
             'plotname': 'black'}
            
    ##Preparing Statistics for Screen "How we see the world"
    ak_stats=pd.read_pickle(maindir+datadir+arsenydir+'Stats.pkl')
    
    from Slides_for_print_function import f_alpha, f_beta
    bt_all=pd.read_pickle(maindir+datadir+arsenydir+'FF3x2.pkl')
    # Make as % and reduce decimals
    bt=f_alpha(bt_all, row=['Alpha (p.a.)'], decimals=2)
    bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)    
    # bt_web=bt.iloc[0:2]
    
    if isAlpha == True: 
        bt_web=bt
    else:
        bt_web=bt.drop('Alpha (p.a.)', axis=0)
        
    from Slides_for_print_function import stats_periods_for_print2   
    # ak_stats_for_print=stats_periods_for_print2(ak_stats)    
    # ak_stats_web=pd.concat([ak_stats_for_print, bt_web], axis=0)
    ak_stats_web = stats_periods_for_print2(ak_stats)
    for row in bt_web.index:
        for col in ak_stats_web.columns:
            if col in bt_web.columns:
                ak_stats_web.loc[row, col] = bt_web.loc[row,col]
            else:
                ak_stats_web.loc[row, col] = '-'
        
    ak_stats_web.to_csv(maindir+datadir+webdir+'Stats_for_web.csv')
    
    # # Make HTML with company styling
    # from Slides_for_print_function import stat_html
    # stat_html(ak_stats_web, 
    #           maindir+datadir+webdir+'Stats_for_web')
        
    ## Preparing French-Fama model for Slide 8
    #Load from file+index_col=[0]
    # reload(Slides_for_print_function)
    # #Make HTML with company styling      
    # stat_html(bt[periods_ff], maindir+datadir+'FF3x2_for_print')
    
    
    # ## Preparing Factsheet for Slide 9
    # from Slides_for_print_function import f_fsnet, factsheet_html
    # # feestring='1.0-20-5'
    # fs_net=pd.read_csv(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv', index_col=[0])
    # factsheet_html(f_fsnet(fs_net), maindir+datadir+webdir+'Fact_sheet_after_fees')
    
    from shutil import copyfile
    copyfile(maindir+datadir+intdir+filename,
             maindir+datadir+webdir+filename)
    
    ## Copying plots
    from shutil import copyfile
    copyfile(maindir+datadir+'Internal_use/Plots/'+'ARQuant_vs_Benchmarks_Inception.png',
             maindir+datadir+webdir+'ARQuant_vs_Benchmarks_Inception.png')
    
    # copyfile(maindir+datadir+'Internal_use/Plots/'+'Drawdoans_Periods_Inception.png',
    #          maindir+datadir+webdir+'Drawdoans_Periods_Inception.png')
    
       
    print('*** Tables and plots for print and website are completed ***')
    print('\n')  
    
    return
#%%
def update_web_SPY(maindir, datadir, arsenydir, intdir, filename ='', isAlpha=True):
    print('\n')  
    print('*** Preparing tables and plots for print and website ***')
    
    from os import chdir, makedirs
    import pandas as pd 
    
    webdir='Website_slides/'
    makedirs(maindir+datadir+webdir, exist_ok=True)

    ## PRINTING and PLOTING for Slides 5, 6, 7, 8, 9
    chdir(maindir)
    import Slides_for_print_function
    
    # specify the custom font to use
    import matplotlib.pyplot as plt
    plt.rcParams['font.family']= 'Avenir'
    # to check all fonts available
    # import matplotlib.font_manager
    # matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    # plt.rcParams['font.Avenir'] = 'Avenir'
    
    dicclrs={'arquant':'#ea6639',   # '#dc6d45'
             'benchmark1':'#43884e',
             'benchmark2':'#6b6c6d',
             'benchmark3': '#b5583c',
             'background':'#edb6a2', # '#f2d1c6'
             'dates': '#afb1b2',    # '#d6d7d8'
             'plotname': 'black'}
            
    ##Preparing Statistics for Screen "How we see the world"
    ak_stats=pd.read_pickle(maindir+datadir+arsenydir+'Stats.pkl')
    
    # from Slides_for_print_function import f_alpha, f_beta
    # bt_all=pd.read_pickle(maindir+datadir+arsenydir+'FF3x2.pkl')
    # Make as % and reduce decimals
    # bt=f_alpha(bt_all, row=['Alpha (p.a.)'], decimals=2)
    # bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)    
    # bt_web=bt.iloc[0:2]
    
    # if isAlpha == True: 
    #     bt_web=bt
    # else:
    #     bt_web=bt.drop('Alpha (p.a.)', axis=0)
        
    from Slides_for_print_function import stats_periods_for_print2   
    # ak_stats_for_print=stats_periods_for_print2(ak_stats)    
    # ak_stats_web=pd.concat([ak_stats_for_print, bt_web], axis=0)
    ak_stats_web = stats_periods_for_print2(ak_stats)
    # for row in bt_web.index:
    #     for col in ak_stats_web.columns:
    #         if col in bt_web.columns:
    #             ak_stats_web.loc[row, col] = bt_web.loc[row,col]
    #         else:
    #             ak_stats_web.loc[row, col] = '-'
        
    ak_stats_web.to_csv(maindir+datadir+webdir+'Stats_for_web.csv')
    
    # # Make HTML with company styling
    # from Slides_for_print_function import stat_html
    # stat_html(ak_stats_web, 
    #           maindir+datadir+webdir+'Stats_for_web')
        
    ## Preparing French-Fama model for Slide 8
    #Load from file+index_col=[0]
    # reload(Slides_for_print_function)
    # #Make HTML with company styling      
    # stat_html(bt[periods_ff], maindir+datadir+'FF3x2_for_print')
    
    
    # ## Preparing Factsheet for Slide 9
    # from Slides_for_print_function import f_fsnet, factsheet_html
    # # feestring='1.0-20-5'
    # fs_net=pd.read_csv(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv', index_col=[0])
    # factsheet_html(f_fsnet(fs_net), maindir+datadir+webdir+'Fact_sheet_after_fees')
    
    from shutil import copyfile
    copyfile(maindir+datadir+intdir+filename,
             maindir+datadir+webdir+filename)
    
    ## Copying plots
    from shutil import copyfile
    copyfile(maindir+datadir+'Internal_use/Plots/'+'ARQuant_vs_Benchmarks_Inception.png',
             maindir+datadir+webdir+'ARQuant_vs_Benchmarks_Inception.png')
    
    # copyfile(maindir+datadir+'Internal_use/Plots/'+'Drawdoans_Periods_Inception.png',
    #          maindir+datadir+webdir+'Drawdoans_Periods_Inception.png')
    
       
    print('*** Tables and plots for print and website are completed ***')
    print('\n')  
    
    return