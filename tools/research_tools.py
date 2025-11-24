import os
from typing import List

import railtracks as rt
from pydantic import BaseModel, Field

NOTE_TAKING_SYSTEM_PROMPT = """
You are a Note-Taking Agent. You are given a paragraph and a user research brief.
Your task is to extract concise, relevant notes based on the paragraph, focusing
specifically on information that aligns with the research brief.

Identify key points, insights, or findings that contribute to the user’s research goals.
Additionally, include any important or high-impact sentences from the paragraph so they
can be highlighted later.
"""

USER_PROMPT = """
take notes for the following paragraph given the research brief.
## paragraph
{par}
## Research brief.
{research_brief}

"""
class NotesSchema(BaseModel):
    notes: str = Field(description="This field is to store the notes the llm or agent takes")
    important_sentences: List[str] = Field(description="This field is to store the important sentences the llm or agent takes. This has to store the sentences in the same form as present from the paragraphs supplied")

@rt.function_node
def generate_research_brief(research_brief: str) -> str:
    """Return a formatted research brief.

    Args:
        research_brief (str):
            The text of the research brief to be formatted and returned.

    Returns:
        str: A formatted string that includes the provided research brief.
    """
    rt.context.put("research_brief", research_brief)
    return f"This is the research brief: \n\n {research_brief}"


@rt.function_node
def get_research_brief() -> str:
    """Retrieve the currently stored research brief from the railtracks context.

    Returns:
        str: The stored research brief if one exists. If no research brief
        has been generated, returns a default message indicating its absence.
    """
    return rt.context.get("research_brief", "No research brief generated.")


@rt.function_node
async def read_write_notes_for_papers_in_a_directory(directory: str, user_research_brief: str):
    """
    Reads a collection of papers stored in a virtual directory and prepares them
    for note-taking and summarization.

    This function accesses the Railtracks context's virtual file system (VFS) to
    locate a directory containing downloaded research papers. It prints the user's
    research brief for context, then iterates through all files in the directory,
    printing each file name. This serves as the entry point for workflows that
    involve reading papers, generating summaries, and writing structured notes.

    Args:
        directory (str): The name of the virtual directory containing the papers
            that will be reviewed.
        user_research_brief (str): A textual summary of the user's research goals,
            provided to guide the note-taking and summarization process.

    Returns:
        str: A message confirming that all papers in the specified directory have
            been processed for reading and note-generation.

    Raises:
        KeyError: If the directory does not exist in the virtual file system.
    """
    model = rt.llm.PortKeyLLM(os.getenv("MODEL", "@openai/gpt-4.1-2025-04-14"))
    reading_agent = rt.agent_node(name="note-taking agent",llm=model,system_message=NOTE_TAKING_SYSTEM_PROMPT,output_schema=NotesSchema)
    summarizing_a
    vfs = rt.context.get("vfs")
    print(user_research_brief)
    directories = vfs.get("directories")
    virtual_directory = directories.get(directory)
    for file in virtual_directory:
        for paragraph in paragraphs:
            response = rt.call(reading_agent,USER_PROMPT.format(par=paragraph,user_research_brief=user_research_brief))
            print(response.structured.notes)
            print(response.structured.important_sentences)
    return f"Finished reading all papers in directory {directory}"



