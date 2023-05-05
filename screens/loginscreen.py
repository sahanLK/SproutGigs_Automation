import logging
import threading
from datetime import datetime
import requests
from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QListWidget, QVBoxLayout, QListWidgetItem, QDialog, QLineEdit
from functions.driverfns import filter_mt
from functions.fns import get_file_logger, get_syslogger
from livecontrols import LiveControls
from picosetup import SetupPico
from qtdesigner.login_screen import Ui_LoginScreen
from qtdesigner.dialogearningstat import Ui_earning_stats
from qtdesigner.dialogsystemcheck import Ui_system_stat
from qtdesigner.dialogconfirm import Ui_confirm_dialog
from qtdesigner.dialog_add_account import Ui_add_account
from tabshandler import TabsHandler
import pathlib
from database import get_session, User, LoginInfo, Earnings

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/loginscreen.log", 'w+')
sys_logger = get_syslogger()

# database session
session = get_session()


def get_ip_from_aws():
    """
    Reach the amazon web server to get the current ip address
    :return:
    """
    try:
        ip = requests.get('https://ident.me/', timeout=5).text.strip()
        return ip
    except Exception as e:
        print(f"[ ERROR ]{' ' * 5}IP not detected.")
        logger.warn(f"Couldn't reach amazon: {e}")


class LoginScreen(QMainWindow, Ui_LoginScreen):
    """
    Login Screen of the application.
    """

    """
    Currently exists accounts in the database.
    """
    active_accounts = []

    """
    Visible state of the password field
    """
    password_visible = False

    """
    Dialog Box interfaces to be used later for building the ui
    """
    system_stat_ui = Ui_system_stat()
    add_account_ui = Ui_add_account()

    """
    No of devices Allowed in pc.
    """
    no_of_devices = 30

    def __init__(self):
        super(LoginScreen, self).__init__()
        self.threadpool = QThreadPool()

        self.add_account_dialog = None
        self.sign_in_confirm_dialog = None
        self.acc_select_dlg = None

        self.main_screen = None
        self.setupUi(self)

        self.system_check_messages = {
            "database": None,
            "ip": None,
            "ip_conflict": None,
        }

        # Action Bar
        self.action_add_account.triggered.connect(self.add_account)
        self.action_remove_account.triggered.connect(self.remove_account)

        # Interface modifications
        self.toolBar.setMovable(False)
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.create_dialogs()

        # Toolbar actions
        account_select_action = QAction(QIcon('icons/user.png'), '', self)
        account_select_action.triggered.connect(self.select_account)

        enter_main_action = QAction(QIcon('icons/enter.png'), '', self)
        enter_main_action.triggered.connect(self.open_sign_in_confirmation)

        report_action = QAction(QIcon('./icons/report.png'), '', self)
        report_action.triggered.connect(self.show_report)

        # Adding actions into toolbar
        self.toolBar.addAction(account_select_action)
        self.toolBar.addAction(enter_main_action)
        self.toolBar.addAction(report_action)

        # Button action defining
        self.but_check.clicked.connect(self.system_check)
        self.but_login.clicked.connect(self.sign_in)
        self.check_show_pwd.clicked.connect(self.toggle_password)

    def create_dialogs(self):
        # Sign in confirmation dialog.
        self.sign_in_confirm_dialog = QDialog(parent=self)
        sign_in_confirm_ui = Ui_confirm_dialog()
        sign_in_confirm_ui.setupUi(self.sign_in_confirm_dialog)
        sign_in_confirm_ui.confirm_msg.setText("Did you sign in successfully ?")
        sign_in_confirm_ui.yes_button.clicked.connect(self.open_main_screen)
        sign_in_confirm_ui.no_button.clicked.connect(self.close_sign_in_dialog)
        
    def close_sign_in_dialog(self):
        self.sign_in_confirm_dialog.close()

    def close_add_acc_dialog(self):
        self.add_account_dialog.close()

    def add_account(self):
        # Add account dialog
        self.add_account_dialog = QDialog(parent=self)
        self.add_account_ui.setupUi(self.add_account_dialog)
        self.add_account_ui.cancel_but.clicked.connect(self.close_add_acc_dialog)
        self.add_account_ui.add_acc_but.clicked.connect(self.add_new_account)

        # Hardcode the devices required. Devices should be added manually like below.
        # Also don't show the accounts that are already being assigned.
        # using = [device[0] for device in db_handler.select_filtered('accounts', ['device'])]
        using = [user.device for user in session.query(User).all()]
        allowed = [no+1 for no in range(self.no_of_devices) if no+1 not in using]

        # If all the devices in use, disable the combo box.
        if not allowed:
            self.add_account_ui.combo_devices.setEnabled(False)

        for no in allowed:
            self.add_account_ui.combo_devices.addItem(f"device {no}")
        self.add_account_dialog.exec()

    def add_new_account(self):
        """
        Add a new account into the database
        :return:
        """
        email = self.add_account_ui.email_field.text()
        pwd = self.add_account_ui.pwd_field.text()
        device = self.add_account_ui.combo_devices.currentText()
        if not email or not pwd or not device:
            return

        device_no = int(device.split()[1])
        # If the selected device has already associated with another account, do not add.
        if session.query(User).filter(User.device == device_no).first():
            return

        try:
            session.add(User(email=email, pwd=pwd, device=device_no))
            session.commit()
            self.close_add_acc_dialog()
        except Exception as e:
            print(e)
            logger.error(f"Error when adding account: {e}")
        finally:
            self.add_account_ui.email_field.clear()
            self.add_account_ui.pwd_field.clear()

    def remove_account(self):
        d = QDialog()
        d.exec()

    def show_report(self):
        d = QDialog(parent=self)
        ui = Ui_earning_stats()
        ui.setupUi(d)
        today = str(datetime.now()).split()[0]
        record = session.query(Earnings).filter(Earnings.date == today).first()
        if record:
            tasks, usd = record.tasks, record.usd
            ui.daily_tasks.setText(str(tasks))
            ui.daily_earned.setText(f"$ {usd}")
        d.exec_()

    def select_account(self):
        self.acc_select_dlg = QDialog(parent=self)
        self.acc_select_dlg.setMinimumSize(250, 300)
        self.acc_select_dlg.setMaximumSize(400, 400)
        self.acc_select_dlg.setWindowTitle("Select an account")

        self.active_accounts = {email: pwd for (email, pwd) in session.query(User.email, User.pwd).all()}

        layout = QVBoxLayout()
        accounts = QListWidget()
        for email in self.active_accounts.keys():
            account = QListWidgetItem(email)
            account.setFont(QFont("Calibri", 12, 400, False))
            accounts.addItem(account)
        accounts.itemClicked.connect(self.account_selected)
        layout.addWidget(accounts)

        self.acc_select_dlg.setLayout(layout)
        self.acc_select_dlg.exec_()

    def account_selected(self, account):
        logger.info(f"Account selected: {account.text()}")
        email = account.text()
        self.input_email.setText(email)
        self.input_pwd.setText(self.active_accounts[email])
        self.acc_select_dlg.close()
        self.but_login.setEnabled(False)

    def toggle_password(self):
        if self.password_visible:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_visible = False
        else:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_visible = True

    def system_check(self):
        # If login credentials are not available, nothing to check.
        email = self.input_email.text()
        pwd = self.input_pwd.text()
        if not email or not pwd:
            logger.info(f"Email or password not given. returning")
            return

        d = QDialog(parent=self)
        self.system_stat_ui.setupUi(d)

        def _thread():
            # Database already checked. Just add a message
            self.system_stat_ui.database_msg.setText("Online")

            # Check the ip status.
            if self.__ip_ok(email):
                print(f"[ OK ]{' ' * 5}No ip conflict\n\nAll checked. Good to go")
                self.system_stat_ui.ip_conflict_msg.setText("No IP conflict")
                self.but_login.setEnabled(True)

        t = threading.Thread(target=_thread)
        t.start()
        d.exec_()

    def __ip_ok(self, curr_account: str):
        """
        Check if the current ip address has already used to sign in
        for another account.
        :param curr_account: The account user trying to sign in, now.
        :return:
        """
        self.current_ip = get_ip_from_aws()
        if not self.current_ip:
            self.system_stat_ui.ipv4_msg.setText("Not detected")
            self.system_stat_ui.ip_conflict_msg.setText("Not detected")
            return False
        self.system_stat_ui.ipv4_msg.setText(str(self.current_ip))
        logger.debug(f"[ OK ]{' ' * 5}Detected IPv4:  {self.current_ip}")

        # Check database for ip conflicts
        entry = session.query(LoginInfo).filter(LoginInfo.ip == self.current_ip).first()
        if entry:
            prev_account = entry.account
            if entry.account.lower() != curr_account.lower():
                # Current ip has used to log in for another account.
                conflict_msg = f"IP conflict with  {prev_account}{' ' * 4}\nDate: {entry.date}"
                logger.debug(conflict_msg)
                self.system_stat_ui.ip_conflict_msg.setText(conflict_msg)
                return False
            else:
                self.system_stat_ui.ip_conflict_msg.setText("No IP conflict")

            # Even if the current ip has already used, it has used to log in to the same account. That's ok.
            return True
        else:
            # New ip address. Add this ip into the database at the actual moment of sign in.
            # Because user maybe checked the system and leave the app without login in.
            # If now update the database with this ip address we may have an ip record that
            # actually did not use to log into the site.
            return True

    def sign_in(self):
        def _thread():
            self.but_login.setEnabled(False)
            # Check the ip address again because some DHCP connections can cause ip changes.
            ip = get_ip_from_aws()
            if ip != self.current_ip:
                logger.debug(f"[ INFO ]{' ' * 5}IP change detected\n[ ERROR ]"
                             f"{' ' * 5}System recheck required.")
                return

            # Make a new record with new ip address, if it does not exist.
            if not session.query(LoginInfo).filter(
                    LoginInfo.ip == self.current_ip).first():
                try:
                    timestamp = str(datetime.now()).split('.')[0]
                    session.add(LoginInfo(
                        account=self.input_email.text(),
                        ip=self.current_ip,
                        date=timestamp))
                    session.commit()
                except Exception as e:
                    logger.critical(f"Error when updating login info: {e}\n Stopped sign in process")
                    return

            pico_setup = SetupPico()
            pico_setup.init_setup(
                email=self.input_email.text(),
                password=self.input_pwd.text(),
                browser='edge')

            if TabsHandler.go_to_jobs_tab():
                filter_mt()

        t = threading.Thread(target=_thread, daemon=True)
        t.start()
        # Login and filtering for marketing test should be successful at here.

    def open_sign_in_confirmation(self):
        self.sign_in_confirm_dialog.exec()

    def open_main_screen(self):
        self.sign_in_confirm_dialog.close()
        LiveControls.screens['main_screen'].show()
        self.hide()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QMainWindow, QApplication
    import sys

    app = QApplication(sys.argv)
    screen = LoginScreen()
    screen.show()
    app.exec_()
