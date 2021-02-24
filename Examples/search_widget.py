import sys
# from PyQt4.QtGui  import *
# from PyQt4.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        self.le_search = QLineEdit()  # self.   +++

        se_btn = QPushButton("Search")
        se_btn.clicked.connect(self.find_item)

        self.listwidget = QListWidget()
        self.total_list = ["machine", "mac1", "printer", "Printer", "xerox bundles", "2mac"]
        self.listwidget.addItems(self.total_list)

        hbox = QHBoxLayout()
        hbox.addWidget(self.le_search)  # self.   +++
        hbox.addWidget(se_btn)

        auto_search_vbox = QVBoxLayout(self)
        auto_search_vbox.addLayout(hbox)
        auto_search_vbox.addWidget(self.listwidget)

    def find_item(self):
        #        out = self.listwidget.findItems("mac", QtCore.Qt.MatchExactly)          # ---
        #        out = self.listwidget.findItems(self.le_search.text(), Qt.MatchExactly)
        out = self.listwidget.findItems(self.le_search.text(),
                                        Qt.MatchContains |  # +++
                                        Qt.MatchCaseSensitive)  # +++

        print("out->", [i.text() for i in out])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
