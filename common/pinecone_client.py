# -*- coding:utf-8 -*-
# @FileName  : pinecone_client.py
# @Time      : 2023/7/25
# @Author    : LaiJiahao
# @Desc      : PineCone客户端

import os
import pinecone
from typing import List
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class PineconeClient:
    PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")

    def __init__(self):
        pinecone.init(
            api_key=os.getenv("PINECONE_KEY"),
            environment=os.getenv("PINECONE_ENV")
        )
        self._index = pinecone.Index(os.getenv("PINECONE_INDEX"))

    def insert(self, vectors: List) -> bool:
        delete_result = self._index.delete(delete_all=True, namespace=self.PINECONE_NAMESPACE)
        delete_result = eval(str(delete_result))
        if delete_result:
            return False
        upsert_response = self._index.upsert(vectors=vectors, namespace=PineconeClient.PINECONE_NAMESPACE)
        upsert_response = eval(str(upsert_response))
        print(upsert_response)
        # upsert_result = upsert_response.get("upsertedCount")
        # print(upsert_result)
        # if upsert_result is None:
        #     return False

        return True

    def search(self, query_embedding: List, top_k: int = 6) -> List[int]:
        results = self._index.query(query_embedding, top_k=top_k, namespace=self.PINECONE_NAMESPACE)
        ids = [int(value["id"]) for value in results["matches"]]
        return ids
