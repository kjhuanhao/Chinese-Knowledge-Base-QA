# -*- coding:utf-8 -*-
# @FileName  : embedding_vector.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 向量化数据


import pandas as pd
from typing import List
from text2vec import SentenceModel
from common.pinecone_client import PineconeClient
from pandas import DataFrame

class EmbeddingsVectorTool:

    # 获取某个文本的向量数据
    @staticmethod
    def get_text_embedding(text):
        print(text)
        model = SentenceModel("./text2vec-base-chinese")
        embeddings = model.encode(text)
        return embeddings.tolist()

    # 获取dataFrame的向量数据
    def get_df_embedding(self, df: pd.DataFrame) -> List:
        df_embedding = {idx: self.get_text_embedding(r.summary) for idx, r in df.iterrows()}
        vectors = []
        count = 0
        for embed_index in df_embedding:
            var = {
                "id": str(count),
                "values": df_embedding[embed_index],
            }
            vectors.append(var)
            count += 1
        return vectors

    # 与问题匹配相似度
    def get_query_with_similarity(
            self, query: str, df: DataFrame
    ) -> List:
        query_embedding = self.get_text_embedding(query)
        pinecone_client = PineconeClient()
        ids = pinecone_client.search(query_embedding=query_embedding)
        items = []
        for _ in ids:
            items.append(df.iloc[_].to_dict())
        return items