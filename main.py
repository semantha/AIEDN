import streamlit as st
import ast
from semantha import Semantha


semantha = Semantha()
st.config.set_option("theme.primaryColor", "#BE25BE")
st.set_page_config(
    page_title="🦸🏼‍♀️ semantha® Daniel Jung Mathe Suche", page_icon="favicon.png"
)
# display a title
im, title = st.columns(2)
im.image(
    "https://www.semantha.de/wp-content/uploads/Semantha-positiv-RGB.png",
    use_column_width="always",
)
title.title("semantha® Daniel Jung Mathe Suche")
# display a description of your app
st.write(
    "Gib deine Mathefrage ein und ich werde Dir eine passende Stelle von einem Daniel Jung Video anzeigen."
)
# display a search input
search_string = st.text_input(
    label="Suche", value="Wie kann man Brüche erweitern?", label_visibility="collapsed"
)


with st.sidebar:
    st.title("Weitere Wissensquellen")
    st.write("👥 [Matheforum](https://de.wikipedia.org/wiki/Quadratur_des_Kreises)")
    st.write(
        "📚 [Matheskript](https://de.wikipedia.org/wiki/Gro%C3%9Fer_Fermatscher_Satz)"
    )

    st.write("")
    level = st.radio(
        "Welches Leistungsniveau bist Du?", ["Sekundarstufe I", "Sekundarstufe II"]
    )
    if level == "Sekundarstufe I":
        tags = "base"
    else:
        tags = "base,11"
    st.write("")
    debug = st.checkbox("🐞 Debug Mode", value=False)

    if debug:
        mode = st.radio(
            "Retrieval Mode:", ["document_fingerprint", "fingerprint"],
            index=0
        )
        sentence_filter_size = st.slider("max sentences", min_value=0, max_value=100, value=5)
        document_filter_size = st.slider("video filter size", min_value=0, max_value=100, value=3)
    else:
        mode = "document_fingerprint"
        document_filter_size = 5
        sentence_filter_size = 3

_, _, col, _, _ = st.columns(5)
if col.button("🔍 Suche"):
    with st.spinner("🦸🏼‍♀️ Ich suche ein passendes Video..."):
        results = semantha.query_library(
            search_string,
            mode=mode,
            tags=tags,
            document_filter_size=document_filter_size,
            sentence_filter_size=sentence_filter_size
        )
        if results.empty:
            st.error("🦸🏼‍♀️ Ich konnte leider kein passendes Video finden.")
        else:
            st.success("Gefunden! Hier ist dein Ergebnis!", icon="🦸🏼‍♀️")
            st.session_state["tabs"] = ["Video #1"]

            for i, row in results.iterrows():
                if i >= 2:
                    st.session_state["tabs"].append(f"Video #{i}")

            tabs = st.tabs(st.session_state["tabs"])
            for i, row in results.iterrows():
                results.at[i, "Metadata"] = ast.literal_eval(row["Metadata"])
                video_id = results.at[i, "Metadata"]["id"]
                start = results.at[i, "Metadata"]["start"]
                content = results.at[i, "Content"]
                category = results.at[i, "Tags"]
                category = [tag for tag in category if tag not in ["base", "11"]]
                category = ", ".join(category)
                with tabs[i - 1]:
                    st.write(f'Daniel sagt: "{content}..."')
                    st.write(f"🏷️ Tags: {category}")
                    st.video(video_id, start_time=start)
            if debug:
                with st.expander("Ergebnisse", expanded=False):
                    st.write(results)
