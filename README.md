# Link Parser API

一个基于 FastAPI 的链接元数据解析 API。

用户提交一个网页 URL，API 会异步抓取网页 HTML，并提取页面的标题、描述和主图信息，返回结构化 JSON 数据。

本项目适合作为 FastAPI 后端工程学习项目，涵盖项目分层、Pydantic 数据校验、异步 HTTP 请求、HTML 解析、错误处理和自动化测试。

## 功能特性

- FastAPI 构建 API 服务
- Pydantic 请求与响应模型校验
- 使用 httpx 异步抓取网页 HTML
- 使用 BeautifulSoup 解析 HTML
- 提取页面标题 `title`
- 提取 Open Graph 描述 `og:description`
- 提取普通 description
- 提取 Open Graph 图片 `og:image`
- 支持 User-Agent 请求头
- 支持超时、HTTP 错误、非 HTML 响应处理
- 自定义业务异常 `ParserError`
- 使用 pytest 编写自动化测试
- 使用 httpx.MockTransport 避免测试依赖真实网络
- 使用 monkeypatch 测试 API 层逻辑

## 技术栈

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- httpx
- BeautifulSoup4
- pytest
- pytest-asyncio

## 项目结构

```text
Link-Parser-API/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── endpoints.py
│   ├── core/
│   │   └── schemas.py
│   ├── services/
│   │   └── parser.py
│   └── db/
│       └── models.py
├── tests/
│   └── test_parser.py
├── requirements.txt
├── LearningGuide.md
└── TaskProcessing.md
