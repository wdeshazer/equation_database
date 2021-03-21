"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

# import sys
# from PyQt5.QtCore import Qt, QSize
# noinspection PyUnresolvedReferences
from typing import Optional
from PyQt5.uic import loadUi
# from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtWidgets import (
    QApplication, QLineEdit, QTextEdit,
    QListWidget, QDialog, QDialogButtonBox
)
from equation_group import EquationGroup
from equations import GroupedEquations


class EquationGroupDialog(QDialog):
    """Equation Group Dialog"""
    def __init__(self, *args, eqn_group: Optional[EquationGroup] = None, eqn: Optional[GroupedEquations] = None,
                 **kwargs):
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

        self.eqn_group: Optional[EquationGroup] = eqn_group
        self.eqn: Optional[GroupedEquations] = eqn
        self.populate_equation_group_list()

    def accept(self, verbose=False) -> None:
        """Accept additions to Equation Group"""
        self.eqn_group.new_record(name=self.new_eq_group_l_edit.text(),
                                  notes=self.notes_textbox.toPlainText(),
                                  verbose=verbose)
        super().accept()

    def reject(self) -> None:
        """Reject additions to Equation Group"""
        print('rejected')
        super().reject()

    def populate_equation_group_list(self):
        """Populates the equation list box"""
        records = self.eqn_group.all_records
        for record in records.itertuples():
            self.existing_eq_group_list.addItem(record.name)

    def equation_group_selected(self):
        """Updates equation group selected"""
        ind = self.existing_eq_group_list.currentIndex().row()

        associated_note = self.eqn_group.all_records.iloc[ind]['notes']
        if associated_note is None:
            associated_note = ''
        self.existing_notes_textbox.setText(associated_note)

        eq_grp_id = self.eqn_group.all_records.index[ind]
        self.eqn.set_records_for_parent(parent_id=eq_grp_id)
        self.populate_equation_listbox()

    def populate_equation_listbox(self):
        """Populate equation listbox"""
        eq_lb: QListWidget = self.eq_list
        eqn = self.eqn

        eq_lb.clear()
        if eqn.selected_data_records is not None:
            for row in eqn.selected_data_records:
                eq_lb.addItem(row.name)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app_eqn_group = EquationGroup()
    app_eqn = GroupedEquations()
    dlg = EquationGroupDialog(eqn_group=app_eqn_group, eqn=app_eqn)
    dlg.show()
    sys.exit(app.exec_())
