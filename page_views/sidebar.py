from page_views.abstract_page import AbstractPage
import streamlit as st

from semantha import DenseOnlyRanking, SparseFilterDenseRanking, HybridRanking

_DENSE_ONLY_RANKING = "DenseOnlyRanking"
_SPARSE_FILTER_DENSE_RANKING = "SparseFilterDenseRanking"
_HYBRID_RANKING = "HybridRanking"


class Sidebar(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager
        self.max_matches = 5
        self.ranking_strategy = _DENSE_ONLY_RANKING
        self.filter_size = 3
        self.alpha = 0.7
        self.enable_usage_tracking = True
        self.debug = False

    def get_max_matches(self):
        return self.max_matches

    def get_ranking_strategy(self):
        if self.ranking_strategy == _DENSE_ONLY_RANKING:
            return DenseOnlyRanking
        elif self.ranking_strategy == _SPARSE_FILTER_DENSE_RANKING:
            return SparseFilterDenseRanking
        elif self.ranking_strategy == _HYBRID_RANKING:
            return HybridRanking
        else:
            raise ValueError(f"Unknown ranking strategy '{self.ranking_strategy}'")

    def get_filter_size(self):
        return self.filter_size

    def get_alpha(self):
        return self.alpha

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
                self.enable_usage_tracking = st.checkbox(
                    "Enable usage tracking", value=True
                )
                self.max_matches = st.slider(
                    "Maximum matches", min_value=0, max_value=10, value=5
                )

                # self.filter_by_videos = st.checkbox("Filter by videos", value=True)
                self.ranking_strategy = st.radio("Ranking Strategy", options=["DenseOnlyRanking", "SparseFilterDenseRanking", "HybridRanking"])
                if self.ranking_strategy == _SPARSE_FILTER_DENSE_RANKING or self.ranking_strategy == _HYBRID_RANKING:
                    self.filter_size = st.slider(
                        "Sparse filter size", min_value=0, max_value=10, value=3
                    )
                if self.ranking_strategy == _HYBRID_RANKING:
                    self.alpha = st.slider(
                        "Alpha", min_value=0.0, max_value=2.0, step=0.05, value=0.7
                    )
                st.markdown("**ID CG**: _UiiZP2HjUSNCSLFyZjwk3J_")
                st.markdown("**ID EG**: _igCY5s4YztSjvswBfHARLm_")

    def restart(self):
        st.session_state.clear()
        self.page_manager.restart()

    def show_video_page(self):
        st.session_state.page = 1
