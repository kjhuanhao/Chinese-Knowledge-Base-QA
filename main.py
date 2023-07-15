import uvicorn
import os

from fastapi import Body, UploadFile, FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from utils.initialize_storage import Storage
from common.status_code import HttpStatusCode
from common.api_status_manage import ApiStatusManagement
from service.openai_service import call_openai

app = FastAPI()


# 初始化接口
@app.post("/initialize")
def initialize():
    storage = Storage(file_root='data/' + os.getenv("CSV_FILE_NAME"))
    return JSONResponse(storage.initialize())


# 询问接口
@app.post("/ask")
def ask(body: dict):
    return StreamingResponse(call_openai(body['question']), media_type='text/event-stream')


# api_key状态管理接口
@app.get("/api_key/valid")
def api_key_management():
    try:
        data = ApiStatusManagement.get_billing()
        return JSONResponse(
            {
                "code": HttpStatusCode.SUCCESS.value,
                "data": data
            }
        )
    except Exception as e:
        return JSONResponse(
            {
                "code": HttpStatusCode.SERVER_ERROR.value,
                "msg": "服务器出错",
                "error": e
            }
        )


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
    return JSONResponse(status_code=500, content={"code": HttpStatusCode.SERVER_ERROR.value, "msg": str(exc)})


# api_key欠费接口
@app.get("/api_key/invalid")
def owe():
    return JSONResponse({
        "code": HttpStatusCode.SUCCESS.value, "data": ApiStatusManagement().get_invalid_api_keys()
    })


# 删除apikey接口
@app.post("/api_key/delete_api_key")
def delete_api_key(emails_list: list[str] = Body(embed=True)):
    return JSONResponse(ApiStatusManagement().delete_api_keys(emails_list))


@app.get("/")
async def homepage():
    return "test"


if __name__ == "__main__":
    uvicorn.run(host="127.0.0.1", port=8000, app=app)
