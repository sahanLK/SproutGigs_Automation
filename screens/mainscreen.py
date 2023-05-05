import logging
import random
import threading
import time
from PyQt5.QtWidgets import QAction, QVBoxLayout, QScrollArea, QGroupBox, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QDialog
from functions.driverfns import get_driver
from functions.fns import get_file_logger, get_syslogger
from jobshandler import JobsHandler
from livecontrols import LiveControls
from miner import BlogData, AdData
from tabshandler import TabsHandler
from qtdesigner.main_screen import Ui_MainScreen
from qtdesigner.dialogconfirm import Ui_confirm_dialog
from PyQt5.QtWidgets import QWidget
from qtdesigner.widgets.widget_submission import Ui_submit_widget
from qtdesigner.widgets.widget_job_update import Ui_job_update_widget
from regexes import RE_HTTP_LINK
from keyfunctions import KeyFunctions
from PyQt5.QtCore import pyqtSignal, QThreadPool
import pathlib
from ai import Ai, BooleanCheck
from widgetshandler import MainScreenWidgetsHandler
from database import get_session, SubmissionItemChoice
from database import Job

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/mainscreen.log", 'w+')
sys_logger = get_syslogger()

jh = JobsHandler()
Kf = KeyFunctions()
tabs_handler = TabsHandler()
session = get_session()


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


class JobUpdateWidget(QWidget):
    def __init__(self, sub_item, blog_data, ad_data, *args, **kwargs):
        super(JobUpdateWidget, self).__init__(*args, **kwargs)
        self.widget = Ui_job_update_widget()
        self.widget.setupUi(self)

        # set the submission item text
        self.widget.item_text.setText(sub_item.text)

        # Data required for submission
        self.job: Job = sub_item.job
        self.blog_data: BlogData = blog_data
        self.ad_data: AdData = ad_data

        # Change sub_item text font size
        f = self.widget.item_text.font()
        f.setPointSize(12)  # sets the size to 27
        self.widget.item_text.setFont(f)

        self.widget.but_af.clicked.connect(self.ad_first)
        self.widget.but_ls.clicked.connect(self.last_sentence)
        self.widget.but_al.clicked.connect(self.ad_link)
        self.widget.but_lp.clicked.connect(self.last_paragraph)
        self.widget.but_pt.clicked.connect(self.post_title)
        self.widget.but_aa.clicked.connect(self.ad_about)
        self.widget.but_ac.clicked.connect(self.ad_contact)
        self.widget.but_bl.clicked.connect(self.post_link)
        self.widget.but_lw.clicked.connect(self.last_word)

        # The 5 choice fields
        self.fields = [
            self.widget.choice_1,
            self.widget.choice_2,
            self.widget.choice_3,
            self.widget.choice_4,
            self.widget.choice_5,
        ]

        # 5 clear buttons
        self.widget.clear_choice_1.clicked.connect(lambda: self.widget.choice_1.clear())
        self.widget.clear_choice_2.clicked.connect(lambda: self.widget.choice_2.clear())
        self.widget.clear_choice_3.clicked.connect(lambda: self.widget.choice_3.clear())
        self.widget.clear_choice_4.clicked.connect(lambda: self.widget.choice_4.clear())
        self.widget.clear_choice_5.clicked.connect(lambda: self.widget.choice_5.clear())

    def get_first_empty(self):
        """
        Gets the first empty choice field from 5 choice fields.
        :return:
        """
        for f in self.fields:
            if not f.text():
                return f

    def already_filled(self, item):
        """
        Check if the given item is already filled into another choice field or not.
        """
        for f in self.fields:
            if f.text() == item:
                return True

    def ad_first(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.first_url):
                field.setText(self.ad_data.first_url)

    def last_sentence(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_sentences:
                if not self.already_filled(item):
                    field.setText(item)
                    break

    def ad_link(self):
        field = self.get_first_empty()
        if field:
            for item in self.ad_data.links:
                if not self.already_filled(item):
                    field.setText(item)
                    break

    def last_paragraph(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_paragraphs:
                if not self.already_filled(item):
                    field.setText(item)
                    break

    def post_title(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.titles:
                if not self.already_filled(item):
                    field.setText(item)
                    break

    def ad_about(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.about_url):
                field.setText(self.ad_data.about_url)

    def ad_contact(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.contact_url):
                field.setText(self.ad_data.contact_url)

    def post_link(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.posts:
                if not self.already_filled(item):
                    field.setText(item)
                    break

    def last_word(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_words:
                if not self.already_filled(item):
                    field.setText(item)
                    break


class MainScreen(QMainWindow, Ui_MainScreen):
    """
    Main Screen of the application
    """

    """
    Signal: Update the widget areas.
    """
    sig_update_widgets = pyqtSignal()

    """
    Signal: Job details update dialog open
    """
    sig_job_update = pyqtSignal()

    def __init__(self):
        super(MainScreen, self).__init__()
        self.blog_data = None
        self.ad_data = None
        self.threadpool = QThreadPool()

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
        run_action.setCheckable(True)

        autopilot_action = QAction(QIcon('./icons/bot.png'), '', self)
        autopilot_action.triggered.connect(self.activate_auto_pilot)
        autopilot_action.setCheckable(True)

        # Adding actions into toolbar
        self.toolBar.addAction(autopilot_action)
        self.toolBar.addAction(run_action)

        # Defining button actions
        self.but_miner_submit.clicked.connect(self._thread_miner_submit)
        self.but_skip.clicked.connect(self.job_skip)
        self.but_hide.clicked.connect(self.job_hide)

        # Slots for custom signals
        self.sig_update_widgets.connect(self.scroll_submit_widgets_update)
        self.sig_job_update.connect(self.open_job_update_window)

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

    def _thread_miner_submit(self):
        t = threading.Thread(target=self.miner_submit, daemon=True)
        t.start()

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

        job = JobsHandler.current_job_obj
        if not job:
            logger.critical("No active job running")
            return

        sub_items = [s.text for s in job.submission_items]
        self.blog_data = BlogData(
            url,
            mine_titles=BooleanCheck.titles_req(sub_items),
            mine_post_content=BooleanCheck.post_data_req(sub_items))

        self.ad_data = AdData(url, driver=get_driver())

        # Open the job details update window
        # This window details should be properly filled.
        self.sig_job_update.emit()

    def open_job_update_window(self):
        self.but_miner_submit.setEnabled(True)

        self.d = QDialog(parent=self)
        widget_layout = QVBoxLayout()
        widget_layout.setSpacing(0)

        job: Job = JobsHandler.current_job_obj

        # All the update widgets
        widgets = []

        for sub_item in job.submission_items:
            item = JobUpdateWidget(
                sub_item=sub_item,
                blog_data=self.blog_data,
                ad_data=self.ad_data,
            )
            widget_layout.addWidget(item)
            widgets.append(item)

        groupbox = QGroupBox()
        groupbox.setLayout(widget_layout)

        scroll = QScrollArea()
        scroll.setWidget(groupbox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(800)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)

        save_btn = QPushButton("Update and Submit")
        save_btn.setFont(QFont('Times', 10))
        save_btn.setFixedHeight(50)
        save_btn.clicked.connect(
            lambda: self.save_and_submit(widgets))
        main_layout.addWidget(save_btn)
        self.d.setLayout(main_layout)
        self.d.exec()

    def save_and_submit(self, widgets):
        def get_choices(sub_text):
            """
            Returns the choices according to the given
            <SubmissionItem> text.
            """
            for w in widgets:
                w: JobUpdateWidget = w
                if w.widget.item_text.text() == sub_text:
                    # Found the related submission item
                    rel_choices = []
                    for i in w.fields:
                        rel_choices.append(i.text())
                    return rel_choices

        job = JobsHandler.current_job_obj
        for sub_item in job.submission_items:
            # get the choices for this submission item
            choices = get_choices(sub_item.text)

            for ch in choices:
                obj = SubmissionItemChoice(text=ch)

                # Add to the choices of current <SubmissionItem>
                sub_item.choices.append(obj)

        self.submit()
        self.d.close()

    @staticmethod
    def submit():
        """
        Submit the proofs into the actual webpage
        """
        driver = get_driver()
        job = JobsHandler.current_job_obj

        for sub_item in job.submission_items:
            print(sub_item.text, "-> ", sub_item.field_id)
            # skip file submissions
            if str(sub_item.field_id).lower().startswith('file'):
                continue

            # Fill the box
            choice = random.choice(list(sub_item.choices))
            tabs_handler.go_to_doing_job_tab()
            driver.execute_script(f"$('#{sub_item.field_id}').val('{choice.text}');")

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

    @staticmethod
    def activate_auto_pilot():
        """
        Fully safe 100% automated action that select and submit tasks automatically
        using the previously submitted tasks
        """
        driver = get_driver()

        # get all the choices available jobs
        jobs = set()
        for job in session.query(Job).all():
            choices_ok = True
            for sub in job.submission_fields:
                # Even if one submission field does not have choices, do not select
                if not len(sub.choices) > 0:
                    choices_ok = False
                    break
            if choices_ok:
                jobs.add(job)

        # Complete selected jobs one by one
        for job in jobs:
            url = jh.get_job_url(job.job_id)
            driver.open_url(url, target='_blank', force_chk_config=False)
            if not jh.go_to_doing_job_tab():
                logger.warning(
                    "Job has expired or another error occurred when switching to tab")
                continue

            for sub_item in job.submission_items:
                # real textarea id of the submission page
                textarea_id = sub_item.field_id
                val = random.choice(sub_item.choices).text
                # Fill the proofs
                driver.execute_script(f"$('{textarea_id}').val('{val}');")

            # # Start the submit button click process
            # btn_text = driver.execute_script("return $('#submit-proof-btn').text();")
            # btn_text = str(btn_text).lower().strip()
            #
            # if not btn_text == 'submit proof':
            #     # Probably I need to wait some time before submission
            #     _time = btn_text.split(' ')[1]
            #     try:
            #         minutes, seconds = int(_time.split(':')[0]), int(_time.split(':')[1])
            #         total_wait = (minutes * 60) + seconds + 2
            #         print(f"Waiting {total_wait} seconds for submission")
            #         time.sleep(total_wait)
            #     except ValueError:
            #         logger.error(f"Error when splitting time counter value with: {_time}")
            #         break
            #
            # # All good submit the job
            # driver.execute_script("$('#submit-proof-btn').click();")
            #
            # # wait more than a monite before next job
            print("Waiting more than a minute")
            time.sleep(60 + random.randint(2, 10))

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


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainScreen()
    window.show()
    app.exec_()
