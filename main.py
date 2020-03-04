# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:10:17 2019

@author: JimchanChen
"""
from prettytable import PrettyTable
import pandas as pd
from pytdx.hq import TdxHq_API,TDXParams
from pytdx.exhq import TdxExHq_API
import tdx_tools
import time
import config
import subprocess
from colorama import init,Fore,Back,Style
import numpy as np
import serial  
def realtimevol():#取分笔成交的数据
    realvol = []
    for i in stlist:
        rtsvol = api.get_transaction_data(i[0], i[1], 0, 5)
        rtsvol = pd.DataFrame(rtsvol,columns=['vol'])
         
        if len(rtsvol['vol'].tail(1).values) > 0: 
            rtsvol = rtsvol['vol'].tail(1).values[0]
            realvol.append(rtsvol)    
        else:
            continue

    return pd.Series(realvol, name='realvol')

def realtimestock():
    #stlist提取多只个股的信息  stokname是把个股的中文名再放进去
     
    rtsdata = api.get_security_quotes(stlist)

    rtsdata = pd.DataFrame(rtsdata)
#    print (rtsdata)
#    print (rtsvol)
    if len(rtsdata) >= 0:
    
        rtsdata['zd'] = rtsdata.price - rtsdata.last_close
        rtsdata['zdf'] = (rtsdata.price - rtsdata.last_close)/rtsdata.last_close
        rtsdata['zdf'] = rtsdata.zdf.map(lambda x:format(x,'.2%'))
        rtsdata['stname'] = stname
        rtsdata = rtsdata[['stname','code','price','last_close','ask1','bid1','ask_vol1','bid_vol1','zd','zdf']]
    
        rtsdata = rtsdata.round(2)
        
        rtsvol = realtimevol()
    #    print (rtsvol)
        rtsdata = pd.concat([rtsdata,rtsvol],axis=1)
        return rtsdata
    else:
        return np.nan
 
#stockname = cf.get("stock01","marketid")
def kzhq():
    
#    kzhq_datainput = cfkz.sections()
    kzhq_out = []
    
    
    for i in cf.cfqihuo:
#            time.sleep(1) 
#        kzhqData = kzhqapi.get_instrument_bars(TDXParams.KLINE_TYPE_5MIN,int(i["marketid"]),i['code'], 0, 200)#7: 扩展行情查询k线数据
        
        kzhqData = kzhqapi.get_instrument_bars(cf.category,int(i["marketid"]),i['code'], 0, cf.categorycount)#7: 扩展行情查询k线数据
        kzhqdf = pd.DataFrame(kzhqData, columns=['datetime', 'open', 'high', 'low', 'close'],)
    #            pd.to_datetime( df["datetime"] ,format="%Y-%m-%d %H:%M:%S") 
    #        df["datetime"] = pd.to_datetime(df["datetime"],format="%Y-%m-%d %H:%M:%S")
        kzhqdf['stockname'] = i["stockname"]
        kzhqdf['code'] = i['code']
        #df = df.set_index('code')
        kzhqdf['last_k_c'] = kzhqdf['close'].shift(1)
        kzhqdf['last_k_l'] = kzhqdf['low'].shift(1)
        kzhqdf['dc_hband'] = tdx_tools.donchian_channel_hband(kzhqdf.close,cf.dc_count)
        kzhqdf['dc_lband'] = tdx_tools.donchian_channel_lband(kzhqdf.close,cf.dc_count)
        kzhqdf['dc_break'] = np.where((kzhqdf['close'] > kzhqdf['dc_hband'].shift(1)),1,
                    np.where((kzhqdf['close'] < kzhqdf['dc_lband'].shift(1)),-1,0))#这里是算突破的信号，当往上突破为1，当往下突破为-1，震荡区间为0
        
        kzhqdf["sma5"] = kzhqdf['close'].rolling(5).mean()
        kzhqdf["sma10"] = kzhqdf['close'].rolling(10).mean()
        kzhqdf["sma20"] = kzhqdf['close'].rolling(20).mean()
        kzhqdf["sma89"] = kzhqdf['close'].rolling(89).mean()
        kzhqdf["sma144"] = kzhqdf['close'].rolling(144).mean()
        kzhqdf["sma89144"] = np.where(kzhqdf['close']>kzhqdf['sma89'],1,np.where(kzhqdf['close']<kzhqdf['sma144'],-1,0))
        kzhqdf["sma51020"] = np.where(kzhqdf['close']>kzhqdf['sma5'],1,np.where(kzhqdf['close']<kzhqdf['sma20'],-1,0))
        kzhqdf = kzhqdf.dropna()
        kzhqdf = tdx_tools.SuperTrend(kzhqdf,period = cf.st_period_fast,multiplier=cf.st_mult_fast,)
#        kzhqdf = tdx_tools.SuperTrendSlow(kzhqdf,period = cf.st_period_slow,multiplier=cf.st_mult_slow,)
    
    
        if len(kzhqdf) >0:

            kzhq_out.append(kzhqdf.iloc[-1]) 
    #        print (kzhqdf.iloc[-1])
            kzhqdf = pd.DataFrame(kzhq_out).reset_index().drop(columns=['index'])#将个股最后一条的数据整合到一个新的df 里并重置列名
            kzhqdf = kzhqdf.round(2)
            #print (df)
        else:
            continue
   
    return kzhqdf


def candleIndex():
    #category 从confg文件中导入配置  修改获取K线的周期

        
#        sh = api.to_df(api.get_index_bars(0,0,"399001",1,400))  #获得指数
    
    skout = []   
    for i in (cf.cfstock):

        
        data = api.get_security_bars(cf.category,int(i["marketid"]),i['code'],0,categorycount) 
        stockdf = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close'],)
#            print (stockdf)
#            pd.to_datetime( df["datetime"] ,format="%Y-%m-%d %H:%M:%S") 
#        df["datetime"] = pd.to_datetime(df["datetime"],format="%Y-%m-%d %H:%M:%S")
        stockdf['stockname'] = i["stockname"]
        stockdf['code'] = i["code"]
        stockdf['last_k_c'] = stockdf['close'].shift(1)
        stockdf["last_k_l"] = stockdf['low'].shift(1)
        stockdf['dc_hband'] = tdx_tools.donchian_channel_hband(stockdf.close,cf.dc_count)
        stockdf['dc_lband'] = tdx_tools.donchian_channel_lband(stockdf.close,cf.dc_count)
        stockdf['dc_break'] = np.where((stockdf['close'] > stockdf['dc_hband'].shift(1)),1,
                np.where((stockdf['close'] < stockdf['dc_lband'].shift(1)),-1,0))#这里是算突破的信号，当往上突破为1，当往下突破为-1，震荡区间为0
        

        #df = df.set_index('code')
        stockdf["sma5"] = stockdf['close'].rolling(5).mean()
        stockdf["sma10"] = stockdf['close'].rolling(10).mean()
        stockdf["sma20"] = stockdf['close'].rolling(20).mean()
        stockdf["sma89"] = stockdf['close'].rolling(89).mean()
        stockdf["sma144"] = stockdf['close'].rolling(144).mean()
        
        stockdf["sma89144"] = np.where(stockdf['close']>stockdf['sma89'],1,np.where(stockdf['close']<stockdf['sma144'],-1,0))
        stockdf["sma51020"] = np.where(stockdf['close']>stockdf['sma5'],1,np.where(stockdf['close']<stockdf['sma20'],-1,0))
        

        stockdf = stockdf.dropna()
        stockdf = tdx_tools.SuperTrend(stockdf,period=cf.st_period_fast,multiplier=cf.st_mult_fast,)
#        stockdf = tdx_tools.SuperTrendSlow(stockdf,period=cf.st_period_slow,multiplier=cf.st_mult_slow,)
#        print (stockdf.T)
        if len(stockdf) >0:
            skout.append(stockdf.iloc[-1]) 
        else:
            continue;
            
    
    stockdf = pd.DataFrame(skout).reset_index().drop(columns=['index'])#将个股最后一条的数据整合到一个新的df 里并重置列名
 
    stockdf = stockdf.round(2) 
       
    return stockdf
def pttable(df):
    #把Dataframe的格式转成表格美化
    table = PrettyTable(df.columns.tolist()) 
    for i in range(0, len(df)):#将每一行的Dataframe 添加到table
        table.add_row(df.iloc[i].tolist() ) 
    for j in list(df.columns):#表格内的文字靠右对齐
        table.align[j] = "r" 
#    table.sort_key("")
#    table.reversesort = True
    return table

    
def call():
    try:
        rts_stock = realtimestock()
        kzhqdf = kzhq()
        stockdf = candleIndex()
        oncesend = tdx_tools.oncetime()
        
#        if len(kzhqdf)>0 and len(stockdf)>0 and len(rtstock)>0:

        colum = ["datetime",'code','stockname',
                 'close','last_k_l','last_k_c','dc_break',
                 'st_f','st_reverseFast',
                 'sma51020','sma89144',]
        stockdf = stockdf[colum]

        kzhqdf = kzhqdf[colum]

#            df = pd.concat([stockdf, kzhqdf],axis=0).reset_index(drop=True)#：将df2中的列添加到df1的尾部\
#        print (colum)
        
        
        table_hist_stock = pttable(stockdf)
        table_hist_qihuo = pttable(kzhqdf)
        talbe_real = pttable(rts_stock)
        
#        print ("--"*50)
        
        #涨停监控==========================================================
   
#        bid_vol = rts_stock.iloc[-2]['bid_vol1']
#        if bid_vol<25000:
#            print ('涨停板随后可能被打开%s' % (rts_stock.iloc[-2]['stockname']))
#            ser = serial.Serial()
#            ser.baudrate = 9600 
#            ser.port = 'COM3' 
##            print(ser)  
#            ser.open()
##            print(ser.is_open)
#            ser.write("1".encode("utf-8"))
#            ser.close()
#            
        #涨停监控结束 ==========================================================
        
        sendme = []
        for i in stockdf.index:
            
            if stockdf.iloc[i].st_f > 0:#当st_f为1的时候说明当根K线为反转K
                #此参数捕捉SUPERTREND的反转点
#                print ("[%s]:的快线SUPERTREND发出反转K信号,..." % stockdf.iloc[i].stockname)
                sendme.append("[%s]:的快线SUPERTREND发出反转K信号,..." % stockdf.iloc[i].stockname)
            if stockdf.iloc[i].dc_break == 1 and stockdf.iloc[i].sma89144 == 1 and stockdf.iloc[i].sma51020 == 1:
#                print ("[%s]:五线之上，并发生突破，是买入信号" % stockdf.iloc[i].stockname)
                sendme.append(stockdf.iloc[i]) 
            if stockdf.iloc[i].close < stockdf.iloc[i].last_k_c and stockdf.iloc[i].sma89144 == 1 and stockdf.iloc[i].sma51020 != 1:
#                print (Back.GREEN+"[%s]:收盘价低于前K线的最低价低于5日均线:高于SMA89和144:==>市场短期可能回调！！！！！" % stockdf.iloc[i].stockname)   
#                print (Style.RESET_ALL)
                sendme.append("[%s]:收盘价低于前K线的最低价低于5日均线:高于SMA89和144:==>市场短期可能回调！！！！！" % stockdf.iloc[i].stockname)
            
        if oncesend==True:
            print(sendme)
#            tdx_tools.sohu_sendmail("26201084@qq.com","五分钟发送一次：这是一封测试邮件%s\n" % table_hist_stock)
            print ("已发送一次数据")
            
        subprocess.call(winorlinux,shell=True)  
        """显示菜单"""
        print ("欢迎使用【股票期货预警系统】V1.0")
        print ("*"*60)
        print ("actionStock",)
        print ("*"*60)

        print("当前K线周期为：%s" % (tdx_tools.k_zhouqi()))
        
        print(Back.BLACK + str(table_hist_stock))
        print(Back.BLACK + str(table_hist_qihuo))
        print(Back.BLACK + str(talbe_real))
        print (sendme)
        print (Style.RESET_ALL)
        
        
        
                
        return True
#        else:
#            return False
    except:
        return False

if __name__ == '__main__':
    import config 
    import datetime

    api = TdxHq_API()
    kzhqapi = TdxExHq_API()
    winorlinux = tdx_tools.winorlinux()
    api.connect('58.63.254.191', 7709);
    kzhqapi.connect('218.80.248.229', 7721);
    cf = config

    
#    print (sendme)
    categorycount = config.categorycount
    stname = []
    stlist = []
    stime = datetime.datetime.now().replace(hour=9,minute=00,second=0,microsecond=0)
    etime = datetime.datetime.now().replace(hour=23,minute=00,second=0,microsecond=0)
    for i in cf.cfstock:
        st = (i["marketid"],i["code"])
        stlist.append(st)
        stname.append(i["stockname"])
        

    
    cout =1
    while True:
        time.sleep(1) 
        if stime < datetime.datetime.now() < etime:
            
            
            bol = call()
            cout = cout+1   
            
            if bol == False:
                print ("正在重连...")
                api.connect('58.63.254.191', 7709);
                kzhqapi.connect('218.80.248.229', 7721);
               
        else:
#            pass

            
            print ("现在是非交易时间\n{0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                 
