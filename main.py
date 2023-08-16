import uvicorn
import os

from typing import Dict
from fastapi import Body, UploadFile, FastAPI, WebSocket
from fastapi.responses import JSONResponse
from common.status_code import HttpStatusCode
from utils.api_status_manage import ApiStatusManagement
from service.openai_service import call_openai
from fastapi.middleware.cors import CORSMiddleware
from utils.initialize_storage import Storage
from loguru import logger

app = FastAPI()

# 配置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许发送凭据 (如 cookies)
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头部
)

connected_websockets = set()


# 初始化接口
@app.post("/initialize")
def initialize(body: Dict[str, str]):
    storage = Storage()
    result = storage.initialize(body["filename"], body["file_type"])
    return result


# 询问接口
@app.websocket("/ask")
async def ask(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            if data:
                logger.info("收到信息" + data)
                async for content in call_openai(data):
                    await websocket.send_text(content)
                break
    finally:
        await websocket.close()


# api_key添加接口
@app.post("/api_key/add")
def add_api_key(api_key: list[dict[str, str]] = Body(embed=True)):
    return JSONResponse(ApiStatusManagement().add_api_key(api_key))


# 上传文件接口
@app.post("/upload_file/")
async def create_upload_file(file: UploadFile):
    fn = file.filename
    save_path = f'./data/'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_file = os.path.join(save_path, fn)
    f = open(save_file, 'wb')
    data = await file.read()
    f.write(data)
    f.close()

    return JSONResponse(
        {
            "code": HttpStatusCode.SUCCESS.value,
            "data": "上传成功",
        }
    )


# 全局异常处理
@app.exception_handler(Exception)
async def handle_exception(request, exc):
    return JSONResponse(status_code=500, content={"code": HttpStatusCode.ERROR.value, "msg": str(exc)})


# 删除apikey接口
@app.post("/api_key/delete_api_key")
def delete_api_key(emails_list: list[str] = Body(embed=True)):
    return JSONResponse(ApiStatusManagement().delete_api_keys(emails_list))


# 获取所有apikey接口
@app.get("/api_key/get_all_api_keys")
def get_all_api_keys():
    return JSONResponse(ApiStatusManagement().get_all_api_keys())


@app.get("/")
async def homepage():
    return "test"


if __name__ == "__main__":
    if not os.path.isfile(".env"):
        raise RuntimeError("请先配置.env文件")
    uvicorn.run(host="127.0.0.1", port=8000, app=app)
