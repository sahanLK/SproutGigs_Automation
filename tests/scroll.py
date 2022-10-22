import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QListWidgetItem
from scrollbar import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.add.clicked.connect(self.add_)
        self.remove.clicked.connect(self.remove_)
        self.clear.clicked.connect(self.clear_)

    def add_(self):
        print("Adding")
        self.listWidget.addItem(QListWidgetItem("Sahan"))

    def remove_(self):
        print("Removing")

    def clear_(self):
        print("Clearing")
        self.listWidget.clear()




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()