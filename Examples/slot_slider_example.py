"""
https://stackoverflow.com/questions/36434706/pyqt-proper-use-of-emit-and-pyqtsignal
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLCDNumber, QSlider, QVBoxLayout
)
from PyQt5.QtCore import pyqtSlot, Qt


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.lcd = QLCDNumber(self)
        self.sld = QSlider(Qt.Horizontal, self)
        self.initUI()

    @staticmethod
    def print_label(value):
        print(value)

    def log_label(self, value):
        """log to a file"""
        pass

    @pyqtSlot(int)
    def on_sld_valueChanged(self, value):
        self.lcd.display(value)
        self.print_label(value)
        self.log_label(value)

    def initUI(self):

        vbox = QVBoxLayout()
        vbox.addWidget(self.lcd)
        vbox.addWidget(self.sld)

        self.setLayout(vbox)
        self.sld.valueChanged.connect(self.on_sld_valueChanged)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Signal & slot')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
