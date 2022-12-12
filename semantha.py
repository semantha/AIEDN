import json
from typing import Dict

import requests
from requests import Response
import pandas as pd
import streamlit as st


class SemanthaConnectionException(Exception):
    """SemanthaConnectionException"""


def _build_headers_for_json_request(api_key) -> Dict[str, str]:
    __headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    return __headers


class Semantha:
    def __init__(self):
        self.__server_base_url = st.secrets['semantha']['base_url']
        self.__api_key = st.secrets['semantha']['api_key']
        self.__domain = st.secrets['semantha']['domain']

    def query_library(self, text: str, threshold=0.4, max_references=1, tags=None):
        url = f"{self.__server_base_url}/api/domains/{self.__domain}/references?maxreferences={max_references}"
        headers = _build_headers_for_json_request(self.__api_key)
        payload = {
            'text': text,
            'similaritythreshold': str(threshold),
            'withcontext': str(False)
        }
        if tags is not None:
            payload['tags'] = tags
        response = requests.post(url, headers=headers, files=payload)
        if response.status_code != 200:
            print(response)
            return {}
        json_response = json.loads(response.content.decode())
        result_dict = {}
        if 'references' in json_response:
            for ref in json_response['references']:
                result_dict[ref['documentId']] = {
                    "doc_name": self.__get_ref_doc_name(ref['documentId'], self.__domain),
                    "content": self.__get_document_content(ref['documentId'], self.__domain),
                    "similarity": float(ref['similarity']),
                    "metadata": self.__get_ref_doc_metadata(ref['documentId'], self.__domain)
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
        response = self.__get_ref_doc(doc_id, domain)
        json_response = json.loads(response.content.decode())
        content = ""
        if "pages" in json_response:
            for page in json_response["pages"]:
                for c in page["contents"]:
                    if "paragraphs" in c:
                        content += "\n".join([par["text"] for par in c["paragraphs"]])
        else:
            return ""
        return content

    def __get_ref_doc_name(self, doc_id: str, domain: str) -> str:
        response = self.__get_ref_doc(doc_id, domain)
        json_response = json.loads(response.content.decode())
        return json_response['name']

    def __get_ref_doc_metadata(self, doc_id: str, domain: str) -> str:
        response = self.__get_ref_doc(doc_id, domain)
        json_response = json.loads(response.content.decode())
        return json_response['metadata']
    
    def __get_ref_doc(self, doc_id: str, domain: str) -> Response:
        url = f"{self.__server_base_url}/api/domains/{domain}/referencedocuments/"
        headers = _build_headers_for_json_request(self.__api_key)
        response = requests.get(url + doc_id, headers=headers)
        if response.status_code != 200:
            raise SemanthaConnectionException(f"Unable to fetch document from Semantha.\n"
                                              f"Doc id is: {doc_id}\n"
                                              f"Status code is: {response.status_code}")
        return response