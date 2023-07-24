# -*- coding:utf-8 -*-
# @FileName  : openai_service.py
# @Time      : 2023/7/6
# @Author    : LaiJiahao
# @Desc      : 业务模块

import asyncio
import os


from dotenv import load_dotenv
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from parsers import csv_parser
from utils.prompt import PromptTool
from typing import AsyncIterable, Awaitable
from common.dynamic_module import dynamic_key, dynamic_proxy

load_dotenv(verbose=True,override=True)


async def wait_done(fn: Awaitable, event: asyncio.Event):
    try:
        await fn
    except Exception as e:
        print(e)
        event.set()

    finally:
        event.set()


async def call_openai(question: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    df = csv_parser.tokenlizer_csv('data/' + os.getenv("CSV_FILE_NAME"))
    proxy = dynamic_proxy()
    api_key = dynamic_key()

    prompt_tool = PromptTool(question=question, df=df)

    # 智能prompt，根据相似度返回前三个
    build_prompt = prompt_tool.create_prompt()
    prompt = build_prompt['prompt']
    print(prompt)
    possibility_question = build_prompt['possibility_question']

    # print(prompt)

    model = ChatOpenAI(streaming=True,
                       verbose=True,
                       callbacks=[callback],
                       openai_api_key=api_key,
                       model_name="gpt-3.5-turbo",
                       openai_api_base=proxy,
                       max_retries=1)

    coroutine = wait_done(model.agenerate(messages=[[HumanMessage(content=prompt)]]), callback.done)
    task = asyncio.create_task(coroutine)

    async for token in callback.aiter():
        if token == "NO":
            yield f"对不起，您的问题没有在我们的问答库，您可以尝试换个问法，或者提交反馈给我们，如下是相似的问题: \n{possibility_question}"
        else:
            yield f'{token}'

    await task
