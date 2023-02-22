import ast
import io
from abc import abstractmethod
from itertools import filterfalse

import pandas as pd
import semantha_sdk
import streamlit as st
from semantha_sdk.model.document import Document


def _to_text_file(text: str):
    input_file = io.BytesIO(text.encode("utf-8"))
    input_file.name = "input.txt"
    return input_file


class RankingStrategy:

    def __init__(self, semantha):
        self._semantha = semantha

    @abstractmethod
    def rank(self, sentence_references, video_references=None) -> list:
        raise NotImplementedError("Abstract method")


class DenseOnlyRanking(RankingStrategy):

    def rank(self, sentence_references, video_references=None) -> list:
        return sentence_references


class SparseFilterDenseRanking(RankingStrategy):

    def rank(self, sentence_references, video_references=None) -> list:
        if video_references is None:
            return sentence_references
        else:
            video_ids = [self._semantha.parse("id", c) for c in video_references]
            sentence_references[:] = filterfalse(
                lambda sentence: self._semantha.parse("id", sentence) not in video_ids,
                sentence_references
            )
            return sentence_references


class HybridRanking(RankingStrategy):

    def rank(self, sentence_references, video_references=None) -> list:
        pass


class Semantha:
    def __init__(self):
        semantha_secrets = st.secrets["semantha"]
        self.__sdk = semantha_sdk.login(
            server_url=semantha_secrets["base_url"],
            key=semantha_secrets["api_key"],
        )
        self.__domain = semantha_secrets["domain"]
        self.__tracking_domain = semantha_secrets.get("tracking_domain", default=None)

    def query_library(self,
                      text: str,
                      tags: str,
                      threshold: float = 0.4,
                      max_matches: int = 5,
                      ranking_strategy: RankingStrategy.__class__ = DenseOnlyRanking,
                      sparse_filter_size: int = 5):
        if st.session_state.control:
            sentence_references = self.__get_sentence_refs_control(text, tags, threshold, max_matches)
        else:
            sentence_references = self.__get_sentence_refs_aiedn(text, tags, threshold, max_matches)

            video_references = None
            if ranking_strategy is SparseFilterDenseRanking or ranking_strategy is HybridRanking:
                video_references = self.__get_video_refs_aiedn(text, tags, sparse_filter_size)

            ranker = ranking_strategy(self)
            sentence_references = ranker.rank(sentence_references, video_references)

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
                "tags": set(self.__get_ref_doc(candidate.document_id, self.__domain).tags) - {"TRANSCRIPT_LEVEL", "SENTENCE_LEVEL", "CONTROL"},
            }

        return self.__get_matches(result_dict)

    def __get_sentence_refs_control(self, text: str, tags: str, threshold: float, max_matches: int):
        return self.__sdk.domains(self.__domain).references.post(
                file=_to_text_file(text),
                similarity_threshold=threshold,
                max_references=max_matches,
                with_context=False,
                tags="+".join(["CONTROL"] + [tags]),
                mode="document"
            ).references

    def __get_sentence_refs_aiedn(self, text: str, tags: str, threshold: float, max_matches: int):
        return self.__sdk.domains(self.__domain).references.post(
                file=_to_text_file(text),
                similarity_threshold=threshold,
                max_references=max_matches,
                with_context=False,
                tags="+".join(["SENTENCE_LEVEL"] + [tags]),
                mode="fingerprint"
            ).references

    def __get_video_refs_aiedn(self, text: str, tags: str, sparse_filter_size: int):
        return self.__sdk.domains(self.__domain).references.post(
                    file=_to_text_file(text),
                    max_references=sparse_filter_size,
                    with_context=False,
                    tags="+".join(["TRANSCRIPT_LEVEL"] + [tags]),
                    mode="document"
                ).references

    def add_to_library(self, content: str, tag: str) -> None:
        if not self.__tracking_domain:
            return
        self.__sdk.domains(self.__tracking_domain).reference_documents.post(file=_to_text_file(content), tags=tag)

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

    def parse(self, key, document):
        from urllib.parse import urlparse, parse_qs
        document = self.__get_ref_doc(document.document_id, self.__domain)
        value = ast.literal_eval(document.metadata)[key]
        if key == "id":
            # parse id from youtube url
            parse_result = urlparse(value)
            query_params = parse_qs(parse_result.query)
            return query_params["v"][0]
