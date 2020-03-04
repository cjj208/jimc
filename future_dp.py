import config
from pytdx.exhq import TdxExHq_API
import pandas as pd

import prettytable as pt
class Datacent:
    def __init__(self):
        self.cf = config
        self.qihuo_api = TdxExHq_API()
        self.cflen = 0
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
    def qihuoK(self,cflen,):
        data = self.qihuo_api.get_instrument_bars(self.cf.category,int(self.cf.cfqihuo[cflen]["marketid"]),self.cf.cfqihuo[cflen]['code'], 0, self.cf.categorycount)#7: 扩展行情查询k线数据
        df = pd.DataFrame(data, columns=['datetime','stockname', 'open', 'high', 'low', 'close',  'code',],)
        df['stockname'] = self.cf.cfqihuo[cflen]["stockname"]
        df['code'] = self.cf.cfqihuo[cflen]["code"]
        return df
if __name__ == '__main__':
    import time
    import socket 
    c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    c.connect(('172.20.155.136',6100))
    datacent = Datacent()
    datacent.qihuo_connectSer()
    column = ['datetime','stockname', 'open', 'high', 'low', 'close',  'code',]
    table = pt.PrettyTable(column)
    while True:
        time.sleep(0.5)
        qihuocount = list(range(len(config.cfqihuo))) 
        
#        print (qihuocount)
        dataReturn = []
        for j in qihuocount:
            qihuodf = datacent.qihuoK(j).tail(1).round(1)
           
            if len(qihuodf)>0:
                qihuodf = qihuodf.iloc[-1].to_dict()
   
                dataReturn.append(qihuodf)
                table.add_row(qihuodf.values())
                
                
            else:
                continue
        qihuodf = pd.DataFrame(dataReturn)
        print (table)
#        print (qihuodf)
        row00 = str(qihuodf.loc[0].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row01 = str(qihuodf.loc[1].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row02 = str(qihuodf.loc[2].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row03 = str(qihuodf.loc[3].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row04 = str(qihuodf.loc[4].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row05 = str(qihuodf.loc[5].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row06 = str(qihuodf.loc[6].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        row07 = str(qihuodf.loc[7].to_dict()).replace('\'','').replace(':','=').replace(',',';')
        toviz = row00 +','+ row01 +','+ row02 +','+ row03 +','+ row04 +','+ row05 +','+ row06 +','+ row07
        s = ("-1 RENDERER*FUNCTION*DataPool*Data SET stocks[0-7]={%s};\0" % (toviz))
        s = s.encode('utf-8')
        c.send(s)
                
        
        
        
        
        
        