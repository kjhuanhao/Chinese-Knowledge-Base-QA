# -*- coding:utf-8 -*-
# @FileName  : prompt.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 构建prompt

import tiktoken
import pandas as pd
from utils.embedding_vector import EmbeddingsVectorTool


class PromptTool:
    def __init__(self, question: str, df: pd.DataFrame):
        self.question = question
        self.df = df

    # 创建一个prompt
    def create_prompt(self) -> dict:
        encoding = tiktoken.get_encoding("gpt2")
        separator_len = len(encoding.encode("\n* "))
        vector = EmbeddingsVectorTool()

        relevant_sections = vector.get_query_with_similarity(self.question, self.df)

        chosen_sections = []
        chosen_sections_len = 0
        possibility_questions = []

        # example {'question': '有晨跑吗？', 'answer': '没有', 'summarized': 'question: 有晨跑吗？; answer: 没有', 'tokens': 18}
        for item in relevant_sections:
            chosen_sections_len += item.get("tokens") + separator_len
            if chosen_sections_len > 1000:
                break

            chosen_sections.append("\n* " + item.get("summary").replace("\n", ""))

            if len(possibility_questions) < 3:
                possibility_questions.append(item.get("question"))

        possibility_question = ""
        count = 1

        for p in possibility_questions:
            possibility_question += str(count) + ". " + p + "\n"
            count += 1

        header = f""" Choose the semantic meaning of the text below to answer my question. If the question is unrelated to the text below, you must reply the identifier: NO" """
        prompt = header + "".join(chosen_sections) + "\n\n Q: " + self.question + "\n A:"
        build_prompt = {"prompt": prompt, "possibility_question": possibility_question}
        print(build_prompt)
        return build_prompt
