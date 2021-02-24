"""
https://stackoverflow.com/questions/43667782/pyqt4-filter-by-text-on-a-qlistview-using-setrowhidden
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent=parent)
        vLayout = QVBoxLayout(self)
        hLayout = QHBoxLayout()

        self.lineEdit = QLineEdit(self)
        hLayout.addWidget(self.lineEdit)

        self.filter = QPushButton("filter", self)
        hLayout.addWidget(self.filter)
        self.filter.clicked.connect(self.filterClicked)

        self.list = QListView(self)

        vLayout.addLayout(hLayout)
        vLayout.addWidget(self.list)

        self.model = QStandardItemModel(self.list)

        codes = [
            'LOAA-05379',
            'LOAA-04468',
            'LOAA-03553',
            'LOAA-02642',
            'LOAA-05731'
        ]

        for code in codes:
            item = QStandardItem(code)
            item.setCheckable(True)
            self.model.appendRow(item)
        self.list.setModel(self.model)

    def filterClicked(self):
        filter_text = str(self.lineEdit.text()).lower()
        for row in range(self.model.rowCount()):
            if filter_text in str(self.model.item(row).text()).lower():
                self.list.setRowHidden(row, False)
            else:
                self.list.setRowHidden(row, True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dialog()
    ex.show()
    sys.exit(app.exec_())
