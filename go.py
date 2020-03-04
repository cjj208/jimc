# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:08:56 2019
new cccccccccccccccccccccccc
@author: JimchanChen
"""
import pandas as pd
from pytdx.exhq import TdxExHq_API
from pytdx.hq import TdxHq_API
import config
import numpy as np
import tdx_tools
import time
import subprocess
import prettytable as pt
import ta
class Datacent:
    def __init__(self):
        self.cf = config
        self.tools = tdx_tools
        self.qihuo_api = TdxExHq_API()
        self.gupiao_api = TdxHq_API()
        self.cflen = 0
        self.table = pt.PrettyTable()

   
    def gupiao_connectSer(self):
        self.gupiao_api.connect('58.63.254.191', 7709)
        
        gupiaoret = self.gupiao_api.connect('58.63.254.191', 7709)
        if gupiaoret == False:
            print ("股票没有连接。。。")
            return gupiaoret
        else:
            print("已连接股票数据服务")
            gupiaoret = True
            return gupiaoret

    def qihuo_connectSer(self):
        
        self.qihuo_api.connect('218.80.248.229', 7721)
        
        qihuoret = self.qihuo_api.connect('218.80.248.229', 7721)
        if qihuoret == False:
            print ("期货没有连接。。。")
            return qihuoret
        else:
            print("已连接期货数据服务")
            qihuoret = True
            return qihuoret
        
            
    def realtimestock(self,):
#        stlist提取多只个股的信息  stokname是把个股的中文名再放进去
        stlist = []
        stname = []
        for i in config.cfstock:
            st = (i["marketid"],i["code"])
            stlist.append(st)
            stname.append(i["stockname"])
        rtsdata = self.gupiao_api.get_security_quotes(stlist)
    
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
            
    #        rtsvol = realtimevol()
        #    print (rtsvol)
    #        rtsdata = pd.concat([rtsdata,rtsvol],axis=1)
            return rtsdata
        else:
            return np.nan
    def candlelink(self):
        df['看涨抱线'] = np.where((df.open_last_1>df.close_last_1) 
                & (df.open<df.close_last_1) 
                & (df.close>df.open_last_1)
                ,1,0)
        
        df['看涨孕线'] = np.where((df.open_last_1 > df.close_last_1) 
                & (df.open<df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open>df.close_last_1)
                ,1,0)
        df['看跌吞没'] = np.where((df.open_last_1<df.close_last_1) 
                & (df.open>df.close) 
                & (df.close<df.open_last_1)
                & (df.open>df.close_last_1)
                ,1,0)
                
        df['看跌孕线'] = np.where((df.open_last_1 < df.close_last_1) 
                & (df.open>df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open<df.close_last_1)
                ,1,0)
        
        df['看涨刺透'] = np.where((df.open_last_1 > df.close_last_1)
                & (df.open<df.close)
                & (df.close > (np.abs(df.close_last_1 - df.open_last_1)/2) + df.close_last_1)
                & (df.open<df.close)
                & (df.open_last_1 > df.close)
                & (df.open_last_1 >df.open)
                ,1,0)
        
        df['乌云盖顶'] = np.where((df.open_last_1 < df.close_last_1)
            & (df.open > df.close)
            & (df.close < (np.abs(df.close_last_1 - df.open_last_1)/2) + df.open_last_1)
            & (df.close_last_1 < df.open)
            & (df.open_last_1 < df.close)
            ,1,0)
        return df
    def qihuoK(self,cflen,):
        #cflen = 0
        data = self.qihuo_api.get_instrument_bars(self.cf.category,
                        int(self.cf.cfqihuo[cflen]["marketid"]),
                        self.cf.cfqihuo[cflen]['code'], 0,
                        self.cf.categorycount)#7: 扩展行情查询k线数据
        #sh = self.api.to_df(self.api.get_index_bars(3,1,"000001",1,400))  #获得指数

        df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close'],)
        df['stockname'] = self.cf.cfqihuo[cflen]["stockname"]
        df['code'] = self.cf.cfqihuo[cflen]["code"]

        df['dc_hband'] = self.tools.donchian_channel_hband(df.close,self.cf.dc_count)
        df['dc_lband'] = self.tools.donchian_channel_lband(df.close,self.cf.dc_count)
        df['dc_break'] = np.where((df['close'] > df['dc_hband'].shift(1)),1,
                np.where((df['close'] < df['dc_lband'].shift(1)),-1,0))#这里是算突破的信号，当往上突破为1，当往下突破为-1，震荡区间为0
        
    
        #df = df.set_index('code')
        df["sma5"] = df['close'].rolling(5).mean()
        df["sma10"] = df['close'].rolling(10).mean()
        df["sma20"] = df['close'].rolling(20).mean()
        df["sma89"] = df['close'].rolling(89).mean()
        df["sma144"] = df['close'].rolling(144).mean()
        
        df["sma89144"] = np.where(df['close']>df['sma89'],1,np.where(df['close']<df['sma144'],-1,0))
        df["sma51020"] = np.where(df['close']>df['sma5'],1,np.where(df['close']<df['sma20'],-1,0))
        df['open_last_1'] = df['open'].shift(1)
        df['high_last_1'] = df['high'].shift(1)
        df["low_last_1"] = df['low'].shift(1)
        df['close_last_1'] = df['close'].shift(1)
        df["rsi"] = ta.momentum.rsi(df.close,n=14,)
        df['stoch'] = ta.momentum.stoch(df.high,df.low,df.close,14)
        
        df['看涨抱线'] = np.where((df.open_last_1>df.close_last_1) 
                & (df.open<df.close_last_1) 
                & (df.close>df.open_last_1)
                ,1,0)
        
        df['看涨孕线'] = np.where((df.open_last_1 > df.close_last_1) 
                & (df.open<df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open>df.close_last_1)
                ,1,0)
        df['看跌吞没'] = np.where((df.open_last_1<df.close_last_1) 
                & (df.open>df.close) 
                & (df.close<df.open_last_1)
                & (df.open>df.close_last_1)
                ,1,0)
                
        df['看跌孕线'] = np.where((df.open_last_1 < df.close_last_1) 
                & (df.open>df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open<df.close_last_1)
                ,1,0)
        
        df['看涨刺透'] = np.where((df.open_last_1 > df.close_last_1)
                & (df.open<df.close)
                & (df.close > (np.abs(df.close_last_1 - df.open_last_1)/2) + df.close_last_1)
                & (df.open<df.close)
                & (df.open_last_1 > df.close)
                & (df.open_last_1 >df.open)
                ,1,0)
        
        df['乌云盖顶'] = np.where((df.open_last_1 < df.close_last_1)
            & (df.open > df.close)
            & (df.close < (np.abs(df.close_last_1 - df.open_last_1)/2) + df.open_last_1)
            & (df.close_last_1 < df.open)
            & (df.open_last_1 < df.close)
            ,1,0)
        df['看涨一线穿'] = np.where((df.sma5>df.sma10)&(df.open < df.sma10)&(df.close>df.sma5)&(df.close>df.close_last_1),1,0)
        df['看跌一线穿'] = np.where((df.sma5<df.sma10)&(df.open > df.sma10)&(df.close<df.sma5)&(df.close<df.close_last_1),1,0)
        df = df.dropna()
        df = self.tools.SuperTrend(df,period=self.cf.st_period_fast,multiplier=self.cf.st_mult_fast,)
    #        print (stockdf.T)
#            if len(stockdf) >0:
#                skout.append(stockdf.iloc[-1]) 
#            else:
#                continue;
#        print (stockdf)
        stockdf = pd.DataFrame(df).reset_index().drop(columns=['index'])#将个股最后一条的数据整合到一个新的df 里并重置列名
        stockdf = stockdf.round(2) 
        return stockdf


    
    def gupiaoK(self,cflen,):
        #category 从confg文件中导入配置  修改获取K线的周期
    
        '''
        sh = api.to_df(api.get_index_bars(0,0,"399001",1,400))  #获得指数
        return sh
        '''
#        skout = []   
#        for i in self.cf.cfstock:

        data = self.gupiao_api.get_security_bars(self.cf.category,int(self.cf.cfstock[cflen]["marketid"]),
                                          self.cf.cfstock[cflen]['code'],0,self.cf.categorycount) 
        df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close'],)
        df['stockname'] = self.cf.cfstock[cflen]["stockname"]
        df['code'] = self.cf.cfstock[cflen]["code"]

        df['dc_hband'] = self.tools.donchian_channel_hband(df.close,self.cf.dc_count)
        df['dc_lband'] = self.tools.donchian_channel_lband(df.close,self.cf.dc_count)
        df['dc_break'] = np.where((df['close'] > df['dc_hband'].shift(1)),1,
                np.where((df['close'] < df['dc_lband'].shift(1)),-1,0))#这里是算突破的信号，当往上突破为1，当往下突破为-1，震荡区间为0
        
    
        #df = df.set_index('code')
        df["sma5"] = df['close'].rolling(5).mean()
        df["sma10"] = df['close'].rolling(10).mean()
        df["sma20"] = df['close'].rolling(20).mean()
        df["sma89"] = df['close'].rolling(89).mean()
        df["sma144"] = df['close'].rolling(144).mean()
        
        df["sma89144"] = np.where(df['close']>df['sma89'],1,np.where(df['close']<df['sma144'],-1,0))
        df["sma51020"] = np.where(df['close']>df['sma5'],1,np.where(df['close']<df['sma20'],-1,0))
        df['open_last_1'] = df['open'].shift(1)
        df['high_last_1'] = df['high'].shift(1)
        df["low_last_1"] = df['low'].shift(1)
        df['close_last_1'] = df['close'].shift(1)
        
        
        df['看涨抱线'] = np.where((df.open_last_1>df.close_last_1) 
                & (df.open<df.close_last_1) 
                & (df.close>df.open_last_1)
                ,1,0)
        
        df['看涨孕线'] = np.where((df.open_last_1 > df.close_last_1) 
                & (df.open<df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open>df.close_last_1)
                ,1,0)
        df['看跌吞没'] = np.where((df.open_last_1<df.close_last_1) 
                & (df.open>df.close) 
                & (df.close<df.open_last_1)
                & (df.open>df.close_last_1)
                ,1,0)
                
        df['看跌孕线'] = np.where((df.open_last_1 < df.close_last_1) 
                & (df.open>df.close) 
                & (np.abs(df.high-df.low) < np.abs(df.open_last_1-df.close_last_1))
                & (df.open<df.close_last_1)
                ,1,0)
        
        df['看涨刺透'] = np.where((df.open_last_1 > df.close_last_1)
                & (df.open<df.close)
                & (df.close > (np.abs(df.close_last_1 - df.open_last_1)/2) + df.close_last_1)
                & (df.open<df.close)
                & (df.open_last_1 > df.close)
                & (df.open_last_1 >df.open)
                ,1,0)
        
        df['乌云盖顶'] = np.where((df.open_last_1 < df.close_last_1)
            & (df.open > df.close)
            & (df.close < (np.abs(df.close_last_1 - df.open_last_1)/2) + df.open_last_1)
            & (df.close_last_1 < df.open)
            & (df.open_last_1 < df.close)
            ,1,0)       
        df['看涨一线穿'] = np.where((df.sma5>df.sma10)&(df.open < df.sma10)&(df.close>df.sma5)&(df.close>df.close_last_1),1,0)
        df['看跌一线穿'] = np.where((df.sma5<df.sma10)&(df.open > df.sma10)&(df.close<df.sma5)&(df.close<df.close_last_1),1,0)
        
        df = df.dropna()
        df = self.tools.SuperTrend(df,period=self.cf.st_period_fast,multiplier=self.cf.st_mult_fast,)
    #        print (stockdf.T)
#            if len(stockdf) >0:
#                skout.append(stockdf.iloc[-1]) 
#            else:
#                continue;
#        print (stockdf)
        stockdf = pd.DataFrame(df).reset_index().drop(columns=['index'])#将个股最后一条的数据整合到一个新的df 里并重置列名
        stockdf = stockdf.round(2) 
        return stockdf

    

    

        
if __name__ == '__main__':
    
    import datetime
    datacent = Datacent()

    winorlinux = datacent.tools.winorlinux()
  
    table = pt.PrettyTable()
    #stime01 = datetime.datetime.now().replace(hour=9,minute=00,second=0,microsecond=0)

    stime01 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month, day = datetime.datetime.now().day, hour=9,minute=00,second=0,microsecond=0)
    etime01 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=11,minute=30,second=0,microsecond=0)
    
    stime02 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=13,minute=00,second=0,microsecond=0)
    etime02 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=15,minute=00,second=0,microsecond=0)
    
    stime03 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=21,minute=00,second=0,microsecond=0)
    etime03 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=23,minute=00,second=0,microsecond=0)
    
    conbol = False


    while conbol==False:
        print ("进入主循环")

        if datacent.qihuo_connectSer() and datacent.gupiao_connectSer():
            conbol = True
            print ("已链接")


            if conbol==True:
                while True:
                    
                    stime = time.localtime(time.time())
                    
                    
#                    stime01 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month, day = datetime.datetime.now().day, hour=9,minute=00,second=0,microsecond=0)
#                    etime01 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=11,minute=30,second=0,microsecond=0)
#    
#                    stime02 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=13,minute=00,second=0,microsecond=0)
#                    etime02 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=15,minute=00,second=0,microsecond=0)
#    
#                    stime03 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=21,minute=00,second=0,microsecond=0)
#                    etime03 = datetime.datetime.now().replace(year= datetime.datetime.now().year,month = datetime.datetime.now().month,day = datetime.datetime.now().day, hour=23,minute=00,second=0,microsecond=0)
#                    
                    calltime = (9<=stime.tm_hour<11) | (13<=stime.tm_hour<18) | (21<=stime.tm_hour<23)
####################
                    if calltime:
                        print ("当前是否为交易时间：%s"%calltime)
                        gupiaocount = list(range(len(config.cfstock)))
                        qihuocount = list(range(len(config.cfqihuo))) 
                        
                        column = ['datetime', 'open', 'high', 'low', 'close', 'stockname', 'code',
                        'dc_hband', 'dc_lband', 'dc_break', 'sma5',
                       'sma10', 'sma20', 'sma89', 'sma144', 'sma89144', 'sma51020','open_last_1','high_last_1',
                       'low_last_1','close_last_1','看涨抱线', '看涨孕线', '看跌吞没', '看跌孕线','看涨刺透', '乌云盖顶','看涨一线穿','看跌一线穿',
                       'supertrend', 'st_reverseFast', 'st_f']
                        

                        gupiaoRec = []
                        table = pt.PrettyTable(column)
                        for i in gupiaocount:
                            gupiaodf = datacent.gupiaoK(i).tail(1)
                            if len(gupiaodf)>0:
                                gupiaodf = gupiaodf.iloc[-1].to_dict()
            
                                gupiaoRec.append(gupiaodf)
                                table.add_row(gupiaodf.values())
                                table.align='r'
                                
                            else:
                                continue
    #                                print ("conbol = False")
    #                                conbol = False
    #                                break
                                
                        for j in qihuocount:
                            qihuodf = datacent.qihuoK(j).tail(1)
                           
                            if len(qihuodf)>0:
                                qihuodf = qihuodf.iloc[-1].to_dict()
                   
                                gupiaoRec.append(qihuodf)
                                table.add_row(qihuodf.values())
                                
                            else:
                                continue
    #                                print ("conbol = False")
    #                                conbol = False
    #                                break
                        if len(gupiaoRec):
                            
                            df = pd.DataFrame(gupiaoRec,columns=gupiaoRec[0].keys())
        
                        else:
                            conbol = False
                            print ("当前未取得数据，尝试重连")
                            print ("conbol = False")
                            while conbol == False:
                               
                                if (datacent.qihuo_connectSer()) and (datacent.gupiao_connectSer()):
                                    
                                    conbol = True
                                    print ('重连成功\n'*10)
                                    break
                                
                                
                             
                             
                             
                        
                        subprocess.call(winorlinux,shell=True)  
                        table = table.get_string(fields=
                                ['datetime','code','stockname','close','dc_break',
                                 'sma89144','sma51020','supertrend','看涨抱线','看涨孕线', 
                                 '看跌吞没', '看跌孕线','看涨刺透', '乌云盖顶','看涨一线穿','看跌一线穿',
                                 'st_reverseFast','st_f',])
                        
                        
                        print (table)
                        #print (df)
                        print("当前K线周期为：%s" % (tdx_tools.k_zhouqi()))
                        print ("conbol：%s" % conbol)
                        #sendmail=========================================
                        mailbol = []
                        
                        if datacent.tools.oncetime() == True:
                            for i in df.index:
                                if (df.iloc[i]['sma89144']==1) & (df.iloc[i]['sma89144']==1) & (df.iloc[i]['st_f']==1):
                                    ret = ("%s||%s:五线之上,supertrend向上突破" % (df.iloc[i]['datetime'].strip(),df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                    pass
                                
                                elif (df.iloc[i]['sma89144']==-1) & (df.iloc[i]['sma89144']==-1) & (df.iloc[i]['st_f']==-1):
                                    ret = ("%s||%s:五线之下,supertrend向上突破" % (df.iloc[i]['datetime'].strip(),df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                    
                                elif df.iloc[i]['看涨抱线'] ==1:
                                    ret = ("%s:出现看涨抱线" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看涨孕线'] ==1:
                                    ret = ("%s:看涨孕线" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看跌吞没'] ==1:
                                    ret = ("%s:看跌吞没" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看跌孕线'] ==1:
                                    ret = ("%s:看跌孕线" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看涨刺透'] ==1:
                                    ret = ("%s:看涨刺透" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['乌云盖顶'] ==1:
                                    ret = ("%s:乌云盖顶" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看涨一线穿'] ==1:
                                    ret = ("%s:看涨一线穿" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)
                                elif df.iloc[i]['看跌一线穿'] ==1:
                                    ret = ("%s:看跌一线穿" % (df.iloc[i]['stockname'].strip()))
                                    mailbol.append(ret)                           
                                else:
                                    print ("没有出现信号%s"%str(datetime.datetime.now()))
                            if len(mailbol):#存在即为真
                                tdx_tools.sohu_sendmail(config.mail_addr_1,sub="%s"%(mailbol),mesg="message!!%s" % mailbol)
                                time.sleep(10)
                                if config.mail_addr_2 != "":
                                    tdx_tools.sohu_sendmail(config.mail_addr_2,sub="%s"%(mailbol),mesg="message!!%s" % mailbol)
                                    time.sleep(10)
                                    
                                else:
                                    continue
                                time.sleep(3)
                                print (ret)
                                print ("发送一次邮件")

                        print("%s"%str(datetime.datetime.now()))
####################
                    else:
                        
                        time.sleep(10)
                        subprocess.call(winorlinux,shell=True)  
                        print ("当前时间为：%s"%str(datetime.datetime.now()))
                        print ("非交易时段")
                        print ("conbol:%s" % conbol)
                        print ("calltime:%s" % calltime)
                        if calltime == False:
                            conbol=False
                            break
                                                    
                                
