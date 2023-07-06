# -*- coding:utf-8 -*-
# @FileName  : prompt.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 构建prompt

import tiktoken
import pandas as pd
from utils.embedding_vector import EmbeddingsVectorTool


class PromptTool:
    def __init__(self, question: str, context_embeddings: dict, df: pd.DataFrame):
        self.question = question
        self.context_embeddings = context_embeddings
        self.df = df

    # 创建一个prompt
    def create_prompt(self) -> dict:
        encoding = tiktoken.get_encoding("gpt2")
        separator_len = len(encoding.encode("\n* "))
        vector = EmbeddingsVectorTool()

        relevant_document_sections = vector.get_docs_with_similarity(self.question, self.context_embeddings)
        chosen_sections = []
        chosen_sections_len = 0
        chosen_sections_indexes = []
        possibility_questions = []

        for _, section_index in relevant_document_sections:
            document_section = self.df.loc[section_index]
            chosen_sections_len += document_section.tokens + separator_len
            if chosen_sections_len > 500:
                break

            chosen_sections.append("\n* " + document_section.summarized.replace("\n", ""))
            if len(possibility_questions) < 3:
                possibility_questions.append(document_section.question)

            chosen_sections_indexes.append(str(section_index))

        possibility_question = ""
        count = 1
        for p in possibility_questions:
            possibility_question += str(count) + ". " + p + "\n"
            count += 1

        header = f""" Choose the semantic meaning of the text below to answer my question. If the question is unrelated to the text below, you must reply the identifier: NO" """
        prompt = header + "".join(chosen_sections) + "\n\n Q: " + self.question + "\n A:"
        build_prompt = {"prompt": prompt, "possibility_question": possibility_question}

        return build_prompt
