# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 13:55:14 2017

@author: dell
"""

import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys

if __name__ == "__main__":

    startdate = '2014-01-01'
    enddate = '2017-08-31'
    codelist = ['160706', '161017', '040008', '110022', '110011', '020003', '160211']

    # Read command line arguments
    if len(sys.argv) > 1:
        startdate = sys.argv[1]
        if len(sys.argv) > 2:
            enddate = sys.argv[2]
            if len(sys.argv) > 3:
                del codelist[:]
                codelist = sys.argv[3:]

    # portfolio weights
    weightlist = [1/len(codelist) for i in codelist]

    print(startdate, enddate, codelist)

    # Generate URLs from start date, end date and code list
    urls = ['http://data.funds.hexun.com/outxml/detail/openfundnetvalue.aspx?fundcode='
          +fundcode+'&startdate='+startdate+'&enddate='+enddate
          for fundcode in codelist]
    namelist = []
    timeserieslist = []

    # Create time series from XML content at the URLs
    for url in urls:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read()
        tree = ET.fromstring(data)
        
        # Append dates and net values to the lists respectively
        datelist = []
        valuelist = []
        for child in tree:
            if child.tag == 'Data':
                datelist.append(datetime.strptime(child.find('fld_enddate').text, '%Y-%m-%d'))
#                valuelist.append(float(child.find('fld_unitnetvalue').text))
                valuelist.append(float(child.find('fld_netvalue').text))

        # Create a time series from the lists
        valuelist = [i/valuelist[-1] for i in reversed(valuelist)]
        datelist = list(reversed(datelist))
        fundname = tree.find('fundcode').text + ' ' + tree.find('fundname').text
        namelist.append(fundname)
        x = np.array(datelist)
        y = np.array(valuelist)
        ts = pd.Series(y, index=x, name=fundname)
        timeserieslist.append(ts)

    # Concatenate time series
    df = pd.concat(timeserieslist, axis=1)

    # The portfolio is a weighted sum of the funds
    df2 = df.copy()
    for i in range(len(weightlist)):
        df2[namelist[i]] = df2[namelist[i]] * weightlist[i]

    portfolioname = 'portfolio'
    df[portfolioname] = df2.sum(axis=1, skipna=False)  

    # Calculate risk-adjusted return
    std = df.std()
    retstd = (df.iloc[[-1]] - 1) / std
    risk_adjusted_return = df.iloc[[0,-1]].append(std.rename('standard deviation')).append(retstd.iloc[0].rename('return/standard deviation'))
    print(risk_adjusted_return)

    # Plot funds and the portfolio
    plt.plot(df)
    myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
    namelist.append(portfolioname+' '+','.join(["{:.2f}".format(i) for i in weightlist]))
    plt.legend(namelist, prop=myfont)
    plt.grid()
    plt.show()
