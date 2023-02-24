import json
import os

from page_views.abstract_page import AbstractPage
import streamlit as st


class EntryPage(AbstractPage):
    def __init__(self, page_manager, sidebar):
        super().__init__()
        self.__page_manager = page_manager
        self.__dummy = ""
        self.__sidebar = sidebar
        with open(os.path.join(os.getcwd(), "ids", "provided_ids.json")) as fp:
            self.__user_ids = json.load(fp)

    def display_page(self):
        placeholder = st.empty()
        with placeholder.container():
            st.write(
                "Herzlich Willkommen zu unserer Studie, gib uns zunächst bitte deine Studien-ID an."
            )
            if self.__sidebar.get_enter_to_submit():
                user_id = st.text_input(
                    "Studien-ID",
                    key="user_id_text_input",
                    value="",
                    type="default",
                    max_chars=7,
                )
                _, _, col, _, _ = st.columns(5)
                button = col.button(
                    "✅ Bestätigen", help="Klicke hier um deine ID zu bestätigen."
                )
                if (button or self.__dummy != user_id) and self.__check_user_id(user_id):
                    self.__dummy = user_id
                    self.__submit_form(user_id)
            else:
                with st.form(key="user_id_form"):
                    user_id = st.text_input(
                        "Studien-ID",
                        key="user_id_text_input",
                        value="",
                        type="default",
                        max_chars=22,
                    )
                    _, _, col, _, _ = st.columns(5)
                    button = col.form_submit_button(
                        "✅ Bestätigen", help="Klicke hier um deine ID zu bestätigen."
                    )
                    if button and self.__check_user_id(user_id):
                        self.__submit_form(user_id)

    def __submit_form(self, user_id):
        st.session_state.user_id = user_id
        st.session_state.control = self.__user_ids[user_id]
        self.__page_manager.nextpage()

    def __check_user_id(self, user_id):
        if user_id not in self.__user_ids.keys():
            st.error("Bitte gib eine gültige Studien-ID an.", icon="🕵🏻")
            return False
        return True
