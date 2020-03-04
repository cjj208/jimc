# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 09:36:38 2020

@author: JimchanChen
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__title__ = 'test py ctp of se'
__author__ = 'HaiFeng'
__mtime__ = '20190506'

from py_ctp.trade import CtpTrade
from py_ctp.quote import CtpQuote
from py_ctp.enums import *
import time


class TestTrade(object):
    def __init__(self, addr: str, broker: str, investor: str, pwd: str, appid: str, auth_code: str, proc: str):
        self.front = addr
        self.broker = broker
        self.investor = investor
        self.pwd = pwd
        self.appid = appid
        self.authcode = auth_code
        self.proc = proc

        self.t = CtpTrade()
        self.t.OnConnected = self.on_connect
        self.t.OnUserLogin = lambda o, x: print('Trade logon:', x)
        self.t.OnDisConnected = lambda o, x: print(x)
        self.t.OnRtnNotice = lambda obj, time, msg: print(f'OnNotice: {time}:{msg}')
        self.t.OnErrRtnQuote = lambda obj, quote, info: None
        self.t.OnErrRtnQuoteInsert = lambda obj, o: None
        self.t.OnOrder = lambda obj, o: None
        self.t.OnErrOrder = lambda obj, f, info: None
        self.t.OnTrade = lambda obj, o: None
        self.t.OnInstrumentStatus = lambda obj, inst, stat: None

    def on_connect(self, obj):
        self.t.ReqUserLogin(self.investor, self.pwd, self.broker, self.proc, self.appid, self.authcode)

    def run(self):
        self.t.ReqConnect(self.front)
        # self.t.ReqConnect('tcp://192.168.52.4:41205')

    def release(self):
        self.t.ReqUserLogout()


class TestQuote(object):
    """TestQuote"""

    def __init__(self, addr: str, broker: str, investor: str, pwd: str):
        """"""
        self.front = addr
        self.broker = broker
        self.investor = investor
        self.pwd = pwd

        self.q = CtpQuote()
        self.q.OnConnected = lambda x: self.q.ReqUserLogin(self.investor, self.pwd, self.broker)
        self.q.OnUserLogin = lambda o, i: self.q.ReqSubscribeMarketData('rb2005',)
        
    def run(self):
        self.q.ReqConnect(self.front)

    def release(self):
        self.q.ReqUserLogout()


if __name__ == "__main__":
    
    front_trade = 'tcp://180.168.146.187:10100'
    front_quote = 'tcp://180.168.146.187:10110'
    broker = '9999'
    investor = '090828'
    pwd = 'jimc1230'
    appid = 'simnow_client_test'
    auth_code = '0000000000000000'
    proc = ''
    '''
    
    front_trade = 'tcp://61.186.254.131:42205'
    front_quote = 'tcp://61.186.254.131:42213'
    broker = '6666'
    investor = '12345678'
    pwd = 'CS123456'
    appid = 'client_jimchan_1.0'
    auth_code = '4J3MO7CZNTE6IU4L'
    proc = ''
    '''
    if investor == '':
        investor = input('invesotr:')
        pwd = input('password:')
        appid = input('appid:')
        auth_code = input('auth code:')
        proc = input('product info:')
    tt = TestTrade(front_trade, broker, investor, pwd, appid, auth_code, proc)
    tt.run()
#    time.sleep(5)
    #买入限价单
#     tt.t.ReqOrderInsert('fu2005', DirectType.Buy, OffsetType.Open, 2005, 1)
     #卖出限价单
#    tt.t.ReqOrderInsert('rb2005', DirectType.Sell, OffsetType.Open, 3421, 1)
     #平仓
#    tt.t.ReqOrderInsert('fu2005', DirectType.Sell, OffsetType.Open, 2044, 1)
     
#    tt.t.ReqOrderInsert('rb2005', DirectType.Sell, OffsetType.Close, 3421, 1)
     #撤单
    #tt.t.ReqOrderAction(list(tt.t.orders)[-1])
#    time.sleep(3)
#    qq = TestQuote(front_quote, broker, investor, pwd)
#    qq.run()

    # time.sleep(6)
    # for inst in tt.t.instruments.values():
    #     print(inst)
#    input()
#    tt.release()
#    qq.release()
#    input()