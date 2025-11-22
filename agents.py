import asyncio
import os

from dotenv import load_dotenv
import railtracks as rt
from pydantic import BaseModel, Field

from prompts import SYSTEM_PROMPT_FOR_ARXIV_AGENT, SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR, ARXIV_AGENT_DESCRIPTION, \
    ARXIV_QUERY_PARAM_DESCRIPTION, SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR_WRITING_AGENT, \
    SYSTEM_PROMPT_FOR_WEB_SEARCH_AGENT, WEB_SEARCH_AGENT_DESCRIPTION
from tools.arxiv_tools import search_and_download_papers, get_arxiv_query, execute_search
from tools.tavily_search_tool import generate_websearch_query, execute_web_search
from tools.todo_tools import write_todo, read_todo
from tools.research_tools import get_research_brief,generate_research_brief
from tools.util_tools import think_tool

load_dotenv()


class ArxivQuery(BaseModel):
    query: str = Field(description="The arXiv search query (e.g., 'transformer models').")

def build_arxiv_agent(model,with_schema=False):
    agent = None
    manifest = rt.ToolManifest(
        description=ARXIV_AGENT_DESCRIPTION,
        parameters=[rt.llm.Parameter(
            name="prompt",
            description=ARXIV_QUERY_PARAM_DESCRIPTION,
            param_type="string",
        )]
    )
    if with_schema:
        agent = rt.agent_node(
            name="ARXIV Agent",
            llm=model,
            system_message=SYSTEM_PROMPT_FOR_ARXIV_AGENT,
            tool_nodes=[get_arxiv_query,think_tool,execute_search],
            output_schema=ArxivQuery,
            manifest=manifest,
        )
    else:
        agent = rt.agent_node(
            name="ARXIV Agent",
            llm=model,
            system_message=SYSTEM_PROMPT_FOR_ARXIV_AGENT,
            tool_nodes=[get_arxiv_query,think_tool,execute_search],
            manifest=manifest,
        )
    return agent

def build_research_coordinator(model):
    arxiv_agent = build_arxiv_agent(model)
    agent = rt.agent_node(
        name = "Research Coordinator",
        llm=model,
        system_message=SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR,
        tool_nodes=[write_todo,read_todo,arxiv_agent,search_and_download_papers,get_research_brief,generate_research_brief])
    return agent

def build_websearch_agent(model):
    manifest = rt.ToolManifest(
        description=WEB_SEARCH_AGENT_DESCRIPTION,
        parameters=[rt.llm.Parameter(
            name = "prompt",
            description =
        )]
    )
    agent = rt.agent_node(
        name = "Web Search Agent",
        llm=model,
        system_message=SYSTEM_PROMPT_FOR_WEB_SEARCH_AGENT,
        tool_nodes=[generate_websearch_query,think_tool,execute_web_search],
        manifest=manifest
    )
    return agent

def create_writing_agent(model,summaries):
    agent = rt.agent_node(
            name="writing Agent",
            llm=model,
            system_message=SYSTEM_PROMPT_FOR_RESEARCH_COORDINATOR_WRITING_AGENT
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

@rt.session(context={"vfs": {"directories":{
}}})
async def main1():
    model = rt.llm.PortKeyLLM(os.getenv("MODEL", "@openai/gpt-4.1-2025-04-14"))
    agent = build_research_coordinator(model)
    message_history = []
    while True:
        user_input = input("Enter a query: ")
        if user_input.strip() == "quit":
            break
        message_history.append(rt.llm.UserMessage(user_input))
        response = await rt.call(agent,message_history)
        message_history = response.message_history
        print("Current Message History: ")
        print(response.message_history)


if __name__ == "__main__":
    asyncio.run(main1())
