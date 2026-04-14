# AI 学习助手

一个面向学习与备课场景的轻量级 AI Web 工具，帮助用户将 PDF 学习资料快速转化为结构化总结。

项目聚焦一条清晰的核心链路：

`上传 PDF -> 提取文本 -> 大模型生成总结 -> 展示与复制结果`

在基础总结能力之上，项目还支持“目标 × 场景”的个性化输出，让同一份资料可以针对不同学习目的生成不同风格的结果。

## 项目亮点

- 支持单个 PDF 上传与文本提取，适合讲义、论文、复习资料等常见学习文档。
- 基于 DashScope `qwen-turbo` 生成结构化总结，输出更适合学习使用，而不是泛泛摘要。
- 提供个性化输出能力，可根据不同目标和使用场景生成差异化结果。
- Web 页面支持拖拽上传、状态提示、结果展示与一键复制，便于快速上手。
- 采用本地运行方式，无需复杂部署，适合作为 MVP、课程项目或 AI 产品作品集展示。

## 个性化输出

项目通过两组参数控制模型输出风格：

- `目标`
  - `exam`：考前冲刺
  - `understand`：入门理解
  - `teach`：授课备课
- `场景`
  - `self_study`：自主复习
  - `preview_review`：课前预习 / 课后复盘
  - `note_taking`：整理笔记
  - `sharing`：讲解分享

这套设计不是切换不同模型，而是基于不同目标和场景动态拼装 Prompt，从而改变模型关注重点、表达风格和输出结构。

## 技术栈

- `Python 3.13+`
- `Flask`：Web 服务与路由
- `pypdf`：PDF 文本提取
- `DashScope`：大模型调用
- `HTML / CSS / JavaScript`：前端页面与交互
- `python-dotenv`：本地环境变量管理

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd ai学习助手
```

### 2. 创建并激活虚拟环境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件，内容如下：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_MODEL=qwen-turbo
```

说明：

- `DASHSCOPE_API_KEY` 为阿里云 DashScope 平台的 API Key
- `DASHSCOPE_MODEL` 默认为 `qwen-turbo`，也可以替换为你希望使用的兼容模型

### 5. 启动项目

```bash
python app.py
```

浏览器访问：

`http://127.0.0.1:5000/`

## 使用流程

1. 选择或拖拽上传一个 PDF 文件
2. 选择你的学习目标和使用场景
3. 点击“生成考点总结”
4. 查看结果并一键复制

## 项目结构

```text
ai学习助手/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ README.md
├─ services/
│  ├─ pdf_parser.py
│  └─ summarizer.py
├─ static/
│  ├─ app.js
│  └─ style.css
└─ templates/
   └─ index.html
```

## 核心实现思路

### 1. PDF 解析

后端使用 `pypdf` 提取 PDF 中的纯文本内容，并限制页数范围，保证处理速度和模型输入成本可控。

### 2. Prompt 编排

系统根据用户选择的“目标”和“场景”，为模型动态注入：

- 当前任务重点
- 输出结构要求
- 表达方式约束

从而使同一份文档在不同使用目的下产生不同风格的总结结果。

### 3. 模型生成

后端通过 DashScope SDK 调用 `qwen-turbo`，将清洗后的文档文本与定制 Prompt 一并发送给模型，获取最终总结结果。

## 当前限制

- 当前版本仅支持单个 PDF 文件
- 更适合文本型 PDF，不支持 OCR 扫描件解析
- 暂不支持批量处理、多轮问答和结果导出
- 大模型调用依赖外部网络与 DashScope API Key

## Roadmap

- 支持 OCR，兼容扫描版 PDF
- 支持批量上传与多文件合并总结
- 支持 Markdown / Word 导出
- 支持长文档分段处理与更稳定的总结策略
- 支持基于 RAG 的问答能力

## 适用场景

- 大学生 / 考研生整理复习资料
- 教师 / 助教快速提炼讲义重点
- AI 产品经理 / 开发者展示教育场景 AI MVP
- 课程作业、毕业设计或作品集展示

## 贡献

欢迎通过 Issue 或 Pull Request 提出建议、修复问题或扩展功能。

如果你计划二次开发，建议优先从以下方向切入：

- 增强 PDF 清洗能力
- 优化 Prompt 模板和结果结构
- 增加导出、OCR、RAG 等扩展模块

## 免责声明

本项目仅用于学习、研究与作品集展示。模型生成内容可能存在遗漏或偏差，请勿直接用于高风险决策场景。
