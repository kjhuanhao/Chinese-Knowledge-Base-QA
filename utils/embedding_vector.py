# -*- coding:utf-8 -*-
# @FileName  : embedding_vector.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 向量化数据

import numpy as np
import pandas as pd
import openai

from typing import Dict, List, Tuple
from numpy import ndarray
from common.dynamic_module import dynamic_key, dynamic_proxy


class EmbeddingsVectorTool:

    # 获取某个文本的向量数据
    @staticmethod
    def get_text_embedding(text, embedding_mode='text-embedding-ada-002'):
        proxy = dynamic_proxy()
        api_key = dynamic_key()
        result = openai.Embedding.create(
            model=embedding_mode,
            input=text,
            api_base=proxy,
            api_key=api_key
        )
        return result['data'][0]['embedding']

    # 计算相似度
    @staticmethod
    def calculate_vector_similarity(x: List[float], y: List[float]) -> ndarray:
        return np.dot(np.array(x), np.array(y))

    # 获取dataFrame的向量数据
    def get_df_embedding(self, df: pd.DataFrame):
        return {idx: self.get_text_embedding(r.summarized) for idx, r in df.iterrows()}

    # 与问题匹配相似度
    def get_docs_with_similarity(self, query: str, df_embedding: Dict[Tuple[str, str], np.array]) -> List[
        Tuple[float, Tuple[str, str]]]:
        query_embedding = self.get_text_embedding(query)

        document_similarities = sorted(
            [
                (self.calculate_vector_similarity(query_embedding, doc_embedding), doc_index) for
                doc_index, doc_embedding in
                df_embedding.items()

            ], reverse=True)
        return document_similarities
