from livecontrols import LiveControls


class MainScreenWidgetsHandler:
    def __init__(self):
        self.main_screen = LiveControls.screens['main_screen']

    def clear_submission_widgets(self) -> None:
        layout = self.main_screen.scroll_submit_widgets.parent().layout()
        layout.removeWidget(self.main_screen.scroll_submit_widgets.widget())

    def update_submission_widgets(self) -> None:
        self.main_screen.emit_submit_widget_update_signal(self.main_screen)
