import logging
import sys
import threading
from typing import Union
from PyQt5.QtWidgets import QAction, QApplication, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDialog
from data_splitter import BlogsDataSplitter, AdDataSplitter
from functions.driverfns import get_driver
from functions.fns import list_to_str, get_file_logger, get_syslogger
from jobshandler import JobsHandler
from livecontrols import LiveControls
from miner import BlogData, AdData
from picoconstants import db_handler
from submitter import ProofsSubmitter
from tabshandler import TabsHandler
from qtdesigner.main_screen import Ui_MainScreen
from webcrapy.urlmaster import UrlMaster
from qtdesigner.dialogconfirm import Ui_confirm_dialog
from PyQt5.QtWidgets import QWidget
from qtdesigner.widgets.widget_submission import Ui_submit_widget
from regexes import RE_HTTP_LINK
from keyfunctions import KeyFunctions
from PyQt5.QtCore import pyqtSignal
import pathlib
from ai import BooleanCheck
from widgetshandler import MainScreenWidgetsHandler

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/mainscreen.log", 'w+')
sys_logger = get_syslogger()

jh = JobsHandler()
Kf = KeyFunctions()
tabs_handler = TabsHandler()
submitter = ProofsSubmitter()


"""
Both <BlogData> and <BlogDataSplitter> has same attribute names.
Both <AdData> and <AdDataSplitter> has same attribute names.
So they are commonly accesses here in the code. In case of class attribute name change in
one of the class will produce errors.
"""


class SubmissionWidget(QWidget):
    def __init__(self, identity, lbl: str):
        super(SubmissionWidget, self).__init__()
        self.id = identity
        self.label = lbl

        self.widget = Ui_submit_widget()
        self.widget.setupUi(self)
        self.widget.lbl.setText(self.label)

        self.widget.but_bl.clicked.connect(lambda: Kf.submit_blog_link(self.id))
        self.widget.but_pt.clicked.connect(lambda: Kf.submit_post_title(self.id))
        self.widget.but_lw.clicked.connect(lambda: Kf.submit_last_word(self.id))
        self.widget.but_ls.clicked.connect(lambda: Kf.submit_last_sentence(self.id))
        self.widget.but_lp.clicked.connect(lambda: Kf.submit_last_paragraph(self.id))
        self.widget.but_af.clicked.connect(lambda: Kf.submit_ad_first(self.id))
        self.widget.but_aa.clicked.connect(lambda: Kf.submit_ad_about(self.id))
        self.widget.but_ac.clicked.connect(lambda: Kf.submit_ad_contact(self.id))
        self.widget.but_al.clicked.connect(lambda: Kf.submit_ad_inside(self.id))
        self.widget.but_clear.clicked.connect(lambda: Kf.clear_textarea(self.id))


class MainScreen(QMainWindow, Ui_MainScreen):
    """
    Main Screen of the application
    """

    """
    Signal: Update the widget areas.
    """
    sig_update_widgets = pyqtSignal()

    def __init__(self):
        super(MainScreen, self).__init__()
        self.running = False
        self.driver = None
        self.setupUi(self)

        # Triggering menu items events
        self.actionDatabase_Manager.triggered.connect(self.open_db_manager)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.exit)
        self.actionDeveloper.triggered.connect(self.show_developer_info)

        # Toolbar Actions
        run_action = QAction(QIcon('./icons/run-fast.png'), '', self)
        run_action.triggered.connect(self.start_or_stop)

        autopilot_action = QAction(QIcon('./icons/bot.png'), '', self)
        autopilot_action.triggered.connect(self.activate_auto_pilot)

        # Adding actions into toolbar
        self.toolBar.addAction(autopilot_action)
        self.toolBar.addAction(run_action)

        # Defining button actions
        self.but_db_submit.clicked.connect(self._thread_db_submit)
        self.but_miner_submit.clicked.connect(self._thread_miner_submit)
        self.but_skip.clicked.connect(self.job_skip)
        self.but_hide.clicked.connect(self.job_hide)

        # Slots for custom signals
        self.sig_update_widgets.connect(self.scroll_submit_widgets_update)

        # ScrollArea
        self.scroll_submit_widgets.setWidgetResizable(True)

    def start_or_stop(self, *args):
        """
        Perform a toggle action based on progress is running or not.
        :param args:
        :return:
        """
        if self.running:
            self.running = False
            self.stop_running()
        else:
            self.running = True
            driver = get_driver()
            if driver:
                jh.update_jobs()
                LiveControls.jobs_running = True
                t = threading.Thread(target=self.start_running)
                t.start()

    def start_running(self, *args):
        sys_logger.info("Started running")
        logger.info('started running')
        self.driver = get_driver()
        jh.select_a_job()

    def scroll_submit_widgets_update(self):
        """
        Update the scroll area of submission widgets.
        :return:
        """
        vbox = QVBoxLayout()
        widget = QWidget()
        for identity, lbl in LiveControls.submission_widgets.items():
            vbox.addWidget(SubmissionWidget(identity=identity, lbl=lbl))
        widget.setLayout(vbox)
        self.scroll_submit_widgets.setWidget(widget)

    @classmethod
    def emit_submit_widget_update_signal(cls, instance):
        """
        Emit the signal to update the new submission widgets.
        :param instance:
        :return:
        """
        instance.sig_update_widgets.emit()

    def get_blog_url(self):
        """
        Returns the blog site url from the input field.
        :return:
        """
        url = self.input_url.text()
        matches = [match for match in RE_HTTP_LINK.finditer(url)]
        return url if matches else None

    def _thread_db_submit(self):
        t = threading.Thread(target=self.db_submit, daemon=True)
        t.start()

    def _thread_miner_submit(self):
        t = threading.Thread(target=self.miner_submit, daemon=True)
        t.start()

    def db_submit(self):
        """
        Actions for database submission button.
        :return:
        """
        url = self.get_blog_url()
        if not url:
            sys_logger.debug("Blog url is empty or invalid. returning")
            return
        sys_logger.debug(f"DB_SUBMIT: initiated with {url}")
        self.but_db_submit.setText("Submitting..")
        self.but_db_submit.setEnabled(False)

        blog_domain = UrlMaster(url).domain
        record = db_handler.select_filtered('blogs', [], f'blog_domain="{blog_domain}"')

        if record:  # Blog data from database
            logger.info("Blog data from database")
            sys_logger.debug("DB_SUBMIT: Blog data from database")
            blog_data = BlogsDataSplitter(blog_domain)
        else:   # Blog data from Miner
            logger.info("DB_SUBMIT_BUT ->  Blog data from miner")
            sys_logger.debug("DB_SUBMIT: Blog data from miner")
            blog_data = BlogData(url,
                                 mine_titles=BooleanCheck.titles_req(),
                                 mine_post_content=BooleanCheck.post_data_req())
            store_new_mined_blog_data(blog_domain, blog_data, force_rm_exist=False)

        # Gathering Ad data
        ad_data = AdData(url, driver=get_driver())
        ad_domain = UrlMaster(ad_data.first_url).domain

        if not ad_data.links and not (ad_data.about_url or ad_data.contact_url):
            # Ad data from database
            logger.info("DB_SUBMIT ->  Ad data from Database")
            sys_logger.debug("DB_SUBMIT: Ad data from database")

            ad_data = AdDataSplitter()
        else:
            logger.info("Ad data from miner")
            sys_logger.debug("DB_SUBMIT: Ad data from miner")
            # Ad data from miner
            # Miner found better ad data. Store it
            store_new_mined_ad_data(ad_domain, ad_data)

        blog_data = get_blog_data_as_dict(blog_data)
        ad_data = get_ad_data_as_dict(ad_data)
        if update_current_blog_and_ad_data(blog_data, ad_data):
            sys_logger.info("DB_SUBMIT: Submitting proofs")
            submit_proofs()
            sys_logger.info("DB_SUBMIT: Done")
        else:
            sys_logger.error("DB_SUBMIT: Failed")

        # Enable the button again
        MainScreenWidgetsHandler().but_db_submit_set_default()

    def miner_submit(self):
        """
        Actions for miner submit button.
        :return:
        """
        url = self.get_blog_url()
        if not url:
            sys_logger.debug("Blog url is empty or invalid. returning")
            return
        sys_logger.debug(f"MINER_SUBMIT: initiated with {url}")
        self.but_miner_submit.setText("Submitting..")
        self.but_miner_submit.setEnabled(False)

        blog_domain = UrlMaster(url).domain
        blog_data = BlogData(url,
                             mine_titles=BooleanCheck.titles_req(),
                             mine_post_content=BooleanCheck.post_data_req())   # New blog data from miner
        logger.debug("Blog data from miner")
        sys_logger.debug("MINER_SUBMIT: Blog data from miner")
        exists = BlogsDataSplitter(blog_domain)  # just for checking whether new data is better than older

        if exists.entry:
            # Compare new blog data and old blog data. Then update the record if,
            # new data is better than older data.
            if len(blog_data.posts) >= len(exists.posts) and \
                    len(blog_data.titles) >= len(exists.titles) and \
                    len(blog_data.last_words) >= len(exists.last_words) and \
                    len(blog_data.last_sentences) >= len(exists.last_sentences) and \
                    len(blog_data.last_paragraphs) >= len(exists.last_paragraphs):

                # Update the existing blog data record with new latest info.
                store_new_mined_blog_data(blog_domain, blog_data, force_rm_exist=True)
                logger.info("MINER_SUBMIT ->  Existing Blog data updated.")
                sys_logger.info("MINER_SUBMIT ->  Existing Blog data updated.")
            else:
                logger.info("MINER_SUBMIT ->  Older blog data is better than new blog data.")
                sys_logger.info("MINER_SUBMIT ->  Older blog data is better than new blog data.")

        # Ad data from miner
        ad_data = AdData(url, driver=get_driver())
        ad_domain = UrlMaster(ad_data.first_url).domain

        if not ad_data.links and not (ad_data.about_url or ad_data.contact_url):
            # Using ad data from database.
            logger.info("MINER_SUBMIT ->  Using ad data from database")
            sys_logger.info("MINER_SUBMIT ->  Ad data from database")
            ad_data = AdDataSplitter()  # Will get ad data from database
        else:
            logger.info("MINER_SUBMIT ->  Ad data from miner")
            sys_logger.info("MINER_SUBMIT ->  Ad data from miner")
            # Update ad_sites table with this site, if a record does not exist for this site.
            store_new_mined_ad_data(ad_domain, ad_data)

        blog_data = get_blog_data_as_dict(blog_data)
        ad_data = get_ad_data_as_dict(ad_data)

        if update_current_blog_and_ad_data(blog_data, ad_data):
            sys_logger.info("MINER_SUBMIT: Submitting proofs")
            submit_proofs()
            sys_logger.info("MINER_SUBMIT: Done")
        else:
            sys_logger.error("MINER_SUBMIT: Failed")

        # Enable the button again
        MainScreenWidgetsHandler().but_miner_submit_set_default()

    def show_developer_info(self):
        d = QDialog()
        d.exec()

    def open_db_manager(self):
        d = QDialog()
        d.exec()

    def open_settings(self):
        d = QDialog()
        d.exec()

    def activate_auto_pilot(self):
        """
        A Special mode that submit tasks automatically, if the submitter can submit all the proofs.
        Should be avoided using this method in case of poor auto submission capabilities.
        """
        pass

    def stop_running(self, *args):
        self.running = False

    def job_skip(self):
        """
        Applies all the job skipping protocols.
        :return:
        """
        def _thread():
            if self.running:
                jh.skip_job()
                self.start_running()
        t = threading.Thread(target=_thread)
        t.start()

    def job_hide(self):
        """
        Applies all the job hiding protocols.
        :return:
        """
        def _thread():
            if self.running:
                self.input_url.clear()
                jh.hide_job()
                self.start_running()
        t = threading.Thread(target=_thread)
        t.start()

    def exit(self):
        def switch_to_login():
            def kill_driver():
                LiveControls.kill_driver()

            t = threading.Thread(target=kill_driver)
            t.start()

            LiveControls.screens['login_screen'].show()
            self.hide()
            LiveControls.screens['login_screen'].but_login.setEnabled(False)
            close_dialog()

        def close_dialog():
            d.close()

        d = QDialog(parent=self)
        ui = Ui_confirm_dialog()
        ui.setupUi(d)
        ui.confirm_msg.setText("Sure you want to exit ?")
        ui.yes_button.clicked.connect(switch_to_login)
        ui.no_button.clicked.connect(close_dialog)
        d.exec()


def submit_proofs():
    if tabs_handler.go_to_doing_job_tab():
        driver = get_driver()
        submitter.submit_proofs(driver)


def get_ad_data_as_dict(ad_data: Union[AdDataSplitter, AdData]) -> dict:
    ad_data = {
        "first_url": ad_data.first_url,
        "about_url": ad_data.about_url,
        "contact_url": ad_data.contact_url,
        "links": list_to_str(ad_data.links),
    }
    return ad_data


def get_blog_data_as_dict(blog_data: Union[BlogsDataSplitter, BlogData]) -> dict:
    blog_data = {
        "links": list_to_str(blog_data.posts),
        "titles": list_to_str(blog_data.titles),
        "paragraphs": list_to_str(blog_data.last_paragraphs),
        "sentences": list_to_str(blog_data.last_sentences),
        "words": list_to_str(blog_data.last_words),
    }
    return blog_data


def store_new_mined_blog_data(domain: str, blog_data: BlogData, force_rm_exist: bool) -> None:
    if not domain:
        return

    if force_rm_exist:
        db_handler.delete_records('blogs', f'blog_domain="{domain}"')

    try:
        db_handler.add_record('blogs', [
            domain,
            list_to_str(blog_data.posts),
            list_to_str(blog_data.titles),
            list_to_str(blog_data.last_words),
            list_to_str(blog_data.last_sentences),
            list_to_str(blog_data.last_paragraphs),
        ])
        sys_logger.error(f"Table: blogs updated successfully")
    except Exception as e:
        sys_logger.error(f"Table: blogs update failed: {e}")


def store_new_mined_ad_data(domain: str, ad_data: AdData) -> None:
    # Store ad site data only if perfect.
    about = ad_data.about_url
    contact = ad_data.contact_url
    links = list_to_str(ad_data.links)
    first = ad_data.first_url
    if not domain or not(about or contact) or len(links) < 3:
        sys_logger.debug("Ad Data not enough for storing into database")
        return  # Not perfect

    try:
        db_handler.add_record('ad_sites', [
            domain,
            first if first else '',
            about if about else '',
            contact if contact else '',
            links,
        ])
    except Exception as e:
        logger.info(f"Ad data storing failed: {e}")
        sys_logger.warn(f"Ad data storing failed: {e}")


def update_current_blog_and_ad_data(blog_data: dict, ad_data: dict):
    """
    Update the current_blog_and_ad_data table.
    :param blog_data: dict:
    :param ad_data: dict:
    :return:
    """
    # Update the current blog and ad data table
    db_handler.clear_tb('current_blog_and_ad_data')

    try:
        db_handler.add_record('current_blog_and_ad_data', [
            blog_data['links'],
            blog_data['titles'],
            blog_data['paragraphs'],
            blog_data['sentences'],
            blog_data['words'],
            ad_data['first_url'],
            ad_data['contact_url'],
            ad_data['about_url'],
            ad_data['links'],
        ])
        sys_logger.debug(f"Table: current_blog_and_ad_data updated successfully")
        return True
    except Exception as e:
        sys_logger.critical(f"Table: current_blog_and_ad_data update failed: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = MainScreen()
    screen.show()
    app.exec()
