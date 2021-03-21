"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Optional
# noinspection PyUnresolvedReferences
from PyQt5.uic import loadUi
# from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication, QTextEdit, QMessageBox, QAbstractItemView,
    QListWidget, QDialog, QDialogButtonBox, QGraphicsView, QPushButton,
    QGraphicsScene
)
from db_utils import my_connect
from CustomWidgets.filter_list_widget import EDFilterListWidget
from equations import GroupedEquations
from time_logging import TimeLogger


class EquationDialog(QDialog):
    """Eqution Dialog"""

    def __init__(self, eqn: GroupedEquations, *args, my_conn: Optional[dict] = None, t_log: Optional[TimeLogger] = None,
                 verbose: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi('equation_dialog.ui', self)
        # Info Widgets
        self.buttonbox: QDialogButtonBox = self.findChild(QDialogButtonBox, 'buttonBox')
        equation_list: QListWidget = self.findChild(QListWidget, 'equation_list')

        self.eqn_group_list: QListWidget = self.findChild(QListWidget, 'eqn_group_list')
        self.notes_text_edit: QTextEdit = self.findChild(QTextEdit, 'notes_text_edit')
        self.image_g_view: QGraphicsView = self.findChild(QGraphicsView, 'image_g_view')
        self.my_conn: Optional[dict] = my_connect(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.t_log: Optional[TimeLogger] = t_log
        self.eqn = eqn
        self._insert_button('Insert Selected')
        self._new_eq_button('New Equation')
        self.buttonbox.addButton(QDialogButtonBox.Cancel)
        self.scene = QGraphicsScene()
        self.image_g_view.setScene(self.scene)

        self.equation_filter_list: EDFilterListWidget = EDFilterListWidget(self)
        layout = equation_list.parent().layout()
        layout.replaceWidget(equation_list, self.equation_filter_list)
        self.populate_equation_list()
        self.equation_list.close()
        self.equation_filter_list.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.equation_filter_list.list.selectionModel().selectionChanged.connect(self.select_one_equation)

    def select_one_equation(self):
        """Select One Eqution"""
        print("You are here")
        inds = self.equation_filter_list.list.selectedIndexes()
        if 0 < len(inds) < 2:
            self._populate_equation_details(inds[0].row())
        else:
            self._clear_equation_details()

    def _insert_button(self, text):
        btn = QPushButton(self.tr("&" + text))
        btn.setDefault(True)
        self.buttonbox.addButton(btn, QDialogButtonBox.AcceptRole)

    def _new_eq_button(self, text):
        btn = QPushButton(self.tr("&" + text))
        btn.setDefault(False)
        btn.clicked.connect(self.new_equation)
        self.buttonbox.addButton(btn, QDialogButtonBox.ActionRole)

    def _populate_equation_details(self, ind):
        eqn = self.eqn
        record = eqn.records_not_selected_unique[ind]
        self.notes_text_edit.setText(record.notes)

        img = QImage.fromData(record.image)
        pixmap = QPixmap.fromImage(img)

        scene = self.scene
        scene.addPixmap(pixmap)
        # self.latex_graphicbox.setScene(scene)
        self.image_g_view.show()

        p_records = eqn.other_parents(my_conn=self.my_conn, child_id=record.Index)

        self.eqn_group_list.clear()
        for record in p_records:
            self.eqn_group_list.addItem(record.name)

    def _clear_equation_details(self):
        self.eqn_group_list.clear()
        self.notes_text_edit.clear()
        self.scene.clear()

    def accept(self) -> None:
        """Accept the insertion of new equation into equation_group"""
        eqn = self.eqn
        f_list = self.equation_filter_list
        inds = f_list.selectedIndexes()

        if len(inds) == 0:
            msg = QMessageBox()
            msg.setText('Please Select Some Equations to Insert')
            msg.exec_()
            return

        for selected_item in f_list.selectedItems():
            ind = selected_item.row()
            child_id = eqn.records_not_selected_unique[ind].Index
            eqn.associate_parent(my_conn=self.my_conn, t_log=self.t_log,
                                 parent_id=eqn.selected_parent_id, child_id=child_id)

            item = self.equation_filter_list.takeItem(ind)
            self.parent().addItem(item)

        print('Accept')
        super().accept()

    def new_equation(self):
        """New Equation"""
        eqn = self.eqn
        eqn.new_record(my_conn=self.my_conn, t_log=self.t_log, parent_id=eqn.selected_parent_id)
        eqn.pull_grouped_data()
        eqn.set_records_for_parent()
        new = eqn.selected_data_records[-1]
        self.parent().addItem(new.name)
        super().accept()

    def reject(self) -> None:
        """Reject"""
        print('rejected')
        super().reject()

    def populate_equation_list(self):
        """Populate Equation List"""
        records = self.eqn.records_not_selected_unique
        for record in records:
            self.equation_filter_list.addItem(record.name)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app_eqn = GroupedEquations()
    app_eqn.set_records_for_parent(parent_id=1)
    dlg = EquationDialog(eqn=app_eqn)
    dlg.show()
    sys.exit(app.exec_())
