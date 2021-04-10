import os
import pandas as pd
from pandas_datareader import data
from datetime import datetime

class DataFetcher():
    def fetch():
        if not os.path.isfile("csv/006400.KS.csv"):
            stock = data.DataReader('006400.KS', 'yahoo', datetime(2000, 1, 1))
            stock.to_csv("csv/006400.KS.csv")
            print("csv updated")
        else:
            print("csv already exists")

    def getStockByTimeline(stock, timeline=""):
        df = pd.read_csv("csv/{0}.csv".format(stock))
        df = df.set_index(pd.DatetimeIndex(df["Date"]))
        if timeline == "month":
            offset = pd.DateOffset(years=5)
        elif timeline == "week":
            offset = pd.DateOffset(years=2)
        elif timeline == "day":
            offset = pd.DateOffset(months=6)
        else:
            print("error: timeline not correct")
        offsetDate = pd.to_datetime(datetime.now()) - offset
        dfRange = df.loc[offsetDate.date() : datetime.now().date()]

        return dfRange

    def getStockByDate(stock, ogdatestr, length):
        df = pd.read_csv("csv/{0}.csv".format(stock))
        df = df.set_index(pd.DatetimeIndex(df["Date"]))
        ogdate = pd.to_datetime(ogdatestr).date() - pd.DateOffset(days=1)
        newdate = ogdate - pd.DateOffset(days=int(length))
        dfRange = df.loc[newdate:ogdate]

        return dfRange

    def getStock(stock):
        df = pd.read_csv("csv/{0}.csv".format(stock))
        return df
