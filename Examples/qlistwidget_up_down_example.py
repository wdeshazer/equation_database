"""
Example from: https://stackoverflow.com/a/57915796/9705687

Easy Text Example from: https://stackoverflow.com/questions/10957392/moving-items-up-and-down-in-a-qlistwidget
"""

import sys
import random
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QWidget,
    QHBoxLayout, QVBoxLayout, QApplication, QListWidget, QTextEdit,
    QListWidgetItem, QLayout, QLineEdit)


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        addButton = QPushButton('+')
        addButton.clicked.connect(self.addrow)
        delButton = QPushButton('-')
        delButton.clicked.connect(self.delrow)
        upButton = QPushButton('▲', parent = self)
        upButton.clicked.connect(self.rowup)
        downButton = QPushButton('▼', parent = self)
        downButton.clicked.connect(self.rowdown)

        hbox = QHBoxLayout()
        hbox.addWidget(addButton)
        hbox.addWidget(delButton)
        hbox.addWidget(upButton)
        hbox.addWidget(downButton)

        self.listbox = QListWidget()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.listbox)
        vbox.setStretch(0,1)
        vbox.setStretch(1,4)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Test')
        self.show()

    def rowup(self):

        row_num = self.listbox.currentRow()

        if row_num > 0:
            row = self.listbox.itemWidget(self.listbox.currentItem())
            itemN = self.listbox.currentItem().clone()

            self.listbox.insertItem(row_num -1, itemN)
            self.listbox.setItemWidget(itemN, row)

            self.listbox.takeItem(row_num+1)
            self.listbox.setCurrentRow(row_num-1)

    def rowdown(self):

        row_num = self.listbox.currentRow()

        if row_num == -1:
            # no selection. abort
            return
        elif row_num < self.listbox.count():
            row = self.listbox.itemWidget(self.listbox.currentItem())
            itemN = self.listbox.currentItem().clone()


            self.listbox.insertItem(row_num + 2, itemN)
            self.listbox.setItemWidget(itemN, row)

            self.listbox.takeItem(row_num)
            self.listbox.setCurrentRow(row_num+1)

    def addrow(self):
        row = self.makerow()
        itemN = QListWidgetItem()
        itemN.setSizeHint(row.sizeHint())

        self.listbox.addItem(itemN)  # add itemN to end of list. use insertItem
                                     # to insert in specific location
        self.listbox.setItemWidget(itemN, row)


    def delrow(self):
        if self.listbox.currentRow() == -1:
            # no selection. delete last row
            row_num = self.listbox.count() - 1
        else:
            row_num = self.listbox.currentRow()

        item = self.listbox.takeItem(row_num)

        del item

    def makerow(self):

        widget = QWidget()
        hbox = QHBoxLayout()
        r = random.random()
        r = '%f' % r
        print(r)
        label = QLabel(r)
        textedit = QLineEdit()
        button = QPushButton('Ouvrir reference art %s' % r)
        hbox.addWidget(label)
        hbox.addWidget(textedit)
        hbox.addWidget(button)
        hbox.addStretch()
        hbox.setSizeConstraint(QLayout.SetFixedSize)


        widget.setLayout(hbox)

        return widget


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
