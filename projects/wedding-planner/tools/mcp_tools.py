import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_tools(timeout=60):

    client = MultiServerMCPClient(
        {
            "lieux": {
                "command": "python",
                "transport": "stdio",
                "args": ["D:/marchine_learning/Agent_course/agentic-labs/projects/wedding-planner/tools/mcp_lieux.py"],
            },

            "traiteur": {
                "command": "python",
                "transport": "stdio",
                "args": ["D:/marchine_learning/Agent_course/agentic-labs/projects/wedding-planner/tools/mcp_traiteur.py"]
            }
        }
    )

    tools = await asyncio.wait_for(client.get_tools(), timeout=timeout) 

    return  tools

if "__main__" == __name__:
    asyncio.run(get_mcp_tools())