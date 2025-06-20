# zotero_mcp
[中文](./README_zh.md) | [English](./README.md)

支持通过 MCP 协议连接 Zotero，包含自定义的服务端和客户端，无需依赖如 Claude 应用、Cursor 等工具。
## 环境配置
```
conda create -n mcp python=3.12 -y
conda activate mcp
pip install -r requirements.txt
```

## 运行MCP

首先创建 `.env` 文件，并填写以下变量。

```
model=""
llm_api_base = ""
llm_api_key=""
zotero_api_key=''
library_id=''
```
`model`是LLM的名称，`llm_api_base`是LLM的url，`llm_api_key` 是 LLM 的 API Key，其中 `zotero_api_key` 点击 [zotero官网](https://www.zotero.org/settings/keys) 创建，你的[library_id](https://www.zotero.org/settings/keys)，如下图:
![library_id](./img/user_id.png)

然后启动服务端：
```bash
python ./server.py
```

打开一个新的终端窗口，运行客户端：
```bash
python ./client.py
```

测试效果如下：

提前在 Zotero 中上传文件：

![Zotero 上传文件截图](./img/image.png)

通过 MCP 接入 Zotero，查询文档内容：

![查询文档内容截图](./img/image-1.png)
