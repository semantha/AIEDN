import ast
from page_views.abstract_page import AbstractPage
import streamlit as st

from semantha import DenseOnlyRanking


class SearchPage(AbstractPage):
    def __init__(self, page_id, page_manager, sidebar, semantha):
        super().__init__(page_id)
        self.page_manager = page_manager
        self.sidebar = sidebar
        self.semantha = semantha
        self.__dummy = ""

    def display_page(self):
        # display a description of your app
        st.write(
            "Gib deine Mathefrage ein und ich werde Dir eine passende Stelle von einem Daniel Jung Video anzeigen."
        )
        # display a search input
        if self.sidebar.enter_to_submit:
            search_string = self.__search_form()
            _, _, col, _, _ = st.columns(5)
            button = col.button("🔍 Suche")
            if button or self.__dummy != search_string:
                self.__search(search_string)
        else:
            with st.form(key="search_form"):
                search_string = self.__search_form()
                _, _, col, _, _ = st.columns(5)
                button = col.form_submit_button("🔍 Suche")
            if button:
                self.__search(search_string)

    def __search_form(self):
        if st.session_state.control:
            search_string = st.text_input(
                label="Suche",
                value="",
                placeholder="Gib hier deine Stichwörter ein...",
                label_visibility="collapsed",
            )
        else:
            search_string = st.text_area(
                label="Suche",
                value="",
                placeholder="Gib hier deine Frage ein...",
                label_visibility="collapsed",
            )

        return search_string

    def __search(self, search_string):
        tags = "base,11"
        if search_string == "":
            st.error("Bitte gib zuerst eine Frage ein!", icon="🕵🏻")
        else:
            self.__content_search(search_string, tags)

    def __content_search(self, search_string, tags):
        with st.spinner("🕵🏻 Ich suche ein passendes Video..."):
            results = self.semantha.query_library(
                search_string,
                tags=tags,
                max_matches=self.sidebar.get_max_matches(),
                ranking_strategy=self.sidebar.get_ranking_strategy(),
                sparse_filter_size=self.sidebar.get_filter_size(),
                alpha=self.sidebar.get_alpha()
            )
            if results.empty:
                self.__no_match_handling(search_string)
            else:
                self.__match_handling(search_string, results)

    def __match_handling(self, search_string, results):
        st.success(f"Erledigt! Ich habe {len(results)} passende Videos für dich gefunden!", icon="🕵🏻")
        if self.sidebar.get_enable_usage_tracking():
            self.semantha.add_to_library(
                content=search_string, tag=st.session_state.user_id
            )

        st.session_state["tabs"] = ["Video #1"]
        for i, row in results.iterrows():
            if i >= 2:
                st.session_state["tabs"].append(f"Video #{i}")

        tabs = st.tabs(st.session_state["tabs"])
        for i, row in results.iterrows():
            self.__display_result(results, i, row, tabs)
        if self.sidebar.get_debug():
            self.__debug_view(results)

    def __debug_view(self, results):
        with st.expander("Ergebnisse", expanded=False):
            st.write(results)

    def __no_match_handling(self, search_string):
        st.error(
            "Ich konnte leider kein passendes Video finden.",
            icon="🕵🏻",
        )
        if self.sidebar.get_enable_usage_tracking():
            self.semantha.add_to_library(
                content=search_string, tag=st.session_state.user_id + ",no_match"
            )

    def __display_result(self, results, i, row, tabs):
        results.at[i, "Metadata"] = ast.literal_eval(row["Metadata"])
        video_id = results.at[i, "Metadata"]["id"]
        start = 0 if st.session_state.control else results.at[i, "Metadata"]["start"]
        content = results.at[i, "Content"]
        category = results.at[i, "Tags"]
        category = [tag for tag in category if tag not in ["base", "11"]]
        category = ", ".join(category)
        video = results.at[i, "Name"].split("_")[0]
        with tabs[i - 1]:
            if not st.session_state.control:
                st.markdown(f'💬 **Daniel sagt:** "_{content}..._"')
            st.markdown(f"🏷️ **Tags:** _{category}_")
            st.video(video_id, start_time=start)
            st.markdown(f"📺 **Video:** _{video}_")
