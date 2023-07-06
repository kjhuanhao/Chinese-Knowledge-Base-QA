# -*- coding:utf-8 -*-
# @FileName  : initialize_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 初始化csv向量数据，存入redis
import os
from utils.embedding_vector import EmbeddingsVectorTool
from utils.redis_storage import RedisTool
from parsers.csv_parser import tokenlizer_csv
from common.status_code import HttpStatusCode


class Storage:
    def __init__(self, file_root: str):
        self.file_root = file_root
        self.embedding_vector_tool = EmbeddingsVectorTool()

    def initialize(self) -> dict:
        """
        将csv文件中的向量数据存入redis
        :return:
        """
        df = tokenlizer_csv(self.file_root)
        df_embedding = self.embedding_vector_tool.get_df_embedding(df)
        redis_tool = RedisTool()
        redis_tool.set(os.getenv("REDIS_CSV_NAME"), str(df_embedding))
        vector_data = redis_tool.get(os.getenv("REDIS_CSV_NAME"))

        if vector_data is not None:
            return {
                "code": HttpStatusCode.SUCCESS.value,
                "data": "初始化成功",
            }
        else:
            return {
                "code": HttpStatusCode.SERVER_ERROR.value,
                "msg": "初始化失败",
            }
# Storage('../common/wt.csv').initialize()
