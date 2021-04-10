import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout,
QVBoxLayout, QLabel, QStackedWidget)
import matplotlib
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.animation as anim
from dataFetcher import DataFetcher
from custplot import custplot, getRsi

matplotlib.use("QT5Agg")

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(1100, 650)
        self.setWindowTitle("Stok Viewer")
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        dailyBtn = QPushButton("Daily", self)
        weeklyBtn = QPushButton("Weeky", self)
        monthlyBtn = QPushButton("Monthly", self)
        dailyBtn.clicked.connect(lambda: self.plot("day"))
        weeklyBtn.clicked.connect(lambda: self.plot("week"))
        monthlyBtn.clicked.connect(lambda: self.plot("month"))
        timelineBtnBox = QHBoxLayout()
        timelineBtnBox.addStretch(1)
        timelineBtnBox.addWidget(dailyBtn)
        timelineBtnBox.addWidget(weeklyBtn)
        timelineBtnBox.addWidget(monthlyBtn)

        # widgets and layouts for plotting
        self.ybuffer = 5.5 # buffer area for bottom and top(%)
        self.zoomSpeed = 5 # How much area to zoom for one scroll
        self.figure = Figure()
        self.canvas = Canvas(self.figure)
        self.canvas.mpl_connect("button_press_event", self.onPressEvent)
        self.canvas.mpl_connect("button_release_event", self.onReleaseEvent)
        self.canvas.mpl_connect("scroll_event", self.onScrollEvent)
        self.chartBox = QHBoxLayout()
        self.chartBox.addWidget(self.canvas)
        vbox.addLayout(timelineBtnBox)
        vbox.addLayout(self.chartBox)
        self.plot("day")
        self.show()

    def plot(self, timeline=""):
        self.figure.clf()
        self.df = DataFetcher.getStockByTimeline("006400.KS", timeline)
        self.ax = self.figure.add_subplot()
        rsiList = getRsi(self.df)
        self.canvas.draw_idle()
        custplot(self.ax, self.df)

        ### 중복되는 기능, delete it later
        self.lineEndList = []
        self.lineStartList = []
        for obj in self.ax.get_children():
            if type(obj) is type(matplotlib.collections.LineCollection([])):
                self.lineStartList.append(obj.get_paths()[0].get_extents().get_points()[0][1])
                self.lineEndList.append(obj.get_paths()[0].get_extents().get_points()[1][1])
        ###
        self.autoscale()

    def onPressEvent(self, event):
        # check if the pressed button was "LEFT"
        if not event.button == 1:
            return

        self.lineEndList = []
        self.lineStartList = []
        for obj in self.ax.get_children():
            if type(obj) is type(matplotlib.collections.LineCollection([])):
                self.lineStartList.append(obj.get_paths()[0].get_extents().get_points()[0][1])
                self.lineEndList.append(obj.get_paths()[0].get_extents().get_points()[1][1])

        for obj in self.ax.get_children():
            if type(obj) is type(matplotlib.patches.Rectangle):
                break
                #print(obj)

        self.xStart = self.ax.get_xlim()[0]
        self.xCursor = event.x
        self.cidDrag = self.canvas.mpl_connect("motion_notify_event", self.onDragEvent)

    def onDragEvent(self, event):
        xlim = self.ax.get_xlim()
        # make drag limits to prevent overflow
        ###
        # IMPLMENT PENDING
        ###
        movement = (event.x - self.xCursor) / 10
        self.xCursor = event.x
        self.ax.set_xlim(xlim[0] - movement, xlim[1] - movement)
        self.autoscale()
        self.canvas.draw_idle()

    def onReleaseEvent(self, event):
        self.canvas.mpl_disconnect(self.cidDrag)

    # method for getting new range of axes and updating them to the df
    def updateAxes(self):
        # calculate how much x axis was moved
        xlim = self.ax.get_xlim()
        xEnd = -xlim[0]
        
        # get new df
        ogdate = self.df["Date"].iloc[0]
        newdf = DataFetcher.getStockByDate("006400.KS", ogdate, xEnd)
        newax = custplot(self.ax, newdf, timeline="day")

        # update the new df to the ax
        background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(newax)
        self.canvas.blit(self.ax.bbox)

    def onScrollEvent(self, event):
        xlim = self.ax.get_xlim()
        width = xlim[1] - xlim[0]
        if event.button == "up" or event.button == "down":
            if event.button == "up":
                xmin = xlim[0] + (width / 100 * self.zoomSpeed)
                xmax = xlim[1] - (width / 100 * self.zoomSpeed)
            else:
                xmin = xlim[0] - (width / 100 * self.zoomSpeed)
                xmax = xlim[1] + (width / 100 * self.zoomSpeed)
            self.ax.set_xlim(xmin, xmax)
            self.autoscale()
            self.canvas.draw_idle()
        else:
            print("error: unrecognized scroll movement")

    # method for autoscaling y axis heights according to y limits
    def autoscale(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        # check if updating lines are out of bound
        start = int(xlim[0]) if int(xlim[0]) > 0 else 0
        end = int(xlim[1]) if int(xlim[1]) < len(self.df["High"]) else (len(self.df["High"]) - 1)
        # get the highest and lowest point of y from start to end
        highest = max(self.lineEndList[start:end+1])
        lowest = min(self.lineStartList[start:end+1])

        height = highest - lowest
        self.ax.set_ylim(lowest - (height / 100 * self.ybuffer), 
            highest + (height / 100 * self.ybuffer))

app = QApplication(sys.argv)
gui = MainWidget()
sys.exit(app.exec_())
