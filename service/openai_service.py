# -*- coding:utf-8 -*-
# @FileName  : openai_service.py
# @Time      : 2023/7/6
# @Author    : LaiJiahao
# @Desc      : 业务模块

import json

from dotenv import load_dotenv
from httpx import AsyncClient
from utils.prompt import PromptTool
from utils.dynamic_module import dynamic_key

load_dotenv(verbose=True, override=True)


async def call_openai(question: str):
    url = "https://api.openai.com/v1/chat/completions"
    api_key = dynamic_key()
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    prompt_tool = PromptTool()
    prompt = prompt_tool.create_prompt(question=question)
    send_prompt = prompt["prompt"]

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": send_prompt}],
        "temperature": 0.5,
        "stream": True
    }

    async with AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=data, timeout=20) as response:
            async for line in response.aiter_lines():
                if line.strip() == "":
                    continue
                line = line.replace("data: ", "")
                if line == "[DONE]":
                    return
                data = json.loads(line)
                choices = data.get("choices")
                if choices is None or len(choices) == 0 or choices[0].get("finish_reason") is not None:
                    return
                yield choices[0]["delta"]["content"]


