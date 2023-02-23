import time
from page_views.abstract_page import AbstractPage
import streamlit as st

_CONTROL_GROUP_VIDEO = "https://www.youtube.com/watch?v=NseWRQ1JYoM"
_EXPERIMENTAL_GROUP_VIDEO = "https://www.youtube.com/watch?v=7Twnmhe948A"
_EXPERIMENTAL_GROUP_VIDEO_LENGTH = 5
_CONTROL_GROUP_VIDEO_LENGTH = 5


class VideoPage(AbstractPage):
    def __init__(self, page_manager):
        self.__page_manager = page_manager

    def display_page(self):
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        video_url, video_length = self.__choose_video()
        st.video(video_url)
        _, _, col, _, _ = st.columns(5)
        time.sleep(video_length)
        col.button(
            "⏭️ Weiter",
            on_click=self.__page_manager.nextpage,
            key="next_button_video_not_done",
            help="Klicke hier um zur nächsten Seite zu gelangen.",
        )

    @staticmethod
    def __choose_video():
        if st.session_state.control:
            return _CONTROL_GROUP_VIDEO, _CONTROL_GROUP_VIDEO_LENGTH
        return _EXPERIMENTAL_GROUP_VIDEO, _EXPERIMENTAL_GROUP_VIDEO_LENGTH
