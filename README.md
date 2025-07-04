# zotero_mcp
[English](./README.md) | [中文](./README_zh.md)

Support connecting Zotero via MCP with a custom server and client, without the need for tools like the Claude app or Cursor.

## Environment configuration
```
conda create -n mcp python=3.12 -y
conda activate mcp
pip install -r requirements.txt
```

## Run MCP

First, create a `.env` file and fill in the following variables. `zotero_api_key` needs to be obtained from the Zotero official website, and `api_key` is your LLM's API key:

```
zotero_api_key=''
api_key=""
```
First, create a `.env` file and fill in the following variables:

```  
model=""  
llm_api_base = ""  
llm_api_key=""  
zotero_api_key=''  
library_id=''  
```  

`model` is the name of the LLM, `llm_api_base` is the URL of the LLM, and `llm_api_key` is the API Key for the LLM. The `zotero_api_key` can be created by visiting the [Zotero](https://www.zotero.org/settings/keys), and your [library_id](https://www.zotero.org/settings/keys) is shown below:  
![library_id](./img/user_id.png)


Then start the server:
```bash
python ./server.py
```

Open a new terminal window and run the client:
```bash
python ./client.py
```

Here's the testing result:

Upload files in Zotero in advance:

![Zotero upload screenshot](./img/image.png)

Query document content via MCP:

![Query document content screenshot](./img/image-1.png)
