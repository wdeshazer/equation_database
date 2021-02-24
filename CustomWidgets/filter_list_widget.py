"""
    Filter List Widget with add remove buttons
"""
import sys
from typing import Union
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListView, QLineEdit,
    QSizePolicy, QListWidgetItem, QFrame, QLabel
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from CustomWidgets.add_remove_buttons import EDAddRemoveButtons


class EDFilterListWidget(QWidget):
    """FilterListWidget Combines a QLineEdit and a QListView"""
    add = pyqtSignal()
    remove = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()

        filter_frame = QFrame(self)
        filter_h_layout = QHBoxLayout(filter_frame)
        filter_h_layout.setContentsMargins(0, 0, 0, 0)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        filter_frame.setSizePolicy(size_policy)

        filter_lbl = QLabel("Filter")
        self.line_edit = QLineEdit(self)

        filter_h_layout.addWidget(filter_lbl)
        filter_h_layout.addWidget(self.line_edit)

        h_layout.addWidget(filter_frame)
        self.line_edit.textEdited.connect(self.filter)

        self.list = QListView(self)
        self.model = QStandardItemModel(self.list)
        self.list.setModel(self.model)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list.setSizePolicy(size_policy)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.list)

        self.controls = EDAddRemoveButtons(parent=self)
        self.controls.add_btn.clicked.connect(self.add_item)
        self.controls.rm_btn.clicked.connect(self.remove_item)
        v_layout.addWidget(self.controls)

    def filter(self, filter_text):
        """Hides rows that do not have the pattern"""
        for row in range(self.model.rowCount()):
            if filter_text in str(self.model.item(row).text()).lower():
                self.list.setRowHidden(row, False)
            else:
                self.list.setRowHidden(row, True)

    @pyqtSlot()
    def add_item(self):
        """Add item"""
        self.add.emit()

    @pyqtSlot()
    def remove_item(self):
        """Remove Item"""
        self.remove.emit()

    def clear(self):
        """Clear the model"""
        self.model.clear()

    # pylint: disable=invalid-name
    def takeItem(self, row: int):
        """Take Item from the list"""
        item = self.model.takeItem(row)
        self.model.takeRow(row)
        return item

    # pylint: disable=invalid-name
    def addItem(self, item: Union[QListWidgetItem, QStandardItem, str]):
        """Add Item to the list"""
        if isinstance(item, str):
            item = QStandardItem(item)
        self.model.appendRow(item)

    def count(self):
        """Convenience method"""
        return self.model.rowCount()

    def item(self, row):
        """Convenience method to reveal model method"""
        return self.model.item(row)

    # pylint: disable=invalid-name
    def selectedIndexes(self):
        """Convenience Function to revel selectionModel option"""
        return self.list.selectionModel().selectedIndexes()

    # pylint: disable=invalid-name
    def selectedItems(self):
        """Convenience to replicate functionality in QListWidget"""
        inds = self.selectedIndexes()
        items = [self.item(i.row()) for i in inds]
        return items


if __name__ == '__main__':
    app = QApplication(sys.argv)
    codes = [
        'LOAA-05379',
        'LOAA-04468',
        'LOAA-03553',
        'LOAA-02642',
        'LOAA-05731'
    ]

    ex = EDFilterListWidget()

    for code in codes:
        an_item = QStandardItem(code)
        an_item.setCheckable(True)
        ex.model.appendRow(an_item)

    ex.show()
    sys.exit(app.exec_())
