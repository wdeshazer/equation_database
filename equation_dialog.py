"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

# import sys
# from PyQt5.QtCore import Qt, QSize
# noinspection PyUnresolvedReferences
from PyQt5.uic import loadUi
# from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtWidgets import (
    QTextEdit,
    QListWidget, QDialog, QDialogButtonBox, QGraphicsView
)
# from equation_group import EquationGroup


class Equation_Dialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(Equation_Dialog, self).__init__(*args, **kwargs)
        loadUi('equation_dialog.ui', self)
        # Info Widgets
        self.buttonbox: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonbox')
        self.equation_listbox: QListWidget = self.findChild(QListWidget, 'equation_listbox')
        self.eq_group_listbox: QListWidget = self.findChild(QListWidget, 'eq_group_listbox')
        self.notes_textbox: QTextEdit = self.findChild(QTextEdit, 'notes_textbox')
        self.graphicsView: QGraphicsView = self.findChild(QGraphicsView, 'graphicsView')

    def accept(self, verbose=False) -> None:
        self.eq_group.insert(name=self.new_eq_group_lEdit.text(),
                             notes=self.notes_textbox.toPlainText(),
                             verbose=verbose)
        super().accept()

    def reject(self) -> None:
        print('rejected')
        super().reject()

    def populateEquationList(self):
        records = self.eq_group.records
        if records:
            for record in records:
                self.existing_eq_group_list.addItem(record.name)
