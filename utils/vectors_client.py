# -*- coding:utf-8 -*-
# @FileName  : vectors_client.py
# @Time      : 2023/8/8
# @Author    : LaiJiahao
# @Desc      : Chroma向量数据库客户端

import uuid
import numpy as np

from concurrent.futures import ThreadPoolExecutor
from common.embedding import EmbeddingModel
from typing import List
from loguru import logger
from langchain.docstore.document import Document
from utils.redis_storage import RedisTool
from similarities import Similarity


class VectorsClient:
    _collection_name = "chinese_qa"

    def __init__(self):
        self._client = RedisTool()

    def add(self, documents: List[Document]):
        """
        向量数据库添加文档
        :param file_name: 文档名称
        :param documents: 使用langchain文档加载器加载的文档
        :return:
        """
        embedding_model = EmbeddingModel()

        texts = [doc.page_content for doc in documents]
        logger.info("正在向量化文本数据")
        # texts_embeddings = [embedding_model.get_embedding(text) for text in texts]

        meta_datas = [doc.metadata for doc in documents]
        ids = [str(uuid.uuid4()) for _ in range(len(documents))]

        logger.info('正在存入向量数据库...')

        # datas = []
        logger.info("总数据大小: " + str(len(documents)))

        def process_document(i):
            id_ = ids[i]
            embedding = embedding_model.get_embedding(texts[i])
            data = {
                "id": id_,
                "text": texts[i],
                "embedding": embedding,
                "metadata": meta_datas[i]
            }
            self._client.set(self._collection_name + f":{id_}", data)
            logger.info("embed data: " + str(i))
            # datas.append(data)

        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(len(documents)):
                executor.submit(process_document, i)

        # collections = self._collection_name + f":{file_name}"
        # self._client.set(collections, datas)

        logger.info("向量数据库存入完成")
        return True

    def reset(self):
        """
        重置向量数据库
        """
        redis_tool = RedisTool()
        keys = redis_tool.get_keys(self._collection_name + ":*")
        redis_tool.delete(keys)

    def similarity_search(self, query: str, top_k: int = 5) -> List:
        """
        向量数据库相似度余弦搜索
        :param query: 询问语句
        :param top_k: 返回的相似文本数量
        :return: 相似性文本的列表
        """
        redis_tool = RedisTool()
        embedding_model = EmbeddingModel()
        collections_key = self._collection_name + ":*"
        collections = redis_tool.get_values(collections_key)
        search = Similarity(model_name_or_path=embedding_model.embedding_model_name)
        query_embedding = embedding_model.get_embedding(query)

        cos_sim_list = []
        for value in collections:
            text_embedding = value["embedding"]
            score = float(np.array(search.score_functions["cos_sim"](query_embedding, text_embedding))[0][0])
            cos_sim_list.append(
                {
                    "text": value["text"],
                    "score": score
                }
            )

        cos_sim_list.sort(key=lambda x: x["score"], reverse=True)

        return cos_sim_list[:top_k]
