from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import AgentWorkflow
# from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.workflow import Context

import os
import dotenv
import asyncio

dotenv.load_dotenv()

# llm = AzureOpenAI(
#     azure_deployment="",
#     azure_endpoint="",
#     api_key=os.getenv(""),
#     api_version="",
# )

llm = OpenAILike(
    model=os.getenv("model"),
    api_base = os.getenv("llm_api_base"),
    temperature=0.6,
    max_tokens=1024,
    api_key=os.getenv("llm_api_key"),
    is_chat_model=True,
)

mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tool = McpToolSpec(client=mcp_client)

# 代理
async def get_agent(tools):
    tools = await tools.to_tool_list_async()
    agent = AgentWorkflow.from_tools_or_functions(
        tools,
        llm=llm,
        system_prompt="""
            You are an AI assistant that can fetch data from Zotero.
            Use the available tools to interact with the Zotero library.
        """,
    )
    return agent


async def handle_user_message(message_content, agent, agent_context):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if hasattr(event, "tool_name"):
            print(f"Calling tool {event.tool_name} with kwargs {getattr(event, 'tool_kwargs', {})}")

    response = await handler
    return str(response)


async def main():
    agent = await get_agent(mcp_tool)
    agent_context = Context(agent)

    tools = await mcp_tool.to_tool_list_async()
    print("可用工具：")
    for tool in tools:
        print(f"- {tool.metadata.name}: {tool.metadata.description}")

    while True:
        user_input = input("Enter your message: ")
        if user_input == "exit":
            break
        print("User:", user_input)
        response = await handle_user_message(user_input, agent, agent_context)
        print("Agent:", response)

if __name__ == "__main__":
    asyncio.run(main())