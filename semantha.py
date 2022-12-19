import io

import pandas as pd
import streamlit as st

import semantha_sdk
from semantha_sdk.model.Document import Document

def _to_text_file(text: str):
    input_file = io.BytesIO(text.encode("utf-8"))
    input_file.name = "input.txt"
    return input_file
class Semantha:
    def __init__(self):
        self.__server_base_url = st.secrets['semantha']['base_url']
        self.__api_key = st.secrets['semantha']['api_key']
        self.__domain = st.secrets['semantha']['domain']
        self.__sdk = semantha_sdk.login(self.__server_base_url, self.__api_key)

    def query_library(self, text: str, threshold=0.4, max_references=1, tags=None):
        doc = self.__sdk.domains.get_one(self.__domain).references.post(file=_to_text_file(text),
                                                                 similarity_threshold=threshold,
                                                                 max_references=max_references,
                                                                 with_context=False,
                                                                 tags=tags)
        result_dict = {}
        if doc.references:
            for ref in doc.references:
                result_dict[ref.document_id] = {
                    "doc_name": self.__get_ref_doc_name(ref.document_id, self.__domain),
                    "content": self.__get_document_content(ref.document_id, self.__domain),
                    "similarity": ref.similarity,
                    "metadata": self.__get_ref_doc_metadata(ref.document_id, self.__domain)
                }
        return self.__get_matches(result_dict)

    @staticmethod
    def __get_matches(results):
      matches = pd.DataFrame.from_records(
            [
                [
                    r["doc_name"],
                    r["content"].replace("\n", "<br>"),
                    int(round(r["similarity"], 2) * 100),
                    r["metadata"]
                ]
                for r in list(results.values())
            ],
            columns=["Name", "Content", "Similarity", "Metadata"],
        )
      matches.index = range(1, matches.shape[0] + 1)
      matches.index.name = "Rank"
      return matches

    def __get_document_content(self, doc_id: str, domain: str) -> str:
        doc = self.__get_ref_doc(doc_id, domain)
        content = ""
        for p in doc.pages:
            for c in p.contents:
                content += "\n".join([par.text for par in c.paragraphs])
        return content

    def __get_ref_doc_name(self, doc_id: str, domain: str) -> str:
        return self.__get_ref_doc(doc_id, domain).name

    def __get_ref_doc(self, doc_id: str, domain: str) -> Document:
        return self.__sdk.domains.get_one(domain).reference_documents.get_one(document_id=doc_id)

    def __get_ref_doc_metadata(self, doc_id: str, domain: str) -> str:
        return self.__get_ref_doc(doc_id, domain).metadata
