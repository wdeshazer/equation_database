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
from collections import namedtuple
from typing import Optional
# region Windows Task Bar Icon
import ctypes
import screeninfo

from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, QItemSelection, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter,
    QHBoxLayout, QVBoxLayout, QMainWindow, QGroupBox,
    QLabel, QLineEdit, QFrame, QComboBox,
    QSpacerItem, QSizePolicy, QPushButton, QGridLayout, QGraphicsScene,
    QTextEdit, QGraphicsView, QTableWidget, QGraphicsDropShadowEffect,
    QAction, QAbstractItemView, QTableWidgetItem, QMessageBox,
    QAbstractButton
)

from scipy.constants import golden_ratio
from psycopg2 import connect
from latex_data_widget import LaTexTextEdit
from config import config
from equation_group import EquationGroup
from db_utils import my_connect
from equation_group_dialog import EquationGroupDialog
from equation_dialog import EquationDialog
from equations import GroupedEquations  # , EquationRecord
from variables import GroupedVariables, GroupedVariableRecord
from variable_dialog import VariableDialog
from CustomWidgets.filter_list_widget import EDFilterListWidget
from unit import Unit
from type_table import TypeTable
from time_logging import TimeLogger

WINDOW_LEFT_START = 300
WINDOW_TOP_START = 300
WINDOW_HEIGHT = 1500

if platform.system() == "Windows":
    outer_log = TimeLogger()
    outer_log.new_event('Starting Windows Stuff: ')

    displays = screeninfo.get_monitors()

    if len(displays) == 2:
        WINDOW_LEFT_START = 3200
        WINDOW_TOP_START = 25
        WINDOW_HEIGHT = 900
    elif len(displays) == 3:
        my_mon = displays[2]
        WINDOW_LEFT_START = my_mon.x + int(my_mon.width / 20)
        WINDOW_TOP_START = 300
        WINDOW_HEIGHT = 1500

    # for item in obj:
    #     if item.Name == 'Dell S2240T(HDMI)':
    #         window_left_start = 3200
    #         window_top_start = 25
    #         window_height = 900

    MYAPPID = 'deshazersoftware.equationdatabase.equationdatabase.0.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MYAPPID)

    outer_log.new_event('Finished Windows Stuff')


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
        l_handle.setMaximumSize(self.width * 10, self.width * 12)
        layout = QHBoxLayout(self.handle(self.count() - 1))
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


StateData = namedtuple('StateData', ['selected', 'deselected', 'details'])
RESET: bool = False


# pylint: disable=too-many-instance-attributes, too-many-statements, too-many-public-methods
class Window(QMainWindow):
    """Main Window for Application"""

    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        super().__init__(*args, **kwargs)

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
        t_log = TimeLogger()

        verbose = True
        my_conn = my_connect(t_log=t_log, verbose=verbose)
        self.my_conn = my_conn

        t_log.new_event("Start Gui Build: ")

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

        self.equation_filter_list = EDFilterListWidget(self.eq_group_gbox)
        self.equation_listbox = self.equation_filter_list.list
        # self.equation_listbox = QListWidget(self.eq_group_gbox)
        self.equation_listbox.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.equation_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.equation_listbox.selectionModel().selectionChanged.connect(self.select_one_equation)
        self.equation_filter_list.add.connect(self.add_equation)
        self.equation_filter_list.remove.connect(self.remove_equation)

        self.eq_group_v_layout.addWidget(self.equation_filter_list)
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

        # This would be great for when one wants to filter content based on what is being typed
        # self.latex_textbox.textChanged.connect(self.update_latex_image)

        self.latex_graphicbox = QGraphicsView(self.latex_gbox)
        self.scene = QGraphicsScene()
        self.latex_graphicbox.setScene(self.scene)
        # self.latex_graphicbox.setMinimumSize(QSize(907, 369))

        self.latex_textbox = LaTexTextEdit(my_conn=my_conn, parent=self.latex_gbox, t_log=t_log, scene=self.scene,
                                           graphics_view=self.latex_graphicbox, verbose=verbose)

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
        self.var_add_btn.clicked.connect(self.add_variable)

        self.var_rm_btn = QPushButton("-")
        self.var_rm_btn.setObjectName("add_rm_btn")
        self.var_rm_btn.clicked.connect(self.remove_variable)
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
        self.detail_v_splitter.setSizes([int(self.width * 0.7 * 0.5), int(self.width * 0.7 * 0.5)])
        self.eq_details_v_layout.addWidget(self.detail_v_splitter)

        # endregion

        # region Main Splitter splits the equation groups list view from the details view
        # -----------------------------------------------------------------------------------------------------------
        self.main_splitter = Customsplitter()
        self.main_splitter.addWidget(self.eq_group_gbox)
        self.main_splitter.addWidget(self.eq_details_gbox)
        self.main_splitter.setSizes([int(self.width * 0.3), int(self.width * 0.7)])
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

        t_log.new_event("End GUI Build")

        self.state_data = dict()
        # t_log.new_event("Equation Group Load")
        self.eqn_grp = EquationGroup(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.eq = GroupedEquations(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.var = GroupedVariables(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.unit = Unit(my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.eq_type = TypeTable(name='equation_type', my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.var_type = TypeTable(name='variable_type', my_conn=my_conn, t_log=t_log, verbose=verbose)
        self.unit_type = TypeTable(name='unit_type', my_conn=my_conn, t_log=t_log, verbose=verbose)

        t_log.new_event("Data Finished Loading")

        self.eq_grp_id: int = 1  # Can envision it pulling user specified state information someday
        self.eqn_records_for_eqn_group = None  # Gets Populated when equations are present
        self.eq_id: tuple = (1,)  # Same comment as eq_grp_id
        self.var_records_for_eqns = None  # Gets populated when eqn_group_gets selected
        self.selected_equation = None  # Stores the selected equation
        self.latex_textbox.db_ref = self.eq
        self.equation_taken: bool = False

        t_log.new_event("Populating Boxes")
        self.refresh_eqn_group_combo_box()
        self.populate_equation_listbox()
        t_log.new_event("Populating Boxes")
        self.app.setStyleSheet(open('equation_db.css').read())
        t_log.new_event("Finished Style Sheet")
        print()
        print('Total Time: ', t_log.total_time())

        # endregion

    @pyqtSlot()
    def new_equation_group(self):
        """Adds a new equation group"""
        dlg = EquationGroupDialog(self, eqn_group=self.eqn_grp, eqn=self.eq)

        if dlg.exec_():
            self.eqn_grp = dlg.eqn_group
            last_inserted = self.eqn_grp.all_records.iloc[-1]
            self.eq_group_cbox.addItem(last_inserted['name'])
            self.eq_group_cbox.setCurrentIndex(self.eq_group_cbox.count() - 1)
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

    def refresh_eqn_group_combo_box(self):
        """Refresh equation group combo box"""
        self.eq_group_cbox.clear()
        records = self.eqn_grp.all_records.itertuples()
        for record in records:
            self.eq_group_cbox.addItem(record.name)

    def clear_boxes(self, equation_selected: bool = True):
        """Clear all widgets"""

        if equation_selected is False:
            self.equation_filter_list.clear()
        self.name_l_edit.clear()
        self.codefile_l_edit.clear()
        self.type_cbox.clear()
        self.latex_textbox.clear()
        self.scene.clear()
        self.variables_tbl.clearContents()
        self.notes_textbox.clear()

    def select_a_type_cbox(self, a_type: str = None):
        """Select a type check box"""
        type_cbox = self.type_cbox

        for a_type_name in self.eq_type.types():
            type_cbox.addItem(a_type_name)

        ind = self.eq_type.index(a_type)
        type_cbox.setCurrentIndex(ind)

    def populate_equation_listbox(self):
        """Populate equation listbox"""
        self.reset_selected_equation_data()
        eq_fl = self.equation_filter_list
        eq = self.eq

        self.clear_boxes(equation_selected=False)
        if eq.selected_data_records is not None:
            for row in eq.selected_data_records:
                eq_fl.addItem(row.name)

    def reset_selected_equation_data(self):
        """Reset Selected Equation Data"""
        eq_grp_cb = self.eq_group_cbox

        ind = eq_grp_cb.currentIndex()

        eq_grp = self.eqn_grp
        eq_grp_id = eq_grp.all_records.index[ind]
        self.eq_grp_id = eq_grp_id

        eq = self.eq

        eq.set_records_for_parent(parent_id=eq_grp_id)

    @pyqtSlot(QItemSelection, QItemSelection)
    def select_one_equation(self, selected: QItemSelection, deselected: QItemSelection):
        """This type of selection shows all equation details"""

        # This makes an equation removed behave like an empty selection
        if self.equation_taken is True:
            deselected = selected
            self.equation_taken = RESET

        self.state_data.update(selected=selected)
        self.state_data.update(deselected=deselected)

        # First selection
        first_selection = deselected.isEmpty() is True and selected.isEmpty() is False
        # print('First Selection is: ', first_selection)

        # This means an equation was selected and then another equation was selection
        normal_selection = deselected.isEmpty() is False and selected.isEmpty() is False
        # print('Normal Selection is: ', normal_selection)

        # This means an equation was deselected, but there wasn't a new selection
        # There are two conditions when this happens. 1) All selections cleared 2) Record is deleted
        empty_selection = (deselected.isEmpty() is False and selected.isEmpty() is True) and \
            self.equation_taken is False
        # print('Empty Selection is: ', empty_selection)

        if normal_selection or empty_selection:
            self.capture_details_current_state()
            dirty_data = self.state_data['dirty_data']
            if dirty_data['new']:
                up_box = QMessageBox()
                keys = dirty_data['new'].keys()

                up_box.setIcon(QMessageBox.Question)
                up_box.setText('Changes were made')
                up_box.setWindowTitle('Save Changes')
                up_box.setDetailedText('Additional details')
                fmt = '{key}\n\twas: {value}\n\tis: {new_val}\n'
                msg = ''
                for key in keys:
                    if key == 'notes':
                        msg += '\tNotes were changed\n'
                    else:
                        msg += fmt.format(key=key, value=dirty_data['old'][key], new_val=dirty_data['new'][key])
                up_box.setDetailedText(msg)
                up_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                up_box.setDefaultButton(QMessageBox.Save)
                # noinspection PyUnresolvedReferences
                up_box.buttonClicked.connect(self.allow_equation_change)
                up_box.exec_()
            else:
                self.refresh_equation_details()

        if first_selection:
            self.refresh_equation_details()

        # region selcted/deselected Example
        # Selected and Deselected are lists of QModelIndex's, so to access methods associated with a QModelIndex
        # One must access the list first
        # if selected.isEmpty() is True:
        #     print('No selcted Data')
        # else:
        #     for item in selected.indexes():
        #         print('\nSelected has data:')
        #         print('\tRow: ', str(item.row()))
        #         print('\tData: ', item.data())
        #
        # if deselected.isEmpty() is True:
        #     print('No deselcted Data')
        # else:
        #     for item in deselected.indexes():
        #         print('DeSelected has data:')
        #         print('\tRow: ', str(item.row()))
        #         print('\tData: ', item.data())
        # endregion

    def _selected_eqn_group_id(self):
        ind = self.eq_group_cbox.currentIndex()
        rcd = self.eqn_grp.all_records[ind]
        return rcd.eqn_group_id

    def refresh_equation_details(self):
        """Refresh Equation Details"""
        eq_lb = self.equation_listbox
        eq = self.eq

        self.clear_boxes()

        ind = eq_lb.selectedIndexes()

        for i in ind:  # There is only one
            selected_eqn = eq.selected_data_records[i.row()]
            self.selected_equation = selected_eqn
            self.name_l_edit.setText(selected_eqn.name)
            self.codefile_l_edit.setText(selected_eqn.code_file_path)
            self.select_a_type_cbox(a_type=selected_eqn.type_name)
            self.latex_textbox.setText(selected_eqn.latex)
            self.latex_textbox.setAlignment(Qt.AlignLeft)
            self.latex_textbox.latex_data = selected_eqn.latex_obj
            self.latex_textbox.db_ref_id = selected_eqn.Index
            self.show_latex_image(selected_eqn.image)
            self.notes_textbox.setText(selected_eqn.notes)
            self.var.set_records_for_parent(parent_id=selected_eqn.Index)
            self.show_variable_table()
            # self.populate_equation_type_cbox(selected=eqs['type'][ind])

    def capture_details_current_state(self):
        """Capture the details current state"""
        deselected = self.state_data['deselected']

        rcd = deselected.indexes()
        deselected_eqn = self.eq.selected_data_records[rcd[0].row()]

        details_data = dict(
            name=self.name_l_edit.text(),
            type_name=self.type_cbox.currentText(),
            code_file_path=self.codefile_l_edit.text(),
            latex=self.latex_textbox.toPlainText(),
            notes=self.notes_textbox.toPlainText()
        )

        self.state_data.update(details_state=details_data)

        dirty_data = dict(old=dict(), new=dict())
        for key, value_new in details_data.items():
            value_old = getattr(deselected_eqn, key)
            value_old = '' if value_old is None else value_old
            if value_old != value_new:
                print('Adding key: ', key, ' value: ', value_new)
                dirty_data['new'].update({key: value_new})
                dirty_data['old'].update({key: value_old})

        self.state_data.update(dirty_data=dirty_data)

    @pyqtSlot(QAbstractButton)
    def allow_equation_change(self, response: QAbstractButton):
        """Allow Equation Change"""
        # selected: QItemSelection = self.state_data['selected']
        deselected: QItemSelection = self.state_data['deselected']
        dirty_data = self.state_data['dirty_data']

        if response.text() == 'Discard':
            print('Ok')
            self.refresh_equation_details()
        elif response.text() == 'Save':
            d_rcd = deselected.indexes()
            ind = d_rcd[0].row()
            deselected_eqn = self.eq.selected_data_records[ind]

            new_dd: dict = dirty_data['new']

            eq_id = deselected_eqn.Index
            self.eq.update(an_id=eq_id, data=new_dd, verbose=True)
            if 'name' in new_dd.keys():
                item = self.equation_listbox.item(ind)
                item.setText(new_dd['name'])

            dirty_data = dict(new=None, old=None)
            self.state_data.update(dirty_data=dirty_data)
            # response.close()
            self.reset_selected_equation_data()
            self.refresh_equation_details()

    def show_variable_table(self):
        """Show Variable table"""
        var = self.var
        tbl = self.variables_tbl
        tbl.clearContents()

        if var.selected_data_records is not None:
            var_records = var.selected_data_records
            tbl.setRowCount(len(var_records))

            header = self.table_info('header')

            tbl.setColumnCount(len(header))
            tbl.setHorizontalHeaderLabels(header)

            for i, record in enumerate(var_records):
                self.add_record_to_variable_table(record=record, row=i)

    @staticmethod
    def table_info(info):
        """Convenience function to collocate information for the table"""
        header = ['Variable', 'Name', 'Dimension', 'Unit', 'Unit Name', 'Type of Variable']
        column = dict(var_image=0, var_name=1, dimension=2, unit_image=3, unit_name=4)
        data = header if info == 'header' else column
        return data

    def add_record_to_variable_table(self, record: GroupedVariableRecord, row: int = None):  # , verbose: bool = False):
        """Add record to variable table"""
        tbl = self.variables_tbl

        column = self.table_info('column')

        # This will add a row
        if row is None:
            row = tbl.rowCount()

        img = QImage.fromData(record.image)
        pixmap = QPixmap.fromImage(img)
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        tbl.setCellWidget(row, column['var_image'], lbl)
        tbl.setItem(row, column['var_name'], QTableWidgetItem(record.name))
        tbl.setItem(row, column['dimension'], QTableWidgetItem(str(record.dimensions)))

        un_id_for_var = record.unit_id

        unit = self.unit.all_records[un_id_for_var]
        if unit.image is not None:
            img = QImage.fromData(unit.image)
            pixmap = QPixmap.fromImage(img)
            lbl = QLabel()
            lbl.setPixmap(pixmap)
            tbl.setCellWidget(row, column['unit_image'], lbl)
        tbl.setItem(row, column['unit_name'], QTableWidgetItem(unit.name))

    def show_latex_image(self, image: Optional[bytes] = None):
        """Show Latex Image"""

        if image is None:
            pass
        else:
            img = QImage.fromData(image)
            pixmap = QPixmap.fromImage(img)

            scene = self.scene
            scene.addPixmap(pixmap)
            # self.latex_graphicbox.setScene(scene)
            self.latex_graphicbox.show()

    def select_multiple_equations(self, verbose: bool = False):
        """This type of selction only shows associated variables"""

    def load_variables(self, parent_id: int = 1):
        """Method to populate variables table widget"""

    @pyqtSlot()
    def add_variable(self):
        """Add Equation to Equation Database"""
        dlg = VariableDialog(var=self.var, my_conn=self.my_conn, parent=self)

        if dlg.exec_():
            print('Inserted')
            self.var.set_records_for_parent()
            # self.update_variable_insert_order()

    def update_variable_insert_order(self):
        """Update Variable Insertion Order"""
        var = self.var
        var_tbl = self.variables_tbl

        order = dict()
        for i in range(var_tbl.rowCount()):
            var_name = var_tbl.item(i, 2)
            order.update({var_name: i})
        var.update_insertion_order_for_selected(order=order)

    @pyqtSlot()
    def remove_variable(self):
        """Remove variable from equation"""
        inds = self.equation_listbox.selectedIndexes()
        parent_id = self.eq.selected_parent_id
        eqn = self.eq

        if len(inds) == 0:
            msg = QMessageBox()
            msg.setText('Please select an equation to remove')
            msg.exec_()
            return

        for ind in inds:
            i = ind.row()
            child_id = eqn.selected_data_records[i].Index
            eqn.disassociate_parent(my_conn=self.my_conn, parent_id=parent_id, child_id=child_id)
            self.equation_taken = True
            self.equation_listbox.takeItem(i)

        self.eq.set_records_for_parent(parent_id=self.eq.selected_parent_id)

    def add_equation(self):
        """Add Equation to Equation Database"""
        dlg = EquationDialog(eqn=self.eq, my_conn=self.my_conn, parent=self.equation_filter_list)

        if dlg.exec_():
            print('Inserted')
            self.eq.set_records_for_parent()
            self.update_equation_insert_order()

    def update_equation_insert_order(self):
        """Update Insertion Order"""
        eq = self.eq
        eq_lb = self.equation_filter_list

        order = dict()
        for i in range(eq_lb.count()):
            order.update({eq_lb.item(i).text(): i})
        eq.update_insertion_order_for_selected(order=order)

    def remove_equation(self):
        """Remove Equation from equation group"""
        inds = self.equation_listbox.selectedIndexes()
        parent_id = self.eq.selected_parent_id
        eqn = self.eq

        if len(inds) == 0:
            msg = QMessageBox()
            msg.setText('Please select an equation to remove')
            msg.exec_()
            return

        for ind in inds:
            i = ind.row()
            child_id = eqn.selected_data_records[i].Index
            eqn.disassociate_parent(my_conn=self.my_conn, parent_id=parent_id, child_id=child_id)
            self.equation_taken = True
            self.equation_filter_list.takeItem(i)

        self.eq.set_records_for_parent(parent_id=self.eq.selected_parent_id)


def main():
    """Main of the eqatuation database"""
    db_params = config()
    conn = connect(**db_params)

    ui = Window()  # pylint: disable=invalid-name
    ui.show()
    conn.close()
    sys.exit(ui.app.exec_())


if __name__ == '__main__':
    main()
