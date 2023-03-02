import streamlit as st
from streamlit_player import st_player

from page_views.abstract_page import AbstractPage

_CONTROL_GROUP_VIDEO = "https://vimeo.com/803009708"
_EXPERIMENTAL_GROUP_VIDEO = "https://vimeo.com/803009422"


class VideoPage(AbstractPage):
    def __init__(self, page_manager):
        self.__page_manager = page_manager
        if "video_first_time" not in st.session_state:
            st.session_state.video_first_time = True

    def display_page(self):
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        video_url = self.__choose_video()
        st_player(video_url, height=400, playing=True, config={
            "vimeo": {
                "playerOptions": {
                    "color": "#BE25BE",
                    "title": False,
                }
            }
        })
        _, _, col, _, _ = st.columns(5)
        col.button(
            "⏭️ Weiter",
            on_click=self.__page_manager.nextpage,
            key="next_button_video_not_done",
            help="Klicke hier um zur nächsten Seite zu gelangen.",
        )

    @staticmethod
    def __choose_video():
        if st.session_state.control:
            return _CONTROL_GROUP_VIDEO
        return _EXPERIMENTAL_GROUP_VIDEO
