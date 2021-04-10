import sys
from dataFetcher import PlotStock
from PyQt5.QtWidgets import QApplication, QWidget

class StokViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initChart()

    def initUI(self):
        self.resize(1100, 650)
        self.setWindowTitle("Stok Viewer")
        self.show()

    def initChart(self):
        plotter = PlotStock()
        plotter.plot()

def main():
    app = QApplication(sys.argv)
    stok = StokViewer()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()