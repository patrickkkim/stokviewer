import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from datetime import datetime

# How much x label to appear in the x axis(tick + 1)
tick = 5

def custplot(ax, df, chartType="", timeline=""):
    # Plot vertical lines and boxes
    xticklabelList = np.array([])
    if timeline == "week" or timeline == "month":
        counter = 0
        if timeline == "week":
            step = 5
        else:
            step = 30
        for i in range(0, df["Date"].size, step):
            dates = df["Date"].iloc[i:i+step]
            date = dates.iloc[-1]
            xticklabelList = np.append(xticklabelList, date)
            slicedDf = df.iloc[i:i+step]
            low = slicedDf["Low"].min(axis=0)
            high = slicedDf["High"].max(axis=0)
            opn = slicedDf["Open"].iloc[0]
            close = slicedDf["Close"].iloc[-1]
            color, height, bottom = barData(opn, close)
            ax.bar(date, height, 0.8, bottom, color=color, zorder=0.2)
            ax.vlines(date, low, high, color=color, linewidth=0.5, zorder=0.1)
            counter += 1
        labelLen = counter
    else:
        labelLen = df["Date"].size
        for date, low, high, opn, close in zip(
            df["Date"], df["Low"], df["High"], df["Open"], df["Close"]):
            xticklabelList = np.append(xticklabelList, date)
            color, height, bottom = barData(opn, close)
            ax.bar(date, height, 0.8, bottom, color=color, zorder=0.2)
            ax.vlines(date, low, high, color=color, linewidth=0.5, zorder=0.1)

    # Adjust interval tick of xlabel
    setXticks(ax, xticklabelList[labelLen : 0 : -int(labelLen/tick)])

# Calculates data needed for bar plots.(color, height, bottom)
def barData(opn, close):
    if opn > close:
        color = "#ff6960"
        height = opn - close
        bottom = close
    else:
        color = "#00ca73"
        height = close - opn
        bottom = opn
    return (color, height, bottom)

def setXticks(ax, xtickList):
    ax.set_xticks(xtickList)
    ax.set_xticklabels(xtickList)

# RSI = 100 - [100 / (1 + RS)]
# RS = Average Gain / Average Loss
# First Average Gain = Sum of Gains over the past periods(default=14) / 14
#        ``        Loss = Sum of Losses over                 ``
# Average Gain = [(prev Average Gain) * 13 + current Gain] / 14
# Average Loss =                        ``
def getRsi(df, period=14):
    if df["Date"].size < period or period < 2:
        return False

    prevClose = df["Close"].iloc[0]
    gainSum = 0
    lossSum = 0
    for close in df["Close"].iloc[1:period]:
        if close > prevClose:
            # gain
            gainSum += close - prevClose
        else:
            # loss
            lossSum += prevClose - close
        prevClose = close

    avgGain = gainSum / period
    avgLoss = lossSum / period
    
    rsiList = [0] * period
    prevClose = df["Close"].iloc[period-1]
    for close in df["Close"].iloc[period:]:
        if close > prevClose:
            # gain
            gain = close - prevClose
            loss = 0
        else:
            # loss
            loss = prevClose - close
            gain = 0
        avgGain = (avgGain * (period - 1) + gain) / period
        avgLoss = (avgLoss * (period - 1) + loss) / period
        rs = avgGain / avgLoss
        rsi = 100 - (100 / (1 + rs))
        rsiList.append(rsi)
        prevClose = close

    return rsiList

# Simple Moving Average = (A1 + A2 + ... + An) / n
# A = average in period n
# n = number of time periods
def getSMA(df):
    pass

# Exponential Moving Average(today) = [Vt * s / (1 + d)] + EMAy * [1 - s / (1 + d)]
# EMAy = EMA yesterday
# Vt = Value Today
# s = smoothing
# d = number of days
def getEMA(df):
    pass