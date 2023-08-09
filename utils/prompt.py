# -*- coding:utf-8 -*-
# @FileName  : prompt.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 构建prompt

import tiktoken
from utils.vectors_client import VectorsClient
from typing import Dict


class PromptTool:

    def create_prompt(self, question) -> Dict[str, str]:
        question_tokens = self.get_tokens(question)

        vectors_client = VectorsClient()
        similarities_documents = vectors_client.similarity_search(question)

        reference_documents = ""
        tokens = question_tokens
        documents_tokens = [self.get_tokens(doc) for doc in similarities_documents]

        for i in range(len(similarities_documents)):
            if tokens + documents_tokens[i] > 3850:
                break
            reference_documents += f"\n{similarities_documents[i]}"
            tokens += documents_tokens[i]

        header = f""" 你是一个文档查询助手，你的任务是根据一段参考文本，回答我的问题，如果我的问题和参考文本无关，请回复：对不起，知识库中无此相关答案"""

        prompt = header + "\n参考文本:\n" + f"'''{reference_documents}'''" + f"\n我的问题是: {question}"
        print(prompt)
        return {
            "prompt": prompt,
            "documents": reference_documents
        }

    @staticmethod
    def get_tokens(text) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        token_integers = encoding.encode(text)
        tokens = len(token_integers)
        return tokens
