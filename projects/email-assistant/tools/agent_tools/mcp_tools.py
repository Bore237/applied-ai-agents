import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_tools():
    client = MultiServerMCPClient({
        "gmail_server": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "server.mcp_gmail"]
        }
    })
    
    tools = await client.get_tools()

    return tools

if __name__ =="__main__":
    asyncio.run(get_mcp_tools())