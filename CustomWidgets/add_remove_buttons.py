"""
Add Remove Button controls for use with List type widgets
"""
import sys
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout,
    QSizePolicy, QSpacerItem
)
# from PyQt5.QtGui import QStandardItemModel, QStandardItem


class EDAddRemoveButtons(QWidget):
    """Add Remove Buttons Can be added to any widget that has an insertion paradigm.
       Currently, it is envisioned for lists and maybe tables only
       Parent must have add and remove methods"""
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        h_layout = QHBoxLayout(self)

        self.add_btn = QPushButton("+", self)
        self.add_btn.setObjectName("add_rm_btn")
        ar_w = 50
        self.add_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.rm_btn = QPushButton("-", self)
        self.rm_btn.setObjectName("add_rm_btn")
        self.rm_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        h_layout.setSpacing(2)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Fixed)

        h_layout.addItem(h_spacer)
        h_layout.addWidget(self.add_btn)
        h_layout.addWidget(self.rm_btn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EDAddRemoveButtons()
    ex.show()
    sys.exit(app.exec_())
