import railtracks as rt
import asyncio
from research_agentTool import agent_websearch

def create_mcp(tool_list,server_name):
    mcp = rt.create_mcp_server(
        tool_list,
        server_name=server_name
    )
    return mcp

    
    


async def main():
    # Create MCP server
    mcp = create_mcp([agent_websearch], "big fucking server")

    # Run MCP server in background
    server_task = asyncio.create_task(mcp.run(transport="streamable-http"))

    # Optionally stop server if you want to end the program
    server_task.cancel()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
