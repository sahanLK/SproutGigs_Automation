"""
This file contains a class that only contains the class variables to access universally
all over the programme to control the application behaviour when running.
"""


class LiveControls:
    """
    Live controls
    """

    """
    Application Screens
    """
    screens = {
        "main_screen": None,
        "login_screen": None,
    }

    """
    Webdriver instance to be used across all over the programme.
    """
    from devices.device import Edge
    driver: Edge = None

    """
    Type of web browser using for current session
    """
    browser = None

    """
    Stop link opening process for history page screenshot.
    """
    stop_link_open = False

    """
    If links for snapshot has already opened or not.
    used to prevent opening links twice if keylogger send multiple requests.
    """
    snap_links_opened = False

    """
    Current Submission widgets on the scroll area.
    Whenever this list updated, the the scroll area should be updated.
    Must be cleared after job skip, submission or hide.
    """
    submission_widgets = {}

    """
    Whether user has clicked the run button or not.
    This will be used to prevent selecting jobs before clicking the run button in main screen
    """
    jobs_running = False

    @classmethod
    def set_default(cls):
        cls.stop_link_open = False
        cls.snap_links_opened = False

    @classmethod
    def kill_driver(cls):
        if cls.driver:
            try:
                cls.driver.quit()
            except Exception as e:
                print("Failed to kill webdriver: {}".format(e))

