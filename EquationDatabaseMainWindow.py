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
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter,
    QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox,
    QLabel, QLineEdit, QFrame, QComboBox,
    QSpacerItem, QSizePolicy, QPushButton, QGridLayout,
    QTextEdit, QGraphicsView, QTableWidget, QGraphicsDropShadowEffect,
    QListWidget, QAction, QAbstractItemView  # , QMessageBox
)

from scipy.constants import golden_ratio
from equation_group_dialog import Equation_Group_Dialog
from psycopg2 import connect
from config import config
from equation_group import EquationGroup
from equation import Equation
from variable import Variable
from unit import Unit
from type_table import TypeTable

# region Windows Task Bar Icon
import ctypes

window_left_start = 300
window_top_start = 300
window_height = 1500

if platform.system() == "Windows":
    import wmi

    obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)

    displays = [x for x in obj if x.PNPClass == 'Monitor']

    if len(displays) == 2:
        window_left_start = 3200
        window_top_start = 25
        window_height = 900
    elif len(displays) == 3:
        window_left_start = 7600
        window_top_start = 300
        window_height = 1500

    # for item in obj:
    #     if item.Name == 'Dell S2240T(HDMI)':
    #         window_left_start = 3200
    #         window_top_start = 25
    #         window_height = 900

    myappid = 'deshazersoftware.equationdatabase.equationdatabase.0.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
# endregion


class Handle(QWidget):
    def paintEvent(self, e=None):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(133, 45, 145), Qt.Dense5Pattern))
        painter.drawRect(self.rect())


class customSplitter(QSplitter):

    def __init__(self, *args):
        super(customSplitter, self).__init__(*args)
        self.width = None

    def addWidget(self, wdg):
        super().addWidget(wdg)
        self.width = self.handleWidth()
        l_handle = Handle()
        l_handle.setMaximumSize(self.width*10, self.width*12)
        layout = QHBoxLayout(self.handle(self.count()-1))
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(l_handle)


class eqButton(QPushButton):
    """"""
    def __init__(self, *args, **kwargs):
        super(eqButton, self).__init__(*args, **kwargs)
        """Constructor for eqButton"""
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(10, 10)
        self.setGraphicsEffect(effect)


class Window(QMainWindow):

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        super(Window, self).__init__(*args, **kwargs)

        self.styleSheet = """
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
        self.left = window_left_start
        # self.left = 0
        self.top = window_top_start
        self.height = window_height
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
        new_eqn_group_action.triggered.connect(self.newEquationGroup)

        eqn_group_info_action = QAction(QIcon('Icons/info_icon256x256.png'), '&Equation Group Information', self)
        eqn_group_info_action.setShortcut('Alt+I')
        eqn_group_info_action.setStatusTip('Equation Group Information')

        self.toolbar.addAction(save_action)
        self.toolbar.addAction(new_eqn_action)
        empty1 = QWidget(self.toolbar)
        ew: int = 50
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
        self.eq_group_vLayout = QVBoxLayout(self.eq_group_gbox)
        self.eq_group_vLayout.setSpacing(5)

        self.eq_group_cbox = QComboBox(self.eq_group_gbox)
        self.eq_group_cbox.activated.connect(self.populateEquationListBox)

        self.eq_group_vLayout.addWidget(self.eq_group_cbox)

        self.analyze_frame = QFrame(self.eq_group_gbox)
        self.analyze_hLayout = QHBoxLayout(self.analyze_frame)
        self.analyze_hLayout.setContentsMargins(10, 0, 10, 15)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.analyze_frame.setSizePolicy(size_policy)

        self.filter_frame = QFrame(self.eq_group_gbox)
        self.filter_hLayout = QHBoxLayout(self.filter_frame)
        self.filter_hLayout.setContentsMargins(0, 0, 0, 0)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.filter_frame.setSizePolicy(size_policy)

        self.filter_lbl = QLabel("Filter")
        self.filter_lEdit = QLineEdit(self.eq_group_gbox)
        self.filter_hLayout.addWidget(self.filter_lbl)
        self.filter_hLayout.addWidget(self.filter_lEdit)
        self.eq_group_vLayout.addWidget(self.filter_frame)

        self.equation_listbox = QListWidget(self.eq_group_gbox)
        self.equation_listbox.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.equation_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.equation_listbox.itemClicked.connect(self.select_one_equation)
        self.equation_listbox.itemSelectionChanged.connect(self.select_multiple_equations)

        self.eq_group_vLayout.addWidget(self.equation_listbox)

        # TODO add refresh to listbox here

        self.eq_add_btn = QPushButton("+")
        self.eq_add_btn.setObjectName("add_rm_btn")
        ar_w = 50
        self.eq_add_btn.setFixedSize(QSize(ar_w, int(ar_w)))
        self.eq_add_btn.clicked.connect(self.addEquation)

        self.eq_rm_btn = QPushButton("-")
        self.eq_rm_btn.setObjectName("add_rm_btn")
        self.eq_rm_btn.setFixedSize(QSize(ar_w, int(ar_w)))

        self.eq_add_rm_frame = QFrame(self.eq_group_gbox)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.eq_add_rm_frame.setSizePolicy(size_policy)
        self.eq_add_rm_hLayout = QHBoxLayout(self.eq_add_rm_frame)
        self.eq_add_rm_hLayout.setSpacing(2)
        hSpacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.eq_add_rm_hLayout.addItem(hSpacer)
        self.eq_add_rm_hLayout.addWidget(self.eq_add_btn)
        self.eq_add_rm_hLayout.addWidget(self.eq_rm_btn)
        self.eq_group_vLayout.addWidget(self.eq_add_rm_frame)

        # endregion

        # region Equation Details - Right Frame
        # -----------------------------------------------------------------------------------------------------------
        self.eq_details_gbox = QGroupBox("Equation Details")  # Entire encapsulating Gbox
        self.eq_details_vLayout = QVBoxLayout(self.eq_details_gbox)

        # region Equation Header added to Equation Details
        # **********************************************************
        self.eq_header_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.eq_header_frame.setSizePolicy(size_policy)
        self.eq_header_gLayout = QGridLayout(self.eq_header_frame)
        self.eq_details_vLayout.addWidget(self.eq_header_frame)

        self.name_label = QLabel("Equation Name")
        self.name_lEdit = QLineEdit()
        self.eq_header_gLayout.addWidget(self.name_label, 0, 0)
        self.eq_header_gLayout.addWidget(self.name_lEdit, 0, 1)

        self.codefile_label = QLabel("Code File")
        self.codefile_lEdit = QLineEdit()
        self.eq_header_gLayout.addWidget(self.codefile_label, 1, 0)
        self.eq_header_gLayout.addWidget(self.codefile_lEdit, 1, 1)

        self.type_label = QLabel("Type")
        self.type_cbox = QComboBox()
        self.type_cbox.setMinimumWidth(700)
        self.eq_header_gLayout.addWidget(self.type_label, 0, 2)
        self.eq_header_gLayout.addWidget(self.type_cbox, 0, 3)

        self.associated_eq_groups_btn = eqButton("Associated Eq Groups")
        self.eq_header_gLayout.addWidget(self.associated_eq_groups_btn, 1, 3)
        self.eq_header_gLayout.setAlignment(self.associated_eq_groups_btn, Qt.AlignLeft)
        self.details_btn = eqButton("Other Details")
        self.eq_header_gLayout.addWidget(self.details_btn, 1, 3)
        self.eq_header_gLayout.setAlignment(self.details_btn, Qt.AlignRight)
        # endregion

        # region LaTeX added to Equation Details
        # **********************************************************

        self.latex_gbox = QGroupBox("LaTeX")
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.latex_gbox.setSizePolicy(size_policy)
        self.latex_vLayout = QVBoxLayout(self.latex_gbox)
        self.latex_textbox = QTextEdit(self.latex_gbox)
        self.latex_graphicbox = QGraphicsView(self.latex_gbox)
        # self.latex_graphicbox.setMinimumSize(QSize(907, 369))

        self.latexSplitter = customSplitter(Qt.Vertical)  # Note Handle for a vertical splitter is oriented Horizontally
        self.latexSplitter.addWidget(self.latex_textbox)
        self.latexSplitter.addWidget(self.latex_graphicbox)
        self.latex_vLayout.addWidget(self.latexSplitter)

        self.latex_btn_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.latex_btn_frame.setSizePolicy(size_policy)
        self.latex_btn_hLayout = QHBoxLayout(self.latex_btn_frame)
        self.latex_btn_hLayout.setContentsMargins(0, 0, 1, 10)
        self.latex_template_btn = eqButton("Template")
        self.latex_update_btn = eqButton("Update")
        hSpacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.latex_btn_hLayout.addWidget(self.latex_template_btn)
        self.latex_btn_hLayout.addItem(hSpacer)
        self.latex_btn_hLayout.addWidget(self.latex_update_btn)
        self.latex_vLayout.addWidget(self.latex_btn_frame)

        # endregion

        # region Variables Notes
        self.var_notes_frame = QFrame(self.eq_details_gbox)
        self.var_notes_vLayout = QVBoxLayout(self.var_notes_frame)
        # self.var_notes_frame.setLayout(self.var_notes_vLayout)

        self.variables_gbox = QGroupBox("Variables")
        self.variables_vLayout = QVBoxLayout(self.variables_gbox)
        self.variables_vLayout.setSpacing(5)
        # self.variables_gbox.setLayout(self.var_notes_vLayout)
        self.variables_tbl = QTableWidget(self.variables_gbox)
        self.variables_vLayout.addWidget(self.variables_tbl)

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
        self.var_add_rm_hLayout = QHBoxLayout(self.var_add_rm_frame)
        self.var_add_rm_hLayout.setSpacing(2)
        hSpacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.var_add_rm_hLayout.addItem(hSpacer)
        self.var_add_rm_hLayout.addWidget(self.var_add_btn)
        self.var_add_rm_hLayout.addWidget(self.var_rm_btn)
        self.variables_vLayout.addWidget(self.var_add_rm_frame)

        self.notes_gbox = QGroupBox("Notes")
        self.notes_vLayout = QVBoxLayout(self.notes_gbox)
        # self.notes_gbox.setLayout(self.notes_vLayout)
        self.notes_textbox = QTextEdit(self.notes_gbox)
        self.notes_vLayout.addWidget(self.notes_textbox)

        self.notes_btn_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.notes_btn_frame.setSizePolicy(size_policy)
        self.notes_btn_hLayout = QHBoxLayout(self.notes_btn_frame)
        self.notes_btn_hLayout.setContentsMargins(0, 0, 1, 10)
        self.notes_update_btn = eqButton("Update")
        hSpacer = QSpacerItem(20, 40, QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.notes_btn_hLayout.addItem(hSpacer)
        self.notes_btn_hLayout.addWidget(self.notes_update_btn)
        self.notes_vLayout.addWidget(self.notes_btn_frame)

        self.var_notes_vsplt = customSplitter(Qt.Vertical)
        self.var_notes_vsplt.addWidget(self.variables_gbox)
        self.var_notes_vsplt.addWidget(self.notes_gbox)
        self.var_notes_vLayout.addWidget(self.var_notes_vsplt)

        # endregion

        self.detail_vSplitter = customSplitter()
        self.detail_vSplitter.addWidget(self.latex_gbox)
        self.detail_vSplitter.addWidget(self.var_notes_frame)
        self.detail_vSplitter.setSizes([int(self.width*0.7*0.5), int(self.width*0.7*0.5)])
        self.eq_details_vLayout.addWidget(self.detail_vSplitter)

        # endregion

        # region Main Splitter splits the equation groups list view from the details view
        # -----------------------------------------------------------------------------------------------------------
        self.mainSplitter = customSplitter()
        self.mainSplitter.addWidget(self.eq_group_gbox)
        self.mainSplitter.addWidget(self.eq_details_gbox)
        self.mainSplitter.setSizes([int(self.width*0.3), int(self.width*0.7)])
        # endregion

        # region Main Window Creation
        self.mainFrame = QFrame()
        self.mainLayout = QVBoxLayout(self.mainFrame)
        self.mainLayout.addWidget(self.mainSplitter)

        self.setCentralWidget(self.mainFrame)

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

        self.refreshEqnGroupComboBox()
        self.populateEquationListBox()
        self.app.setStyleSheet(self.styleSheet)
        # TODO add callback for ComboxBox selection changed

        # endregion

    def newEquationGroup(self):
        dlg = Equation_Group_Dialog(self)

        if dlg.exec_():
            self.eqn_grp = dlg.eqn_group
            self.eq_group_cbox.addItem(self.eqn_grp.last_inserted.name)
            self.eq_group_cbox.setCurrentIndex(self.eq_group_cbox.count()-1)
        else:
            print('Cancel!')

    def getEquationGroup(self):
        return self.eqn_grp

    def getEquations(self):
        return self.eq

    def populate_equation_type_cbox(self, selected: int = 1):
        tcb = self.type_cbox

        types = self.eq_type.types()

        for tp in types:
            tcb.addItem(tp)

    def refreshEqnGroupComboBox(self, new_record=None, verbose: bool = False):
        self.eq_group_cbox.clear()
        records = self.getEquationGroup().records

        record_names = records['name']
        if verbose is True:
            print(records)

        for name in record_names:
            self.eq_group_cbox.addItem(name)

    # TODO populate listbox
    def populateEquationListBox(self, verbose: bool = False):
        eq_grp_cb = self.eq_group_cbox
        eq_lb = self.equation_listbox

        ind = eq_grp_cb.currentIndex()
        eq_grp = self.getEquationGroup()
        eq_grp_id = eq_grp.records[eq_grp.id_name][ind]
        self.eq_grp_id = eq_grp_id

        eqs = self.getEquations()

        eq_lb.clear()
        records_for_group = eqs.get_records_for_parent(parent_id=eq_grp_id)
        self.eqn_records_for_eqn_group = records_for_group

        names = records_for_group['name']
        if verbose is True:
            print(eq_grp_id, names)

        for name in names:
            eq_lb.addItem(name)

    def select_one_equation(self, item, verbose: bool = False):
        """This type of selection shows all equation details"""
        eq_lb = self.equation_listbox
        eq_grp_id = self.eq_grp_id

        eq = self.eq
        var = self.var

        ind = eq_lb.selectedIndexes()

        eqs = self.eqn_records_for_eqn_group

        for i in ind:  # There is only one
            ind = i.row()
            self.name_lEdit.setText(item.text())
            self.codefile_lEdit.setText(eqs['code_file_path'][ind])
            self.populate_equation_type_cbox(selected=eqs['type'][ind])

    def select_multiple_equations(self, verbose: bool = False):
        """This type of selction only shows associated variables"""

    def load_variables(self, parent_id: int = 1):
        rcds = self.var.records_not_in_parent(parent_id=(parent_id, ))
        print(rcds)

    def addEquation(self):
        dlg = Equation_Group_Dialog(self)

        if dlg.exec_():
            self.eqn_grp = dlg.eq_group
            self.eq_group_cbox.addItem(self.eqn_grp.last_inserted.name)
            self.eq_group_cbox.setCurrentIndex(self.eq_group_cbox.count() - 1)
        else:
            print('Cancel!')


def main(*args, **kwargs):
    db_params = config()
    conn = connect(**db_params)

    ui = Window()
    ui.show()
    conn.close()
    sys.exit(ui.app.exec_())


if __name__ == '__main__':
    main()
