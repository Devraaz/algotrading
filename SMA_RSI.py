from __future__ import print_function
from ctypes import alignment
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import plotly.graph_objects as go
import streamlit as st

from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi





st.title("ALGORITHMIC TRADING")
st.header("MINOR **PROJECT**")
st.write("(This is a small project which will do the Backtesting and show the result whether in 1 yr using this strategy with 1Lac capital you are Profitable or Not)")
tick = st.text_input("Enter Stock Name:  (Add \".ns \" at the end for eg. SBIN.IN)")
data = yf.download(tickers =  tick , period = '300d' , interval = '1d')
data.to_csv('candle.csv')
st.dataframe(data)


fig = go.Figure()
fig.add_trace(go.Candlestick(x = data.index, 
                      open = data['Open'],
                      high = data['High'],
                       close = data['Close'],
                       low = data['Low']
                        
                      ))
fig.update_layout(
    title = tick, 
    yaxis_title = "PRICE", 
    xaxis_title = "DATE"
)

with st.container():
    st.plotly_chart(fig)

# STARTING OF THE PYALGOTRADE



class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, rsiPeriod):
        super(MyStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
    
        
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.__rsi = rsi.RSI(feed[instrument].getPriceDataSeries(), rsiPeriod)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
    
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1] and self.__rsi[-1] > 50.0:
                self.__position = self.enterLong(self.__instrument, 10, True)
    
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod, rsiPeriod):
    st.subheader("Initial Portfolio value: Rs 1,00,000 ")
    feed = quandlfeed.Feed()
    feed.addBarsFromCSV("data", "candle.csv")

    
    myStrategy = MyStrategy(feed, "data", smaPeriod, rsiPeriod)
    myStrategy.run()
    st.subheader("Final portfolio value: Rs%.2f" % myStrategy.getBroker().getEquity())
    global fin, inita
    fin = myStrategy.getBroker().getEquity()
    inita = 100000

    profit = fin-inita
    ROI = (profit/inita)*100

    st.subheader('Profit/Loss: ')
    st.subheader(round(profit, 3))
    st.subheader("ROI: ")
    st.subheader(round(ROI, 3))

run_strategy(50,14)

st.text("")
st.text("")
st.subheader( 'Presented by ')
st.write("Devraj Dora (1801292055)")
st.write("Shailesh Kumar Choudhury( 1921292021)")
st.write("Sanujit Chhotaray (1801292134)")
st.write("Sourav Mohanty (1801292169)")
                
st.write("Complete")


