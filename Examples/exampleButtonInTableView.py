from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    tab = QtWidgets.QTableView()
    sti = QtGui.QStandardItemModel()
    sti.appendRow([QtGui.QStandardItem(str(i)) for i in range(4)])
    tab.setModel(sti)
    tab.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    tab.setIndexWidget(sti.index(0, 3), QtWidgets.QPushButton("button"))
    tab.show()
    sys.exit(app.exec_())