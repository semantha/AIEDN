from page_views.abstract_page import AbstractPage
import streamlit as st


class EntryPage(AbstractPage):
    def __init__(self, page_id, page_manager):
        super().__init__(page_id)
        self.page_manager = page_manager
        self.user_id = None

    def display_page(self):
        st.write(
            "Herzlich Willkommen zu unserer Studie, gib uns zunächst bitte deine Studien-ID an."
        )

        with st.form(key="user_id_form"):
            self.user_id = st.text_input(
                "Studien-ID", value="", key="user_id", type="default", max_chars=12
            )
            _, _, col, _, _ = st.columns(5)
            col.form_submit_button(
                "✅ Bestätigen",
                on_click=self.page_manager.nextpage,
                help="Klicke hier um deine ID zu bestätigen.",
            )

    def get_user_id(self):
        return self.user_id
