import asyncio
from fastmcp import Client

client = Client('http://127.0.0.1:8008/mcp')

async def main():
    async with client:
        # 基础服务端交互
        # await client.ping()

        # 列出可用操作
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(tools)
        print(resources)

        # 执行操作
        result = await client.call_tool("greet", {"name": "王维"})
        print(result)

asyncio.run(main())
