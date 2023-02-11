import sys
import unittest
from picoconstants import db_handler
from screens.mainscreen import MainScreen
from PyQt5.QtWidgets import QApplication


class TestMainScreen(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMainScreen, self).__init__(*args, **kwargs)
        self.app = QApplication(sys.argv)
        self.screen = MainScreen()
        self.screen.show()
        self.app.exec()

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_db_submit(self):
        self.screen.db_submit()

    def test_miner_submit(self):
        self.screen.miner_submit()

    def test_get_blog_url(self):
        pass


if __name__ == "__main__":
    unittest.main()
