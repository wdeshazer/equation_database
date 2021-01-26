"""
https://www.geeksforgeeks.org/pyqt5-changing-color-of-pressed-push-button/
"""
# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title 
        self.setWindowTitle("Python ")

        # setting geometry 
        self.setGeometry(100, 100, 600, 400)

        # calling method 
        self.UiComponents()

        # showing all the widgets 
        self.show()

        # method for widgets

    def UiComponents(self):
        # creating push button widget
        button = QPushButton("Button ", self)

        # setting geometry 
        button.setGeometry(200, 100, 100, 40)

        # adding background color to button 
        # and background color to pressed button 
        button.setStyleSheet("QPushButton"
                             "{"
                             "background-color : lightblue;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : red;"
                             "}"
                             )

    # create pyqt5 app


App = QApplication(sys.argv)

# create the instance of our Window 
window = Window()

# start the app 
sys.exit(App.exec()) 
