# Chinese Knowledge Base QA 中文知识库问答

## 介绍
这个项目是一个基于openAI的中文知识库问答系统，可以用于智能客服等场景

## 项目用途
智能客服等要求根据特定文件的中文对话系统

## 项目原理示意图
![pPnnZAe.md.png](https://s1.ax1x.com/2023/08/11/pPnnZAe.md.png)(https://imgse.com/i/pPnnZAe)

## 项目默认支持的文件格式
- docs
- pdf
- md
- csv

## 项目特色
- [x] 由于小程序不支持event-stream，本项目基于websocket实现流式传输的效果，适用更多场景
- [x] 基于openAI的ChatModel`(gpt-3.5-turbo)`
- [x] 支持多个api_key动态更换api_key
- [x] 基于chroma存储向量数据和进行相似度检索，默认的检索方式是余弦搜索
- [x] 支持openAI代理
- [x] ~~实现api_key状态管理，可查询用量余额，基于openAI账号的api_key管理~~
- [x] 运维复杂度低，只需要引入redis数据库，即可快速构建
- [x] 智能问答推荐，实现更加精准的答复
- [x] 使用[M3e-base中文嵌入模型](https://huggingface.co/moka-ai/m3e-base)，召回文档能力更强
- [x] 一键Docker部署
- [ ] 队列问答，解决高并发问题
- [ ] 智能缓存，问题重复下，无需走openAI接口，实现快速响应

> 由于官方的余额查询相关接口鉴权方法更换，现已去除此功能

## 使用说明

### 配置
需要修改`env_template`为`.env`文件，具体参数说明如下：
- OPENAI_API_BASE：openAI代理地址设置，例如：`https://xxxxx.com/v1` ，如果无需使用代理，请留空即可，默认会走官方接口
- EXPIRE_DAYS：所有api_key在redis中的可留存时间，例如：`60` (默认单位为`天数`)
- REDIS_HOST：redis主机地址，例如`127.0.0.1`
- REDIS_PORT：redis端口号，例如：`6379`
- REDIS_PASSWORD：redis密码，没有密码则为空即可
- REDIS_DB：redis数据库，例如：`0`


### 部署运行
#### 直接运行
1. 安装必备模块
```bash
pip install -r requirements.txt
```

2. 安装项目依赖的模型，如果速度慢可以自行下载该模型，在此项目根目录下命名为`m3e-base`，存放模型数据
```bash
git lfs install
git clone https://huggingface.co/moka-ai/m3e-base
```

3. fastapi使用的是`uvicorn`，本项目`app.py`直接运行即可
```bash
python3 main.py
```

#### Docker部署
1. 下载本项目代码
```shell
git clone https://github.com/kjhuanhao/Chinese-Knowledge-Base-QA.git
```

2. 安装项目依赖的模型，如果速度慢可以自行下载该模型，在此项目根目录下命名为`m3e-base`，存放模型数据
```bash
git lfs install
git clone https://huggingface.co/moka-ai/m3e-base
```

3. 构建镜像
自行修改`<>`中的内容
```shell
docker build -t <your_images_tag> Chinese-Knowledge-Base-QA/
```

4. 运行容器
自行修改`<>`中的内容
```shell
docker run -id -p 13010:8000 --name <your_container_name> -v $PWD/db:/root/chineseQA <your_images_tag>
```


## 相关接口

### 1. 初始化接口
在使用之前需要初始化你的文件，在初始化过程中，会获取相关的embeddings然后存储到本地的chroma向量数据库，会创建一个db文件夹存储向量数据，用于后续的相关问答操作
> 由于向量化需要时间，此接口速度会较慢，暂时未做边界处理，当然可以打包db文件夹，替换服务器内的db文件夹，这样就不需要初始化了
```
POST /initialize
content-type: application/json

{
    "filename": "we",
    "file_type": "csv"
}

```

**成功示例**
```
{
    "code": 200,
    "data": "初始化成功",
}

```


**失败示例**
```
{
    "code": 500,
    "data": "初始化失败",
}
```

### 2. 上传文件接口
目前仅支持单文件上传，上传后会存储在项目data目录下
```
POST /upload_file
content-type: multipart/form-data
```

**成功示例**
```
{
    "code": 200,
    "data": "上传成功"
}
```


### 3. 问答接口
接口只接受普通文本，返回也是文本，问答接口无上下文，建议前端可以根据业务需要每次收发信息后，可以断开并重新建立连接，默认的gpt等待时间为30s，如果超过30s未响应socket会断开连接
```
GET /ask
Upgrade: websocket
Connection: Upgrade
```


### 4. 添加api_key接口
```
POST /api_key/add
content-type: application/json

{
    "api_key": [
        {
            "your_email1":"your_api_key"
        },
        {
            "your_email2":"your_api_key2"
        }
    ]
}
```

**成功示例**
```
{
    "code": 200,
    "data": [
        {
            "your_email1":"your_api_key"
        },
        {
            "your_email2":"your_api_key2"
        }
    ]
}
```
### 5. 查询所有的api_key接口
```
GET /api_key/get_all_api_keys
```

**成功示例**
```
{
    "code": 200,
    "data": [
        {
            "email": "dk@xx.com",
            "api_key": "sk-"
        },
        {
            "email": "A@xx.com",
            "api_key": "sk-"
        },
        {
            "email": "Fe@xx.com",
            "api_key": "sk-"
        },
        {
            "email": "S@xx.com",
            "api_key": "sk-"
        },
        {
            "email": "C@xx.com",
            "api_key": "sk-"
        }
    ]
}
```