"""
Add Remove Button controls for use with List type widgets
"""
import sys
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QSizePolicy, QSpacerItem
)
# from PyQt5.QtGui import QStandardItemModel, QStandardItem


class EDShiftButtons(QWidget):
    """Add Remove Buttons Can be added to any widget that has an insertion paradigm.
       Currently, it is envisioned for lists and maybe tables only
       Parent must have add and remove methods"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        v_layout = QVBoxLayout(self)

        self.shift_right_btn = QPushButton(">", self)
        self.shift_right_btn.setObjectName("add_rm_btn")
        ar_w = 50
        self.shift_right_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.shift_left_btn = QPushButton("<", self)
        self.shift_left_btn.setObjectName("add_rm_btn")
        self.shift_left_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        v_layout.setSpacing(2)
        v_layout.setContentsMargins(0, 0, 0, 0)
        h_spacer = QSpacerItem(20, 40, QSizePolicy.Fixed, QSizePolicy.Expanding)
        h_spacer2 = QSpacerItem(20, 40, QSizePolicy.Fixed, QSizePolicy.Expanding)

        v_layout.addItem(h_spacer)
        v_layout.addWidget(self.shift_right_btn)
        v_layout.addWidget(self.shift_left_btn)
        v_layout.addItem(h_spacer2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EDShiftButtons()
    ex.show()
    sys.exit(app.exec_())
