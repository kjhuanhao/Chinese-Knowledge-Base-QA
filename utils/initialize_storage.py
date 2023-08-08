# -*- coding:utf-8 -*-
# @FileName  : initialize_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 将data文件夹中的文件进行向量化

from utils.vectors_client import VectorsClient
from common.status_code import HttpStatusCode
from typing import Dict


class Storage:

    def __init__(self, file_root: str):
        self._file_root = file_root

    def initialize(self) -> Dict:

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
