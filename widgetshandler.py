from livecontrols import LiveControls


class MainScreenWidgetsHandler:
    def __init__(self):
        self.main_screen = LiveControls.screens['main_screen']

    def clear_submission_widgets(self) -> None:
        layout = self.main_screen.scroll_submit_widgets.parent().layout()
        layout.removeWidget(self.main_screen.scroll_submit_widgets.widget())

    def update_submission_widgets(self) -> None:
        self.main_screen.emit_submit_widget_update_signal(self.main_screen)

    def but_db_submit_set_default(self):
        self.main_screen.but_db_submit.setText("Submit With Database")
        self.main_screen.but_db_submit.setEnabled(True)

    def but_miner_submit_set_default(self):
        self.main_screen.but_miner_submit.setText("Submit With Miner")
        self.main_screen.but_miner_submit.setEnabled(True)

    def clear_blog_url_field(self):
        self.main_screen.input_url.clear()


