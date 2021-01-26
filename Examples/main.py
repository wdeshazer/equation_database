# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
from PyQt5 import QtWidgets


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Create the application object
app = QtWidgets.QApplication(sys.argv)

# Create the form object
first_window = QtWidgets.QWidget()

# Set window size
first_window.resize(400, 300)

# Set the form title
first_window.setWindowTitle("The first pyqt program")

# Show form
first_window.show()

# Run the program
sys.exit(app.exec())