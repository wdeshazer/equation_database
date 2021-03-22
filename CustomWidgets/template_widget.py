"""
Dialog for managing show_template_manager files
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from PyQt5.uic import loadUi  # noqa
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QTextEdit, QDialogButtonBox, QComboBox, QDialog,
                             QFileDialog, QMessageBox)
from template import TemplateTable, TemplateRecordInput
from latex_data import LatexData


class TemplateWidget(QDialog):
    """Variable Dialog manages the state of Variables"""
    templates_tbl: TemplateTable
    changed = pyqtSignal(int)
    record_id: int
    button_box: QDialogButtonBox
    text_edit: QTextEdit
    available_cb: QComboBox

    # pylint: disable=too-many-instance-attributes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Info Widgets
        try:
            loadUi('CustomWidgets/template_widget.ui', self)
        except FileNotFoundError:
            loadUi('template_widget.ui', self)

        self.available_cb.currentIndexChanged.connect(self.selected_data)

        save_btn = self.button_box.button(QDialogButtonBox.Save)
        save_btn.clicked.connect(self.new_from_source)
        save_btn.setText('New from Source')

        self.button_box.button(QDialogButtonBox.Open).clicked.connect(self.open)

        discard_btn = self.button_box.button(QDialogButtonBox.Discard)
        discard_btn.clicked.connect(self.delete_template)
        discard_btn.setText('Delete Template')

        self.button_box.button(QDialogButtonBox.Close).clicked.connect(self.reject)

    def set_template_data(self, data: LatexData):
        """Populate Widget with LatexData"""
        self.templates_tbl = data.template_table()
        self.record_id = data.template_id

        self._init_available_templates()

    def _init_available_templates(self):
        """Initialize Available templates"""
        ids = self.templates_tbl.available_template_ids()
        self.available_cb.clear()
        for an_id in ids:
            self.available_cb.addItem(str(an_id))

        # the_selected_id = self.data_tbl.latex_
        self.select_template_id()

    def select_template_id(self, an_id: int = None):
        """Select a template id"""
        if an_id == -1:
            ids = self.templates_tbl.available_template_ids()
            an_id = ids[-1]
        elif an_id is None:
            an_id = self.record_id

        ind = self.templates_tbl.data_df.index.get_loc(an_id)
        self.available_cb.setCurrentIndex(ind)

    def selected_data(self, index: int):
        """Respond to changes in Template ID Combobox"""
        self.set_text_data(self.templates_tbl.data_df.iloc[index]['data'])

    def set_text_data(self, data: str):
        """Populate TextEdit with Template Data"""
        self.text_edit.setText(data)

    def new_from_source(self):
        """Save Template file"""
        data = self.text_edit.toPlainText()
        user = self.templates_tbl.my_conn['db_params']['user']
        new_record = TemplateRecordInput(data=data, created_by=user)
        self.templates_tbl.new_record(new_record=new_record)
        self.templates_tbl.pull_data()
        self._init_available_templates()
        self.select_template_id(-1)

    def open(self) -> None:
        """Open File"""
        filenames = QFileDialog.getOpenFileName(self.parent(), "LaTeX Template", "LaTeX", "LaTeX Files (*.tex)")

        if filenames[0] != '':
            f_handle = open(filenames[0], 'r')  # New line
            data = f_handle.read()
            f_handle.close()
            self.set_text_data(data)
            self.available_cb.addItem('')
            new_ind = self.available_cb.count()
            self.available_cb.currentIndexChanged.disconnect(self.selected_data)
            self.available_cb.setCurrentIndex(new_ind)
            self.available_cb.currentIndexChanged.connect(self.selected_data)

    def delete_template(self):
        """Discard Template"""
        an_ind = int(self.available_cb.currentText())
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this Template?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.templates_tbl.delete(id_tup=(an_ind,))
            self.templates_tbl.pull_data()
            self._init_available_templates()
            self.select_template_id()

    def reject(self) -> None:
        """Reject"""
        current_id = self.available_cb.currentText()

        if current_id == '':
            msg = 'Save New Template and Update Image with Template?'
        elif self.record_id != int(current_id):
            msg = 'Update Image with Template?'
        else:
            super().accept()
            return

        reply = QMessageBox.question(self, 'Window Close', msg,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if current_id == '':
                self.new_from_source()
            new_id = int(self.available_cb.currentText())
            self.record_id = new_id
            self.changed.emit(new_id)  # noqa
            super().accept()
        else:
            self.select_template_id(self.record_id)
            super().reject()


if __name__ == "__main__":
    import sys
    from db_utils import my_connect
    from variables import Variables, VariableRecord

    @pyqtSlot(int)
    def response(an_id: int):
        """Test Function for Connecting response"""
        print('Selcted template: {}'.format(an_id))

    app = QApplication(sys.argv)
    a_conn = my_connect()

    var_tbl = Variables(my_conn=a_conn)
    var: VariableRecord = var_tbl.record(1)

    dlg = TemplateWidget()
    dlg.set_template_data(var.latex_obj)
    dlg.changed.connect(response)  # noqa

    dlg.show()
    sys.exit(app.exec_())
