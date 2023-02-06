import re
from collections import defaultdict
from dataclasses import dataclass

import pandas as pd
import streamlit as st

import semantha_sdk
from semantha_sdk.model import Document

def get_sentences(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

def merge_sentences(lib: pd.DataFrame) -> pd.DataFrame:
    lib["Name"] = lib["Name"].apply(lambda name: re.split("_[0-9]+"[0]))
    merge = defaultdict(lambda: "")
    for sentence in sentences:
        merge[sentence.title] += sentence.text
    return pd.DataFrame({"title": merge.keys(), "content": merge.values()})



@dataclass
class Sentence:
    _semantha_document: Document

    @property
    def text(self):
        content = ""
        for p in self._semantha_document.pages:
            for c in p.contents:
                content += "\n".join([par.text for par in c.paragraphs])
        return content

    @property
    def title(self):
        return re.split("_[0-9]+", self._semantha_document.name)[0]


def access_endpoint():
    print("access endpoint")
    api = semantha_sdk.login(
        server_url=st.secrets["semantha"]["base_url"],
        key=st.secrets["semantha"]["api_key"]
    )
    domain = api.domains.get_one(st.secrets["semantha"]["domain"])
    print("got domain")
    return domain.reference_documents

def get_sentences():
    endpoint = access_endpoint()
    documents = endpoint.get_all().documents
    print("got documents")
    for document in documents:
        print("yield")
        yield Sentence(endpoint.get_one(document.id))
#    return [Sentence(endpoint.get_one(document.id)) for document in documents]

def get_metadata() -> str:
    return "pass"

def create_transcripts(sentences: list[Sentence]) -> pd.DataFrame:
    print("merging sentences")
    merge = defaultdict(lambda: "")
    for sentence in sentences:
        print(sentence)
        merge[sentence.title] += sentence.text
    return pd.DataFrame({"title": merge.keys(), "content": merge.values()})

def augment(transcripts: pd.DataFrame, metadata) -> pd.DataFrame:
    pass

def create_library(transcripts: pd.DataFrame):
    transcripts.to_excel("transcripts.xlsx")


if __name__ == "__main__":
    sentences, metadata = get_sentences(), get_metadata()
    transcripts = create_transcripts(sentences)
    transcripts = augment(transcripts, metadata)
    create_library(transcripts)
