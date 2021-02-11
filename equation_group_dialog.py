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


class EquationGroupDialog(QDialog):
    """Equation Group Dialog"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi('eq_group_dialog.ui', self)
        # Info Widgets
        self.buttonbox: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonbox')
        self.existing_eq_group_list: QListWidget = self.findChild(QListWidget, 'existing_eq_group_list')
        self.existing_eq_group_list.itemSelectionChanged.connect(self.equation_group_selected)

        self.eq_list: QListWidget = self.findChild(QListWidget, 'eq_list')
        self.existing_notes_textbox: QTextEdit = self.findChild(QTextEdit, 'existing_notes_text_edit')
        self.new_eq_group_l_edit: QLineEdit = self.findChild(QLineEdit, 'new_eq_group_l_edit')
        self.notes_textbox: QTextEdit = self.findChild(QTextEdit, 'notes_text_edit')

        self.eqn_group = EquationGroup()
        self.populate_equation_list()

    def accept(self, verbose=False) -> None:
        """Accept additions to Equation Group"""
        self.eqn_group.insert(name=self.new_eq_group_l_edit.text(),
                              notes=self.notes_textbox.toPlainText(),
                              verbose=verbose)
        super().accept()

    def reject(self) -> None:
        """Reject additions to Equation Group"""
        print('rejected')
        super().reject()

    def populate_equation_list(self):
        """Populates the equation list box"""
        records = self.get_equation_group().records
        if records:
            for record in records:
                self.existing_eq_group_list.addItem(record.name)

    def get_equation_group(self):
        """Returns a reference to the equation group object"""
        return self.eqn_group

    def equation_group_selected(self):
        """Updates equation group selected"""
        ind = self.existing_eq_group_list.currentIndex().row()

        associated_note = self.eqn_group.records[ind].notes
        self.existing_notes_textbox.setText(associated_note)
