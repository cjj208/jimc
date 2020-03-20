# 引入TqSdk模块
from datetime import date
from tqsdk import TqApi,TqBacktest, TargetPosTask
# 创建api实例，设置web_gui=True生成图形化界面
api = TqApi(backtest=TqBacktest(start_dt=date(2020, 2, 12), end_dt=date(2020, 3, 12)),web_gui=True)
# 订阅 cu2002 合约的10秒线
klines = api.get_kline_serial("SHFE.cu2005", data_length=200,duration_seconds=5*60)
while True:
    # 通过wait_update刷新数据
    api.wait_update()
 
    