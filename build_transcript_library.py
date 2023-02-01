import re
import os
from collections import defaultdict

import streamlit as st
from tqdm import tqdm
import semantha_sdk


def get_domain():
    api = semantha_sdk.login(
        server_url=st.secrets["semantha"]["base_url"],
        key=st.secrets["semantha"]["api_key"]
    )
    return api.domains.get_one(st.secrets["semantha"]["domain"])

def get_documents():
    endpoint = get_domain().reference_documents
    infos = endpoint.get_all().documents
    for info in infos:
        yield endpoint.get_one(info.id)

def get_content(document) -> str:
    content = ""
    for p in document.pages:
        for c in p.contents:
            content += "\n".join([par.text for par in c.paragraphs])
    return content

def get_library_size() -> int:
    endpoint = get_domain().reference_documents
    statistics = endpoint.get_statistic()
    return statistics.library_size

def merge_contents() -> dir[str, str]:
    transcripts = defaultdict(lambda: "")
    for document in tqdm(get_documents(), total=get_library_size()):
        video_title = re.split("_[0-9]+", document.name)[0]
        transcripts[video_title] += get_content(document)
    return transcripts

def dump_transcripts(transcripts: dir) -> None:
    os.makedirs("transcripts", exist_ok=True)
    for title, contents in transcripts.items():
        with os.open(f"transcripts\\{title}", "w") as file:
            file.write(contents)






if __name__ == "__main__":
    from pprint import pprint
    transcripts = merge_contents()
    pprint(transcripts)
