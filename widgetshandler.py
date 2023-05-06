from livecontrols import LiveControls


class MainScreenWidgetsHandler:
    def __init__(self):
        self.main_screen = LiveControls.screens['main_screen']

    def but_go(self):
        self.main_screen.but_go.setEnabled(True)

    def clear_blog_url_field(self):
        self.main_screen.input_url.clear()


