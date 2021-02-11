"""
https://stackoverflow.com/questions/6832499/qsplitter-show-a-divider-or-a-margin-between-the-two-widgets
https://www.learnpyqt.com/tutorials/creating-your-first-window/
https://www.youtube.com/watch?v=3tpsg9Nrsxo
https://stackoverflow.com/questions/7167929/pyqt-qsplitter-issue
https://www.youtube.com/watch?v=IXjNGRCCfxw

App Icon:
https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105

Qt Stylesheet Reference
https://code.i-harness.com/en/docs/qt~5.11/stylesheet-reference

Qt Shadow
https://forum.qt.io/topic/41975/setstylesheet-to-qpushbutton-box-shadow/8
"""

__author__ = "William DeShazer"
__version__ = "0.1.0"
__license__ = "MIT"

import platform
import sys
# region Windows Task Bar Icon
import ctypes

from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter,
    QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox,
    QLabel, QLineEdit, QFrame, QComboBox,
    QSpacerItem, QSizePolicy, QPushButton, QGridLayout,
    QTextEdit, QGraphicsView, QTableWidget, QGraphicsDropShadowEffect,
    QListWidget, QAction, QAbstractItemView  # , QMessageBox
)

from scipy.constants import golden_ratio
from psycopg2 import connect
from config import config
from equation_group import EquationGroup
from equationgroupdialog import EquationGroupDialog
from equation import Equation
from variable import Variable
from unit import Unit
from type_table import TypeTable


WINDOW_LEFT_START = 300
WINDOW_TOP_START = 300
WINDOW_HEIGHT = 1500

if platform.system() == "Windows":
    import wmi

    obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)

    displays = [x for x in obj if x.PNPClass == 'Monitor']

    if len(displays) == 2:
        WINDOW_LEFT_START = 3200
        WINDOW_TOP_START = 25
        WINDOW_HEIGHT = 900
    elif len(displays) == 3:
        WINDOW_LEFT_START = 7600
        WINDOW_TOP_START = 300
        WINDOW_HEIGHT = 1500

    # for item in obj:
    #     if item.Name == 'Dell S2240T(HDMI)':
    #         window_left_start = 3200
    #         window_top_start = 25
    #         window_height = 900

    MYAPPID = 'deshazersoftware.equationdatabase.equationdatabase.0.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MYAPPID)
# endregion


class Handle(QWidget):
    """Handle for Sliders"""
    def paintEvent(self, e=None):  # pylint: disable=invalid-name, unused-argument, missing-function-docstring
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(133, 45, 145), Qt.Dense5Pattern))
        painter.drawRect(self.rect())


class Customsplitter(QSplitter):
    """Splitter with no Margins and using handle"""

    def __init__(self, *args):
        super().__init__(*args)
        self.width = None

    def addWidget(self, wdg):  # pylint: disable=invalid-name
        """Add Widget with Custom Handle"""
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*10, self.width*12)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(l_handle)


class EquationButton(QPushButton):
    """Personalized equation button"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(10, 10)
        self.setGraphicsEffect(effect)


# pylint: disable=too-many-instance-attributes, too-many-statements
class Window(QMainWindow):
    """Main Window for Application"""

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        super().__init__(*args, **kwargs)

        self.style_sheet = """
            QWidget {
                font-size: 14pt;
            }
        
            QPushButton {
                background-color: qLinearGradient(x1:0, y1:0, x2: 1, y2: 1, stop: 0 #A3A1FF, stop: 0.7 #852D91,
                    stop:1 #6253e1);
                color: #ffffff;
                border-style: outset;
                border-width: 1px;
                border-radius:10px;
                border-color: black;
                padding-top: 2px;
                padding-bottom: 3px;
                padding-right: 22px;
                padding-left: 20px;
           }
            
            QPushButton::pressed {
                background-color: #852D91;
            }
            
            QPushButton:hover:!pressed {
                background-color: qLinearGradient(x1:0, y1:0, x2: 1, y2: 1, stop: 0 #A1A1FF, stop: 0.7 #8d7be5,
                    stop:1 #6253e1);
            }

            QPushButton#add_rm_btn {
                background-color: qlineargradient(spread:pad, x1:0.013, y1:1, x2:0, y2:0.12, stop:0 
                    rgba(0, 0, 0, 255), stop:1 rgba(150, 180, 255, 255));
                color: #ffffff;
                border-style: flat;
                border-width: 3px;
                border-radius: 0px;
                border-color: black;
                padding: 0px;
            }
            
            QPushButton#add_rm_btn::pressed {
                background-color: gray;
            }
            
            QPushButton#add_rm_btn:hover:!pressed {
                background-color: #8d7be5;
            }
            
            QMainWindow{
             background-color: #afbcc6;
            }

            QGroupBox{
                font-size: 18pt;
            }
        """

        # Some good colors:
        # #afbcc6, #b9afc6, #afb0c6

        self.title = "Equation Database"
        self.left = WINDOW_LEFT_START
        # self.left = 0
        self.top = WINDOW_TOP_START
        self.height = WINDOW_HEIGHT
        self.width = int(self.height * golden_ratio)

        # region ToolBar
        self.toolbar = self.addToolBar('Save')
        self.toolbar.setIconSize(QSize(128, 128))

        save_action = QAction(QIcon('Icons/save_button_256x256.png'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save Equation Group')

        analyze_action = QAction(QIcon('Icons/analyze_cog_512x512.png'), '&Analyze', self)
        analyze_action.setShortcut('Alt+A')
        analyze_action.setStatusTip('Analyze Equation Group')

        new_eqn_action = QAction(QIcon('Icons/sigma_icon_256x256.png'), '&New Equation', self)
        new_eqn_action.setShortcut('Ctrl+N')
        new_eqn_action.setStatusTip('New Equation')

        new_eqn_group_action = QAction(QIcon('Icons/new_eq_group_1000x1000.png'), '&New Equation Group', self)
        new_eqn_group_action.setShortcut('Alt+N')
        new_eqn_group_action.setStatusTip('New Equation Group')
        new_eqn_group_action.triggered.connect(self.new_equation_group)

        eqn_group_info_action = QAction(QIcon('Icons/info_icon256x256.png'), '&Equation Group Information', self)
        eqn_group_info_action.setShortcut('Alt+I')
        eqn_group_info_action.setStatusTip('Equation Group Information')

        self.toolbar.addAction(save_action)
        self.toolbar.addAction(new_eqn_action)
        empty1 = QWidget(self.toolbar)
        ew: int = 50  # pylint: disable=invalid-name
        empty1.setFixedWidth(ew)
        empty2 = QWidget(self.toolbar)
        empty2.setFixedWidth(ew)
        self.toolbar.addWidget(empty1)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(empty2)
        self.toolbar.addAction(new_eqn_group_action)
        self.toolbar.addAction(analyze_action)
        self.toolbar.addAction(eqn_group_info_action)

        # endregion

        # region Equation Group - Left Frame
        # -----------------------------------------------------------------------------------------------------------
        self.eq_group_gbox = QGroupBox("Equation Group")
        self.eq_group_gbox.setMinimumWidth(200)
        self.eq_group_v_layout = QVBoxLayout(self.eq_group_gbox)
        self.eq_group_v_layout.setSpacing(5)

        self.eq_group_cbox = QComboBox(self.eq_group_gbox)
        self.eq_group_cbox.activated.connect(self.populate_equation_listbox)

        self.eq_group_v_layout.addWidget(self.eq_group_cbox)

        self.analyze_frame = QFrame(self.eq_group_gbox)
        self.analyze_h_layout = QHBoxLayout(self.analyze_frame)
        self.analyze_h_layout.setContentsMargins(10, 0, 10, 15)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.analyze_frame.setSizePolicy(size_policy)

        self.filter_frame = QFrame(self.eq_group_gbox)
        self.filter_h_layout = QHBoxLayout(self.filter_frame)
        self.filter_h_layout.setContentsMargins(0, 0, 0, 0)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.filter_frame.setSizePolicy(size_policy)

        self.filter_lbl = QLabel("Filter")
        self.filter_l_edit = QLineEdit(self.eq_group_gbox)
        self.filter_h_layout.addWidget(self.filter_lbl)
        self.filter_h_layout.addWidget(self.filter_l_edit)
        self.eq_group_v_layout.addWidget(self.filter_frame)

        self.equation_listbox = QListWidget(self.eq_group_gbox)
        self.equation_listbox.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.equation_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.equation_listbox.itemClicked.connect(self.select_one_equation)
        self.equation_listbox.itemSelectionChanged.connect(self.select_multiple_equations)

        self.eq_group_v_layout.addWidget(self.equation_listbox)

        self.eq_add_btn = QPushButton("+")
        self.eq_add_btn.setObjectName("add_rm_btn")
        ar_w = 50
        self.eq_add_btn.setFixedSize(QSize(ar_w, int(ar_w)))
        self.eq_add_btn.clicked.connect(self.add_equation)

        self.eq_rm_btn = QPushButton("-")
        self.eq_rm_btn.setObjectName("add_rm_btn")
        self.eq_rm_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.eq_add_rm_frame = QFrame(self.eq_group_gbox)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.eq_add_rm_frame.setSizePolicy(size_policy)
        self.eq_add_rm_h_layout = QHBoxLayout(self.eq_add_rm_frame)
        self.eq_add_rm_h_layout.setSpacing(2)
        h_spacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.eq_add_rm_h_layout.addItem(h_spacer)
        self.eq_add_rm_h_layout.addWidget(self.eq_add_btn)
        self.eq_add_rm_h_layout.addWidget(self.eq_rm_btn)
        self.eq_group_v_layout.addWidget(self.eq_add_rm_frame)

        # endregion

        # region Equation Details - Right Frame
        # -----------------------------------------------------------------------------------------------------------
        self.eq_details_gbox = QGroupBox("Equation Details")  # Entire encapsulating Gbox
        self.eq_details_v_layout = QVBoxLayout(self.eq_details_gbox)

        # region Equation Header added to Equation Details
        # **********************************************************
        self.eq_header_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.eq_header_frame.setSizePolicy(size_policy)
        self.eq_header_g_layout = QGridLayout(self.eq_header_frame)
        self.eq_details_v_layout.addWidget(self.eq_header_frame)

        self.name_label = QLabel("Equation Name")
        self.name_l_edit = QLineEdit()
        self.eq_header_g_layout.addWidget(self.name_label, 0, 0)
        self.eq_header_g_layout.addWidget(self.name_l_edit, 0, 1)

        self.codefile_label = QLabel("Code File")
        self.codefile_l_edit = QLineEdit()
        self.eq_header_g_layout.addWidget(self.codefile_label, 1, 0)
        self.eq_header_g_layout.addWidget(self.codefile_l_edit, 1, 1)

        self.type_label = QLabel("Type")
        self.type_cbox = QComboBox()
        self.type_cbox.setMinimumWidth(700)
        self.eq_header_g_layout.addWidget(self.type_label, 0, 2)
        self.eq_header_g_layout.addWidget(self.type_cbox, 0, 3)

        self.associated_eq_groups_btn = EquationButton("Associated Eq Groups")
        self.eq_header_g_layout.addWidget(self.associated_eq_groups_btn, 1, 3)
        self.eq_header_g_layout.setAlignment(self.associated_eq_groups_btn, Qt.AlignLeft)
        self.details_btn = EquationButton("Other Details")
        self.eq_header_g_layout.addWidget(self.details_btn, 1, 3)
        self.eq_header_g_layout.setAlignment(self.details_btn, Qt.AlignRight)
        # endregion

        # region LaTeX added to Equation Details
        # **********************************************************

        self.latex_gbox = QGroupBox("LaTeX")
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.latex_gbox.setSizePolicy(size_policy)
        self.latex_v_layout = QVBoxLayout(self.latex_gbox)
        self.latex_textbox = QTextEdit(self.latex_gbox)
        self.latex_graphicbox = QGraphicsView(self.latex_gbox)
        # self.latex_graphicbox.setMinimumSize(QSize(907, 369))

        self.latex_splitter = Customsplitter(Qt.Vertical)  # Note Handle for a vert splitter is oriented Horizontally
        self.latex_splitter.addWidget(self.latex_textbox)
        self.latex_splitter.addWidget(self.latex_graphicbox)
        self.latex_v_layout.addWidget(self.latex_splitter)

        self.latex_btn_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.latex_btn_frame.setSizePolicy(size_policy)
        self.latex_btn_h_layout = QHBoxLayout(self.latex_btn_frame)
        self.latex_btn_h_layout.setContentsMargins(0, 0, 1, 10)
        self.latex_template_btn = EquationButton("Template")
        self.latex_update_btn = EquationButton("Update")
        h_spacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.latex_btn_h_layout.addWidget(self.latex_template_btn)
        self.latex_btn_h_layout.addItem(h_spacer)
        self.latex_btn_h_layout.addWidget(self.latex_update_btn)
        self.latex_v_layout.addWidget(self.latex_btn_frame)

        # endregion

        # region Variables Notes
        self.var_notes_frame = QFrame(self.eq_details_gbox)
        self.var_notes_v_layout = QVBoxLayout(self.var_notes_frame)
        # self.var_notes_frame.setLayout(self.var_notes_v_layout)

        self.variables_gbox = QGroupBox("Variables")
        self.variables_v_layout = QVBoxLayout(self.variables_gbox)
        self.variables_v_layout.setSpacing(5)
        # self.variables_gbox.setLayout(self.var_notes_v_layout)
        self.variables_tbl = QTableWidget(self.variables_gbox)
        self.variables_v_layout.addWidget(self.variables_tbl)

        self.var_add_btn = QPushButton("+")
        self.var_add_btn.setObjectName("add_rm_btn")
        ar_w = 50
        self.var_add_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.var_rm_btn = QPushButton("-")
        self.var_rm_btn.setObjectName("add_rm_btn")
        self.var_rm_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.var_add_rm_frame = QFrame(self.variables_gbox)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.var_add_rm_frame.setSizePolicy(size_policy)
        self.var_add_rm_h_layout = QHBoxLayout(self.var_add_rm_frame)
        self.var_add_rm_h_layout.setSpacing(2)
        h_spacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.var_add_rm_h_layout.addItem(h_spacer)
        self.var_add_rm_h_layout.addWidget(self.var_add_btn)
        self.var_add_rm_h_layout.addWidget(self.var_rm_btn)
        self.variables_v_layout.addWidget(self.var_add_rm_frame)

        self.notes_gbox = QGroupBox("Notes")
        self.notes_v_layout = QVBoxLayout(self.notes_gbox)
        # self.notes_gbox.setLayout(self.notes_v_layout)
        self.notes_textbox = QTextEdit(self.notes_gbox)
        self.notes_v_layout.addWidget(self.notes_textbox)

        self.notes_btn_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.notes_btn_frame.setSizePolicy(size_policy)
        self.notes_btn_h_layout = QHBoxLayout(self.notes_btn_frame)
        self.notes_btn_h_layout.setContentsMargins(0, 0, 1, 10)
        self.notes_update_btn = EquationButton("Update")
        h_spacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.notes_btn_h_layout.addItem(h_spacer)
        self.notes_btn_h_layout.addWidget(self.notes_update_btn)
        self.notes_v_layout.addWidget(self.notes_btn_frame)

        self.var_notes_vsplt = Customsplitter(Qt.Vertical)
        self.var_notes_vsplt.addWidget(self.variables_gbox)
        self.var_notes_vsplt.addWidget(self.notes_gbox)
        self.var_notes_v_layout.addWidget(self.var_notes_vsplt)

        # endregion

        self.detail_v_splitter = Customsplitter()
        self.detail_v_splitter.addWidget(self.latex_gbox)
        self.detail_v_splitter.addWidget(self.var_notes_frame)
        self.detail_v_splitter.setSizes([int(self.width*0.7*0.5), int(self.width*0.7*0.5)])
        self.eq_details_v_layout.addWidget(self.detail_v_splitter)

        # endregion

        # region Main Splitter splits the equation groups list view from the details view
        # -----------------------------------------------------------------------------------------------------------
        self.main_splitter = Customsplitter()
        self.main_splitter.addWidget(self.eq_group_gbox)
        self.main_splitter.addWidget(self.eq_details_gbox)
        self.main_splitter.setSizes([int(self.width*0.3), int(self.width*0.7)])
        # endregion

        # region Main Window Creation
        self.main_frame = QFrame()
        self.main_layout = QVBoxLayout(self.main_frame)
        self.main_layout.addWidget(self.main_splitter)

        self.setCentralWidget(self.main_frame)

        self.setGeometry(self.left, self.top, self.width, self.height)

        self.setWindowTitle(self.title)
        app_icon = QIcon("Icons/sigma_icon.png")
        self.setWindowIcon(app_icon)
        self.app.setStyle('Oxygen')
        # endregion

        # region Data members
        self.eqn_grp = EquationGroup()
        self.eq = Equation()
        self.var = Variable()
        self.unit = Unit()
        self.eq_type = TypeTable(name='equation_type')
        self.var_type = TypeTable(name='variable_type')
        self.unit_type = TypeTable(name='unit_type')

        self.eq_grp_id: int = 1  # Can envision it pulling user specified state information someday
        self.eqn_records_for_eqn_group = None  # Gets Populated when equations are present
        self.eq_id: tuple = (1,)  # Same comment as eq_grp_id
        self.var_records_for_eqns = None  # Gets populated when eqn_group_gets selected

        self.refresh_eqn_group_combo_box()
        self.populate_equation_listbox()
        self.app.setStyleSheet(self.style_sheet)

        # endregion

    def new_equation_group(self):
        """Adds a new equation group"""
        dlg = EquationGroupDialog(self)

        if dlg.exec_():
            self.eqn_grp = dlg.eqn_group
            self.eq_group_cbox.addItem(self.eqn_grp.last_inserted.name)
            self.eq_group_cbox.setCurrentIndex(self.eq_group_cbox.count()-1)
        else:
            print('Cancel!')

    def get_equation_group(self):
        """Returns eqn_grp variable"""
        return self.eqn_grp

    def get_equation(self):
        """Returns eq variable"""
        return self.eq

    def populate_equation_type_cbox(self):
        """Populates equation type combo box"""
        tcb = self.type_cbox

        types = self.eq_type.types()

        for tp in types:  # pylint: disable=invalid-name
            tcb.addItem(tp)

    def refresh_eqn_group_combo_box(self, verbose: bool = False):
        """Refresh equation group combo box"""
        self.eq_group_cbox.clear()
        records = self.get_equation_group().records

        record_names = records['name']
        if verbose is True:
            print(records)

        for name in record_names:
            self.eq_group_cbox.addItem(name)

    def populate_equation_listbox(self):
        """Populate equation listbox"""
        eq_grp_cb = self.eq_group_cbox
        eq_lb = self.equation_listbox

        ind = eq_grp_cb.currentIndex()
        eq_grp = self.get_equation_group()
        eq_grp_id = eq_grp.records[eq_grp.id_name][ind]
        self.eq_grp_id = eq_grp_id

        eqs = self.get_equation()

        eq_lb.clear()
        eqs.set_records_for_parent(parent_id=eq_grp_id)

        for row in eqs.selected_data_records:
            eq_lb.addItem(row.name)

    def select_one_equation(self):
        """This type of selection shows all equation details"""
        eq_lb = self.equation_listbox
        eq_grp_id = self.eq_grp_id  # pylint: disable=unused-variable

        eq = self.eq
        var = self.var  # pylint: disable=unused-variable

        ind = eq_lb.selectedIndexes()

        for i in ind:  # There is only one
            selected_eqn = eq.selected_data_records[i.row()-1]
            self.name_l_edit.setText(selected_eqn.name)
            self.codefile_l_edit.setText(selected_eqn.code_file_path)
            # self.populate_equation_type_cbox(selected=eqs['type'][ind])

    def select_multiple_equations(self, verbose: bool = False):
        """This type of selction only shows associated variables"""

    def load_variables(self, parent_id: int = 1):
        """Method to populate variables table widget"""

    def add_equation(self):
        """Add Equation to Equation Database"""
        dlg = EquationGroupDialog(self)

        if dlg.exec_():
            self.eqn_grp = dlg.eq_group
            self.eq_group_cbox.addItem(self.eqn_grp.last_inserted.name)
            self.eq_group_cbox.setCurrentIndex(self.eq_group_cbox.count() - 1)
        else:
            print('Cancel!')


def main(*args, **kwargs):  # pylint: disable=unused-argument
    """Main of the eqatuation database"""
    db_params = config()
    conn = connect(**db_params)

    ui = Window()  # pylint: disable=invalid-name
    ui.show()
    conn.close()
    sys.exit(ui.app.exec_())


if __name__ == '__main__':
    main()
