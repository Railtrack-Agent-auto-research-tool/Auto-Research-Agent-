import asyncio
import os

from dotenv import load_dotenv
import railtracks as rt
from pydantic import BaseModel, Field

from prompts import SYSTEM_PROMPT_FOR_ARXIV_AGENT, SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR
from tools.arxiv_tools import search_and_download_papers,get_arxiv_query
from tools.todo_tools import write_todo, read_todo

load_dotenv()


class ArxivQuery(BaseModel):
    query: str = Field(description="The arXiv search query (e.g., 'transformer models').")

def build_arxiv_agent(model,with_schema=False):
    agent = None
    manifest = rt.ToolManifest(
        description="A calculator agent that can perform mathematical calculations and solve math problems.",
        parameters=
    )
    if with_schema:
        agent = rt.agent_node(
            name="ARXIV Agent",
            llm=model,
            system_message=SYSTEM_PROMPT_FOR_ARXIV_AGENT,
            tool_nodes=[get_arxiv_query],
            output_schema=ArxivQuery
        )
    else:
        agent = rt.agent_node(
            name="ARXIV Agent",
            llm=model,
            system_message=SYSTEM_PROMPT_FOR_ARXIV_AGENT,
            tool_nodes=[get_arxiv_query],
        )
    return agent

def build_research_coordinator(model):
    arxiv_agent = build_arxiv_agent(model)
    agent = rt.agent_node(
        name = "Research Coordinator",
        llm=model,
        system_message=SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR,
        tool_nodes=[write_todo,read_todo]
    )


async def main():
    model = rt.llm.PortKeyLLM(os.getenv("MODEL", "@openai/gpt-4.1-2025-04-14"))
    with_schema = False
    agent = build_arxiv_agent(model, with_schema=with_schema)
    response = await rt.call(agent,"Help me find all the papers that are important in transformers")
    print(response.message_history)
    print(response)
    if with_schema:
        print(response.structured.query)
    else:
        print(response.text)

async def main1():
    agent = build_deep_research_agent()

if __name__ == "__main__":
    asyncio.run(main())
