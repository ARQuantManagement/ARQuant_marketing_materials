#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified on 6-April, 2021
@author: alexander

Env GoTrader37_pip
"""
maindir='/users/alexander/Dropbox/5-Finance/myARQuant/Python/'
datadir='Data/Presentation_Inception_2023-01-31/'
arsenydir = 'Presentation_Inputs/'

def update_PowerPoint(maindir, datadir, arsenydir, 
                      pages_stat = {'P1':['Inception', 'L36M', '2022'],
                                    'P2':['2018', '2019', '2020', '2021']} ,
                      pages_ff = {'P1':['Inception', 'L36M', 'L12M'],
                                  'P2':['2018', '2019', '2020', '2021']} ,
                      wsize_stat = {'P1':'14cm;', 'P2':'18cm;'},
                      wsize_ff = {'P1':'10cm;', 'P2':'14cm;'},
                      resolution = 300, pct='', drop_list = [],
                      ):
    print('\n')  
    print('*** Preparing tables and plots for PowerPoint ***')
    
    from os import chdir, makedirs
    import pandas as pd 
    
    ppdir='PowerPoint/'
    makedirs(maindir+datadir+arsenydir+ppdir, exist_ok=True)

    ## PRINTING and PLOTING for Slides 5, 6, 7, 8, 9
    chdir(maindir)
    import Slides_for_print_function
    
    # # specify the custom font to use
    # import matplotlib.pyplot as plt
    # plt.rcParams['font.family']= 'Avenir'
    # # to check all fonts available
    # # import matplotlib.font_manager
    # # matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    # # plt.rcParams['font.Avenir'] = 'Avenir'
    
    # dicclrs={'arquant':'#ea6639',   # '#dc6d45'
    #          'benchmark1':'#43884e',
    #          'benchmark2':'#6b6c6d',
    #          'benchmark3': '#b5583c',
    #          'background':'#edb6a2', # '#f2d1c6'
    #          'dates': '#afb1b2',    # '#d6d7d8'
    #          'plotname': 'black'}
    
    from Slides_for_print_function import stats_periods_for_print2    
    from Slides_for_print_function import stat_html
    from Slides_for_print_function import f_alpha, f_beta
    # from Slides_for_print_function import ff_html
    from Slides_for_print_function import camp_html

    ak_stats_ =pd.read_pickle(maindir+datadir+arsenydir+'Stats.pkl')
    
    bt_all_ =pd.read_pickle(maindir+datadir+arsenydir+'FF3x2.pkl')
    
     ## Preparing French-Fama model for Slide 8
        # Make as % and reduce decimals
    bt=f_alpha(bt_all_,row=['Alpha (p.a.)'], decimals=1)
    bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)
    bt=bt.T
    # bt.index.rename('Periods', inplace=True)

    camp_html(bt, maindir+datadir+arsenydir+ppdir+'CAMP_for_slides',
              size = 'width: 10cm; height: 9.2cm;', row_height = '40px;',
              col_space=None, col_formatter=['40%', '30%', '30%'],
              isLastRow = False, resolution = resolution)   


    for page in pages_stat.keys():
        ak_stats = ak_stats_.loc[pages_stat[page], :]
        # bt_all = bt_all_.loc[:, pages_ff[page]]
        
        ak_stats_for_print=stats_periods_for_print2(ak_stats, drop_list=drop_list)
        ak_stats_for_print.index.rename('Risk/Return (before fees)', inplace=True)
    
    ##Slide 7 - Preparing Statistics
        stat_html(ak_stats_for_print, 
                  maindir+datadir+arsenydir+ppdir+'Stats_for_slides_'+page,
                  size = 'width: '+ wsize_stat[page]+' height: 18.1cm;', 
                  isLastRow = False, bcolor='#f0997a;', resolution = resolution)
        
    # ## Preparing French-Fama model for Slide 8
    #     # Make as % and reduce decimals

    #     bt=f_alpha(bt_all,row=['Alpha (p.a.)'], decimals=2)
    #     bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)    
    
    #     ff_html(bt, maindir+datadir+arsenydir+ppdir+'FF3x2_for_slides_'+page,
    #             size = 'width: '+ wsize_ff[page]+' height: 7cm;', resolution = resolution)   
    
    ## Preparing Factsheet for Slide 9
    from Slides_for_print_function import f_fsnet, factsheet_html
    fs_net=pd.read_csv(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv', index_col=[0])
    factsheet_html(f_fsnet(fs_net,pct=pct), 
                   maindir+datadir+arsenydir+ppdir+'Fact_sheet_after_fees',
                   isLastRow = False,
                   table_width = '100%;', col_width = '7.2%;',
                   # row_height = '50%;',
                   width='24.8cm;', #width was 24.95
                   height = '8.19cm;', #0.91 per row
                   bcolor = '#f0997a;', 
                   resolution = resolution)
    
    from shutil import copyfile
    copyfile(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv',
             maindir+datadir+arsenydir+ppdir+'Fact_sheet_after_fees.csv')
    
    ## Copying plots
    from shutil import copyfile
    copyfile(maindir+datadir+'Internal_use/Plots/'+'ARQuant_vs_Benchmarks_Inception.png',
             maindir+datadir+arsenydir+ppdir+'ARQuant_vs_Benchmarks_Inception.png')
    
    copyfile(maindir+datadir+'Internal_use/Plots/'+'Drawdoans_Periods_Inception.png',
             maindir+datadir+arsenydir+ppdir+'Drawdoans_Periods_Inception.png')
    
       
    print('*** Tables and plots for PowerPoint are completed ***')
    print('\n')  
    
    return

# update_PowerPoint(maindir, datadir, arsenydir)
#%%
def update_PowerPoint_SPY(maindir, datadir, arsenydir, 
                      pages_stat = {'P1':['Inception', 'L36M', '2022'],
                                    'P2':['2018', '2019', '2020', '2021']} ,
                      pages_ff = {'P1':['Inception', 'L36M', 'L12M'],
                                  'P2':['2018', '2019', '2020', '2021']} ,
                      wsize_stat = {'P1':'14cm;', 'P2':'18cm;'},
                      wsize_ff = {'P1':'10cm;', 'P2':'14cm;'},
                      resolution = 300, pct='', drop_list=[],
                      ):
    print('\n')  
    print('*** Preparing tables and plots for PowerPoint ***')
    
    from os import chdir, makedirs
    import pandas as pd 
    
    ppdir='PowerPoint/'
    makedirs(maindir+datadir+arsenydir+ppdir, exist_ok=True)

    ## PRINTING and PLOTING for Slides 5, 6, 7, 8, 9
    chdir(maindir)
    import Slides_for_print_function
        
    from Slides_for_print_function import stats_periods_for_print2    
    from Slides_for_print_function import stat_html
    # from Slides_for_print_function import f_alpha, f_beta
    # from Slides_for_print_function import ff_html
    # from Slides_for_print_function import camp_html

    ak_stats_ =pd.read_pickle(maindir+datadir+arsenydir+'Stats.pkl')
    # ak_stats_ = ak_stats_.drop(drop_list, axis=0)
    # bt_all_ =pd.read_pickle(maindir+datadir+arsenydir+'FF3x2.pkl')
    
     ## Preparing French-Fama model for Slide 8
        # Make as % and reduce decimals
    # bt=f_alpha(bt_all_,row=['Alpha (p.a.)'], decimals=1)
    # bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)
    # bt=bt.T
    # bt.index.rename('Periods', inplace=True)

    # camp_html(bt, maindir+datadir+arsenydir+ppdir+'CAMP_for_slides',
    #           size = 'width: 10cm; height: 9.2cm;', row_height = '40px;',
    #           col_space=None, col_formatter=['40%', '30%', '30%'],
    #           isLastRow = False, resolution = resolution)   


    for page in pages_stat.keys():
        try: 
            ak_stats = ak_stats_.loc[pages_stat[page], :]
            # bt_all = bt_all_.loc[:, pages_ff[page]]
            
            ak_stats_for_print=stats_periods_for_print2(ak_stats, drop_list=drop_list)
            ak_stats_for_print.index.rename('Risk/Return (before fees)', inplace=True)
        
            ##Slide 7 - Preparing Statistics
            stat_html(ak_stats_for_print, 
                      maindir+datadir+arsenydir+ppdir+'Stats_for_slides_'+page,
                      size = 'width: '+ wsize_stat[page]+' height: 18.1cm;', 
                      isLastRow = False, bcolor='#f0997a;', resolution = resolution)
        
        # ## Preparing French-Fama model for Slide 8
        #     # Make as % and reduce decimals
    
        #     bt=f_alpha(bt_all,row=['Alpha (p.a.)'], decimals=2)
        #     bt=f_beta(bt, row=['Beta (S&P500)'], decimals=2)    
        
        #     ff_html(bt, maindir+datadir+arsenydir+ppdir+'FF3x2_for_slides_'+page,
        #             size = 'width: '+ wsize_ff[page]+' height: 7cm;', resolution = resolution)   

        except: print("Passing list-likes to .loc or [] with any missing labels is no longer supported")
    
    ## Preparing Factsheet for Slide 9
    from Slides_for_print_function import f_fsnet, factsheet_html
    fs_net=pd.read_csv(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv', index_col=[0])
    factsheet_html(f_fsnet(fs_net,pct=pct), 
                   maindir+datadir+arsenydir+ppdir+'Fact_sheet_after_fees',
                   isLastRow = False,
                   table_width = '100%;', col_width = '7.2%;',
                   # row_height = '50%;',
                   width='24.8cm;', #width was 24.95
                   height = '8.19cm;', #0.91 per row
                   bcolor = '#f0997a;', 
                   resolution = resolution)
    
    from shutil import copyfile
    copyfile(maindir+datadir+arsenydir+'Fact_Sheet_after_fees.csv',
             maindir+datadir+arsenydir+ppdir+'Fact_sheet_after_fees.csv')
    
    ## Copying plots
    from shutil import copyfile
    copyfile(maindir+datadir+'Internal_use/Plots/'+'ARQuant_vs_Benchmarks_Inception.png',
             maindir+datadir+arsenydir+ppdir+'ARQuant_vs_Benchmarks_Inception.png')
    
    copyfile(maindir+datadir+'Internal_use/Plots/'+'Drawdoans_Periods_Inception.png',
             maindir+datadir+arsenydir+ppdir+'Drawdoans_Periods_Inception.png')
    
       
    print('*** Tables and plots for PowerPoint are completed ***')
    print('\n')  
    
    return