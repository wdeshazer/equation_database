"""
https://www.tutorialspoint.com/pyqt/pyqt_qdialog_class.htm

Threading!!!! https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

from PyQt5.uic import loadUi  # noqa
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
from PyQt5.QtWidgets import (
    QWidget, QApplication, QTextEdit, QGraphicsView, QGraphicsScene, QPushButton,
    QShortcut, QLabel
)

from CustomWidgets.spinner import WaitingSpinner
from CustomWidgets.template_widget import TemplateWidget
from latex_data import LatexData, TemplateID


class LatexWorker(QObject):
    """LaTeX Worker for Threaded running of the Compile statement. Makes spinner possible"""
    compiled = pyqtSignal(object)
    latex_data: LatexData
    text: str
    template_id: TemplateID

    def set_data(self, text: str, template_id: TemplateID):
        """Set Template Data"""
        self.text = text
        self.template_id = template_id

    @pyqtSlot()
    def compile(self):
        """Compile LaTeX"""
        latex_obj = LatexData(latex=self.text, template_id=self.template_id)
        self.compiled.emit(latex_obj)  # noqa


class LatexWidget(QWidget):
    """Variable Dialog manages the state of Variables"""
    latex_data: LatexData
    text_edit: QTextEdit
    graphics_view: QGraphicsView
    template_btn: QPushButton
    spinner: WaitingSpinner
    template_manager: TemplateWidget
    thread: QThread
    latex_worker: LatexWorker()
    compile_btn: QPushButton
    template_id_lbl: QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi('latex_widget.ui', self)

        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        self.compile_sc = QShortcut(QKeySequence('Ctrl+Return'), self)
        self.compile_sc.activated.connect(self.compile)
        self.template_btn.clicked.connect(self.show_template_manager)

        self.spinner = self.my_spinner(self)
        self.template_manager = TemplateWidget()
        self.template_manager.changed.connect(self.update_template)  # noqa

        self.compile_btn.clicked.connect(self.compile)

        # region Thread
        self.thread = QThread()  # no parent
        self.latex_worker = LatexWorker()
        self.latex_worker.moveToThread(self.thread)
        self.latex_worker.compiled.connect(self.thread.quit)  # noqa
        self.latex_worker.compiled.connect(self.set_latex_data)  # noqa
        self.thread.started.connect(self.latex_worker.compile)  # noqa
        # endregion

        self.show()

    @staticmethod
    def my_spinner(parent):
        """Spinner Creation"""
        spinner = WaitingSpinner(
            parent,
            modality=Qt.WindowModal,
            roundness=70.0, opacity=15.0,
            fade=70.0, radius=30.0, lines=12,
            line_length=20.0, line_width=6.0,
            speed=1.0, color=(170, 0, 255)
        )
        return spinner

    @pyqtSlot()
    def compile(self, template_id: TemplateID = None):
        """Compile LaTeX data"""

        self.spinner.start()
        text = self.text_edit.toPlainText()

        if template_id is None:
            template_id = self.latex_data.template_id

        self.latex_worker.set_data(text, template_id)
        self.thread.start()

    @pyqtSlot(object)
    def set_latex_data(self, data: LatexData):
        """Set LatexData Member. Called at initialization and after compile"""
        self.latex_data = data
        self.text_edit.setText(data.latex)
        self.template_manager.set_template_data(data)

        self.template_id_lbl.setText(str(data.template_id))
        self.update_image()

    def update_image(self):
        """Updated Image"""
        img = QImage.fromData(self.latex_data.image)
        pixmap = QPixmap.fromImage(img)
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.spinner.stop()

    def show_template_manager(self):
        """Launch show_template_manager manager"""
        self.template_manager.show()

    @pyqtSlot(int)
    def update_template(self, an_id: TemplateID):
        """Update Template"""
        self.compile(template_id=an_id)


if __name__ == "__main__":
    import sys
    from db_utils import my_connect
    from variables import Variables

    app = QApplication(sys.argv)
    a_conn = my_connect()

    # region Necesary Data for variable details Widget
    app_var = Variables(my_conn=a_conn)
    a_record = app_var.record(6)
    # endregion

    dlg = LatexWidget()
    dlg.set_latex_data(a_record.latex_obj)

    sys.exit(app.exec_())
