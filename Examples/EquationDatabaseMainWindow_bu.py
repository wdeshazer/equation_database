import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter,
    QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox,
    QLabel, QLineEdit
)
from scipy.constants import golden_ratio


class Handle(QWidget):
    def paintEvent(self, e=None):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.Dense6Pattern)
        painter.drawRect(self.rect())


class customSplitter(QSplitter):

    def __init__(self, *args):
        super(customSplitter, self).__init__(*args)
        self.width = None

    def addWidget(self, wdg):
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*2, self.width*10)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(l_handle)


class Window(QMainWindow):

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        super(Window, self).__init__(*args, **kwargs)

        self.styleSheet = """
            QPushButton {
                background-color: #4e4e4e;
                color: #ffffff;
            }
            
            QMainWindow{
                background-color: #4e4e4e;
            }
            
            QGroupBox{
                font-size: 18pt;
            }

            QGroupBox#eqn_grp_gbox{
                width: 600px;
            }
            
        """

        self.left = 100
        self.top = 300
        self.height = 1500
        self.width = int(self.height * golden_ratio)

        self.splt_v = None
        self.wdg = None
        self.v_lt = None
        self.spl_h = None
        self.h_lt = None
        self.w = None
        self.details_v_lt = None
        self.details_gbox = QGroupBox("Equation Details")  # type: QGroupBox
        self.details_upper_hbox = None  # type: QHBoxLayout

        self.setUI()

        sys.exit(self.app.exec_())

    def setUI(self):
        self.splt_v = customSplitter(Qt.Vertical)
        self.splt_v.setHandleWidth(8)

        self.setupLeftBox()

        self.wdg = QWidget()
        self.v_lt = QVBoxLayout(self.wdg)
        self.v_lt.addWidget(self.splt_v)

        self.details_v_lt = QVBoxLayout()
        self.details_upper_hbox = QHBoxLayout()
        self.setupUpperDetails()

        spl_h = customSplitter()
        spl_h.addWidget(self.wdg)
        latex_gbox = QGroupBox("LaTeX")
        spl_h.addWidget(latex_gbox)
        variables_gbox = QGroupBox("Variables")
        spl_h.addWidget(variables_gbox)

        self.spl_h = spl_h

        self.h_lt = QHBoxLayout()
        self.h_lt.addWidget(self.spl_h)
        self.w = QWidget()
        self.w.setLayout(self.h_lt)
        self.w.setGeometry(self.left, self.top, self.width, self.height)
        self.w.show()
        self.app.setStyleSheet(self.styleSheet)

    def setupLeftBox(self):
        eq_grp_gbox = QGroupBox('Equation Group')
        eq_grp_gbox.setObjectName('eqn_grp_gbox')
        self.splt_v.addWidget(eq_grp_gbox)
        # self.splt_v_eq_group.addWidget(QGroupBox("Box 2"))
        # self.splt_v_eq_group.addWidget(QGroupBox("Box 3"))

    def setupUpperDetails(self):
        eq_name_hbox = QHBoxLayout()
        eq_name_lbl = QLabel('Name')
        eq_name_ledit = QLineEdit()
        eq_name_hbox.addWidget(eq_name_lbl)
        eq_name_hbox.addWidget(eq_name_ledit)
        self.details_upper_hbox.ad


if __name__ == '__main__':
    ui = Window()
