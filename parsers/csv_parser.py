# -*- coding:utf-8 -*-
# @FileName  : csv_parser.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : csv文件处理

import tiktoken
import pandas as pd

"""
csv文件 分词器
question：问题 answer：答案 summarized：问题+答案 token：分词长度
"""


def tokenlizer_csv(file_root: str) -> pd.DataFrame:
    embedding_encoding = "cl100k_base"
    encoding = tiktoken.get_encoding(embedding_encoding)

    df = pd.read_csv(file_root)
    df = df[["question", "answer"]]
    df["summary"] = ("question: " + df.question.str.strip() + "; answer: " + df.answer.str.strip())

    df["tokens"] = df.summary.apply(lambda x: len(encoding.encode(x)))
    return df
