import streamlit as st
import ast
from semantha import Semantha


semantha = Semantha()
st.config.set_option("theme.primaryColor", "#BE25BE")
st.set_page_config(page_title='🦸🏼‍♀️ semantha® Daniel Jung Mathe Suche', page_icon='favicon.png')
# display a title
im, title = st.columns(2)
im.image('https://www.semantha.de/wp-content/uploads/Semantha-positiv-RGB.png', use_column_width='always')
title.title('semantha® Daniel Jung Mathe Suche')
# display a description of your app
st.write('Gib deine Mathefrage ein und ich werde Dir eine passende Stelle von einem Daniel Jung Video anzeigen.')
# display a search input
search_string = st.text_input(label="Suche", value="Wie kann man Brüche erweitern?", label_visibility='collapsed')
# design a search button and search semantha® using the methods from above when the button is pressed
# display the results of your search
change_text = """
<style>
div.st-d9 st-ca st-bf st-da st-db {visibility: hidden;}
div.st-d9 st-ca st-bf st-da st-db:before {content: "Wähle deine Themen oder suche in allen Kategorien."; visibility: visible;}
</style>
"""
st.markdown(change_text, unsafe_allow_html=True)
tags = st.multiselect('Wähle deine Themengebiete aus, in denen du suchen möchtest.' ,['Lineare Funktionen', 'Quadratische Funktionen', 'Bruchrechnung', 'Differentialrechnung', 'Polynomfunktionen', 'Bedingte Wahrscheinlichkeit', 'Aussagenlogik/Mengenlehre', 'Taylor-Reihe', 'Reihen', 'Lineare Algebra (Matrizen)'], 'Bruchrechnung')
# level = st.selectbox('Wähle dein Mathe Leistungsniveau', ['Sekundarstufe I', 'Sekundarstufe II', 'Studium'])
# if 'Uneingeschränkt' in tags or tags == []:
#     tags = [level]
# lev_conversion = {'Sekundarstufe I': 'Sek I', 'Sekundarstufe II': 'Sek II', 'Studium': 'Studium'}
# tags = [e.upper() + '+' + lev_conversion[level] for e in tags]
tags = ','.join(tags).upper() if tags else None
_, _, col, _, _ = st.columns(5)
if col.button("🔍 Suche"):
    with st.spinner("🦸🏼‍♀️ Ich suche ein passendes Video..."):
        results = semantha.query_library(search_string, tags=tags) #TODO error handling
        if results.empty:
            st.error("🦸🏼‍♀️ Ich konnte leider kein passendes Video finden.")
        else:
            st.success("Gefunden! Hier ist dein Ergebnis!", icon='🦸🏼‍♀️')
            metadata = ast.literal_eval(results.iloc[0]['Metadata'])
            video_id = metadata['id']
            start = metadata['start']
            st.video(video_id, start_time=start)
            with st.expander("Matches", expanded=False):
                st.write(results)