# -*- coding:utf-8 -*-
# @FileName  : vectors_client.py
# @Time      : 2023/8/8
# @Author    : LaiJiahao
# @Desc      : Chroma向量数据库客户端

import uuid
import chromadb

from concurrent.futures import ThreadPoolExecutor
from common.embedding import EmbeddingModel
from typing import List
from loguru import logger
from langchain.docstore.document import Document


class VectorsClient:
    _collection_name = "chinese_qa"

    def __init__(self):
        self._client = chromadb.PersistentClient(path="db")
        self._collection = self._client.get_or_create_collection(
            name="collection_name",
            metadata={"hnsw:space": "cosine"}  # l2 is the default
        )

    def add(self, documents: List[Document]):
        """
        向量数据库添加文档
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
            document = texts[i]
            meta_data = meta_datas[i]
            self._collection.add(
                ids=id_,
                embeddings=embedding,
                documents=document,
                metadatas=meta_data
            )
            # data = {
            #     "id": id_,
            #     "text": texts[i],
            #     "embedding": embedding,
            #     "metadata": meta_datas[i]
            # }
            # self._client.set(self._collection_name + f":{id_}", data)
            logger.info("embed data: " + str(i + 1))

        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(len(documents)):
                executor.submit(process_document, i)

        logger.info("向量数据库存入完成")
        return True

    def reset(self) -> str:
        """
        重置向量数据库
        """
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(self._collection_name)
        return "重置成功"

    def similarity_search(self, query: str, top_k: int = 5):
        """
        向量数据库相似度余弦搜索
        :param query: 询问语句
        :param top_k: 返回的相似文本数量
        :return: 相似性文本的列表
        """

        embedding_model = EmbeddingModel()
        query_embedding = embedding_model.get_embedding(query)
        results = self._collection.query(query_embedding, n_results=top_k)

        return results["documents"][0]
