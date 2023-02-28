from page_views.entry_page import EntryPage
from page_views.page_manager import PageManager
from page_views.search_page import SearchPage
from page_views.sidebar import Sidebar
from page_views.video_page import VideoPage
import streamlit as st

from semantha import Semantha


class AIEDNPage:
    def __init__(self):
        self.__semantha = Semantha()
        self.__page_manager = PageManager()
        self.__sidebar = Sidebar(self.__page_manager)
        self.__entry_page = EntryPage(self.__page_manager, self.__sidebar)
        self.__video_page = VideoPage(self.__page_manager, self.__sidebar)
        self.__search_page = SearchPage(self.__sidebar, self.__semantha)
        self.__pages = [self.__entry_page, self.__video_page, self.__search_page]

    def display_page(self):
        self.__configure_page()
        self.__sidebar.display_page()

        placeholder = st.empty()

        for i in range(len(self.__pages)):
            if st.session_state.page == i:
                with placeholder.container():
                    self.__pages[i].display_page()

    @staticmethod
    def __configure_page():
        st.config.set_option("theme.primaryColor", "#BE25BE")
        st.set_page_config(
            page_title="🕵🏻 AIEDN - Daniel Jung Mathesuche",
            page_icon="favicon.png",
            initial_sidebar_state="collapsed",
        )
        # display a title
        st.header("🕵🏻 AIEDN - Daniel Jung Mathesuche")
