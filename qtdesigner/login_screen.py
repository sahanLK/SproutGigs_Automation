# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_screen.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginScreen(object):
    def setupUi(self, LoginScreen):
        LoginScreen.setObjectName("LoginScreen")
        LoginScreen.resize(524, 641)
        LoginScreen.setMinimumSize(QtCore.QSize(524, 641))
        LoginScreen.setMaximumSize(QtCore.QSize(524, 641))
        self.centralwidget = QtWidgets.QWidget(LoginScreen)
        self.centralwidget.setMaximumSize(QtCore.QSize(524, 601))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setContentsMargins(-1, 40, -1, -1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMinimumSize(QtCore.QSize(0, 60))
        self.label.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setFamily("Rosewood Std Regular")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(35, 85, 35, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 30)
        self.verticalLayout.setSpacing(25)
        self.verticalLayout.setObjectName("verticalLayout")
        self.input_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_email.setMinimumSize(QtCore.QSize(400, 35))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.input_email.setFont(font)
        self.input_email.setObjectName("input_email")
        self.verticalLayout.addWidget(self.input_email)
        self.input_pwd = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pwd.setMinimumSize(QtCore.QSize(400, 35))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.input_pwd.setFont(font)
        self.input_pwd.setInputMethodHints(QtCore.Qt.ImhNone)
        self.input_pwd.setText("")
        self.input_pwd.setObjectName("input_pwd")
        self.verticalLayout.addWidget(self.input_pwd)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.check_show_pwd = QtWidgets.QCheckBox(self.centralwidget)
        self.check_show_pwd.setObjectName("check_show_pwd")
        self.verticalLayout_2.addWidget(self.check_show_pwd)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.layout_buts_2 = QtWidgets.QVBoxLayout()
        self.layout_buts_2.setContentsMargins(150, 55, 150, 70)
        self.layout_buts_2.setSpacing(15)
        self.layout_buts_2.setObjectName("layout_buts_2")
        self.but_check = QtWidgets.QPushButton(self.centralwidget)
        self.but_check.setMinimumSize(QtCore.QSize(150, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_check.setFont(font)
        self.but_check.setObjectName("but_check")
        self.layout_buts_2.addWidget(self.but_check)
        self.but_login = QtWidgets.QPushButton(self.centralwidget)
        self.but_login.setEnabled(False)
        self.but_login.setMinimumSize(QtCore.QSize(150, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_login.setFont(font)
        self.but_login.setObjectName("but_login")
        self.layout_buts_2.addWidget(self.but_login)
        self.verticalLayout_3.addLayout(self.layout_buts_2)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setEnabled(False)
        self.label_2.setMinimumSize(QtCore.QSize(0, 15))
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Fixedsys")
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        LoginScreen.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LoginScreen)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 524, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        LoginScreen.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(LoginScreen)
        self.toolBar.setMaximumSize(QtCore.QSize(16777215, 30))
        self.toolBar.setObjectName("toolBar")
        LoginScreen.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_add_account = QtWidgets.QAction(LoginScreen)
        self.action_add_account.setObjectName("action_add_account")
        self.action_remove_account = QtWidgets.QAction(LoginScreen)
        self.action_remove_account.setObjectName("action_remove_account")
        self.action_exit = QtWidgets.QAction(LoginScreen)
        self.action_exit.setObjectName("action_exit")
        self.menuFile.addAction(self.action_add_account)
        self.menuFile.addAction(self.action_remove_account)
        self.menuFile.addAction(self.action_exit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(LoginScreen)
        QtCore.QMetaObject.connectSlotsByName(LoginScreen)

    def retranslateUi(self, LoginScreen):
        _translate = QtCore.QCoreApplication.translate
        LoginScreen.setWindowTitle(_translate("LoginScreen", "MainWindow"))
        self.label.setText(_translate("LoginScreen", "SproutGigs"))
        self.input_email.setPlaceholderText(_translate("LoginScreen", " Email"))
        self.input_pwd.setPlaceholderText(_translate("LoginScreen", " Password"))
        self.check_show_pwd.setText(_translate("LoginScreen", "Show Password"))
        self.but_check.setText(_translate("LoginScreen", "System Check"))
        self.but_login.setText(_translate("LoginScreen", "Sign In"))
        self.label_2.setText(_translate("LoginScreen", "Developed by: Sahan Lakshitha"))
        self.menuFile.setTitle(_translate("LoginScreen", "File"))
        self.toolBar.setWindowTitle(_translate("LoginScreen", "toolBar"))
        self.action_add_account.setText(_translate("LoginScreen", "Add Account"))
        self.action_remove_account.setText(_translate("LoginScreen", "Remove Account"))
        self.action_exit.setText(_translate("LoginScreen", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LoginScreen = QtWidgets.QMainWindow()
    ui = Ui_LoginScreen()
    ui.setupUi(LoginScreen)
    LoginScreen.show()
    sys.exit(app.exec_())
