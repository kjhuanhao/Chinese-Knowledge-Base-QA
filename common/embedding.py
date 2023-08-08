# -*- coding:utf-8 -*-
# @FileName  : embedding.py
# @Time      : 2023/8/8
# @Author    : LaiJiahao
# @Desc      : M3E嵌入模型

from sentence_transformers import SentenceTransformer
from loguru import logger
from numpy import ndarray


class EmbeddingModel:
    embedding_model_name = "m3e-base"
    model = SentenceTransformer(embedding_model_name)

    def get_embedding(self, sentence: str) -> ndarray:
        return self.model.encode(sentence).tolist()
