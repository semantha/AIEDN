import time
from page_views.abstract_page import AbstractPage
import streamlit as st


class VideoPage(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager

    def display_page(self):
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        st.video("https://www.youtube.com/watch?v=NseWRQ1JYoM")
        _, _, col, _, _ = st.columns(5)
        time.sleep(5)
        col.button(
            "⏭️ Weiter",
            on_click=self.page_manager.nextpage,
            key="next_button_video_not_done",
            help="Klicke hier um zur nächsten Seite zu gelangen.",
        )
