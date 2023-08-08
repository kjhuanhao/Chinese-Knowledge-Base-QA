# -*- coding:utf-8 -*-
# @FileName  : test.py
# @Time      : 2023/8/8
# @Author    : LaiJiahao
# @Desc      : None

from utils.vectors_client import VectorsClient

vectors_client = VectorsClient()
results = vectors_client.similarity_search("有上床下桌吗")
print(results)