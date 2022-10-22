import os.path
import sys
from PyQt6.QtCore import Qt
from pyqt6_plugins.examplebutton import QtWidgets

from qtdesigner.loginscreen import Ui_LoginScreen
from qtdesigner.mainscreen import Ui_MainScreen
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QDialog
from PyQt6 import QtGui

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    print("failed")
    pass


class AnotherWindow(QMainWindow, Ui_MainScreen):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super(AnotherWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.skip_job)

    def skip_job(self):
        print("Skipping")


class MainWindow(QMainWindow, Ui_LoginScreen):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.check_button.clicked.connect(self.open_another)

    def open_another(self):
        print("Ok")
        self.ui = AnotherWindow()
        self.ui.show()
        # self.hide()



app = QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon('favicon.ico'))
window = MainWindow()
window.show()
app.exec()
