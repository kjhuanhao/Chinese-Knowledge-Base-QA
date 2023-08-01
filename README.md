# CSV_QA

## 介绍
这个项目是一个基于openAI的CSV文件问答系统

## 项目用途
智能客服等要求精准回答的对话系统

## 为什么是csv
csv表格形式有利于构建prompt，可以更加精准进行匹配向量和匹配答案

## 项目特色
- [x] 流式传输
- [x] 基于openAI的ChatModel`(gpt-3.5-turbo)`
- [x] 答案与csv相似度动态匹配，实现动态prompt
- [x] 支持多个api_key动态更换api_key，一定程度上解决3次/min调用的问题
- [x] 基于redis存储csv向量数据
- [x] 支持openAI代理
- [x] ~~实现api_key状态管理，可查询用量余额，基于openAI账号的api_key管理~~
- [x] 运维复杂度低，只需要引入redis数据库，即可快速构建
- [x] 智能问答推荐，实现更加精准的答复
- [ ] 队列问答，解决高并发问题
- [ ] 智能缓存，问题重复下，无需走openAI接口，实现快速响应

> 由于官方的余额查询相关接口鉴权方法更换，现已去除此功能

## 使用说明

### 必备模块 
```bash
pip install -r requirements.txt
```

如果速度慢可以自行下载该模型，在此项目根目录下命名为`text2vec-base-chinese`
```bash
git lfs install
git clone https://huggingface.co/shibing624/text2vec-base-chinese
```

### 配置
需要修改`env_template`为`.env`文件，具体参数说明如下：
- REDIS_CSV_NAME：作为csv文件向量化数据的key值，例如：`we_qa_csv` ，可以不修改
- CSV_FILE_NAME：存储在`data`目录下的csv文件，指定用于问答的csv文件，这里只能指定一个唯一的，例如：`test.csv` 
- OPENAI_API_BASE：openAI代理地址设置，例如：`https://xxxxx.com/v1` ，如果无需使用代理，请留空即可，默认会走官方接口
- EXPIRE_DAYS：所有api_key在redis中的可留存时间，例如：`900` (默认单位为`天数`)
- REDIS_HOST：redis主机地址，例如`127.0.0.1`
- REDIS_PORT：redis端口号，例如：`6379`
- REDIS_PASSWORD：redis密码，没有密码则为空即可
- REDIS_DB：redis数据库，例如：`0`
- PINECONE_KEY：pinecone的key值
- PINECONE_ENV：pinecone环境名称
- PINECONE_INDEX：pinecone索引名称
- PINECONE_NAMESPACE：pinecone命名空间，本项目所有的向量数据都会存储在该命名空间下


### CSV文件说明
csv文件上传后会存储在项目data目录下，项目默认支持两列数据，第一列为`question`，第二列为`answer`，当然你也可以自定义列名或增加列名，
需要修改`parsers`目录中的`csv_parser.py`和utils目录中的`embedding_vector.py`，暂时没有封装好这个地方，后续会进行优化


### 运行
fastapi使用的是`uvicorn`，本项目`app.py`直接运行即可
```bash
python3 main.py
```

## 相关接口

### 1. 初始化接口
在使用之前需要初始化你的csv文件，在初始化过程中，会获取相关的embeddings然后存储到redis中
> 当然，如果你更新了你的csv文件，你也需要重新进行一次初始化操作
```
POST /initialize
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
目前仅支持单文件上传，上传后会存储在项目data目录下，请注意修改.env下的`CSV_FILE_NAME`
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
```
POST /ask
content-type: application/json

{
    "question": "你好",
    "stream": "0" #0: 不使用流式传输，1: 使用流式传输
}
```

**成功示例**
```
text
```

```
{
    "code": 200,
    "data": "text"
}
```


**失败示例**
```
"{"code": "500", "msg": "error"}"
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