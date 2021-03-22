"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Optional, List
from PyQt5.uic import loadUi  # noqa
from PyQt5.QtWidgets import (
    QWidget, QApplication, QTextEdit, QListWidget,
    QLineEdit, QComboBox, QPushButton, QLabel
)
from CustomWidgets.dual_selector_widget import EDDualSelectorWidget
from CustomWidgets.variable_details import VariableDetails
from equations import EquationRecords
from variables import GroupedVariableRecord
from unit import UnitRecord


class VariablesDialog(QWidget):
    """Variable Dialog manages the state of Variables"""
    dual_selector: EDDualSelectorWidget
    variable_details: VariableDetails

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi('variables_dialog_v2.ui', self)


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

    dlg = VariablesDialog()
    # dlg.set_variable_types(var_types=v_types.types())
    dlg.show()
    # dlg.set_data(record=a_record, unit=a_unit, equations=eqns)
    sys.exit(app.exec_())
