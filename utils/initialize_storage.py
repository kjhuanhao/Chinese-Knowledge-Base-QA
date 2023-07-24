# -*- coding:utf-8 -*-
# @FileName  : initialize_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 初始化csv向量数据，存入redis

import pinecone
import os
from utils.embedding_vector import EmbeddingsVectorTool
from parsers.csv_parser import tokenlizer_csv
from common.status_code import HttpStatusCode
from typing import Dict
from common.pinecone_client import PineconeClient

class Storage:

    def __init__(self, file_root: str):
        self._file_root = file_root
        self._embedding_vector_tool = EmbeddingsVectorTool()

    def initialize(self) -> Dict:
        pinecone_client = PineconeClient()
        df = tokenlizer_csv(self._file_root)
        vectors = self._embedding_vector_tool.get_df_embedding(df)
        result = pinecone_client.insert(vectors=vectors)

        if result:
            return {
                "code": HttpStatusCode.SUCCESS.value,
                "data": "初始化成功",
            }
        else:
            return {
                "code": HttpStatusCode.SERVER_ERROR.value,
                "msg": "初始化失败",
            }

