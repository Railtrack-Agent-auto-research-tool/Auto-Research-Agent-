import os

from dotenv import load_dotenv
import railtracks as rt
from prompts import SYSTEM_PROMPT_FOR_ARXIV_AGENT
from tools.arxiv_tools import search_and_download_papers,get_arxiv_query
load_dotenv()

model = rt.llm.PortKeyLLM(os.getenv("MODEL","@openai/gpt-4.1-2025-04-14"))

def build_arxiv_agent():
    agent = rt.agent_node(
        name="ARXIV Agent",
        llm=model,
        system_message=SYSTEM_PROMPT_FOR_ARXIV_AGENT,
        tool_nodes=[get_arxiv_query],
    )