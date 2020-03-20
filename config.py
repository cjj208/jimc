# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:01:01 2019

@author: JimchanChen
"""
'''
0 5分钟K线 1 15分钟K线 
 2 30分钟K线 3 1小时K线 
 4 日K线 5 周K线
 6 月K线 7 1分钟
 8 1分钟K线 9 日K线
 10 季K线 11 年K线
 count -> 用户要请求的 K 线数目，最大值为 800
 '''
category = 0  #设置周期
mail_addr_1 = "26201084@qq.com"
mail_addr_2 = "" #如果需要抄送则在冒号里填入邮箱地址
categorycount = 1000  #取多少根K线
dc_count = 10       #唐奇安通道参数

st_period_fast =10
st_mult_fast =2
st_period_slow =20
st_mult_slow =6

cfstock = [  
 {'marketid': 0,
'code':'000025',
'stockname': '特力A'},
  
 {'marketid': 0,
'code':'002565',
'stockname': '顺灏股份'},
 {'marketid': 1,
'code':'600175',
'stockname': '美都能源'},
]
        
cfqihuo = [  
{'marketid':47,
'code':'IF300',
'stockname':'沪深300'},
 
{'marketid':47,
'code':'IFL8',
'stockname':'沪深主连'},

{'marketid': 28,
'code':'APL8',
'stockname': '苹果主连'},
  
{'marketid': 30,
'code':'RBL8',
'stockname': '螺纹主连'},

{'marketid': 30,
'code':'SPL8',
'stockname': '纸桨主连'},
 
{'marketid':28,
'code':'CJ1912',
'stockname':'红枣主连'},

{'marketid':30,
'code':'AUL8',
'stockname':'黄金主连'},
  
{'marketid':30,
'code':'CUL8',
'stockname':'沪铜主连'},
 
]

