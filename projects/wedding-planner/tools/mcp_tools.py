import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


async def get_mcp_one_tools(name_tools: str, timeout: int=30) -> list[BaseTool]:
    servers = {
        name_tools: {
            "command": "python",
            "transport": "stdio",
            "args": [
                f"D:/marchine_learning/Agent_course/agentic-labs/projects/wedding-planner/servers/mcp_{name_tools}.py"
            ],
        }
    }

    if name_tools == "flight":
        servers["travel_server"] = {
            "url": "https://mcp.kiwi.com",
            "transport": "streamable_http",
        }

    client = MultiServerMCPClient(servers)

    return await asyncio.wait_for(client.get_tools(), timeout=timeout) 


    # for tool in tools:
    #     print("\n----------------")
    #     print(tool.name)
    #     print(type(tool))
    #     print(dir(tool))

if "__main__" == __name__:
    asyncio.run(get_mcp_one_tools("flight"))