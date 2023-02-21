import time
from page_views.abstract_page import AbstractPage
import streamlit as st

CONTROL_GROUP_VIDEO = "https://www.youtube.com/watch?v=NseWRQ1JYoM"
EXPERIMENTAL_GROUP_VIDEO = "https://www.youtube.com/watch?v=7Twnmhe948A"


class VideoPage(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager
        self.video_url = self.choose_video()

    def display_page(self):
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        st.video(self.video_url)
        _, _, col, _, _ = st.columns(5)
        time.sleep(5)
        col.button(
            "⏭️ Weiter",
            on_click=self.page_manager.nextpage,
            key="next_button_video_not_done",
            help="Klicke hier um zur nächsten Seite zu gelangen.",
        )

    @staticmethod
    def choose_video():
        if st.session_state.control:
            return CONTROL_GROUP_VIDEO
        return EXPERIMENTAL_GROUP_VIDEO
