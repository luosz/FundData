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

# 开始日期
startdate = '2012-08-01'
# 结束日期
enddate = '2017-08-31'
# 代码列表
codelist = ['160213', '160716', '110007']
# 组合权重
weightlist = [1/3, 1/3, 1/3]

urls=['http://data.funds.hexun.com/outxml/detail/openfundnetvalue.aspx?fundcode='
      +fundcode+'&startdate='+startdate+'&enddate='+enddate
      for fundcode in codelist]
namelist = []
timeserieslist = []

for url in urls:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    tree = ET.fromstring(data)
    datelist = []
    valuelist = []
    
    for child in tree:
        if child.tag == 'Data':
            datelist.append(datetime.strptime(child.find('fld_enddate').text, '%Y-%m-%d'))
            valuelist.append(float(child.find('fld_netvalue').text))
    
    valuelist = [i/valuelist[-1] for i in reversed(valuelist)]
    datelist = list(reversed(datelist))
    codename = tree.find('fundcode').text + ' ' + tree.find('fundname').text
    namelist.append(codename)
    print(codename, "{:.2f}".format(valuelist[-1]))
    x = np.array(datelist)
    y = np.array(valuelist)
    ts = pd.Series(y, index=x, name=codename)
    timeserieslist.append(ts)
    plt.plot(x, y)

df = pd.concat(timeserieslist, axis=1)
for i in range(len(weightlist)):
    df[namelist[i]] = df[namelist[i]] * weightlist[i]

portfolioname = 'portfolio'
df[portfolioname] = df.sum(axis=1, skipna=False)
plt.plot(df[portfolioname])
myfont = fm.FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
namelist.append(portfolioname+' '+', '.join(["{:.2f}".format(i) for i in weightlist]))
plt.legend(namelist, prop=myfont)
plt.grid()
plt.show()
