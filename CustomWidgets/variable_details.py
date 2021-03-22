"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Optional, List
from PyQt5.uic import loadUi  # noqa
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QWidget, QApplication, QTextEdit, QListWidget,
    QLineEdit, QComboBox, QPushButton, QLabel
)
from CustomWidgets.latex_widget import LatexWidget
from equations import EquationRecords
from variables import GroupedVariableRecord
from unit import UnitRecord


class VariableDetails(QWidget):
    """Variable Dialog manages the state of Variables"""
    latex_widget: LatexWidget
    name_l_edit: QLineEdit
    dimension_l_edit: QLineEdit
    unit_btn: QPushButton
    unit_image_lbl: QLabel
    variable_type_c_box: QComboBox
    equations_list: QListWidget
    notes_text_edit: QTextEdit
    template_btn: QPushButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Info Widgets
        try:
            loadUi('CustomWidgets/variable_details.ui', self)
        except FileNotFoundError:
            loadUi('variable_details.ui', self)

    def set_variable_types(self, var_types: Optional[List[str]] = None):
        """Populate variable types - Usually done once after widget creation"""
        for a_type in var_types:
            self.variable_type_c_box.addItem(a_type)

    def set_data(self, record: GroupedVariableRecord, unit: UnitRecord,
                 equations: Optional[EquationRecords] = None):
        """Populate Widgets based on Record Information"""
        self.name_l_edit.setText(record.name)
        img = QImage.fromData(unit.image)
        self.unit_image_lbl.setPixmap(QPixmap.fromImage(img))
        self.dimension_l_edit.setText(str(record.dimensions))
        self.notes_text_edit.setText(record.notes)
        self.variable_type_c_box.setCurrentText(record.type_name)

        self.latex_widget.set_latex_data(record.latex_obj)

        self.equations_list.clear()
        if equations is not None:
            for eqn in equations:
                self.equations_list.addItem(eqn.name)

    def clear_variable_details(self):
        """Clear widgets"""
        self.equations_list.clear()
        self.notes_text_edit.clear()
        self.scene.clear()


if __name__ == "__main__":
    import sys
    from db_utils import my_connect
    from variables import GroupedVariables  # pylint: disable=ungrouped-imports
    from unit import Unit  # pylint: disable=ungrouped-imports
    from type_table import TypeTable

    app = QApplication(sys.argv)
    my_conn = my_connect()

    # region Necesary Data for variable details Widget
    VAR_ID = 6
    app_var = GroupedVariables(my_conn=my_conn)
    un = Unit(my_conn=my_conn)
    v_types = TypeTable(name='variable_type', my_conn=my_conn)
    # app_var.set_records_for_parent(parent_id=2)
    all_rcds = list(app_var.all_records.itertuples())
    a_record: GroupedVariableRecord = all_rcds[VAR_ID]
    a_unit = un.record(an_id=a_record.unit_id)
    eqns = app_var.other_parents(child_id=VAR_ID)
    # endregion

    dlg = VariableDetails()
    dlg.set_variable_types(var_types=v_types.types())
    dlg.show()
    dlg.set_data(record=a_record, unit=a_unit, equations=eqns)
    sys.exit(app.exec_())
