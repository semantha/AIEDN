import ast
import io
from itertools import filterfalse

import pandas as pd
import semantha_sdk
import streamlit as st
from semantha_sdk.model.document import Document


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

    def query_library(self, text: str, tags: str, threshold=0.4, max_references=5,  mode="document_fingerprint",
                      document_filter_size: int = 5, sentence_filter_size: int = 5):
        sentence_references = self.__sdk.domains(self.__domain).references.post(
            file=_to_text_file(text),
            similarity_threshold=threshold,
            max_references=sentence_filter_size,
            with_context=False,
            tags="+".join(["SENTENCE_LEVEL"] + [tags]),
            mode="fingerprint"
        ).references

        if mode == "document_fingerprint":
            video_references = self.__sdk.domains(self.__domain).references.post(
                file=_to_text_file(text),
                similarity_threshold=threshold,
                max_references=document_filter_size,
                with_context=False,
                tags="+".join(["TRANSCRIPT_LEVEL"] + [tags]),
                mode="document"
            ).references

            # Print video matches for debugging purposes
            # print(f"videos: {[self.__get_ref_doc(ref.document_id, self.__domain).name for ref in video_references]}")

            video_ids = [self.__parse("id", c) for c in video_references]
            sentence_references[:] = filterfalse(
                lambda sentence: self.__parse("id", sentence) not in video_ids,
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
        return self.__sdk.domains(domain).reference_documents(doc_id).get()

    def __parse(self, key, document):
        from urllib.parse import urlparse, parse_qs
        document = self.__get_ref_doc(document.document_id, self.__domain)
        value = ast.literal_eval(document.metadata)[key]
        if key == "id":
            # parse id from youtube url
            parse_result = urlparse(value)
            query_params = parse_qs(parse_result.query)
            return query_params["v"][0]
