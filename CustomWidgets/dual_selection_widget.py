"""
    Filter List Widget with add remove buttons
"""
import sys
from typing import Optional
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QSplitter, QMessageBox
)
from PyQt5.QtGui import QPainter, QBrush, QColor
from CustomWidgets.shift_buttons import EDShiftButtons
from CustomWidgets.filter_list_widget import EDFilterListWidget


class Handle(QWidget):
    """Handle for Sliders"""

    def paintEvent(self, e=None):  # pylint: disable=invalid-name, unused-argument, missing-function-docstring
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(133, 45, 145), Qt.Dense5Pattern))
        painter.drawRect(self.rect())


class Customsplitter(QSplitter):
    """Splitter with no Margins and using handle"""

    def __init__(self, *args):
        super().__init__(*args)
        self.width = None

    def addWidget(self, wdg):  # pylint: disable=invalid-name
        """Add Widget with Custom Handle"""
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width * 10, self.width * 12)
        layout = QHBoxLayout(self.handle(self.count() - 1))
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(l_handle)


class EDDualSelectorWidget(QWidget):
    """FilterListWidget Combines a QLineEdit and a QListView"""
    shift_right = pyqtSignal(int)
    shift_left = pyqtSignal(int)
    isConditionalAccept: bool = False

    def __init__(self, parent=None, model_widget: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.msg_box = self._default_message_box(model_widget)

        v_layout = QVBoxLayout(self)
        splitter = Customsplitter(Qt.Horizontal)  # Note Handle for a vert splitter is oriented Horizontally

        self.controls = EDShiftButtons(parent=splitter)
        self.controls.shift_right_btn.clicked.connect(self.shift_item_right)
        self.controls.shift_left_btn.clicked.connect(self.shift_item_left)

        self.left_f_list = EDFilterListWidget(parent=splitter)

        left_frame = QFrame(self)
        h_layout = QHBoxLayout(left_frame)
        h_layout.addWidget(self.left_f_list)
        h_layout.addWidget(self.controls)
        splitter.addWidget(left_frame)

        self.right_f_list = EDFilterListWidget(parent=splitter)
        right_frame = QFrame(self)
        h_layout_2 = QHBoxLayout(right_frame)
        h_layout_2.addWidget(self.right_f_list)
        splitter.addWidget(right_frame)

        v_layout.addWidget(splitter)

    @staticmethod
    def _default_message_box(modal_widget: Optional[QWidget] = None):
        if modal_widget is None:
            modal_widget = QMessageBox()
            modal_widget.setIcon(QMessageBox.Question)
            modal_widget.setText('Accept Move?')
            modal_widget.setWindowTitle('Move')
            modal_widget.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            modal_widget.setDefaultButton(QMessageBox.Ok)
        return modal_widget

    @pyqtSlot()
    def shift_item_right(self):
        """Add item"""
        if self.isConditionalAccept is True:
            response: int = self.msg_box.exec_()
            if response == 0:
                return
        self.shift_right.emit()  # noqa

    @pyqtSlot()
    def shift_item_left(self):
        """Remove Item"""
        self.shift_left.emit()  # noqa

    # def clear(self):
    #     """Clear the model"""
    #     self.model.clear()
    #
    # # pylint: disable=invalid-name
    # def takeItem(self, row: int):
    #     """Take Item from the list"""
    #     item = self.model.takeItem(row)
    #     self.model.takeRow(row)
    #     return item
    #
    # # pylint: disable=invalid-name
    # def addItem(self, item: Union[QListWidgetItem, QStandardItem, str]):
    #     """Add Item to the list"""
    #     if isinstance(item, str):
    #         item = QStandardItem(item)
    #     self.model.appendRow(item)
    #
    # def count(self):
    #     """Convenience method"""
    #     return self.model.rowCount()
    #
    # def item(self, row):
    #     """Convenience method to reveal model method"""
    #     return self.model.item(row)
    #
    # # pylint: disable=invalid-name
    # def selectedIndexes(self):
    #     """Convenience Function to revel selectionModel option"""
    #     return self.list.selectionModel().selectedIndexes()
    #
    # # pylint: disable=invalid-name
    # def selectedItems(self):
    #     """Convenience to replicate functionality in QListWidget"""
    #     inds = self.selectedIndexes()
    #     items = [self.item(i.row()) for i in inds]
    #     return items


if __name__ == '__main__':
    app = QApplication(sys.argv)
    codes = [
        'LOAA-05379',
        'LOAA-04468',
        'LOAA-03553',
        'LOAA-02642',
        'LOAA-05731'
    ]

    ex = EDDualSelectorWidget()
    #
    # for code in codes:
    #     an_item = QStandardItem(code)
    #     an_item.setCheckable(True)
    #     ex.model.appendRow(an_item)

    ex.show()
    sys.exit(app.exec_())
