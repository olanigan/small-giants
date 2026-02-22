import asyncio
from src.agent import GreedyAgent


async def test_agent():
    agent = GreedyAgent(model_name="ibm/granite4")

    result = await agent.run("Create a simple hello world function in Python", ".")
    print("Result:", result)


if __name__ == "__main__":
    asyncio.run(test_agent())
