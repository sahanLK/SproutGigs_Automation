"""
Picoworkers.com site specific constants (urls, class names, Ids etc...)
"""
import os
import pyautogui
from ezmysqlpy import MySQLPy
from ezmysqlpy.exceptions import ServerConnectionError

"""
BROWSER CONTANTS
"""
# Width of the window
# WINDOW_WIDTH = 1020
WINDOW_WIDTH = pyautogui.size().width * (55 / 100)

# Height of the window
# WINDOW_HEIGHT = 836
WINDOW_HEIGHT = pyautogui.size().height

# X-Coordinate of the browser position
# POSITION_X = 515
POSITION_X = pyautogui.size().width * (25 / 100)

# Y-Coordinates of the browser position
POSITION_Y = 0

# PROGRAM LOCATION TO SAVE CHROME PROFILES AND ETC..
PICO_LOCATION = os.path.join(os.environ['USERPROFILE'], 'Documents', 'Browser Profiles')

"""
LOGIN PAGE CONSTANTS
"""
# Login Url
LOGIN_URL = 'https://sproutgigs.com/login.php'
# LOGIN_URL = 'https://account.google.com'

# Cookie Accept Button X_PATH at the login page.
COOKIE_ACC_BUT_X_PATH = '/html/body/div[3]/div/div/a'

# X-PATH of the login button
LOGIN_BUT_X_PATH = '//*[@id="login-form"]/div[2]/button'

# The ID of the email field in login page
EMAIL_FIELD_ID = 'loginEmailPhone'

# The ID of the password field
PASSWD_FIELD_ID = 'loginPassword'

"""
JOBS PAGE CONSTANTS
"""
# Url of Marketing Test jobs page
MARKETING_TEST_URL = 'https://sproutgigs.com/jobs.php?category=10&sub_category='

"""
ACTIVE JOB CONSTANTS
"""
# The beginning of the url part in the active job page.
DOING_JOB_PAGE_INITIALS = 'https://sproutgigs.com/jobs/submit-task.php?Id='

# Saving location of the history page screenshot.
SNAPSHOT_LOC = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'history_shot.png')

# Class name of the "Hide this job" link in the job page
HIDE_JOB_CLSNAME = 'hide-job'

"""
DATABASE CONSTANTS
"""
# Database Host
DB_HOST = 'localhost'

# Database Username
DB_USER = 'root'

# Database Host Password
DB_PWD = ''

# Database Name
DB_NAME = 'pico_db'


"""
COMMON HANDLERS
"""

db_handler = MySQLPy(DB_HOST, DB_USER, DB_PWD)
if not db_handler.db_exists('pico_db'):
    db_handler.create_db('pico_db')
db_handler.select_db(DB_NAME)



"""
WEB BROWSER CONSTANTS
"""
CHROME_HISTORY_URL = 'chrome://history/'
EDGE_HISTORY_URL = 'edge://history/all'


"""
PROOFS SUBMISSION CONSTANTS
"""
MAX_BLOG_URLS_REQ = 8
MAX_AD_URLS_REQ = 3
