from page_views.entry_page import EntryPage
from page_views.page_manager import PageManager
from page_views.search_page import SearchPage
from page_views.sidebar import Sidebar
from page_views.video_page import VideoPage
import streamlit as st

from semantha import Semantha


class AIEDNPage:
    def __init__(self):
        self.semantha = Semantha()
        self.page_manager = PageManager()
        self.sidebar = Sidebar(-1, self.page_manager)
        self.entry_page = EntryPage(0, self.page_manager)
        self.video_page = VideoPage(1, self.page_manager)
        self.search_page = SearchPage(2, self.page_manager, self.sidebar, self.semantha)
        self.pages = [self.entry_page, self.video_page, self.search_page]
        self.page_dic = {page.get_page_id(): page for page in self.pages}
        self.user_id = None

    def display_page(self):
        self.__configure_page()
        self.sidebar.display_page()

        placeholder = st.empty()
        if st.session_state.page == 0:
            with placeholder.container():
                self.entry_page.display_page()
                self.user_id = self.entry_page.get_user_id()

        if st.session_state.page == 1:
            with placeholder.container():
                self.video_page.display_page()

        if st.session_state.page == 2:
            with placeholder.container():
                self.search_page.set_user_id(self.user_id)
                self.search_page.display_page()

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
