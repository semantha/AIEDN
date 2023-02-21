from page_views.abstract_page import AbstractPage
import streamlit as st


class EntryPage(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager

    def display_page(self):
        st.write(
            "Herzlich Willkommen zu unserer Studie, gib uns zunächst bitte deine Studien-ID an."
        )

        with st.form(key="user_id_form"):
            user_id = st.text_input(
                "Studien-ID",
                key="user_id_text_input",
                type="default",
                max_chars=12,
            )

            _, _, col, _, _ = st.columns(5)
            button = col.form_submit_button(
                "✅ Bestätigen", help="Klicke hier um deine ID zu bestätigen."
            )

        if button and self.check_user_id(user_id):
            self.submit_form(user_id)

    def submit_form(self, user_id):
        # TODO sanity check ID
        st.session_state.user_id = user_id
        self.page_manager.nextpage()

    def check_user_id(self, user_id):
        if user_id == "hyper":
            st.error("Bitte gib eine gültige Studien-ID an.")
            return False
        return True
