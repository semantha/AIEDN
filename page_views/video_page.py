import time

import streamlit as st
from streamlit_player import st_player

from page_views.abstract_page import AbstractPage

_CONTROL_GROUP_VIDEO = "https://vimeo.com/803009708"
_EXPERIMENTAL_GROUP_VIDEO = "https://vimeo.com/803009422"
_EXPERIMENTAL_GROUP_VIDEO_LENGTH = 80
_CONTROL_GROUP_VIDEO_LENGTH = 75


class VideoPage(AbstractPage):
    def __init__(self, page_manager, sidebar):
        self.__page_manager = page_manager
        self.__sidebar = sidebar
        if "video_first_time" not in st.session_state:
            st.session_state.video_first_time = True

    def display_page(self):
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        video_url, video_length = self.__choose_video()
        st_player(video_url, height=400)
        _, _, col, _, _ = st.columns(5)
        if st.session_state.video_first_time and not self.__sidebar.get_video_skippable():
            time.sleep(video_length)
        st.session_state.video_first_time = False
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
