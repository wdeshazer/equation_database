"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Optional
from PyQt5.uic import loadUi  # noqa
# from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QTextEdit, QMessageBox, QAbstractItemView,
    QListWidget, QDialog, QDialogButtonBox, QGraphicsView, QPushButton,
    QGraphicsScene, QLineEdit, QComboBox
)
from db_utils import my_connect
from variables import GroupedVariables
# from unit import Unit
from time_logging import TimeLogger


class VariableDialog(QDialog):
    """Variable Dialog manages the state of Variables"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, var: GroupedVariables, *args, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi('variable_dialog.ui', self)
        # Info Widgets
        self.buttonbox: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonBox')
        self.variable_name_l_edit: QLineEdit = self.findChild(QLineEdit, 'variable_name_l_edit')
        self.dimension_l_edit: QLineEdit = self.findChild(QLineEdit, 'dimension_l_edit')
        self.variable_type_c_box: QComboBox = self.findChild(QComboBox, 'variable_type_c_box')
        self.variables_list: QListWidget = self.findChild(QListWidget, 'variables_list')
        self.equations_list: QListWidget = self.findChild(QListWidget, 'equations_list')
        self.notes_text_edit: QTextEdit = self.findChild(QTextEdit, 'notes_text_edit')
        self.variable_latex_l_edit: QLineEdit = self.findChild(QLineEdit, 'variable_latex_l_edit')
        self.latex_g_view: QGraphicsView = self.findChild(QGraphicsView, 'latex_g_view')
        self.my_conn: Optional[dict] = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.t_log: Optional[TimeLogger] = t_log
        self.var = var
        self._insert_button('Insert Selected')
        self._new_var_button('New Variable')
        self.buttonbox.addButton(QDialogButtonBox.Cancel)
        self.populate_variable_list()
        self.variables_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.variables_list.selectionModel().selectionChanged.connect(self.select_one_variable)
        self.scene = QGraphicsScene()
        self.latex_g_view.setScene(self.scene)

    def select_one_variable(self):
        """Behavior when a selction in the list is made"""
        inds = self.variables_list.selectedIndexes()
        if 0 < len(inds) < 2:
            self._populate_variable_details(inds[0].row())
        else:
            self._clear_variable_details()

    def _insert_button(self, text):
        btn = QPushButton(self.tr("&" + text))
        btn.setDefault(True)
        self.buttonbox.addButton(btn, QDialogButtonBox.AcceptRole)

    def _new_var_button(self, text):
        btn = QPushButton(self.tr("&" + text))
        btn.setDefault(False)
        btn.clicked.connect(self.new_variable)
        self.buttonbox.addButton(btn, QDialogButtonBox.ActionRole)

    def _populate_variable_details(self, ind):
        var = self.var
        record = var.records_not_selected_unique[ind]
        self.variable_name_l_edit.setText(record.name)
        self.dimension_l_edit.setText(str(record.dimensions))
        self.variable_latex_l_edit.setText(record.latex)

        img = QImage.fromData(record.image)
        pixmap = QPixmap.fromImage(img)

        scene = self.scene
        scene.addPixmap(pixmap)
        # self.latex_graphicbox.setScene(scene)
        self.latex_g_view.show()
        self.notes_text_edit.setText(record.notes)

        p_records = var.other_parents(my_conn=self.my_conn, child_id=record.Index)

        self.equations_list.clear()
        for record in p_records:
            self.equations_list.addItem(record.name)

    def _clear_variable_details(self):
        """Clear widgets"""
        self.equations_list.clear()
        self.notes_text_edit.clear()
        self.scene.clear()

    def accept(self) -> None:
        """Accept Selection"""
        var = self.var
        inds = self.variables_list.selectedIndexes()

        if len(inds) == 0:
            msg = QMessageBox()
            msg.setText('Please Select Some Equations to Insert')
            msg.exec_()
            return

        for selected_item in self.variables_list.selectedItems():
            ind = self.variables_list.row(selected_item)
            record = var.records_not_selected_unique[ind]
            child_id = record.Index
            var.associate_parent(my_conn=self.my_conn, t_log=self.t_log,
                                 parent_id=var.selected_parent_id, child_id=child_id)

            win = self.parent()
            var.set_records_for_parent()
            win.show_variable_table()

        print('Accept')
        super().accept()

    def new_variable(self):
        """New Variable"""
        var = self.var
        var.new_record(my_conn=self.my_conn, t_log=self.t_log)
        var.set_records_for_parent()  # reinitializes records not used
        var.pull_grouped_data()
        new = var.latest_record()
        self.variables_list.addItem(new[0].name)

    def reject(self) -> None:
        """Reject Selection"""
        super().reject()

    def populate_variable_list(self):
        """Populate Variables List"""
        records = self.var.records_not_selected_unique
        for record in records:
            self.variables_list.addItem(record.name)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app_var = GroupedVariables()
    app_var.set_records_for_parent(parent_id=2)
    dlg = VariableDialog(var=app_var)
    dlg.show()
    sys.exit(app.exec_())
