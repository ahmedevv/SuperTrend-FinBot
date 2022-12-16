import pandas as pd
import MetaTrader5 as mt5
from supertrend import getSuperTrend
from supertrend import generateSignal
#from supertrenBacktest import Strategy
import time
from datetime import datetime, timedelta


#setting Variables
SYMBOL = 'EURUSD'
TIMEFRAME = mt5.TIMEFRAME_M15
deviation = 20
MAGIC = 999
TICKET = 1612512523
mt5.initialize(login=51054165,      
   password="ywa8FtEY",      
   server="ICMarketsSC-Demo")
#Making Market Order
def makingOrder(volume,orderType,checkData):
    lastRow = len(checkData.index) - 1
    prevRow = lastRow - 1
   
    if orderType == 'Buy':
        if (checkData['superTrend'][lastRow] == False and checkData['superTrend'][prevRow] == True) or (checkData['superTrend'][lastRow] == True and checkData['superTrend'][prevRow] == True):
            SL = checkData['lowerBand'][lastRow] - 0.0001
            TP = checkData['close'][lastRow] - SL 
            TP = 1.5 * TP
            TP = checkData['close'][lastRow] + TP
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": 'EURUSD',
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick('EURUSD').ask,
            'tp' : TP,
            "magic": MAGIC,
            "comment": "Started Position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        print(result)
    else:
        if (checkData['superTrend'][lastRow] == True and checkData['superTrend'][prevRow] == False) or (checkData['superTrend'][lastRow] == False and checkData['superTrend'][prevRow] == False):
            SL = checkData['upperBand'][lastRow] + 0.0001
            TP = SL - checkData['close'][lastRow]
            TP = 1.5 * TP
            TP = checkData['close'][lastRow] - TP
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": 'EURUSD',
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick('EURUSD').bid,
            'tp' : TP,
            "magic": MAGIC,
            "comment": "Started Position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        print(result)


def checkSignal(checkData):
    print("Checking for Signal")
    lastRow = len(checkData.index) - 1
    prevRow = lastRow - 1
    print(checkData.tail(2))
    if (checkData['signal'][prevRow] == 'NoPosition' and checkData['signal'][lastRow] == 'Buy') or (checkData['signal'][prevRow] == 'NoPosition' and checkData['signal'][lastRow] == 'emaBuy') or (checkData['signal'][prevRow] == 'Buy' and checkData['signal'][lastRow] == 'NoPosition') or (checkData['signal'][prevRow] == 'emaBuy' and checkData['signal'][lastRow] == 'NoPosition'):
        order = 'Buy' 
        return order 
    elif (checkData['signal'][prevRow] == 'NoPosition' and checkData['signal'][lastRow] == 'Sell') or (checkData['signal'][prevRow] == 'NoPosition' and checkData['signal'][lastRow] == 'emaSell') or (checkData['signal'][prevRow] == 'Sell' and checkData['signal'][lastRow] == 'NoPosition') or (checkData['signal'][prevRow] == 'emaSell' and checkData['signal'][lastRow] == 'NoPosition'): 
        order = 'Sell'
        return order
    else:
        return 'No Signal' 
    
#trailing SL
def trail_sl(checkData):
    # get position based on ticket_id
    position = mt5.positions_get()

    # check if position exists
    if position:
        position = position[0]
    else:
        print('Position does not exist')

    # get position data
    order_type = position.type
    price_current = position.price_current
    price_open = position.price_open
    sl = position.sl
    print("Checking for Signal")
    lastRow = len(checkData.index) - 1
    prevRow = lastRow - 1
    print(checkData.tail(2))
    #for Buy/emaBuy
    if (checkData['superTrend'][lastRow] == False and checkData['superTrend'][prevRow] == True) or (checkData['superTrend'][lastRow] == True and checkData['superTrend'][prevRow] == True):
        SL = checkData['lowerBand'][lastRow] - 0.0005
        #setting SL above 5 pips of UpperBand for Sell Signal/emaSell
    elif (checkData['superTrend'][lastRow] == True and checkData['superTrend'][prevRow] == False) or (checkData['superTrend'][lastRow] == False and checkData['superTrend'][prevRow] == False):
        SL = checkData['upperBand'][lastRow] + 0.0005

    request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': position.ticket,
            'sl': SL,
            'tp' : position.tp
        }
    result = mt5.order_send(request)
    print(result)
def OpenedPosition():
    position = mt5.positions_get()
    if position:
        position = position[0]
        return True
    else:
        print('Position does not exist')
        return False

# def DailyDrawDown():
#     info = mt5.account_info()
#     print(info.balance)

# settingTradingLimit()

# if __name__ == "__main__":
   

#     while True:
#         print("Fetching Data")
#         data = mt5.copy_rates_from_pos(SYMBOL,TIMEFRAME,0,10000)
#         bars = pd.DataFrame(data)
#         superTrend_data = getSuperTrend(bars)
#         superTrend_data['time'] = pd.to_datetime(superTrend_data['time'],unit='s')
#         superTrend_data = generateSignal(superTrend_data)
#         orderType = checkSignal(superTrend_data)

#         checker = OpenedPosition()
#         if checker == False:
#             if orderType == 'Buy':
#                 print("Opening Buy Position")
#                 makingOrder(1.0,'Buy')
#                 trail_sl(superTrend_data)
#             elif orderType == 'Sell':
#                 print("Opening Sell Position")
#                 makingOrder(1.0,'Sell')
#                 trail_sl(superTrend_data)
#             else:
#                 print("No Signal Found!")
#         elif checker == True:
#             trail_sl(superTrend_data)


        
#         time.sleep((15 * 60)+10)
        

#df = pd.read_csv('superTrendsignal.csv')
# while True:
#     bars = mt5.copy_rates_from_pos(SYMBOL,TIMEFRAME,0,1)
#     df = pd.DataFrame(bars)
#     df['time'] = pd.to_datetime(df['time'],unit='s')
#     print(df)
#     time.sleep(5)
