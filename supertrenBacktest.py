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



class Position:
    def __init__(self, open_datetime, open_price, order_type, volume, sl, tp):
        self.open_datetime = open_datetime
        self.open_price = open_price
        self.order_type = order_type
        self.volume = volume
        self.sl = sl
        self.tp = tp
        self.close_datetime = None
        self.close_price = None
        self.profit = None
        self.status = 'open'
        
    def close_position(self, close_datetime, close_price):
        self.close_datetime = close_datetime
        self.close_price = close_price
        self.profit = (self.close_price - self.open_price) * self.volume if self.order_type == 'Buy' or self.order_type == 'emaBuy' \
                                                                        else (self.open_price - self.close_price) * self.volume
        self.status = 'closed'
        
    def _asdict(self):
        return {
            'open_datetime': self.open_datetime,
            'open_price': self.open_price,
            'order_type': self.order_type,
            'volume': self.volume,
            'sl': self.sl,
            'tp': self.tp,
            'close_datetime': self.close_datetime,
            'close_price': self.close_price,
            'profit': self.profit,
            'status': self.status,
        }
        
        
class Strategy:
    def __init__(self, df, starting_balance, volume):
        self.starting_balance = starting_balance
        self.volume = volume
        self.positions = []
        self.data = df
        
    def get_positions_df(self):
        df = pd.DataFrame([position._asdict() for position in self.positions])
        df['pnl'] = df['profit'].cumsum() + self.starting_balance
        return df
        
    def add_position(self, position):
        self.positions.append(position)
        
    def trading_allowed(self):
        for pos in self.positions:
            if pos.status == 'open':
                return False
        
        return True
    #setting Stop-Loss
    def settingSL(self,index,signalType):
        # Setting SL 5 pips below the Value of lowerBand for Buy Signal
        if signalType == 'Buy' or signalType == 'emaBuy':
            SL = self.data['vwap'][index] - 0.5
        #setting SL above 5 pips of UpperBand for Sell Signal
        elif signalType == 'Sell' or signalType == 'emaSell':
            SL = self.data['vwap'][index] + 0.5
        return SL
    #setting Take profit
    def settingTP(self,index,signalType):
        
        #Setting TP on the Closing price of candle Where the Trend Changes from Buy to Sell or True to Flase
        if signalType == 'Buy' or signalType == 'emaBuy':
            # SL = self.data['lowerBand'][index] - 0.5
            # TP = self.data['close'][index] - SL 
            # TP = 1.5 * TP
            # TP = self.data['close'][index] + TP
            # return TP
            for curr in range(index,len(self.data.index)):
                if self.data['superTrend'][curr] == False:
                    TP = self.data['open'][curr]
                    return TP
                    
                elif self.data['signal'][curr] == '-1':
                    TP = self.data['close'][curr]
                    return TP
                    
            
        elif signalType == 'Sell' or signalType == 'emaSell':
                # SL = self.data['upperBand'][index] + 0.5
                # TP = SL - self.data['close'][index]
                # TP = 1.5 * TP
                # TP = self.data['close'][index] - TP
                # return TP
            for curr in range(index,len(self.data.index)):
                if self.data['superTrend'][curr] == True:
                    TP = self.data['open'][curr]
                    return TP
                   
                elif self.data['signal'][curr] == '-1':
                    TP = self.data['close'][curr]
                    return TP
                    
                

            


    def run(self):
        for i, data in self.data.iterrows():
            
            if data.signal == 'Buy' or data.signal == 'emaBuy' and self.trading_allowed():
                sl = self.settingTP(i,data.signal)
                tp = self.settingTP(i,data.signal)
                self.add_position(Position(data.time, data.close, data.signal, self.volume, sl, tp))
                
            elif data.signal == 'Sell' or data.signal == 'emaSell' and self.trading_allowed():
                sl = self.settingTP(i,data.signal)
                tp = self.settingTP(i,data.signal)
                self.add_position(Position(data.time, data.close, data.signal, self.volume, sl, tp))
             
                
            for pos in self.positions:
                if pos.status == 'open':
                    if (pos.sl >= data.close and pos.order_type == 'Buy' or pos.order_type == 'emaBuy'):
                        pos.close_position(data.time, pos.sl)
                    elif (pos.sl <= data.close and pos.order_type == 'Sell' or pos.order_type == 'emaSell'):
                        pos.close_position(data.time, pos.sl)
                    elif (pos.tp <= data.close and pos.order_type == 'Buy' or pos.order_type == 'emaBuy'):
                        pos.close_position(data.time, pos.tp)
                    elif (pos.tp >= data.close and pos.order_type == 'Sell' or pos.order_type == 'emaSell'):
                        pos.close_position(data.time, pos.tp)
                    

                    
                        
        return self.get_positions_df()  


df = pd.read_csv('superTrendsignal.csv')
superTrend_Strat = Strategy(df, 15000, 100)

result = superTrend_Strat.run()
TotalSum = result['profit'].sum()
print("Total Profit: ",TotalSum)
maxLoss = result['profit'].min()
print("Max Loss: ",maxLoss)
maxProfit = result['profit'].max()
print("Max Profit: ",maxProfit)
result['profit'].values.flatten()
totalLosses = sum(n < 0 for n in result['profit'].values.flatten())
print("Total Losses = ", totalLosses)
totalWins = sum(n > 0 for n in result['profit'].values.flatten())
print("Total Wins = ", totalWins)
print("Maximum Account value Reached: ", result['pnl'].max())
print("Maximum Account Drawdown limit reached: ",result['pnl'].min())

result.to_csv('SuperTrendResult.csv')

        
