import logging
import pathlib


def get_syslogger() -> logging.getLogger():
    """
    Returns a common logger to be used across all over the program files, to capture overall
    system status. With the log file generated by this logger should be able to provide the enough
    information to detect any error on the fly, if something unexpected happen or something goes wrong.
    :return:
    """
    logger = logging.getLogger("SystemLogger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] [%(filename)s  %(funcName)s] line %(lineno)d:  %(message)s')
    file_handler = logging.FileHandler(f"{base_dir}/SYSTEM.LOG", 'w+')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


base_dir = pathlib.Path(__file__).parent.parent.absolute()
sys_logger = get_syslogger()


def str_cleaner(string, rem_spaces=False):
    """
    Removes any unnecessary escape characters.
    :param rem_spaces: Remove spaces also if <rem_spaces> is True.
    :param string:
    :return: Cleaned string.
    """
    dirty_str = str(string)
    cleaned = dirty_str.strip('\n \t \b')
    cleaned = cleaned.replace('\n', '').replace('"', "'")

    if rem_spaces:
        cleaned = cleaned.strip(' ')
    return cleaned


def get_ascii(text: str) -> str:
    """
    Converts the given string into ASCII encoding, if it is not already.
    Special characters, emojis will be lost if exist in the text.
    :param text:
    :return:
    """
    if not text.isascii():
        try:
            text = text.encode('utf-8').decode(encoding='ascii', errors='ignore')
            return text
        except Exception as e:
            sys_logger.critical(f"Ascii conversion error: {e}")


def get_file_logger(name: str, level: int, logfile: str, mode: str) -> logging.getLogger():
    """
    :param name: Name of the logger to passed into: logging.getLogger(name)
    :param level: logging level
    :param logfile: Complete path to the file with file name
    :param mode: File open mode
    :return:
    """
    if not name or not level:
        return

    logger = logging.getLogger(name)
    logger.setLevel(level if level else logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] [%(filename)s  %(funcName)s] line %(lineno)d:  %(message)s')
    file_handler = logging.FileHandler(logfile, mode)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
