import logging
import random
import threading
import time
from PyQt5.QtWidgets import QAction, QVBoxLayout, QScrollArea, QGroupBox, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QDialog
from sqlalchemy import and_

from functions.driverfns import get_driver, modify_doing_job_page
from functions.fns import get_file_logger, get_syslogger
from jobshandler import JobsHandler, get_job_url, get_job_page_source, get_ji_section, get_ap_section
from livecontrols import LiveControls
from miner import BlogData, AdData
from tabshandler import TabsHandler
from qtdesigner.main_screen import Ui_MainScreen
from qtdesigner.dialogconfirm import Ui_confirm_dialog
from PyQt5.QtWidgets import QWidget
from qtdesigner.widgets.widget_job_update import Ui_job_update_widget
from regexes import RE_HTTP_LINK
from keyfunctions import KeyFunctions
from PyQt5.QtCore import pyqtSignal, QThreadPool
import pathlib
from ai import BooleanCheck
from database import get_session, SubmissionItemChoice, SubmissionItem
from database import Job

base_dir = pathlib.Path(__file__).parent.parent.absolute()
logger = get_file_logger(__file__, logging.DEBUG, f"{base_dir}/logs/mainscreen.log", 'w+')
sys_logger = get_syslogger()

jh = JobsHandler()
Kf = KeyFunctions()
tab_h = TabsHandler()
session = get_session()


class JobUpdateWidget(QWidget):
    """
    This widget is used for updating the job details into database
    with clean and 100% accurate details.

    BUT SUBMIT WIDGETS ARE USED TO SUBMIT THE PROOF DIRECTLY INTO WEBPAGE FIELDS.
    """

    """
    A set of all the submitted values into webpage.
    Will be accessed across all the instances.
    """
    cache = set()

    """
    All the <JobUpdateWidget> instances created for current active job.
    This set will be used to prevent filling same item twice into update
    window fields.
    """
    instances = set()

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

        # 5 clear buttons that clear update dialog fields
        self.widget.clear_choice_1.clicked.connect(self.widget.choice_1.clear)
        self.widget.clear_choice_2.clicked.connect(self.widget.choice_2.clear)
        self.widget.clear_choice_3.clicked.connect(self.widget.choice_3.clear)
        self.widget.clear_choice_4.clicked.connect(self.widget.choice_4.clear)
        self.widget.clear_choice_5.clicked.connect(self.widget.choice_5.clear)

        # Submit button actions (Direct submission to webpage)
        self.widget.sub_choice_1.clicked.connect(
            lambda: self.submit_choice(self.widget.choice_1.toPlainText()))
        self.widget.sub_choice_2.clicked.connect(
            lambda: self.submit_choice(self.widget.choice_2.toPlainText()))
        self.widget.sub_choice_3.clicked.connect(
            lambda: self.submit_choice(self.widget.choice_3.toPlainText()))
        self.widget.sub_choice_4.clicked.connect(
            lambda: self.submit_choice(self.widget.choice_4.toPlainText()))
        self.widget.sub_choice_5.clicked.connect(
            lambda: self.submit_choice(self.widget.choice_5.toPlainText()))

    @classmethod
    def add_to_instances(cls, item):
        cls.instances.add(item)

    @classmethod
    def clear_instances(cls):
        cls.instances.clear()

    @classmethod
    def clear_cache(cls):
        cls.cache.clear()

    @classmethod
    def add_to_cache(cls, val):
        cls.cache.add(val)

    @staticmethod
    def fill_to_page(field_id, val):
        """
        Submit the given value into the textarea by using given id
        """
        driver = get_driver()
        try:
            driver.execute_script(
                open(f"{base_dir}/js/choice_submit.js").read(), field_id, val)
        except Exception as e:
            logger.info(f"Error when submitting: {e}")

    def submit_choice(self, val):
        """
        Submit directly to the webpage.
        :type val: Value of the relatted choice field
        """
        sub_item_text = self.widget.item_text.text()
        field_id = self.get_field_id(sub_item_text)
        TabsHandler.go_to_doing_job_tab()
        if val not in self.cache:
            self.fill_to_page(field_id, val)
        self.add_to_cache(val)

    """
    The methods that update the input fields in update window
    """

    def ad_first(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.first_url):
                field.setPlainText(self.ad_data.first_url)

    def last_sentence(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_sentences:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def ad_link(self):
        field = self.get_first_empty()
        if field:
            for item in self.ad_data.links:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def last_paragraph(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_paragraphs:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def post_title(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.titles:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def ad_about(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.about_url):
                field.setPlainText(self.ad_data.about_url)

    def ad_contact(self):
        field = self.get_first_empty()
        if field:
            if not self.already_filled(self.ad_data.contact_url):
                field.setPlainText(self.ad_data.contact_url)

    def post_link(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.posts:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def last_word(self):
        field = self.get_first_empty()
        if field:
            for item in self.blog_data.last_words:
                if not self.already_filled(item)\
                        and item not in self.cache:
                    field.setPlainText(item)
                    break

    def already_filled(self, item):
        """
        This method checks if the item given is available in any other field.
        This not only check in the current instance, but also checks all the
        other instances created with this class.
        """
        for instance in self.instances:
            instance: JobUpdateWidget

            for field in instance.fields:
                if field.toPlainText() == item:
                    return True

    """
    HELPERS
    """

    def get_field_id(self, label):
        """
        Return the submission field id by using given <SubmissionItem> text.
        :type label: string of the <JobUpdateWidget> submission_item text.
        """
        for i in self.job.submission_items:
            i: SubmissionItem
            if i.text == label:
                return str(i.field_id)

    def get_first_empty(self):
        """
        Gets the first empty choice field from 5 choice fields.
        """
        for f in self.fields:
            if not f.toPlainText():
                return f


class MainScreen(QMainWindow, Ui_MainScreen):
    """
    Main Screen of the application
    """

    """
    Signal: Job details update dialog open
    """
    sig_job_update = pyqtSignal()

    """
    Job update dialog window. This is used in <jobsHandler>
    to close the dialog when skipping the job 
    """
    job_update_dialog = None

    """
    Setting: Skip Code Submission jobs
    """
    skip_code_submit = True

    """
    Setting: Skip Code Submission jobs
    """
    skip_file_submit = True

    """
    Programme running state
    """
    running = False

    def __init__(self):
        super(MainScreen, self).__init__()
        self.blog_data = None
        self.ad_data = None
        self.threadpool = QThreadPool()

        self.driver = None
        self.setupUi(self)

        # Triggering menu items events
        self.actionDatabase_Manager.triggered.connect(self.open_db_manager)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.exit)
        self.actionDeveloper.triggered.connect(self.show_developer_info)

        autopilot_action = QAction(QIcon('./icons/bot.png'), '', self)
        autopilot_action.triggered.connect(self.activate_auto_pilot)
        autopilot_action.setCheckable(True)

        update_window_action = QAction(QIcon("./icons/help.png"), '', self)
        update_window_action.triggered.connect(self.sig_job_update.emit)

        # Adding actions into toolbar
        self.toolBar.addAction(autopilot_action)
        self.toolBar.addAction(update_window_action)

        # Defining button actions
        self.but_go.clicked.connect(self._thread_miner_submit)
        self.but_skip.clicked.connect(self.job_skip)
        self.but_hide.clicked.connect(self.job_hide)
        self.but_run.clicked.connect(self.start_or_stop)

        # Slots for custom signals
        self.sig_job_update.connect(self.open_job_update_window)

    @classmethod
    def select_code_sub(cls,):
        cls.skip_code_submit = False

    @classmethod
    def select_file_sub(cls):
        cls.skip_file_submit = False

    @classmethod
    def set_running_stat(cls):
        """
        Toggle the state of running state of the jobs.
        This should be called whenever the <start_or_stop> func is called.
        """
        cls.running = False if cls.running else True

    def start_or_stop(self, *args):
        """
        Perform a toggle action based on progress is running or not.
        :param args:
        :return:
        """
        self.set_running_stat()

        if self.running:
            # Set run button text and color normal
            self.but_run.setText("STOP")

            # Set job selection settings
            if not self.skip_code_sub.isChecked():
                self.select_code_sub()
            if not self.skip_file_sub.isChecked():
                self.select_file_sub()

            driver = get_driver()
            if driver:
                jh.update_jobs()
                t = threading.Thread(target=self.start_running)
                t.start()
        else:
            # Stopping running
            # Set run button text and color
            self.but_run.setText("RUN")

    def start_running(self, *args):
        print("Running")
        self.driver = get_driver()
        jh.select_a_job()

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
        self.but_go.setEnabled(False)

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
        self.but_go.setEnabled(True)

        self.job_update_dialog = QDialog(parent=self)
        self.set_update_dialog_universal(self.job_update_dialog)

        widget_layout = QVBoxLayout()
        widget_layout.setSpacing(0)

        job: Job = JobsHandler.current_job_obj
        if not job:
            return

        # All the update widgets
        widgets = []

        JobUpdateWidget.clear_instances()
        # for sub_item in job.submission_items:
        for sub_item in job.submission_items:
            item = JobUpdateWidget(
                sub_item=sub_item,
                blog_data=self.blog_data,
                ad_data=self.ad_data,
            )
            JobUpdateWidget.add_to_instances(item)
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

        clr_cache_btn = QPushButton("Clear Cache")
        clr_cache_btn.setFont(QFont('Times', 10))
        clr_cache_btn.setFixedHeight(50)
        clr_cache_btn.clicked.connect(JobUpdateWidget.clear_cache)

        main_layout.addWidget(save_btn)
        main_layout.addWidget(clr_cache_btn)

        self.job_update_dialog.setLayout(main_layout)
        self.job_update_dialog.exec()

    @classmethod
    def set_update_dialog_universal(cls, dialog):
        """
        For accessing from other classes
        """
        cls.job_update_dialog = dialog

    def save_and_submit(self, widgets):
        """
        :param widgets: All the <JobUpdateWidget> for current job
        :return:
        """

        def _thread():
            def get_choices(sub_text):
                """
                Returns the choices according to the given
                <SubmissionItem> text. These choices are taken
                from update window fields
                """
                for w in widgets:
                    w: JobUpdateWidget = w
                    if w.widget.item_text.text() == sub_text:
                        # Found the related submission item
                        rel_choices = []
                        for i in w.fields:
                            choice_txt = i.toPlainText().strip()

                            # skip empty choice fields
                            if not choice_txt:
                                continue

                            rel_choices.append(choice_txt)
                        return rel_choices

            job = JobsHandler.current_job_obj
            for sub_item in job.submission_items:
                # get the choices for this submission item
                choices = get_choices(sub_item.text)

                for ch in choices:
                    obj = SubmissionItemChoice(text=ch)

                    # Add to the choices of current <SubmissionItem>
                    sub_item.choices.append(obj)

            # Database operations complete. Now submit
            self.submit()
            self.job_update_dialog.close()

        t = threading.Thread(target=_thread, daemon=True)
        t.start()

    def submit(self):
        """
        Submit the proofs into the actual webpage
        """
        job = JobsHandler.current_job_obj

        for sub_item in job.submission_items:
            # skip file submissions
            if str(sub_item.field_id).lower().startswith('file'):
                continue

            # Fill the box
            choice = random.choice(list(sub_item.choices))
            tab_h.go_to_doing_job_tab()
            JobUpdateWidget.fill_to_page(sub_item.field_id, choice.text)

        # Enable the button again
        self.but_go.setEnabled(True)

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
        using the previously submitted tasks.
        """

        def _thread():
            driver = get_driver()
            if not driver:
                return

            jh.update_jobs()
            for job_id in jh.get_all_job_ids():
                TabsHandler.close_junk()
                TabsHandler.close_doing_job_tab()
                job_url = get_job_url(job_id)
                driver.open_url(job_url, target='_blank')
                modify_doing_job_page()
                source = get_job_page_source()

                if not source:
                    continue

                ji_section: list = get_ji_section(source)
                ap_section: dict = get_ap_section(source)
                print(ap_section)
                lst_ap_section: list = [ap_section[ap] for ap in ap_section]
                print("\n\n list ap")
                print(lst_ap_section)

                # Check if this job has previously completed
                prev_job = None
                for job in session.query(Job).all():
                    job: Job
                    prev_job_ins = [i.text for i in job.instruction_items]
                    prev_job_sub = [s.text for s in job.submission_items]

                    if prev_job_sub == lst_ap_section \
                            and prev_job_ins == ji_section:
                        prev_job = job
                        print("Match found")
                        break
                    else:
                        # Not a match
                        with open('not_matched.txt', 'a') as f:
                            text = f"\n\n=============\n" \
                                   f"Selected Job Instructions\n{str(ji_section)}\n" \
                                   f"Previous Job Instructions\n{str(prev_job_ins)}\n\n" \
                                   f"Selected Job Submission items:\n{str(lst_ap_section)}\n" \
                                   f"Prev Job Submission Items: \n{str(prev_job_sub)}\n" \
                                   f"================"
                            f.write(text)

                # If a match found start the submission process
                if isinstance(prev_job, Job):
                    TabsHandler.go_to_doing_job_tab()
                    for sub_item in prev_job.submission_items:
                        # real textarea id of the submission page
                        textarea_id = sub_item.field_id
                        print("Textarea ID: ", textarea_id)
                        try:
                            val = random.choice(sub_item.choices).text
                        except IndexError:
                            continue
                        print("Value: ", val)
                        # Fill the proofs
                        driver.execute_script(f"$('{textarea_id}').val('{val}');")
                else:   # Not a match
                    continue

                # # Start the submit button click process
                btn_text = driver.execute_script("return $('#submit-proof-btn').text();")
                btn_text = str(btn_text).lower().strip()
                print("Button Text: ", btn_text)

                if not btn_text == 'submit proof':
                    # Probably I need to wait some time before submission
                    _time = btn_text.split(' ')[1]
                    try:
                        minutes, seconds = int(_time.split(':')[0]), int(_time.split(':')[1])
                        total_wait = (minutes * 60) + seconds + 2
                        print(f"Waiting {total_wait} seconds for submission")
                        time.sleep(total_wait)
                    except ValueError:
                        print(f"Error when splitting time counter value with: {_time}")

                # All good submit the job
                print("Time to click the submit button")
                # driver.execute_script("$('#submit-proof-btn').click();")

                # # wait more than a monite before next job
                wait = 60 + random.randint(2, 10)
                print(f"Waiting {wait} minutes")
                time.sleep(wait)

        t = threading.Thread(target=_thread)
        t.start()

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
