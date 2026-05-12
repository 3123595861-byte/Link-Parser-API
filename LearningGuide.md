# Link Parser API 学习流程

这份文档是给阅读本项目代码的人准备的。目标不是直接讲每一行代码，而是帮助你按照合理顺序理解一个 FastAPI 后端项目如何从请求入口、数据校验、业务逻辑、异常处理到自动化测试逐步组成完整 API。

## 项目定位

本项目是一个基于 FastAPI 的链接元数据解析 API。

用户提交一个网页 URL，API 会尝试抓取网页 HTML，并提取：

- 页面标题 `title`
- 页面描述 `description`
- 页面主图 `image`

示例请求：

```json
{
  "url": "https://example.com"
}
```

示例响应：

```json
{
  "url": "https://example.com/",
  "title": "Example Domain",
  "description": null,
  "image": null
}
```

## 你可以通过本项目学习什么

阅读本项目可以学习：

- FastAPI 项目分层结构
- Pydantic 请求与响应模型
- 异步 HTTP 请求
- 使用 `httpx` 抓取网页
- 使用 BeautifulSoup 解析 HTML
- Open Graph 元数据提取
- 自定义业务异常
- API 错误状态码处理
- 日志记录
- pytest 自动化测试
- `httpx.MockTransport` 网络 Mock
- `monkeypatch` 替换业务函数
- Service 层测试与 API 层测试的区别

## 推荐学习顺序

建议按照下面顺序阅读代码。

---

## 第 1 步：先看项目目录结构

先整体观察项目结构：

```text
link-parser-api/
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
└── TaskProcessing.md
```

先记住每个目录的职责：

| 路径 | 职责 |
|---|---|
| `app/main.py` | FastAPI 应用入口 |
| `app/api/endpoints.py` | API 路由层 |
| `app/core/schemas.py` | 请求和响应数据模型 |
| `app/services/parser.py` | 链接解析业务逻辑 |
| `tests/test_parser.py` | 自动化测试 |
| `requirements.txt` | 项目依赖 |

---

## 第 2 步：阅读 `app/main.py`

先从入口文件开始。

重点理解：

- 如何创建 FastAPI 应用
- 如何注册路由
- 为什么 `main.py` 不直接写所有接口

你需要关注类似逻辑：

```python
app = FastAPI(...)
app.include_router(router)
```

这说明：

- `main.py` 负责启动应用
- 具体接口被拆到 `app/api/endpoints.py`

这是后端项目常见分层方式。

---

## 第 3 步：阅读 `app/core/schemas.py`

这个文件定义 API 的数据契约。

重点理解两个模型：

```python
ExtractRequest
ExtractResponse
```

### `ExtractRequest`

用于规定请求体格式。

它要求用户必须传入合法 URL。

### `ExtractResponse`

用于规定响应格式。

它包含：

- `url`
- `title`
- `description`
- `image`

学习重点：

- 为什么要用 Pydantic 模型
- `HttpUrl` 如何自动校验 URL
- 为什么响应模型中某些字段允许为 `None`

---

## 第 4 步：阅读 `app/api/endpoints.py`

这个文件是 API 路由层。

重点看两个接口：

```text
GET /health
POST /extract
```

### `/health`

用于检查服务是否正常运行。

### `/extract`

这是核心接口。

它的流程是：

```text
接收请求
  ↓
Pydantic 校验请求体
  ↓
调用 service 层 extract_metadata
  ↓
返回 ExtractResponse
```

学习重点：

- `APIRouter` 的作用
- `response_model` 的作用
- 为什么路由层不直接解析网页
- 如何把 `ParserError` 转成 HTTP 400
- 如何把未知异常转成 HTTP 500

---

## 第 5 步：阅读 `app/services/parser.py`

这是项目最核心的业务逻辑文件。

建议按下面顺序读：

### 1. `ParserError`

这是自定义业务异常。

它表示：

> 目标网页无法被正常解析，但这不一定是服务器程序崩溃。

例如：

- 目标网站超时
- 目标 URL 返回 404
- 目标内容不是 HTML

### 2. `_fetch_html`

负责抓取网页 HTML。

它做了几件事：

- 使用 `httpx.AsyncClient` 异步请求网页
- 添加浏览器请求头 `User-Agent`
- 设置超时时间
- 检查 HTTP 状态码
- 检查 `content-type` 是否为 HTML
- 把网络异常转换成 `ParserError`

学习重点：

- 为什么抓网页要异步
- 为什么要设置 timeout
- 为什么要检查 `content-type`
- 为什么测试时允许传入自定义 `client`

### 3. `_extract_title`

负责从 HTML 中提取标题。

当前主要从 `<title>` 标签中提取。

### 4. `_extract_description`

负责提取网页描述。

提取优先级：

```text
1. meta property="og:description"
2. meta name="description"
```

### 5. `_extract_image`

负责提取网页主图。

当前主要从：

```html
<meta property="og:image" content="...">
```

中提取。

### 6. `extract_metadata`

这是对外使用的主业务函数。

它把前面的步骤串起来：

```text
_fetch_html
  ↓
_extract_title
  ↓
_extract_description
  ↓
_extract_image
  ↓
ExtractResponse
```

学习重点：

- 为什么业务逻辑不写在路由层
- 为什么辅助函数名前有 `_`
- 为什么主函数支持传入 `client`
- 什么是依赖注入

---

## 第 6 步：理解完整请求流程

当用户请求：

```text
POST /extract
```

并发送：

```json
{
  "url": "https://example.com"
}
```

完整流程是：

```text
用户请求
  ↓
FastAPI 找到 /extract 路由
  ↓
ExtractRequest 校验 URL
  ↓
extract_endpoint 调用 extract_metadata
  ↓
_fetch_html 请求网页 HTML
  ↓
BeautifulSoup 解析 HTML
  ↓
提取 title / description / image
  ↓
组装 ExtractResponse
  ↓
FastAPI 返回 JSON
```

---

## 第 7 步：阅读 `tests/test_parser.py`

测试文件非常重要。

不要只把测试当成“检查代码有没有错”，它也展示了项目设计方式。

重点看三类测试。

### 1. Service 层测试

测试 `extract_metadata`。

它使用：

```python
httpx.MockTransport
```

模拟网页响应，避免真实联网。

学习重点：

- 为什么测试不应该依赖外部网站
- 如何构造假的 HTML 响应
- 如何验证 title / description / image 提取逻辑

### 2. 非 HTML 响应测试

测试当目标 URL 返回 JSON 等非 HTML 内容时，程序是否抛出 `ParserError`。

学习重点：

- 如何测试异常
- `pytest.raises` 的用法
- 为什么解析器要拒绝非 HTML 响应

### 3. API 层测试

测试 `/extract` 接口。

它使用：

```python
TestClient
monkeypatch
```

学习重点：

- 如何测试 FastAPI 接口
- 如何临时替换 service 函数
- 为什么 API 层测试不应该真实联网
- 如何断言状态码和响应 JSON

---

## 第 8 步：运行项目

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn app.main:app --reload
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

测试健康检查：

```text
GET http://127.0.0.1:8000/health
```

测试链接解析：

```text
POST http://127.0.0.1:8000/extract
```

请求体：

```json
{
  "url": "https://example.com"
}
```

---

## 第 9 步：运行测试

执行：

```bash
python -m pytest -v
```

如果一切正常，你应该看到所有测试通过。

测试通过说明：

- Service 层解析逻辑正常
- 非 HTML 响应能被拒绝
- API 层能正确返回成功响应
- API 层能正确处理业务错误

---

## 第 10 步：建议的扩展方向

如果你想继续完善这个项目，可以按下面顺序扩展。

### 1. 完善元数据提取策略

可以增加：

- `og:title` 优先于 `<title>`
- `twitter:title`
- `twitter:description`
- `twitter:image`
- 相对图片 URL 转绝对 URL

### 2. SQLite 持久化

记录每次 API 调用：

- URL
- title
- description
- image
- 请求时间
- 是否成功

### 3. API Key 鉴权

要求请求头携带：

```text
X-API-KEY
```

### 4. 简单限流

限制同一用户短时间内的请求次数。

### 5. 部署

可以考虑：

- Vercel
- Render
- Railway
- Supabase

---

## 推荐学习重点总结

如果你是初学者，建议重点理解：

1. 请求如何进入 FastAPI
2. Pydantic 如何校验数据
3. 路由层为什么只负责接收请求
4. Service 层为什么负责业务逻辑
5. `httpx` 如何请求网页
6. BeautifulSoup 如何解析 HTML
7. 自定义异常如何映射成 HTTP 错误
8. pytest 如何测试异步函数
9. Mock 如何让测试不依赖真实网络
10. 分层设计如何让项目更容易维护

## 项目当前定位

当前版本适合作为一个学习型 MVP 项目。

它已经具备：

- 可运行 API
- 清晰项目结构
- 异步网页抓取
- 元数据解析
- 错误处理
- 自动化测试

但还不是完整商业化版本。

后续仍需补充：

- 数据库存储
- 鉴权
- 限流
- 部署
- 更完整的解析策略
