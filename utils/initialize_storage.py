# -*- coding:utf-8 -*-
# @FileName  : initialize_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 将data文件夹中的文件进行向量化

from utils.vectors_client import VectorsClient
from common.status_code import HttpStatusCode
from utils.files_parser import FileParser


class Storage:

    @staticmethod
    def initialize(filename, file_type):
        """
        初始化向量数据库
        :param filename: 文件名称
        :param file_type: 文件类型
        :return:
        """
        file_parser = FileParser()
        vectors_client = VectorsClient()

        try:
            documents = file_parser.load(filename, file_type)
            result = vectors_client.add(documents)
            return {"code": HttpStatusCode.SUCCESS.value, "msg": "初始化成功", "data": result}
        except Exception as e:
            return {"code": HttpStatusCode.ERROR.value, "msg": "初始化失败", "error": str(e)}


