import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from ta import trend
from datetime import datetime, timedelta
import warnings 
warnings.filterwarnings('ignore')

mt5.initialize(login=51054165,      
   password="ywa8FtEY",      
   server="ICMarketsSC-Demo")

#getting Real time Data from Metatrader5
bars = mt5.copy_rates_range("XAUUSD",mt5.TIMEFRAME_M15,datetime(2022,11,1),datetime.now())

#Converting data to DataFrame
df = pd.DataFrame(bars)


df['time']  = pd.to_datetime(df['time'],unit='s')


#plotting closing Prices on Line graph
# fig = px.line(df,x='time',y='close')
# fig.show()

#Function For Calculating True Range
 
# TR=Max[(H − L),Abs(H − CP),Abs(L−CP)]
# ATR = mean(TR)
def trueRange(df):
    df['prevClose'] = df['close'].shift(1)
    df['high-Low'] = df['high'] - df['low']
    df['high-PC'] = abs(df['high'] - df['prevClose'])
    df['low-PC'] = abs(df['low'] - df['prevClose'])
    TR = df[['high-Low','high-PC','low-PC']].max(axis=1)
    return TR



# var float center = na
# float lastpp = ph ? ph : pl ? pl : na
# if lastpp
#     if na(center)
#         center := lastpp
#     else
#         //weighted calculation
#         center := (center * 2 + lastpp) / 3

# // upper/lower bands calculation
# Up = center - (Factor * atr(Pd))
# Dn = center + (Factor * atr(Pd))


# Up = center - (Factor * atr(Pd))
# Dn = center + (Factor * atr(Pd))

# // get the trend
# float TUp = na
# float TDown = na
# Trend = 0
# TUp := close[1] > TUp[1] ? max(Up, TUp[1]) : Up
# TDown := close[1] < TDown[1] ? min(Dn, TDown[1]) : Dn
# Trend := close > TDown[1] ? 1: close < TUp[1]? -1: nz(Trend[1], 1)
# Trailingsl = Trend == 1 ? TUp : TDown



#calculating PivotPoint
def pivotPoint(df):
    df['PP'] = (df['high']+df['low']+df['close'])/3
    #S1= (P x 2) – Previous high
    df['PLow'] = (df['PP'] * 2) - df['high']
    #R1 = (P x 2) – Previous Low
    df['PHigh'] = (df['PP']*2) - df['low']
    return df










#calculating ATR
def ATR(df,period=10):
    df['TrueRange'] = trueRange(df)
    getAtr = df['TrueRange'].rolling(period).mean()
    return getAtr
#Plotting Basic Bands 
# fig = px.line(df,x='time',y=['close','upperBand','lowerBand'])
# fig.show()

def getSuperTrend(df,period=10,multiplier=1.5):
    
    
    #populating ATR and making Bands
    df['atr'] = ATR(df,period=period)
    df = pivotPoint(df)
    df['upperBand'] = (df['PHigh']) + (multiplier * df['atr'])
    df['lowerBand'] = (df['PLow']) - (multiplier * df['atr'])
    # df['upperBand'] = ((df['high'] + df['low'])/ 2) + (multiplier * df['atr'])
    # df['lowerBand'] = ((df['high'] + df['low'])/ 2) - (multiplier * df['atr'])
    
    #Calculating and Populating EMA
    df['ema'] = trend.ema_indicator(df['close'],window=200)

    #Making SuperTrend
    df['superTrend'] = True
    for curr in range(1,len(df.index)):
        prev = curr - 1
        if df['close'][curr] > df['upperBand'][prev]:
             df['superTrend'][curr] = True
        # if current close price crosses below lowerband
        elif df['close'][curr] < df['lowerBand'][prev]:
             df['superTrend'][curr] = False
        # else, the trend continues
        else:
            df['superTrend'][curr] =  df['superTrend'][prev]


            if  df['superTrend'][curr] == True and df['lowerBand'][curr] < df['lowerBand'][prev]:
                df['lowerBand'][curr] = df['lowerBand'][prev]
            if  df['superTrend'][curr] == False and df['upperBand'][curr] > df['upperBand'][prev]:
                df['upperBand'][curr] = df['upperBand'][prev]
        if df['superTrend'][curr] == True:
            df['upperBand'][curr] = np.nan
        else:
            df['lowerBand'][curr] = np.nan
    return df

getSuperTrend(df)







#plotting data and Saving into a Csv File.
# def plottingData(df):
#     plt.plot(df['close'], label='Close Price')
#     plt.plot(df['lowerBand'], 'g', label = 'Final Lowerband')
#     plt.plot(df['upperBand'], 'r', label = 'Final Upperband')
#     plt.plot(df['ema'], 'black', label = 'ema')
#     plt.show()
   


def generateSignal(df):
    #Kinds of Buy 
    #1. If SuperTrend > 200EMA and SuperTrend changes to True then return 'Buy'
    #2. If SuperTrend is previously True (Buy Signal) but Price(Close Price) < 200 then wait for Price to Break 200 EMA and then return 'emaBuy'
    #3. If SuperTrend < 200EMA and SuperTrend changes to False then return 'Sell'
    #4. If SuperTrend is previously False (Sell Signal) but Price(Close Price) > 200EMA then wait for Price to breakdown 200EMA and then return 
    #'emaSell'
    #5. No Buy Trade if Price is Below 200EMA and Buy signal pop then return '-1'
    #6. No Sell Trade if Price is Above 200EMA and Sell signal POPS. '-1'
    df['signal'] = 'NoPosition'
    for curr in range(199,len(df.index)):
        prev = curr - 1          
        if df['close'][curr] > df['ema'][curr] and df['superTrend'][prev] == False and df['superTrend'][curr] == True:
            df['signal'][curr] = 'Buy'
        elif df['close'][curr] < df['ema'][curr] and df['superTrend'][prev] == True and df['superTrend'][curr] == False:
            df['signal'][curr] = 'Sell'
        elif df['close'][prev] < df['ema'][prev] and df['close'][curr] > df['ema'][curr] and df['superTrend'][prev] == True and df['superTrend'][curr] == True:
            df['signal'][curr] = 'emaBuy'
        elif df['close'][prev] > df['ema'][prev] and df['close'][curr] < df['ema'][curr] and df['superTrend'][prev] == False and df['superTrend'][curr] == False:
            df['signal'][curr]= 'emaSell'
    return df

# df = generateSignal(df)
# print(df)
# df.to_csv('superTrendsignal.csv')
# count = 0
# for curr in range(199,len(df.index)):
#     if df['signal'][curr] == 'Buy' or df['signal'][curr] == 'emaBuy' or df['signal'][curr] == 'Sell' or df['signal'][curr] == 'emaSell':
#         count+=1
# print('Total Positions: ', count)



#Backtesting Script Starts from here
# class Position:
#     def __init__(self, open_datetime, open_price, order_type, volume, sl, tp):
#         self.open_datetime = open_datetime
#         self.open_price = open_price
#         self.order_type = order_type
#         self.volume = volume
#         self.sl = sl
#         self.tp = tp
#         self.close_datetime = None
#         self.close_price = None
#         self.profit = None
#         self.status = 'open'
        
#     def close_position(self, close_datetime, close_price):
#         self.close_datetime = close_datetime
#         self.close_price = close_price
#         self.profit = (self.close_price - self.open_price) * self.volume if self.order_type == 'Buy' or self.order_type == 'emaBuy' \
#                                                                         else (self.open_price - self.close_price) * self.volume
#         self.status = 'closed'
        
#     def _asdict(self):
#         return {
#             'open_datetime': self.open_datetime,
#             'open_price': self.open_price,
#             'order_type': self.order_type,
#             'volume': self.volume,
#             'sl': self.sl,
#             'tp': self.tp,
#             'close_datetime': self.close_datetime,
#             'close_price': self.close_price,
#             'profit': self.profit,
#             'status': self.status,
#         }
        
        
# class Strategy:
#     def __init__(self, df, starting_balance, volume):
#         self.starting_balance = starting_balance
#         self.volume = volume
#         self.positions = []
#         self.data = df
        
#     def get_positions_df(self):
#         df = pd.DataFrame([position._asdict() for position in self.positions])
#         df['pnl'] = df['profit'].cumsum() + self.starting_balance
#         return df
        
#     def add_position(self, position):
#         self.positions.append(position)
        
#     def trading_allowed(self):
#         for pos in self.positions:
#             if pos.status == 'open':
#                 return False
        
#         return True
#     #setting Stop-Loss
#     def settingSL(self,index,signalType):
#         # Setting SL 5 pips below the Value of lowerBand for Buy Signal
#         if signalType == 'Buy' or signalType == 'emaBuy':
#             SL = self.data['lowerBand'][index] - 0.0005
#         #setting SL above 5 pips of UpperBand for Sell Signal
#         elif signalType == 'Sell' or signalType == 'emaSell':
#             SL = self.data['upperBand'][index] + 0.0005
#         return SL
#     #setting Take profit
#     def settingTP(self,index,signalType):
        
#         #Setting TP on the Closing price of candle Where the Trend Changes from Buy to Sell or True to Flase
#         if signalType == 'Buy' or signalType == 'emaBuy':
#             for curr in (index,len(self.data)):
#                 if self.data['superTrend'][curr] == False:
#                     TP = self.data['open'][curr]
#                     break
#             return TP
#         elif signalType == 'Sell' or signalType == 'emaSell':
#             for curr in (index,len(self.data)):
#                 if self.data['superTrend'][curr] == True:
#                     TP = self.data['open'][curr]
#                     break
#             return TP

            


#     def run(self):
#         for i, data in self.data.iterrows():
            
#             if data.signal == 'Buy' or data.signal == 'emaBuy' and self.trading_allowed():
#                 sl = self.settingTP(i,data.signal)
#                 tp = self.settingTP(i,data.signal)
#                 self.add_position(Position(data.time, data.close, data.signal, self.volume, sl, tp))
                
#             elif data.signal == 'Sell' or data.signal == 'emaSell' and self.trading_allowed():
#                 sl = self.settingTP(i,data.signal)
#                 tp = self.settingTP(i,data.signal)
#                 self.add_position(Position(data.time, data.close, data.signal, self.volume, sl, tp))
                
#             for pos in self.positions:
#                 if pos.status == 'open':
#                     if (pos.sl >= data.close and pos.order_type == 'Buy' or pos.order_type == 'emaBuy'):
#                         pos.close_position(data.time, pos.sl)
#                     elif (pos.sl <= data.close and pos.order_type == 'Sell' or pos.order_type == 'emaSell'):
#                         pos.close_position(data.time, pos.sl)
#                     elif (pos.tp <= data.close and pos.order_type == 'Buy' or pos.order_type == 'emaBuy'):
#                         pos.close_position(data.time, pos.tp)
#                     elif (pos.tp >= data.close and pos.order_type == 'Sell' or pos.order_type == 'emaSell'):
#                         pos.close_position(data.time, pos.tp)
                        
#         return self.get_positions_df()  



# superTrend_Strat = Strategy(df, 15000, 100000)

# result = superTrend_Strat.run()
# TotalSum = result['profit'].sum()
# print("Total Profit: ",TotalSum)
# maxLoss = result['profit'].min()
# print("Max Loss: ",maxLoss)
# maxProfit = result['profit'].max()
# print("Max Profit: ",maxProfit)
# result['profit'].values.flatten()
# totalLosses = sum(n < 0 for n in result['profit'].values.flatten())
# print("Total Losses = ", totalLosses)
# totalWins = sum(n > 0 for n in result['profit'].values.flatten())
# print("Total Wins = ", totalWins)
# print("Maximum Account value Reached: ", result['pnl'].max())
# print("Maximum Account Drawdown limit reached: ",result['pnl'].min())

# result.to_csv('SuperTrendResult.csv')

        
