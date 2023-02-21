from page_views.abstract_page import AbstractPage
import streamlit as st


class Sidebar(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager
        self.max_matches = 5
        self.filter_by_videos = True
        self.filter_size = 3
        self.enable_usage_tracking = False
        self.debug = False

    def get_max_matches(self):
        return self.max_matches

    def get_filter_by_videos(self):
        return self.filter_by_videos

    def get_filter_size(self):
        return self.filter_size

    def get_enable_usage_tracking(self):
        return self.enable_usage_tracking

    def get_debug(self):
        return self.debug

    def display_page(self):
        with st.sidebar:
            st.header("⚙️ Einstellungen")
            st.write("")
            st.write("Klicke hier um die Seite neuzustarten:")
            if st.session_state.page >= 2:
                st.button("📹 Video", on_click=self.show_video_page)
            st.button("🔄 Neustart", on_click=self.restart)
            st.write("")
            self.debug = st.checkbox("🐞 Debug Mode", value=False)
            if self.debug:
                self.max_matches = st.slider(
                    "Maximum matches", min_value=0, max_value=10, value=5
                )

                self.filter_by_videos = st.checkbox("Filter by videos", value=True)
                self.filter_size = st.slider(
                    "Filter size", min_value=0, max_value=10, value=3
                )
                self.enable_usage_tracking = st.checkbox(
                    "Enable usage tracking", value=False
                )
                st.markdown("**ID CG**: _UiiZP2HjUSNCSLFyZjwk3J_")
                st.markdown("**ID EG**: _igCY5s4YztSjvswBfHARLm_")

    def restart(self):
        st.session_state.clear()
        self.page_manager.restart()

    def show_video_page(self):
        st.session_state.page = 1
