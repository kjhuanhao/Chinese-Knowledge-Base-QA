# -*- coding:utf-8 -*-
# @FileName  : status_code.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 状态码管理

from enum import Enum


class HttpStatusCode(Enum):
    SUCCESS = 200
    SERVER_ERROR = 500

    def __str__(self):
        return str(self.value)
