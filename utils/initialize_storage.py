# -*- coding:utf-8 -*-
# @FileName  : initialize_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 将data文件夹中的文件进行向量化

from utils.vectors_client import VectorsClient
from common.status_code import HttpStatusCode
from typing import Dict
from utils.files_parser import FileParser


class Storage:

    @staticmethod
    def initialize(filename, file_type) -> Dict:
        """
        初始化向量数据库
        :param filename: 文件名称
        :param file_type: 文件类型
        :return:
        """
        file_parser = FileParser()
        vectors_client = VectorsClient()

        documents = file_parser.load(filename, file_type)
        result = vectors_client.add(documents)

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
