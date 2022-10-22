"""
                    ######## WARNING: DO NOT TOUCH  ########

This file contains just a key logging function, but it should be kept isolated.
If something goes wrong with the code in this file, this be detected by windows
security protocols as a threat (python keylogger).
For some reason, if this file gets deleted by windows, the whole file will be removed.
So, to prevent the program files loss or deletions, don't mix the codes in this file
with any other code files.
"""

import threading
from pynput.keyboard import Listener, Controller, Key

from functions.fns import get_syslogger
from keyfunctions import KeyFunctions
from functions.driverfns import snap_history

Kf = KeyFunctions()
Kc = Controller()

sys_logger = get_syslogger()


def _press_backspace():
    try:
        Kc.press(Key.backspace)
    except Exception as e:
        print("Error when pressing Backspace: {}".format(e))


def key_listener():
    try:
        def exec_thread():
            def _exec_method(key):
                # If the below name contain the word "key",
                # the file will be removed bt windows security protocols.
                name = key
                pressed = str(name).strip("'")

                if pressed == 'Key.up':
                    Kf.select_textarea()
                elif pressed == 'Key.down':
                    Kf.select_textarea()
                elif pressed == 'Key.delete':
                    Kf.skip_job()
                elif pressed == 'Key.insert':
                    Kf.submit_job()
                elif pressed == 'Key.page_down':
                    Kf.clear_already_submitted()
                elif pressed == 'Key.f2':
                    Kf.modify_page()
                elif pressed == 'Key.f4':
                    Kf.stop_snapshot_process()
                elif pressed == 'Key.f8':
                    snap_history()
                elif pressed == 'Key.f9':
                    Kf.clear_textarea()
                elif pressed == '1':
                    _press_backspace()
                    Kf.submit_blog_link()
                elif pressed == '2':
                    _press_backspace()
                    Kf.submit_post_title()
                elif pressed == '3':
                    _press_backspace()
                    Kf.submit_last_word()
                elif pressed == '4':
                    _press_backspace()
                    Kf.submit_last_sentence()
                elif pressed == '5':
                    _press_backspace()
                    Kf.submit_last_paragraph()
                elif pressed == '6':
                    _press_backspace()
                    Kf.submit_ad_first()
                elif pressed == '7':
                    _press_backspace()
                    Kf.submit_ad_inside()
                elif pressed == '8':
                    _press_backspace()
                    Kf.submit_ad_about()
                elif pressed == '9':
                    _press_backspace()
                    Kf.submit_ad_contact()
                elif pressed == '0':
                    _press_backspace()
                    Kf.hide_job()
                else:
                    pass

            with Listener(on_release=_exec_method) as listener:
                listener.join()
        t = threading.Thread(target=exec_thread, daemon=True)
        t.start()
        return True
    except Exception as e:
        sys_logger.error("Listener error: {}".format(e))
        return False
