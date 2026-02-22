from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from src.agent import GreedyAgent

app = Server("granite-coder")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="check_status",
            description="Check if the Granite Coder agent is healthy and ready.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="solve_task",
            description="Solve a coding task using the Greedy architecture.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The coding task to solve.",
                    },
                    "path": {
                        "type": "string",
                        "description": "The path to the codebase.",
                        "default": ".",
                    },
                },
                "required": ["task"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name, arguments):
    if name == "check_status":
        return [TextContent(type="text", text="Granite Coder is ONLINE and Greedy.")]

    elif name == "solve_task":
        task = arguments.get("task")
        path = arguments.get("path", ".")

        agent = GreedyAgent(model_name="ibm/granite4")
        result = agent.run(task, path)

        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
