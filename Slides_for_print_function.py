#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 13:26:07 2021

@author: alexander
"""
import datetime as dt
import pandas as pd

#%%
def stats_periods_for_print(st, rnd=1,
                            yearlist = ['2019', '2020', '2021'],
                            nullifYTD = ["CAGR gross",
                                         "Volatility annualized",
                                         "Sharpe",
                                         "Calmar",
                                         "Sortino",
                                         'Kelly criterion',
                                         'Skewness',
                                         'Kurtosis',
                                         'VaR (5%)',
                                         'CVaR (5%)',
                                         # 'Alpha', 'Beta'
                                         ]):
    if isinstance(st,pd.Series): st = st.to_frame()
    
    stats=st.copy()
    stats.rename(columns={'Historic CVaR (5%)':'CVaR (5%)',
                          'Cornish-Fisher VaR (5%)':'VaR (5%)', 
                          'Recovery time (max days)':'Recovery (max days)',
                          "Sharpe Ratio":'Sharpe',
                          'Growth' : "Cumulative Gross Return",
                          'Return annualized' : "CAGR gross"
                          },  
                  inplace=True
                  )
    
    stats=stats.drop(["Recovery time(75% cases)", 
                      "Win Prob. weekly", "Leverage optimal",
                      "Expected growth", "Years to increase by 1x Vol"], 
                     axis=1)
    stats["Cumulative Gross Return"]= (st['Growth']*100).round(rnd).astype(str)+"%"   
    stats["CAGR gross"]= (st["Return annualized"]*100).round(rnd).astype(str)+"%"

    #Making equal for a full calendar year  
    stats["CAGR gross"].loc[stats.index.intersection(yearlist)] = stats["Cumulative Gross Return"].loc[stats.index.intersection(yearlist)] 

    
    stats["Volatility annualized"]= (st["Volatility annualized"]*100).round(rnd).astype(str)+"%"
    stats["VaR (5%)"]= (st["Cornish-Fisher VaR (5%)"]*100).round(rnd).astype(str)+"%"
    stats["CVaR (5%)"]= (st["Historic CVaR (5%)"]*100).round(rnd).astype(str)+"%"
    stats["Max Drawdown"]= (st["Max Drawdown"]*100).round(rnd).astype(str)+"%"
    stats["Calmar"]=st["Calmar"].round(rnd+1)
    stats["Sortino"]=st["Sortino"].round(rnd+1)
    stats['Kelly criterion']=st["Kelly criterion"].round(rnd+1)

    stats['Recovery (max days)']=st['Recovery time (max days)']
    #Weekly
    stats["Mean Return weekly"]= (st["Mean Return weekly"]*100).round(2).astype(str)+"%"
    stats["Best Week"]= (st["Best Week"]*100).round(rnd).astype(str)+"%"
    stats["Worst Week"]= (st["Worst Week"]*100).round(rnd).astype(str)+"%"
    stats["Average Win weekly"]= (st["Average Win weekly"]*100).round(rnd).astype(str)+"%"
    stats["Average Loss weekly"]= (st["Average Loss weekly"]*100).round(rnd).astype(str)+"%"
    stats["Win rate weekly"]= (st["Win rate weekly"]*100).round(rnd).astype(str)+"%"
    
    cols = stats.columns.intersection(nullifYTD)
    idx = stats.index.intersection(['YTD'])
    stats.loc[idx, cols] = '-' #None         
    # stats[cols] = None         
    # stats.loc[idx] = None        
    return stats.T

def stats_periods_for_print2(st, 
                            yearlist = ['2019', '2020', '2021'],
                            nullifYTD = ["Return ann.",
                                         "Volatility ann.",
                                         'Risk Free Rate',
                                         "Sharpe",
                                         "Calmar",
                                         "Sortino",
                                         'Kelly fraction',
                                         'Skewness',
                                         'Kurtosis',
                                         'VaR (5%)',
                                         'CVaR (5%)',
                                         # 'Information Ratio (SPY)',
                                         # 'Alpha', 'Beta'
                                         ],
                            list_ratio = ["Sharpe","Calmar","Sortino", 
                                          'Skewness', 
                                          # 'Kurtosis', 
                                          'Kelly fraction',
                                          'Beta (to SPY)',
                                          # 'Tracking Error (SPY)','Information Ratio (SPY)'
                                          ],
                            drop_list = []

                            ):
    if isinstance(st,pd.Series): st = st.to_frame()    
    stats=st.copy()
    list_percent = stats.columns.drop(list_ratio).drop('Risk Free Rate')
    list_percent = list_percent.drop(['Start', 'End'])
    
    stats['Risk Free Rate'] = (st['Risk Free Rate']*100).apply(lambda x: "{:.2f}%".format(x) if not pd.isna(x) else '-')
 
    for col in list_percent:
        stats[col] = (st[col]*100).apply(lambda x: "{:.1f}%".format(x) if not pd.isna(x) else '-')

    for col in list_ratio:
        stats[col] = st[col].apply(lambda x: "{:.2f}".format(x) if not pd.isna(x) else '-')
        
    # #Making equal for a full calendar year  
    # stats["CAGR gross"].loc[stats.index.intersection(yearlist)] = stats["Cumulative Gross Return"].loc[stats.index.intersection(yearlist)] 

    cols = stats.columns.intersection(nullifYTD)
    idx = stats.index.intersection(['YTD', 'L3M', 'L1M'])
    stats.loc[idx, cols] = '-' #None         
        
    return stats.drop(drop_list, axis=1).T
    
def f_alpha(bt_all, row=['Alpha (p.a.)'], decimals=2):
    for col in bt_all.columns:
        if decimals==0:
            bt_all.loc[row,col]=(bt_all.loc[row,col]*100).astype(int).astype(str)+"%"
        else:
            bt_all.loc[row,col]=round((bt_all.loc[row,col]*100).astype(float),decimals).astype(str)+"%"            
    return bt_all

def f_beta(bt_all, row=['Beta', 'SMB', 'HML', 'RMW', 'CMA'], decimals=2):
    for col in bt_all.columns:
        bt_all.loc[row,col]=round(bt_all.loc[row,col].astype('float'),decimals)
    return bt_all

# Statists Table -> HTML
def stat_html(df, outputname, 
              size ='width: 18cm; height: 19cm;',
              table_width = '100%;', row_height = '100%;',
              col_space=None, col_formatter=None,
              resolution=200, isLastRow = True, 
              bcolor = '#ea6639;', isWriteHTML = True):
      #  Try letter instead of <style>
      # <link rel="stylesheet" type="text/css" href="style.css"> 

    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
    # create html_string with styles
#                              table-layout: fixed;

    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title>
      <style>
        .dataframe table    { margin-bottom: 1.4em; 
                             width: 100%; 
                             border-collapse: collapse;
                             border-spacing: 0;
                             font-family: "Avenir";
                             }
        .dataframe th       { font-weight: bold; text-align: left; 
                             padding: 5px 25px 5px 10px; 
                             border: 0px;}
        .dataframe tr > *:nth-child(1) { width:35%; }
        .dataframe tr:last-child{ border-bottom: 5px solid'''+bcolor+ '''}
        .dataframe thead th { background:''' +bcolor+''' 
                             padding: 5px 25px 5px 10px;}
        .dataframe td       { text-align: left; 
                             white-space: nowrap;
                             padding: 5px 25px 5px 10px; 
                             border: 0; }
        .dataframe th,td,caption { padding: 5px 25px 5px 10px; }
        .dataframe tbody tr:nth-child(even) td, 
        .dataframe tbody tr.even td { background: #d2d2d2; }
        .dataframe tbody tr:nth-child(even) th, 
        .dataframe tbody tr.even th { background: #d2d2d2; }
        .dataframe tfoot     { font-style: italic; }
        .dataframe caption   { background: #eee; }
                              
         </style>
      </head>
      <body>'''

    html_string += df.reset_index().to_html(index=False, col_space=col_space)
    #Remove space between cells
    html_string=html_string.replace('table border="1"',
                                    'table border="0" cellspacing="0"'
                                    )
    #Add last row with orange color
    if isLastRow:
        html_string=html_string.replace('</style>',
        '''.dataframe tbody tr:last-child td { background:'''+ bcolor+''' }
        .dataframe tbody tr:last-child th { background: '''+ bcolor+''' }
        </style>
        '''
        )  
        html_string=html_string.replace('</tbody>',
        '''<tr style="height: 25px; ">
              <th></th>'''+ 
              len(df.columns)*'<td></td>'+
              # <td></td>
              '''</tr>
              </tbody>'''
              )

    #Set columns width in proportions
    if col_formatter != None:    
        col_width=''
        for w in col_formatter:
            col_width+=('<col style="width:'+w+'">')
        html_string=html_string.replace('<thead>', '<colgroup>'+col_width+'<colgroup><thead>')
    
    #Finishing
    html_string +='''
    </body>
    </html>'''
    
    # OUTPUT AN HTML FILE
    with open(outputname+'.html', 'w') as f:
        f.write(html_string)
    
    from weasyprint.fonts import FontConfiguration
    font_config = FontConfiguration()
    
    from weasyprint import HTML, CSS
    css=CSS(string='''
            @page {
              background: white;''' + size + '''
              display: block;
              margin:  0;
              # margin-bottom: 0;
              }
            @media print {
              body, page {
                margin: 0;
                box-shadow: 0;
                }
            table { table-layout: fixed;
                   width:'''+table_width+'}'+
            '''
            th, td {font-family: "Avenir Next";
              font-size: 16px;}
            tr {height:''' +row_height+'}',
              font_config = font_config)
          
    HTML(outputname+'.html').write_png(outputname+'.png', 
                                       stylesheets=[css], 
                                       resolution=resolution,
                                       font_config = font_config)     
    if not isWriteHTML: 
        from os import remove
        remove(outputname+'.html')

    return 

def ff_html(df, outputname, size ='width: 28cm; height: 5cm;',
            resolution=200):
      #  Try letter instead of <style>
      # <link rel="stylesheet" type="text/css" href="style.css"> 

    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
    # create html_string with styles
    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title>
      <style>
        .dataframe table    { margin-bottom: 1.4em; 
                             width: 100%; 
                             border-collapse: collapse;
                             border-spacing: 0;
                             font-family: "Avenir";
                             }
        .dataframe th       { font-weight: bold; text-align: left; 
                             padding: 5px 25px 5px 10px; 
                             border: 0px;}
        .dataframe tr > *:nth-child(1) { width:35%; }
        .dataframe tr:last-child{ border-bottom: 5px solid #f0997a;}
        .dataframe thead th { background: #f0997a; 
                             padding: 5px 25px 5px 10px;}
        .dataframe td       { text-align: left; 
                             padding: 5px 25px 5px 10px; 
                             border: 0; }
        .dataframe th,td,caption { padding: 5px 25px 5px 10px; }
        .dataframe tbody tr:nth-child(even) td, 
        .dataframe tbody tr.even td { background: #d2d2d2; }
        .dataframe tbody tr:nth-child(even) th, 
        .dataframe tbody tr.even th { background: #d2d2d2; }
        .dataframe tbody tr:last-child td { background: #f0997a; }
        .dataframe tbody tr:last-child th { background: #f0997a; }
        .dataframe tfoot     { font-style: italic; }
        .dataframe caption   { background: #eee; }
                              
         </style>
      </head>
      <body>'''

    html_string += df.to_html()
    #Remove space between cells
    html_string=html_string.replace('table border="1"',
                                    'table border="0" cellspacing="0"'
                                    )
    #Add last row with orange color
    html_string=html_string.replace('</tbody>',
    '''<tr style="height: 25px; ">
          <th></th>'''+ 
          len(df.columns)*'<td></td>'+
          # <td></td>
          '''</tr>
          </tbody>'''
          )
  
    html_string +='''
    </body>
    </html>'''
    
    # OUTPUT AN HTML FILE
    with open(outputname+'.html', 'w') as f:
        f.write(html_string)
    
    from weasyprint import HTML, CSS
    css=CSS(string='''
            @page {
              background: white;''' + size + '''
              display: block;
              margin:  0;
              # margin-bottom: 0;
              }
            @media print {
              body, page {
                margin: 0;
                box-shadow: 0;
                }''')
    HTML(outputname+'.html').write_png(outputname+'.png', 
                                       stylesheets=[css], resolution=resolution) 
    return 

def camp_html(df, outputname, size ='width: 28cm; height: 5cm;',
              col_space=None, col_formatter=None, row_height = '45px;',
              isLastRow = True, resolution=200):
    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
    # create html_string with styles
    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title>
      <style>
        .dataframe table    { margin-bottom: 1.4em; 
                             width: 100%; 
                             border-collapse: collapse;
                             border-spacing: 0;
                             font-family: "Avenir";
                             }
        .dataframe th       { font-weight: bold; text-align: left; 
                             padding: 5px 25px 5px 10px; 
                             border: 0px;}
        .dataframe tr > *:nth-child(1) { width:35%; }
        .dataframe tr:last-child{ border-bottom: 5px solid #f0997a;}
        .dataframe thead th { background: #f0997a; 
                             padding: 5px 25px 5px 10px;}
        .dataframe td       { text-align: left; 
                             padding: 5px 25px 5px 10px; 
                             border: 0; }
        .dataframe th,td,caption { padding: 5px 25px 5px 10px; }
        .dataframe tbody tr:nth-child(even) td, 
        .dataframe tbody tr.even td { background: #d2d2d2; }
        .dataframe tbody tr:nth-child(even) th, 
        .dataframe tbody tr.even th { background: #d2d2d2; }
        .dataframe tfoot     { font-style: italic; }
        .dataframe caption   { background: #eee; }
                              
         </style>
      </head>
      <body>'''

    html_string += df.to_html(col_space=col_space)
    #Remove space between cells
    html_string=html_string.replace('table border="1"',
                                    'table border="0" cellspacing="0"'
                                    )
    #Add last row with orange color
    if isLastRow:
        html_string=html_string.replace('</style>',
        '''.dataframe tbody tr:last-child td { background: #f0997a; }
        .dataframe tbody tr:last-child th { background: #f0997a;}
        </style>
        '''
        )  
        html_string=html_string.replace('</tbody>',
        '''<tr style="height: 40px; ">
              <th></th>'''+ 
              len(df.columns)*'<td></td>'+
              # <td></td>
              '''</tr>
              </tbody>'''
              )
 
    #Set columns width in proportions
    if col_formatter != None:    
        col_width=''
        for w in col_formatter:
            col_width+=('<col style="width:'+w+'">')
        html_string=html_string.replace('<thead>', '<colgroup>'+col_width+'<colgroup><thead>')
    
    #Finishing    
    html_string +='''
    </body>
    </html>'''
    
    # OUTPUT AN HTML FILE
    with open(outputname+'.html', 'w') as f:
        f.write(html_string)
    
    from weasyprint.fonts import FontConfiguration
    font_config = FontConfiguration()
    
    from weasyprint import HTML, CSS
    css=CSS(string='''
            @page {
              background: white;''' + size + '''
              display: block;
              margin:  0;
              # margin-bottom: 0;
              }
            @media print {
              body, page {
                margin: 0;
                box-shadow: 0;
                }'''+
              '''
            th, td {font-family: "Avenir Next";
              font-size: 16px;}
            tr {height:''' +row_height+'}',
              font_config = font_config)
                
    HTML(outputname+'.html').write_png(outputname+'.png', 
                                       stylesheets=[css], 
                                       resolution=resolution,
                                       font_config = font_config) 
    return 

#%%
def factsheet_html(df, outputname, resolution = 200, 
                   isLastRow = True, isWriteHTML = True,
                   table_width= '1400px;', 
                   col_formatter = None, col_width = None,
                   row_height = '100%;', bcolor = '#ea6639;',
                   width='27.8cm;', height = '5.0cm;',font_size='18px'):
      #  Try letter instead of <style>
      # <link rel="stylesheet" type="text/css" href="style.css"> 

    import re
    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

    # Grow page height dynamically if the table is taller than the requested page
    n_rows = len(df) + 1
    height_match = re.search(r'([0-9]*\.?[0-9]+)cm', height)
    if height_match:
        height_cm = float(height_match.group(1))
        needed_height = max(height_cm, 1.6 + n_rows * 0.90)
        if needed_height > height_cm:
            height = f'{needed_height:.2f}cm;'

    # create html_string with styles
    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title>
      <style>
        .dataframe table    { margin-bottom: 1.4em; 
                             width: 100%; 
                             table-layout: fixed;
                             border-collapse: collapse;
                             border-spacing: 0;
                             font-family: "Avenir Next";
                             font-size:'''+font_size+''';
                             }
        .dataframe th       { font-weight: bold; text-align: center;
                             padding: 5px 6px;
                             border: 0px;
                             white-space: nowrap;
                             word-break: keep-all; }
        .dataframe tr:last-child{ border-bottom: 5px solid '''+bcolor+'''}
        .dataframe thead th { background: '''+bcolor+'''
                             padding: 5px 6px;}
        .dataframe td       { text-align: center;
                             padding: 5px 6px;
                             border: 0;
                             white-space: nowrap;
                             overflow-wrap: normal;
                             word-break: keep-all; }
        .dataframe th,td,caption { padding: 5px 6px; }
        .dataframe tbody tr:nth-child(even) td, 
        .dataframe tbody tr.even td { background: #d2d2d2; }
        .dataframe tbody tr:nth-child(even) th, 
        .dataframe tbody tr.even th { background: #d2d2d2; }
        .dataframe tfoot     { font-style: italic; }
        .dataframe caption   { background: #eee; }
        .dataframe thead { display: table-header-group; }
        .dataframe tbody { display: table-row-group; }
        .dataframe tr { page-break-inside: avoid; break-inside: avoid; }
                              
         </style>
      </head>
      <body>'''

    html_string += df.to_html()
    #Remove space between cells
    html_string=html_string.replace('table border="1"',
                                    'table border="0" cellspacing="0"'
                                    )
    
    if col_width != None : #Limit columns widht
        if isinstance(col_width, str):
            cw0=cw1=cw2=col_width                         
        else:
            cw0=str(col_width[0])
            cw1=str(col_width[1])
            cw2=str(col_width[2])
        html_string=html_string.replace('<style>',
            '<style>  .dataframe table    {width:'+cw0+
            'max-width:'+cw1+ 'min-width:'+cw2+'}')                         

    elif col_formatter != None: #Set columns width in proportions
        col_width=''
        for w in col_formatter:
            col_width+=('<col style="width:'+w+'">')
        html_string=html_string.replace('<thead>', '<colgroup>'+col_width+'<colgroup><thead>')
                                        
    #Add last row with orange color - #f0997a before 30-May 2022
    if isLastRow:
        html_string=html_string.replace('</style>',
        '''.dataframe tbody tr:last-child td { background: '''+bcolor+''' }
        .dataframe tbody tr:last-child th { background: '''+bcolor+''' }
        </style>
        ''')                                      
        html_string=html_string.replace('</tbody>',
        '''<tr style="height: 25px; ">
              <th></th>
              <td></td><td></td><td></td>
              <td></td><td></td><td></td>
              <td></td><td></td><td></td>
              <td></td><td></td><td></td>
              <td></td>
              </tr>
              </tbody>'''
                                          )        
    html_string +='''
    </body>
    </html>'''
        
    # OUTPUT AN HTML FILE
    with open(outputname+'.html', 'w') as f:
        f.write(html_string)
    
    
    from weasyprint.fonts import FontConfiguration
    font_config = FontConfiguration()
    
    from weasyprint import HTML, CSS

    cw0 = cw1 = cw2 = 'auto;'
    if col_width is not None:
        if isinstance(col_width, str):
            cw0 = cw1 = cw2 = col_width
        else:
            cw0 = str(col_width[0])
            cw1 = str(col_width[1])
            cw2 = str(col_width[2])

    css=CSS(string='''
            @page {
              background: white;
              width: '''+width+'height: ' +height+'''
              display: block;
              margin:  0;
              margin-bottom: 0;
              }
            @media print {
              body, page {
                margin: 0;
                box-shadow: 0;
                }
            @font-face {
              font-family: "Avenir Next";
              }
            table { table-layout: fixed;
                   width:'''+table_width+''';
                   page-break-inside: avoid;
                   break-inside: avoid; }
            tr {height: '+row_height+'; page-break-inside: avoid; }
            th, td {font-family: "Avenir Next";
              font-size: 16px;
              width:'+cw0+'; max-width:'+cw1+'; min-width:'+cw2+'; }
            ''',
            font_config = font_config)
    HTML(outputname+'.html').write_png(outputname+'.png', 
                                       stylesheets=[css], 
                                       resolution=resolution,
                                       font_config = font_config)
    if not isWriteHTML: 
        from os import remove
        remove(outputname+'.html')        
    return 
#%%
# ДИНАМИЧЕСКИЙ РАСЧЁТ - работает, но надо поправить цвета и размер таблицы
# def factsheet_html_v2(df, outputname, resolution = 200, 
#                    isLastRow = True, isWriteHTML = True,
#                    table_width= '1400px;', 
#                    col_formatter = None, col_width = None,
#                    row_height = '100%;', bcolor = '#ea6639;',
#                    width='27.8cm;', height = '5.0cm;'):
#       #  Try letter instead of <style>
#       # <link rel="stylesheet" type="text/css" href="style.css"> 
      
#     # === НОВОЕ: ДИНАМИЧЕСКИЙ РАСЧЁТ ===
#     import re
#     height_cm = float(re.findall(r'(\d+\.?\d*)', height)[0])  # 5.0 из '5.0cm;'
#     n_rows = len(df) + 1  # строки + header
#     header_h_cm = 0.4  # header толще
#     margins_cm = 0.4   # @page margins
    
#     row_height_cm = max(0.12, (height_cm - header_h_cm - margins_cm) / n_rows)
#     font_size_px = max(8, int(row_height_cm * 37.8 * 0.7))  # 1cm=37.8px, коэффициент сжатия
#     line_height = 1.0 + (row_height_cm * 0.1)  # 1.0-1.1
    
#     row_height_px = f'{row_height_cm * 37.8:.0f}px'
#     print(f"Расчёт: {n_rows}стр, row_h={row_height_cm:.2f}cm, font={font_size_px}px")  # Debug
    
#     pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
#     # create html_string with styles
#     html_string = '''<html><head><title>...</title>
#     <style>
#     .dataframe table { 
#         margin: 0 !important;
#         font-family: "Avenir Next";
#         font-size: '''+str(font_size_px)+'''px !important;  /* НОВОЕ */
#         table-layout: fixed;
#         border-collapse: collapse;
#         border-spacing: 0;
#         height: '''+row_height_px+''' !important;  /* Фикс всей таблицы */
#     }
#     .dataframe th { 
#         font-weight: bold; 
#         padding: 1px 2px !important;  /* Было 5px 25px */
#         height: '''+str(int(row_height_cm * 37.8 * 1.2))+'''px !important;  /* Header выше */
#         line-height: '''+str(line_height)+''' !important;
#         background: '''+bcolor+''';
#         border: 0;
#     }
#     .dataframe td { 
#         padding: 1px 2px !important;  /* Компактно */
#         height: '''+row_height_px+''' !important;
#         line-height: '''+str(line_height)+''' !important;
#         overflow: hidden;
#         white-space: nowrap;
#         text-overflow: ellipsis;
#         border: 0;
#     }
#     .dataframe tr { 
#         height: '''+row_height_px+''' !important;  /* Каждая строка */
#         page-break-inside: avoid;
#     }
#     </style></head><body>''' + df.to_html()


#     #Remove space between cells
#     html_string=html_string.replace('table border="1"',
#                                     'table border="0" cellspacing="0"'
#                                     )
    
#     if col_width != None : #Limit columns widht
#         if isinstance(col_width, str):
#             cw0=cw1=cw2=col_width                         
#         else:
#             cw0=str(col_width[0])
#             cw1=str(col_width[1])
#             cw2=str(col_width[2])
#         html_string=html_string.replace('<style>',
#             '<style>  .dataframe table    {width:'+cw0+
#             'max-width:'+cw1+ 'min-width:'+cw2+'}')                         

#     elif col_formatter != None: #Set columns width in proportions
#         col_width=''
#         for w in col_formatter:
#             col_width+=('<col style="width:'+w+'">')
#         html_string=html_string.replace('<thead>', '<colgroup>'+col_width+'<colgroup><thead>')
                                        
#     #Add last row with orange color - #f0997a before 30-May 2022
#     if isLastRow:
#         html_string=html_string.replace('</style>',
#         '''.dataframe tbody tr:last-child td { background: '''+bcolor+''' }
#         .dataframe tbody tr:last-child th { background: '''+bcolor+''' }
#         </style>
#         ''')                                      
#         html_string=html_string.replace('</tbody>',
#         '''<tr style="height: 25px; ">
#               <th></th>
#               <td></td><td></td><td></td>
#               <td></td><td></td><td></td>
#               <td></td><td></td><td></td>
#               <td></td><td></td><td></td>
#               <td></td>
#               </tr>
#               </tbody>'''
#                                           )        
#     html_string +='''
#     </body>
#     </html>'''
        
#     # OUTPUT AN HTML FILE
#     with open(outputname+'.html', 'w') as f:
#         f.write(html_string)
    
    
#     from weasyprint.fonts import FontConfiguration
#     font_config = FontConfiguration()
    
#     from weasyprint import HTML, CSS
    
#     css=CSS(string='''
#             @page { 
#                 size: '''+width[:-1]+''' '''+height[:-1]+''';
#                 margin: 0.2cm !important;
#             }
#             table { 
#                 max-height: '''+height+''';
#                 page-break-inside: avoid !important;
#                 font-size: '''+str(font_size_px)+'''px !important;
#             }
#             tr, th, td { 
#                 height: '''+row_height_px+''' !important;
#                 padding: 1px 2px !important;
#                 line-height: '''+str(line_height)+''' !important;
#                 font-size: '''+str(font_size_px)+'''px !important;
#             }
#             ''', font_config=font_config)

#     HTML(outputname+'.html').write_png(outputname+'.png', 
#                                        stylesheets=[css], 
#                                        resolution=resolution,
#                                        font_config = font_config)
#     if not isWriteHTML: 
#         from os import remove
#         remove(outputname+'.html')        
#     return 
#%%
def f_fsnet(df, pct='%'):
    df.fillna(' ', inplace=True)
    df1=df.copy()    
    for row in df.index:
        for col in df.columns:
            if df.loc[row,col]!= ' ':
                df1.loc[row,col]=("{0:.2f}"+pct).format(df.loc[row,col] * 100)
    return df1

def format_pct_axis(x, _):
    x *= 100  # lambda x, loc: "{:,}%".format(int(x * 100))
    if x >= 1e12:
        res = '%1.1fT%%' % (x * 1e-12)
        return res.replace('.0T%', 'T%')
    if x >= 1e9:
        res = '%1.1fB%%' % (x * 1e-9)
        return res.replace('.0B%', 'B%')
    if x >= 1e6:
        res = '%1.1fM%%' % (x * 1e-6)
        return res.replace('.0M%', 'M%')
    if x >= 1e3:
        res = '%1.1fK%%' % (x * 1e-3)
        return res.replace('.0K%', 'K%')
    res = '%1.0f%%' % x
    return res.replace('.0%', '%')

def plot_longest_drawdowns(returns, dicclrs, 
                           criteria='days', #or 'max drawdown'
                           isOffset = False, #to change the 1st day of the month to the last day of the previous one
                           periods=5, lw=1.5,
                           fontname='Avenir Next', grayscale=False,
                           # log_scale=False, 
                           yscale = 'linear',
                           figsize=(10, 6), ylabel=True,
                           ytext = "Cumulative Returns",
                           subtitle=True, compounded=True,
                           savefig=None, show=True, save_dd=None,
                           lang='EN',
                           ):
    #colors = ['#348dc1', '#003366', 'red'] #inially
    colors = [dicclrs['arquant'], '#b5583c', dicclrs['background']] #ARQuant, Brown, Light Peach
    if grayscale: colors = ['#000000'] * 3
    
    import matplotlib.pyplot as plt
    import matplotlib.dates as _mdates
    import quantstats.stats as _stats
    from matplotlib.ticker import (FormatStrFormatter as _FormatStrFormatter,
                                   FuncFormatter as _FuncFormatter)

    dd = _stats.to_drawdown_series(returns.fillna(0))
    dddf = _stats.drawdown_details(dd.squeeze())
    
    if isOffset: #change 1st day of the month to the last day of previous month
        dddf1 = pd.to_datetime(dddf['end']) - pd.offsets.MonthEnd(1) 
        dddf['end'] = dddf1.dt.strftime('%Y-%m-%d')
        
    if criteria == 'days':
        longest_dd = dddf.sort_values(by='days', ascending=False, 
                                      kind='mergesort')[:periods]
    else:
        longest_dd = dddf.sort_values(by='max drawdown', ascending=True, 
                                      kind='mergesort')[:periods]
    
    longest_dd.reset_index().to_csv(save_dd)
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # fig.suptitle("Top %.0f Drawdown Periods\n" %
    #               periods, y=1.1, x=0.25, 
    #               fontweight="normal", fontname=fontname,
    #               fontsize=18, color=dicclrs['plotname'])
    if subtitle:
        # plt.rc('text', usetex=True)
        # plt.title(r'\fontsize{30pt}{3em}\selectfont{}{Mean WRFv3.5 LHF\r}{\fontsize{18pt}{3em}\selectfont{}(September 16 - October 30, 2012)}')
        if criteria == 'days':
            if lang=='EN':
                _title="Top %.0f Longest Drawdown Periods\n"
            else:
                _title="%.0f самых длительных периодов просадки\n"
            plt.title(_title %periods, loc='left',
                      fontweight="medium", fontname=fontname,
                      fontsize=18, color=dicclrs['plotname'])
        else :
            if lang=='EN':
                _title="Top %.0f Max Drawdowns \n"
            else:
                _title="%.0f самых больших просадок\n"
            plt.title(_title %periods, loc='left',
                      fontweight="medium", fontname=fontname,
                      fontsize=18, color=dicclrs['plotname'])

        if lang=='EN':        
            dates= "  %s - %s " %(
                returns.index.date[:1][0].strftime('%b \'%y'),
                returns.index.date[-1:][0].strftime('%b \'%y') #'%e %b \'%y'
                )
            # plt.title(dates, loc='center')
            plt.text(0.57, 0.97, dates, 
                      fontdict=dict(fontweight='normal', fontname=fontname,
                      fontsize=14, color=dicclrs['dates']),
                      transform=fig.transFigure
                      )
        else:
            import locale
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
            dates= "  %s - %s " %(
                returns.index.date[:1][0].strftime('%b\'%y'),
                returns.index.date[-1:][0].strftime('%b\'%y') #'%e %b \'%y'
                )
            # plt.title(dates, loc='center')
            plt.text(.73, 0.96, dates, 
                      fontdict=dict(fontweight='normal', fontname=fontname,
                      fontsize=14, color=dicclrs['dates']),
                      transform=fig.transFigure
                      )

    #Plot the line
    fig.set_facecolor('white')
    ax.set_facecolor('white')
    series = _stats.compsum(returns) if compounded else returns.cumsum()
    ax.plot(series, lw=lw, label="Backtest", color=colors[0])
    #PLot spans
    highlight = 'black' if grayscale else dicclrs['background'] # it was initially 'red'
    for _, row in longest_dd.iterrows():
        ax.axvspan(*_mdates.datestr2num([str(row['start']), str(row['end'])]),
                   color=highlight, alpha=.5)
    ## Horizontal line for 0%
    ax.axhline(0, ls="-", lw=1, color="#000000", zorder=2)
    
    ## X -axis
    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()
    # x=returns.index.astype(str).values
    
    #Exclude days from index
    ret2 = returns.reset_index()
    ret2[ret2.columns[0]] = ret2[ret2.columns[0]].apply(lambda x: x.strftime('%Y-%m'))
    ret2.set_index(ret2.columns[0], inplace=True)

    x_ticks=f_xticks(ret2) #mapping ticks
    plt.xticks(x_ticks) # setting ticks
    ax.set_xticklabels(x_ticks)
    fig.autofmt_xdate(bottom=0.2, rotation=0, ha='center', which='both')
    # use a more precise date string for the x axis locations in the toolbar    
    ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_tick_params(labelsize=8, color=dicclrs['dates'])
    
    ## Y -axis
    # plt.yscale("symlog" if log_scale else "linear")
    # if yscale != 'linear': ax1.set_yscale(yscale)
    # else: ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_yscale(yscale)
    if ylabel:
        ax.set_ylabel(ytext, fontname=fontname,
                      fontweight='medium', fontsize=12, color="black")
        ax.yaxis.set_label_coords(-.06, .5)

    ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
    # ax.yaxis.set_major_formatter(plt.FuncFormatter(
    #     lambda x, loc: "{:,}%".format(int(x*100))))

    ax.yaxis.set_tick_params(labelsize=8)

    try:
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass

    try:
        fig.tight_layout()
    except Exception:
        pass
    
    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig, dpi=300)
        else:
            plt.savefig(savefig, dpi=300)

    if show:
        plt.show(block=False)

    plt.close()

    if not show:
        return fig

    return None
'''
def plot_longest_drawdowns_monthly(returns, dicclrs, periods=5, lw=1.5,
                           fontname='Avenir Next', grayscale=False,
                           # log_scale=False, 
                           yscale = 'linear',
                           figsize=(10, 6), ylabel=True,
                           ytext = "Cumulative Returns",
                           subtitle=True, compounded=True,
                           savefig=None, show=True):
    #colors = ['#348dc1', '#003366', 'red'] #inially
    colors = [dicclrs['arquant'], '#b5583c', dicclrs['background']] #ARQuant, Brown, Light Peach
    if grayscale: colors = ['#000000'] * 3
    
    import matplotlib.pyplot as plt
    import matplotlib.dates as _mdates
    import quantstats.stats as _stats
    from matplotlib.ticker import (FormatStrFormatter as _FormatStrFormatter,
                                   FuncFormatter as _FuncFormatter)

    dd = _stats.to_drawdown_series(returns.fillna(0))
    
    from Slides_analytic_function import drawdown_details_monthly
    dddf = drawdown_details_monthly(dd)
    longest_dd = dddf.sort_values(by='days', ascending=False, 
                                  kind='mergesort')[:periods]

    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # fig.suptitle("Top %.0f Drawdown Periods\n" %
    #               periods, y=1.1, x=0.25, 
    #               fontweight="normal", fontname=fontname,
    #               fontsize=18, color=dicclrs['plotname'])
    if subtitle:
        # plt.rc('text', usetex=True)
        # plt.title(r'\fontsize{30pt}{3em}\selectfont{}{Mean WRFv3.5 LHF\r}{\fontsize{18pt}{3em}\selectfont{}(September 16 - October 30, 2012)}')

        plt.title("Top %.0f Drawdown Periods\n" %periods, loc='left',
                  fontweight="medium", fontname=fontname,
                  fontsize=18, color=dicclrs['plotname'])
        
        dates= "  %s - %s " %(
            returns.index.date[:1][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y')
            )
        # plt.title(dates, loc='center')
        plt.text(0.45, 0.97, dates, 
                  fontdict=dict(fontweight='normal', fontname=fontname,
                  fontsize=14, color=dicclrs['dates']),
                  transform=fig.transFigure
                  )
    #Plot the line
    fig.set_facecolor('white')
    ax.set_facecolor('white')
    series = _stats.compsum(returns) if compounded else returns.cumsum()
    ax.plot(series, lw=lw, label="Backtest", color=colors[0])
    #PLot spans
    highlight = 'black' if grayscale else dicclrs['background'] # it was initially 'red'
    for _, row in longest_dd.iterrows():
        ax.axvspan(*_mdates.datestr2num([str(row['start']), str(row['end'])]),
                   color=highlight, alpha=.5)
    ## Horizontal line for 0%
    ax.axhline(0, ls="-", lw=1, color="#000000", zorder=2)
    
    ## X -axis
    # rotate and align the tick labels so they look better
    # fig.autofmt_xdate()
    fig.autofmt_xdate(bottom=0.2, rotation=0, ha='center', which='both')
    # use a more precise date string for the x axis locations in the toolbar    
    ax.fmt_xdata = _mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_tick_params(labelsize=8, color=dicclrs['dates'])
    
    ## Y -axis
    # plt.yscale("symlog" if log_scale else "linear")
    # if yscale != 'linear': ax1.set_yscale(yscale)
    # else: ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_yscale(yscale)
    if ylabel:
        ax.set_ylabel(ytext, fontname=fontname,
                      fontweight='medium', fontsize=12, color="black")
        ax.yaxis.set_label_coords(-.06, .5)

    ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
    # ax.yaxis.set_major_formatter(plt.FuncFormatter(
    #     lambda x, loc: "{:,}%".format(int(x*100))))

    ax.yaxis.set_tick_params(labelsize=8)

    try:
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass

    try:
        fig.tight_layout()
    except Exception:
        pass
    
    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig, dpi=300)
        else:
            plt.savefig(savefig, dpi=300)

    if show:
        plt.show(block=False)

    plt.close()

    if not show:
        return fig

    return None
'''
def f_xticks(dfs_sim1):
    import numpy as np
    long=dfs_sim1.shape[0]
    if long in range(1,7): step=1
    elif long in range(7,13): step=2
    elif long in range(13,25): step=4
    elif long in range(25,37): step=6
    elif long in range(37,49): step=8    
    else: step=long//8
    # filtering dates for ticks
    if step ==1:
        x_ticks=dfs_sim1.index.astype(str).values
    elif step in range(2,6):
        x_ticks=dfs_sim1.iloc[np.arange(1,long, step)].index.astype(str).values
    else:
        x_ticks=dfs_sim1.iloc[np.linspace(0,long-1, step)].index.astype(str).values
    return x_ticks

# plotname='AVESA- Andrew vs Indexies since Inception'
def plot_for_print(dfs_sim1, dicclrs, datadir='Traders/Data/', 
                   plotname='ARQuant-',
                   ytext = "Cumulative Log-Returns",
                   yscale = 'linear', base = 100,
                   figsize=(10,6),
                   c=['b','r','g', 'm', 'y', 'c', 'k'],
                   marker=['o','^', (8,2,0), 'v', '*', '+', 'd'],
                   ls=['-','--','-.', ':', '--','-.', ':'],
                   fontname='Avenir Next', ylabel=True,
                   subtitle=True, show=True, isGrid = True,
                   lang='EN',
                   ):
    import matplotlib.ticker as mtick
    import matplotlib.pyplot as plt
    import matplotlib.dates as _mdates #DateFormatter, AutoDateLocator, AutoDateFormatter, datestr2num
    from matplotlib.ticker import (FormatStrFormatter as _FormatStrFormatter,
                                    FuncFormatter as _FuncFormatter)
    
    dfs_sim2=pd.concat([pd.DataFrame([ [1.,] * dfs_sim1.shape[1] ],
                                     columns=dfs_sim1.columns),
                        dfs_sim1], 
                       axis=0)
    x=dfs_sim2.index.astype(str).values
    # x = _mdates.datestr2num(dfs_sim1.index.astype(str).values)    

    y=dfs_sim2 * base
    ymin=y.min(axis=0).min()
    ymax=y.max(axis=0).max()
    ymax = ymax*1.02 if ymax > 0. else ymax*0.98
    ymin = ymin*1.02 if ymin < 0. else ymin*0.98
        
    fig1, ax1 = plt.subplots(figsize=figsize)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    fig1.set_facecolor('white')
    ax1.set_facecolor('white')

    for col in range(len(y.columns)):    
        ax1.plot(x, y.iloc[:,col], c=c[col], marker=marker[col], ls=ls[col],label=y.columns[col])

    # Y-axis
    if isGrid: 
        ax1.grid(axis='both', linestyle='-', linewidth=0.25)
        ax1.axhline(0, color='black', lw=1)
    ax1.set_yscale(yscale)
    # ax1.autoscale(enable=True, axis='y')
    ax1.set_ylim(ymin, ymax)
    ax1.yaxis.set_tick_params(labelsize=8, which='both')
    if ylabel:
        # plt.ylabel(ytext+'\n ', fontsize=13, fontweight='medium')
        ax1.set_ylabel(ytext+'\n ', fontname=fontname,
                      fontweight='medium', fontsize=12, color="black")
        ax1.yaxis.set_label_coords(-.06, .5)
    #X-axis
    x_ticks=f_xticks(dfs_sim1)
    plt.xticks(x_ticks) # setting ticks
    ax1.set_xticklabels(x_ticks) # setting labels for ticks
    # Positioning ticks
    fig1.autofmt_xdate(bottom=0.2, rotation=0, ha='center', which='both')
    # Sizing and coloring ticks
    ax1.xaxis.set_tick_params(labelsize=8, color=dicclrs['dates'])
    
    ax1.legend(loc='upper left')
    
    if subtitle:
    # plt.rc('text', usetex=True)
    # plt.title(r'\fontsize{30pt}{3em}\selectfont{}{Mean WRFv3.5 LHF\r}{\fontsize{18pt}{3em}\selectfont{}(September 16 - October 30, 2012)}')
        if lang=='EN':
            plt.title("ARQuant Strategy vs Benchmarks", loc='left',
                      fontweight="medium", fontname=fontname,
                      fontsize=18, color=dicclrs['plotname'])
            
            dates= "  %s - %s " %(
                # dfs_sim1.index.to_timestamp(how='start').date[:1][0].strftime('%e %b \'%y'),
                # dfs_sim1.index.to_timestamp(how='end').date[-1:][0].strftime('%e %b \'%y')
                dfs_sim1.index.to_timestamp(how='start').date[:1][0].strftime('%B \'%y'),
                dfs_sim1.index.to_timestamp(how='end').date[-1:][0].strftime('%B \'%y')
                )
            # plt.title(dates, loc='center')
            plt.text(0.58, 0.92, dates, 
                      fontdict=dict(fontweight='normal', fontname=fontname,
                      fontsize=14, color=dicclrs['dates']),
                      transform=fig1.transFigure
                      )
        else:
            import locale
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
            
            plt.title("100%ARQuant+30%SPY и индекс рынка США", loc='left',
                      fontweight="medium", fontname=fontname,
                      fontsize=17, color=dicclrs['plotname'])
            
            dates= "  %s - %s " %(
                # dfs_sim1.index.to_timestamp(how='start').date[:1][0].strftime('%e %b \'%y'),
                # dfs_sim1.index.to_timestamp(how='end').date[-1:][0].strftime('%e %b \'%y')
                dfs_sim1.index.to_timestamp(how='start').date[:1][0].strftime('%b\'%y'),
                dfs_sim1.index.to_timestamp(how='end').date[-1:][0].strftime('%b\'%y')
                )
            # plt.title(dates, loc='center')
            plt.text(0.73, 0.92, dates, 
                      fontdict=dict(fontweight='normal', fontname=fontname,
                      fontsize=14, color=dicclrs['dates']),
                      transform=fig1.transFigure
                      )
            
    # plt.savefig(datadir+plotname+'.png',dpi=400)
    figure = ax1.get_figure()
    figure.savefig(datadir+plotname+'.png', dpi=400, bbox_inches='tight')
    if show: plt.show()
    return

def plot_bar_line(dfs_sim1, dicclrs, datadir='Traders/Data/', 
                   plotname='ARQuant-',
                   ytext = "Returns",
                   yscale = 'linear', 
                   base = 1,
                   figsize=(10,6),
                   c=['b','r','g', 'm', 'y', 'c', 'k'],
                   marker=['o','^', (8,2,0), 'v', '*', '+', 'd'],
                   ls=['-','--','-.', ':', '--','-.', ':'],
                   fontname='Avenir Next', ylabel=True,
                   subtitle=True, show=True, isGrid=True
                   ):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    
    y=dfs_sim1.copy()
    if y.columns[0] == 'Daily':
        xstring = '%d'
        xlabel = y.index[-1].strftime('%B')
        tstring = '%d \ %B'
    else: 
        xstring = '%b-%y'
        # xlabel = y.index[-1].strftime('%Y')
        xlabel=''
        tstring = '%B \'%y'
    
    x=dfs_sim1.index.strftime(xstring)

    fig1, ax1 = plt.subplots(figsize=figsize)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    fig1.set_facecolor('white')
    ax1.set_facecolor('white')

    for col in range(len(y.columns)):
        if 'Cum' not in y.columns[col]:
            ax1.bar(x, y.iloc[:,col], 
                    color= '#ea6639', # - from EG maket, '#f0997a' - from table header, #ea6639' - from dicclrs, 
                    ls=ls[col],label=y.columns[col])
        else:
            ax1.plot(x, y.iloc[:,col], color='#58595A', marker=marker[col], ls=ls[col],label=y.columns[col])

    # Y-axis
    if isGrid: 
        ax1.grid(axis='both', linestyle='-', linewidth=0.25)
        ax1.axhline(0, color='black', lw=1)
    ax1.set_yscale(yscale)
    # start, end = ax1.get_ylim()
    # import numpy as np
    # ax1.yaxis.set_ticks(np.arange(start, end, 5))
    ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:.1f}'))
    ax1.yaxis.set_tick_params(labelsize=8, which='both')
    if ylabel:
        ax1.set_ylabel(ytext+'\n ', fontname=fontname,
                      fontweight='medium', fontsize=12, color="black")
        ax1.yaxis.set_label_coords(-.06, .5)
    
    #X-axis
    x_ticks=x
    plt.xticks(x_ticks) # setting ticks
    ax1.set_xticklabels(x_ticks) # setting labels for ticks
    # Positioning ticks
    fig1.autofmt_xdate(bottom=0.2, rotation=0, ha='center', which='both')
    # Sizing and coloring ticks
    ax1.xaxis.set_tick_params(labelsize=8, color=dicclrs['dates'])
    ax1.set_xlabel(xlabel, fontsize=10, color="black")
    # ax1.grid(axis='x', linestyle=':', linewidth=1)
    
    ax1.legend()
    
    if subtitle:
        plt.title("Monthly and Cumulative Returns", loc='left',
                  fontweight="medium", fontname=fontname,
                  fontsize=18, color='black')
        
        dates= "  %s - %s " %(
            dfs_sim1.index[0].strftime(tstring),
            dfs_sim1.index[-1].strftime(tstring)
            )
        plt.text(0.56, 0.92, dates, 
                  fontdict=dict(fontweight='normal', fontname=fontname,
                  fontsize=14, color=dicclrs['dates']),
                  transform=fig1.transFigure
                  )
    figure = ax1.get_figure()
    figure.savefig(datadir+plotname+'.png', dpi=400, bbox_inches='tight')
    if show: plt.show()
    return

def plot_distribution(returns, dicclrs,                      
                      figsize=(10, 6),
                      fontname='Avenir Next', grayscale=False, 
                      ylabel=True, ytext = 'Monthly Return',
                      subtitle=True, compounded=False,
                      savefig=None, show=True):
    import matplotlib.pyplot as _plt
    import matplotlib.dates as _mdates
    import quantstats.stats as _stats
    from matplotlib.ticker import (
    FormatStrFormatter as _FormatStrFormatter,
    FuncFormatter as _FuncFormatter)
    import pandas as _pd
    import seaborn as _sns
    
    colors = [dicclrs['arquant'], '#b5583c', dicclrs['background']] #ARQuant, Brown, Light Peach
    # if grayscale: colors = ['#000000'] * 3

    if grayscale:
        colors = ['#f9f9f9', '#dddddd', '#bbbbbb', '#999999', '#808080']
    # colors, ls, alpha = _get_colors(grayscale)

    port = _pd.DataFrame(returns.fillna(0))

    # port.columns = ['Daily']

    # apply_fnc = _stats.comp if compounded else _np.sum

    # port['Weekly'] = port['Daily'].resample(
    #     'W-MON').apply(apply_fnc)
    # port['Weekly'].ffill(inplace=True)

    # port['Monthly'] = port['Daily'].resample(
    #     'M').apply(apply_fnc)
    # port['Monthly'].ffill(inplace=True)

    # port['Quarterly'] = port['Daily'].resample(
    #     'Q').apply(apply_fnc)
    # port['Quarterly'].ffill(inplace=True)

    # port['Yearly'] = port['Daily'].resample(
    #     'A').apply(apply_fnc)
    # port['Yearly'].ffill(inplace=True)

    fig, ax = _plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.suptitle("Return Quantiles\n", y=.99,
                 fontweight="bold", fontname=fontname,
                 fontsize=14, color="black")

    if subtitle:
        ax.set_title("\n%s - %s                   " % (
            returns.index.to_timestamp(how='start').date[:1][0].strftime('%e %b \'%y'),
            returns.index.to_timestamp(how='end').date[-1:][0].strftime('%e %b \'%y')
        ), fontsize=12, color='gray')

    fig.set_facecolor('white')
    ax.set_facecolor('white')

    _sns.boxplot(data=port, ax=ax, palette=tuple(colors[:5]))
    # _sns.violinplot(data=port, ax=ax, palette=tuple(colors[:5]))

    ax.yaxis.set_major_formatter(_plt.FuncFormatter(
        lambda x, loc: "{:,}%".format(int(x*100))))

    # if ylabel:
    #     ax.set_ylabel('Returns', fontname=fontname,
    #                   fontweight='bold', fontsize=12, color="black")
    #     ax.yaxis.set_label_coords(-.1, .5)
    #     ax.yaxis.set_label_coords(-.06, .5)
    if ylabel:
        ax.set_ylabel(ytext+'\n ', fontname=fontname,
                      fontweight='medium', fontsize=12, color="black")
        ax.yaxis.set_label_coords(-.06, .5)
        
    fig.autofmt_xdate()

    try:
        _plt.subplots_adjust(hspace=0)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig, dpi=300)
        else:
            _plt.savefig(savefig, dpi=300)

    if show:
        _plt.show(block=False)

    _plt.close()

    if not show:
        return fig

    return None


def regime_plot(vix, lower=16.5, upper =  19.5, ylabel='VIX', figsize=(10,6)):

    # Each term inside parentheses is [False, True, ...]
    # Both terms must be True element-wise for a trigger to occur
    blue = (vix < upper) & (vix.shift() >= upper)
    yellow = (vix < lower) & (vix.shift() >= lower)
    green = (vix > upper) & (vix.shift() <= upper)
    red = (vix > lower) & (vix.shift() <= lower)
    
    mapping = {1: 'blue', 2: 'yellow', 3: 'green', 4: 'red'}
    
    indicator = pd.Series(np.where(blue, 1., np.where(yellow, 2.,
                          np.where(green, 3., np.where(red, 4., np.nan)))),
                          index=vix.index).ffill().map(mapping).dropna()
    vix = vix.reindex(indicator.index)

    import matplotlib.pyplot as plt        
    fig, ax = plt.subplots(figsize=figsize)
    plt.scatter(vix.index, vix, c=indicator, marker='.')
    plt.title(ylabel+' regime')
    plt.ylabel(ylabel)
    
    # x_ticks=f_xticks(vix)
    # setting labels for ticks
    # ax.set_xticklabels(x_ticks) 
    import matplotlib.dates as mdates
    # all your fancy plotting code
    locator=mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))

    # Positioning ticks
    fig.autofmt_xdate(bottom=0.2, rotation=0, ha='center', which='both')
    # Sizing and coloring ticks
    ax.xaxis.set_tick_params(labelsize=8, color=dicclrs['dates'])
    plt.show()
    return

# def period_index(df, period_list):
#     periods={}
#     for per in period_list:
#         if per=='Inception':    periods[per]=df.index
#         elif per=='YTD':        periods[per]=df.loc[str(dt.date.today().year)]
#         elif per[0]=='2':       periods[per]=df.loc[per].index
#         elif per[0]=='L':
#             if isinstance(df.index, pd.PeriodIndex): 
#                 p=per[1:]
#                 p=int(p[:-1])
#                 periods[per]=df.index[-p:]
#             else: periods[per]=df.last(per[1:]).index
#         else: continue
#     return periods

def read_csv(datadir, filename='AVESA_Group_Ltd_U3577443_history.csv'):
    andrew_ret=pd.read_csv(datadir+filename, engine='python')
    andrew_ret['Date']=pd.to_datetime(andrew_ret['Date'], 
                                  infer_datetime_format='%Y-%m-%d')
    andrew_ret.set_index(['Date'], inplace=True)
    return andrew_ret