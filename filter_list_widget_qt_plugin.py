from PyQt5 import QtGui, QtDesigner
from CustomWidgets.filter_list_widget import EDFilterListWidget


class EDFilterListWidgetPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):

        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)

        self.initialized = False

    def initialize(self, core):

        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):

        return self.initialized

    def createWidget(self, parent):
        return EDFilterListWidget(parent)

    def name(self):
        return "EDFilterListWidget"

    def group(self):
        return "PyQt Examples"

    def icon(self):
        _logo_pixmap = QtGui.QPixmap('filter_list_widget.png')
        return QtGui.QIcon(_logo_pixmap)

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return (
               '<widget class="EDFilterListWidget" name=\"filterList\">\n'
               " <property name=\"toolTip\" >\n"
               "  <string>Filter List</string>\n"
               " </property>\n"
               " <property name=\"whatsThis\" >\n"
               "  <string>A filter list includes both a List "
               "and a filter</string>\n"
               " </property>\n"
               "</widget>\n"
               )

    def includeFile(self):
        return "CustomWidgets.filter_list_widget"
