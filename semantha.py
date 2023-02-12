import ast
import io
from functools import partial
from itertools import filterfalse
from operator import contains

import pandas as pd
import semantha_sdk
import streamlit as st
from semantha_sdk.model.Document import Document


def _to_text_file(text: str):
    input_file = io.BytesIO(text.encode("utf-8"))
    input_file.name = "input.txt"
    return input_file




class Semantha:
    def __init__(self):
        self.__sdk = semantha_sdk.login(
            server_url=st.secrets["semantha"]["base_url"],
            key=st.secrets["semantha"]["api_key"],
        )
        self.__domain = st.secrets["semantha"]["domain"]

    def query_library(self, text: str, threshold=0.4, max_references=5, tags=[], mode="document_fingerprint"):
        if tags:
            raise NotImplementedError(f"Received tags to filter by ({tags}), but we need the single tag the API allows for.")

        sentence_references = self.__sdk.domains.get_one(self.__domain).references.post(
            file=_to_text_file(text),
            similarity_threshold=threshold,
            max_references=max_references,
            with_context=False,
            # TODO: tags=["SENTENCE_LEVEL"] + tags,
            tags="SENTENCE_LEVEL",
            mode="fingerprint"
        ).references

        if mode == "document_fingerprint":
            video_references = self.__sdk.domains.get_one(self.__domain).references.post(
                file=_to_text_file(text),
                similarity_threshold=threshold,
                max_references=5,
                with_context=False,
                tags="TRANSCRIPT_LEVEL",
                mode="document"
            ).references

            video_reference_urls = [self.__parse("id", c) for c in video_references]
            sentence_references[:] = filterfalse(
                lambda sentence: self.__parse("id", sentence) in video_reference_urls,
                sentence_references
            )

        result_dict = {}
        for candidate in sentence_references:
            result_dict[candidate.document_id] = {
                "doc_name": self.__get_ref_doc(candidate.document_id, self.__domain).name,
                "content": self.__get_document_content(
                    candidate.document_id, self.__domain
                ),
                "similarity": candidate.similarity,
                "metadata": self.__get_ref_doc(
                    candidate.document_id, self.__domain
                ).metadata,
                "tags": set(self.__get_ref_doc(candidate.document_id, self.__domain).tags) - {"TRANSCRIPT_LEVEL", "SENTENCE_LEVEL"},
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
                    r["metadata"],
                    r["tags"],
                ]
                for r in list(results.values())
            ],
            columns=["Name", "Content", "Similarity", "Metadata", "Tags"],
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

    def __get_ref_doc(self, doc_id: str, domain: str) -> Document:
        return self.__sdk.domains.get_one(domain).reference_documents.get_one(
            document_id=doc_id
        )

    def __parse(self, key, document):
        document = self.__get_ref_doc(document.document_id, self.__domain)
        return ast.literal_eval(document.metadata)[key]
