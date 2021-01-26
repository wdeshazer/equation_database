from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

class Handle(QWidget):
    def paintEvent(self, e=None):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.Dense6Pattern)
        painter.drawRect(self.rect())

class customSplitter(QSplitter):
    def addWidget(self, wdg):
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*2, self.width*10)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(l_handle)

class Window(QMainWindow):
    def setUI(self, MainWindow):
        self.splt_v = customSplitter(Qt.Vertical)
        self.splt_v.setHandleWidth(100)
        self.splt_v.addWidget(QGroupBox("Box 1"))
        self.splt_v.addWidget(QGroupBox("Box 2"))
        self.splt_v.addWidget(QGroupBox("Box 3"))

        self.wdg = QWidget()
        self.v_lt = QVBoxLayout(self.wdg)
        self.v_lt.addWidget(self.splt_v)

        self.spl_h = customSplitter()
        self.spl_h.addWidget(self.wdg)
        self.spl_h.addWidget(QGroupBox("Box 4"))
        self.spl_h.addWidget(QGroupBox("Box 5"))

        self.h_lt = QHBoxLayout()
        self.h_lt.addWidget(self.spl_h)
        self.w = QWidget()
        self.w.setLayout(self.h_lt)
        self.w.setGeometry(0,0,1280,720)
        self.w.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Window()
    ui.setUI(MainWindow)
    sys.exit(app.exec_())