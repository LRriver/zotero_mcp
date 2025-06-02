from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
import asyncio


mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tool = McpToolSpec(client=mcp_client)

# 获取工具列表
async def list_all_tools():
    tools = await mcp_tool.to_tool_list_async()
    for tool in tools:
        print(f"Tool Name: {tool.metadata.name}")
        print(f"Description: {tool.metadata.description}\n")


if __name__ == "__main__":
    asyncio.run(list_all_tools())