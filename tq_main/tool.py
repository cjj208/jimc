from email.header import Header 
from email.mime.text import MIMEText
import smtplib
import win32com.client
import winsound
import time 
import numpy as np
import pandas as pd

def beep():
    count = 0
    while (count < 1):
        time.sleep(0.5)
        spk = win32com.client.Dispatch("SAPI.SpVoice")
        spk.Speak("做多一手")
        winsound.Beep(1500, 500)
        winsound.Beep(1500, 500)
        pass
        count += 1

#%%
#SuperTrend


def SuperTrend(df, period, multiplier, ohlc=['open', 'high', 'low', 'close']):


    ATR(df, period, ohlc=ohlc)
    atr = 'ATR_' + str(period)
    #st = 'ST_' + str(period) + '_' + str(multiplier)
    st = 'supertrend'
    stx = 'STX_' + str(period) + '_' + str(multiplier)
    stx = 'st_reverse'


    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
        df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
        df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[
            i] <= df['final_ub'].iat[i] else \
            df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                     df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= \
                                         df['final_lb'].iat[i] else \
                    df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] < \
                                             df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)
    df['superpoint'] = np.where(
            (df["st_reverse"] != df["st_reverse"].shift(1)) 
            & (df.st_reverse=='up'),1,np.where((df["st_reverse"] 
            != df["st_reverse"].shift(1)) & (df.st_reverse=='down')
            ,-1,0))#当st_f=1则发生短期反转

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb','TR',atr], inplace=True, axis=1)

    df.fillna(0, inplace=True)

    return df


def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):

    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)

        df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA(df, 'TR', atr, period, alpha=True)

    return df


def SMA(df, base, target, period):
    """
    Function to compute Simple Moving Average (SMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the SMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    df[target] = df[base].rolling(window=period).mean()
    df[target].fillna(0, inplace=True)

    return df


def EMA(df, base, target, period, alpha=False):
    """
    Function to compute Exponential Moving Average (EMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    con = pd.concat([df[:period][base].rolling(window=period).mean(), df[period:][base]])

    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = con.ewm(span=period, adjust=False).mean()

    df[target].fillna(0, inplace=True)
    return df

def sohu_sendmail(mail,sub,mesg):

    try:
        mail_host="smtp.sohu.com"  #设置服务器  
        mail_user=("cjj208@sohu.com")    #用户名  
        mail_pass="123qwe@@"   #口令,QQ邮箱是输入授权码，在qq邮箱设置 里用验证过的手机发送短信获得，不含空格  
        sender = 'cjj208@sohu.com'  
        receivers = [(mail)]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱  
        message = MIMEText(mesg, 'plain', 'utf-8')  
        message['From'] = Header(mail_user, 'utf-8')  
        message['To'] =  Header(sender, 'utf-8')  
        subject = (sub)
        message['Subject'] = Header(subject, 'utf-8')  
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)   
        smtpObj.login(mail_user,mail_pass)    
        smtpObj.sendmail(sender, receivers, message.as_string())  
        smtpObj.quit()  
    except Exception as e:
        print ("未发送邮件！%s"% e)

if __name__ == "__main__":
    sendmail = sohu_sendmail("26201084@qq.com",sub="sub",mesg="我要测一下")
    sendmail
    pass