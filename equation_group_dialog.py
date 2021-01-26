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
    QLineEdit, QTextEdit,
    QListWidget, QDialog, QDialogButtonBox
)
from equation_group import EquationGroup


class Equation_Group_Dialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(Equation_Group_Dialog, self).__init__(*args, **kwargs)
        loadUi('eq_group_dialog.ui', self)
        # Info Widgets
        self.buttonbox: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonbox')
        self.existing_eq_group_list: QListWidget = self.findChild(QListWidget, 'existing_eq_group_list')
        self.existing_eq_group_list.itemSelectionChanged.connect(self.equatGroupSelected)

        self.eq_list: QListWidget = self.findChild(QListWidget, 'eq_list')
        self.existing_notes_textbox: QTextEdit = self.findChild(QTextEdit, 'existing_notes_textEdit')
        self.new_eq_group_lEdit: QLineEdit = self.findChild(QLineEdit, 'new_eq_group_lEdit')
        self.notes_textbox: QTextEdit = self.findChild(QTextEdit, 'notes_textEdit')

        self.eqn_group = EquationGroup()
        self.populateEquationList()

    def accept(self, verbose=False) -> None:
        self.eqn_group.insert(name=self.new_eq_group_lEdit.text(),
                              notes=self.notes_textbox.toPlainText(),
                              verbose=verbose)
        super().accept()

    def reject(self) -> None:
        print('rejected')
        super().reject()

    def populateEquationList(self):
        records = self.getEquationGroup().records
        if records:
            for record in records:
                self.existing_eq_group_list.addItem(record.name)

    def getEquationGroup(self):
        return self.eqn_group

    def equatGroupSelected(self):
        ind = self.existing_eq_group_list.currentIndex().row()

        associated_note = self.eqn_group.records[ind].notes
        self.existing_notes_textbox.setText(associated_note)
