"""
LaTeXDataWidget handles the management of LaTeX data. In particular, the automatic compilation of the data
and the redisplay of the graphical image is managed.
"""
from typing import Optional, Union
from dataclasses import dataclass
from PyQt5.QtWidgets import QTextEdit, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtGui import QPixmap, QImage

from time_logging import TimeLogger
from latex_data import LatexData
from grouped_physics_object import GroupedPhysicsObject
from unit import Unit


@dataclass
# pylint: disable=too-many-instance-attributes
class LaTexTextEdit(QTextEdit):
    """LaTexDataWidget manages the state of LatexData when the textEditor goes in and out of focus"""
    latex_data: LatexData = None
    graphics_view: QGraphicsView = None
    scene: QGraphicsScene = None
    db_ref: Union[GroupedPhysicsObject, Unit, None] = None
    db_ref_id: int = None
    text_initial: str = None
    t_log: Optional[TimeLogger] = None
    my_conn: Optional[dict] = None
    verbose: bool = None

    def __init__(self, *args, latex_data: Optional[LatexData] = None, graphics_view: Optional[QGraphicsView] = None,
                 db_ref: Union[GroupedPhysicsObject, Unit, None] = None, my_conn: Optional[dict] = None,
                 verbose: bool = False, t_log: Optional[TimeLogger] = None, scene: Optional[QGraphicsScene] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.latex_data = latex_data
        self.graphics_view = graphics_view
        self.scene = scene
        self.db_ref = db_ref
        self.verbose = verbose
        self.my_conn = my_conn
        self.t_log = t_log

        # Need to figure out how to handle situations where datamembers not properly set

    # pylint: disable=unused-argument, missing-function-docstring, invalid-name
    def focusInEvent(self, event: QFocusEvent) -> None:
        self.text_initial = self.toPlainText()

    def focusOutEvent(self, event: QFocusEvent) -> None:  # pylint: disable=invalid-name,missing-function-docstring
        text_new = self.toPlainText()

        if self.text_initial != text_new:
            self.update_text(text=text_new)

        self.db_ref.update(an_id=self.db_ref_id, latex=self.latex_data)
        # print('Old Text: ', self.text_initial)
        # print('New Text: ', new_text)
        super().focusOutEvent(event)

    def update_text(self, text: str, verbose: bool = False) -> None:
        """Method to update latex text and redisplay"""
        if verbose is False:
            verbose = self.verbose
        self.latex_data.update(my_conn=self.my_conn, t_log=self.t_log, latex=text, verbose=verbose)
        self.show_latex_image()

    def show_latex_image(self):
        """Method to Display image"""
        image = self.latex_data.image
        if image is None:
            pass
        else:
            img = QImage.fromData(image)
            pixmap = QPixmap.fromImage(img)

            self.scene.clear()
            self.scene.addPixmap(pixmap)
            # self.latex_graphicbox.setScene(scene)
            self.graphics_view.show()
