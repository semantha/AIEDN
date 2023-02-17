import streamlit as st
import ast
from semantha import Semantha
import time

if "page" not in st.session_state:
    st.session_state.page = 0


def nextpage():
    st.session_state.page += 1


def restart():
    st.session_state.page = 0


semantha = Semantha()
st.config.set_option("theme.primaryColor", "#BE25BE")
st.set_page_config(
    page_title="🕵🏻 AIEDN - Daniel Jung Mathesuche",
    page_icon="favicon.png",
    initial_sidebar_state="collapsed",
)
# display a title
st.header("🕵🏻 Daniel Jung Mathesuche - AIEDN")

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.write("")
    st.write("Klicke hier um die Seite zu neustarten:")
    restart_button = st.button("🔄 Neustart", on_click=restart)
    st.write("")
    debug = st.checkbox("🐞 Debug Mode", value=False)
    if debug:
        max_matches = st.slider("Maximum matches", min_value=0, max_value=10, value=5)

        filter_by_videos = st.checkbox("Filter by videos", value=True)
        filter_size = st.slider("Filter size", min_value=0, max_value=10, value=3)
        enable_usage_tracking = st.checkbox("Enable usage tracking", value=False)
        show_videos_below_each_other = st.checkbox(
            "Show videos below each other", value=False
        )
    else:
        max_matches = 5
        filter_by_videos = True
        filter_size = 3
        enable_usage_tracking = False
        show_videos_below_each_other = False


placeholder = st.empty()
if st.session_state.page == 0:
    with placeholder.container():
        st.write(
            "Herzlich Willkommen zu unserer Studie, gib uns zunächst bitte deine Studien-ID an."
        )

        with st.form(key="user_id_form"):
            user_id = st.text_input(
                "Studien-ID", value="", key="user_id", type="default", max_chars=12
            )
            _, _, col, _, _ = st.columns(5)
            submit_button = col.form_submit_button(
                "✅ Bestätigen",
                on_click=nextpage,
                help="Klicke hier um deine ID zu bestätigen.",
            )

if st.session_state.page == 1:
    with placeholder.container():
        st.success("🕵🏻 Vielen Dank, wir zeigen dir nun ein kurzes Erklärvideo.")
        st.video("https://www.youtube.com/watch?v=NseWRQ1JYoM")
        _, _, col, _, _ = st.columns(5)
        time.sleep(5)
        next_button = col.button(
            "⏭️ Weiter",
            on_click=nextpage,
            key="next_button_video_not_done",
            help="Klicke hier um zur nächsten Seite zu gelangen.",
        )


if st.session_state.page == 2:
    with placeholder.container():
        # display a description of your app
        st.write(
            "Gib deine Mathefrage ein und ich werde Dir eine passende Stelle von einem Daniel Jung Video anzeigen."
        )
        # display a search input
        with st.form(key="search_form"):
            search_string = st.text_area(
                label="Suche",
                value="",
                placeholder="Gib hier deine Frage ein...",
                label_visibility="collapsed",
            )
            _, _, col, _, _ = st.columns(5)
            button = col.form_submit_button("🔍 Suche")
        if button:
            tags = "base,11"
            if search_string == "":
                st.error("Bitte gib zuerst eine Frage ein!", icon="🕵🏻")
            else:
                with st.spinner("🕵🏻 Ich suche ein passendes Video..."):
                    results = semantha.query_library(
                        search_string,
                        tags=tags,
                        max_matches=max_matches,
                        filter_by_videos=filter_by_videos,
                        filter_size=filter_size,
                    )
                    if results.empty:
                        st.error(
                            "Ich konnte leider kein passendes Video finden.", icon="🕵🏻"
                        )
                        if enable_usage_tracking:
                            semantha.add_to_library(
                                content=search_string, tag=user_id + ",no_match"
                            )
                    else:
                        st.success("Gefunden! Hier ist dein Ergebnis!", icon="🕵🏻")
                        if enable_usage_tracking:
                            semantha.add_to_library(content=search_string, tag=user_id)

                        if not show_videos_below_each_other:

                            st.session_state["tabs"] = ["Video #1"]
                            for i, row in results.iterrows():
                                if i >= 2:
                                    st.session_state["tabs"].append(f"Video #{i}")

                            tabs = st.tabs(st.session_state["tabs"])
                            for i, row in results.iterrows():
                                results.at[i, "Metadata"] = ast.literal_eval(
                                    row["Metadata"]
                                )
                                video_id = results.at[i, "Metadata"]["id"]
                                start = results.at[i, "Metadata"]["start"]
                                content = results.at[i, "Content"]
                                category = results.at[i, "Tags"]
                                category = [
                                    tag for tag in category if tag not in ["base", "11"]
                                ]
                                category = ", ".join(category)
                                video = results.at[i, "Name"].split("_")[0]
                                with tabs[i - 1]:
                                    st.markdown(f'💬**Daniel sagt:** "_{content}..._"')
                                    st.markdown(f"🏷️ **Tags:** _{category}_")
                                    st.video(video_id, start_time=start)
                                    st.markdown(f"📺 **Video:** _{video}_")
                            if debug:
                                with st.expander("Ergebnisse", expanded=False):
                                    st.write(results)

                        else:
                            for i, row in results.iterrows():
                                results.at[i, "Metadata"] = ast.literal_eval(
                                    row["Metadata"]
                                )
                                video_id = results.at[i, "Metadata"]["id"]
                                start = results.at[i, "Metadata"]["start"]
                                content = results.at[i, "Content"]
                                category = results.at[i, "Tags"]
                                category = [
                                    tag for tag in category if tag not in ["base", "11"]
                                ]
                                category = ", ".join(category)
                                video = results.at[i, "Name"].split("_")[0]
                                st.markdown(f'💬**Daniel sagt:** "_{content}..._"')
                                st.markdown(f"🏷️ **Tags:** _{category}_")
                                st.video(video_id, start_time=start)
                                st.markdown(f"📺 **Video:** _{video}_")

                            if debug:
                                with st.expander("Ergebnisse", expanded=False):
                                    st.write(results)
