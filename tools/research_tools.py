import os
from typing import List

import fitz  # PyMuPDF
import railtracks as rt
from pydantic import BaseModel, Field

from tools.util_tools import think_tool


def highlight_sentences_in_pdf(input_pdf_path, output_pdf_path, sentences_to_highlight):
    """
    Highlight a list of sentences in a PDF.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path where the highlighted PDF will be saved.
        sentences_to_highlight (List[str]): List of sentences to highlight.
    """
    doc = fitz.open(input_pdf_path)

    for page in doc:
        for sentence in sentences_to_highlight:
            # Search for the sentence on the page
            text_instances = page.search_for(sentence)
            for inst in text_instances:
                page.add_highlight_annot(inst)

    doc.save(output_pdf_path)
    print(f"Saved highlighted PDF as {output_pdf_path}")


def load_pdf_paragraphs(pdf_path: str):
    """
    Loads a PDF and extracts text split into paragraphs.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[str]: A list of paragraphs extracted from the PDF.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    # Step 1: Extract text from all pages
    for page in doc:
        text = page.get_text("text")  # plain text extraction
        full_text += "\n" + text

    doc.close()

    # Step 2: Normalize whitespace
    cleaned = full_text.replace("\r", "")

    # Step 3: Split into paragraphs
    paragraphs = [
        p.strip()
        for p in cleaned.split("\n\n")
        if p.strip()
    ]

    return paragraphs


NOTE_TAKING_SYSTEM_PROMPT = """
You are a Note-Taking Agent. You are given a paragraph and a user research brief.
Your task is to extract concise, relevant notes based on the paragraph, focusing
specifically on information that aligns with the research brief.

Identify key points, insights, or findings that contribute to the user’s research goals.
Additionally, include any important or high-impact sentences from the paragraph so they
can be highlighted later. Ensure you provide the sentences as it is without any changes.
"""

SUMMARIZATION_SYSTEM_PROMPT = """
You are a research summarization agent. You are given:
1. A list of notes, excerpts, and partial summaries from one or more research papers.
2. The user's research brief describing the topic, scope, and specific goals.

Your task is to synthesize these inputs into **one clear, comprehensive, and coherent summary** that:

- Preserves key insights, main contributions, and important technical details.
- Maintains logical flow and eliminates redundancy.
- Focuses specifically on content that is **relevant to the user’s research brief**.
- Includes traceable references to the source material where appropriate (e.g., key sentences or sections from the papers).

Additional instructions:

- If conflicting information exists in the notes, reconcile it logically or highlight the discrepancy.
- Avoid adding information that is not supported by the provided notes or excerpts.
- Structure the summary to make it readable and usable for further research, writing, or decision-making.
- Emphasize clarity, precision, and completeness while remaining concise where possible.
"""
WRITING_AGENT_SYSTEM_PROMPT = """
You are the Writing Agent. You are provided with:

1. A list of summaries or structured notes from research papers or documents.
2. The user's research brief describing the topic, scope, and specific goals.

Your task is to produce a **well-structured research report** that:

* Follows a clear structure with **Introduction, Body, and Conclusion**.
* Incorporates and synthesizes the content from all provided summaries.
* Ensures that the report strictly aligns with the **user's research brief**, focusing only on relevant content.
* Preserves key insights, technical details, and main contributions from the summaries.
* Maintains logical flow, clarity, and coherence.
* Avoids introducing unsupported, speculative, or extraneous information.

Additional structural instructions:

* The **Introduction** should contextualize the research topic and outline objectives.
* The **Body** should organize findings logically, grouping related insights and highlighting key results, methods, or themes.
* The **Conclusion** should summarize the main takeaways and their relevance to the user's research goals.

Critical workflow requirements:

* **Use the Think tool** whenever reasoning, planning, breaking down complex information, or resolving ambiguities is required.

* **Every time you produce a report—whether it is an initial draft, a revised draft, or the final version—you must call the `generate_report` tool**.  
  This tool must always be used to output any report version.

* **After producing your initial draft (via the `generate_report` tool)**, you must call the **Critique Agent tool**, providing:
  - the draft report, and
  - the user’s research brief.
  The Critique Agent will evaluate clarity, coherence, alignment, completeness, and accuracy.

* **Use the Think tool and Critique Agent feedback** to revise the report.  
  After each revision, again **use the `generate_report` tool** to output the updated draft.

* **Once all critique points are resolved and the report is polished**, produce the **final report** using the `generate_report` tool.

Aim for clarity, precision, and readability while producing a comprehensive, accurate, and well-reasoned research report.
"""



WRITING_AGENT_USER_PROMPT = """
Using the information provided, write a complete research report.

Inputs:
- **Research Brief:**  
{user_research_brief}

- **Summaries / Notes:**  
{summaries}

Instructions:
- Produce a well-structured report with an Introduction, Body, and Conclusion.
- Synthesize insights from the summaries while ensuring strict alignment with the research brief.
- Focus only on information relevant to the brief's objectives and scope.
- Maintain clarity, coherence, and logical flow throughout.

Write the full research report now.
"""







CRITIQUE_AGENT_DESCRIPTION = """
The Critique Agent is responsible for evaluating a drafted research report. 
It analyzes the report for clarity, coherence, alignment with the user's research brief, 
accuracy, completeness, logical structure, and adherence to the provided summaries. 
It provides detailed, actionable feedback that the Writing Agent must use to improve the report.
"""


CRITIQUE_AGENT_SYSTEM_PROMPT = """
You are the Critique Agent. You will be given two inputs:
1. The research brief, which specifies the objectives, scope, constraints, and expected outputs.
2. The report produced by the Writing Agent.

Your task:
- Evaluate the report strictly against the research brief.
- Identify any missing requirements, misalignments, inaccuracies, or deviations.
- Highlight unclear reasoning, unsupported claims, and structural issues.
- Provide specific, actionable feedback that the Writing Agent can use to revise the report.
- If the report fully aligns with the research brief, state this clearly and concisely.

Be objective, thorough, and focused on ensuring the final report adheres to the expectations defined in the research brief.
"""


class ReportSchema(BaseModel):
    report: str = Field(description="This field stores the report generated by the llm.")

class NotesSchema(BaseModel):
    notes: str = Field(description="This field is to store the notes the llm or agent takes")
    important_sentences: List[str] = Field(
        description="This field is to store the important sentences the llm or agent takes. This has to store the sentences in the same form as present from the paragraphs supplied")


class SummarizationSchema(BaseModel):
    summary: str = Field(description="This field is to store the summaries the llm or agent generates")


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
async def generate_report(report: str, markdown_file: str) -> str:
    """
    Writes the research report to a Markdown file, creating the directory if it does not exist,
    and returns a formatted confirmation message.

    Args:
        report (str): The research report content generated by the Writing Agent.
        markdown_file (str): The path to the Markdown file where the report
            should be written (e.g., 'output/report.md').

    Returns:
        str: A formatted string indicating that the report has been generated
             and saved, followed by the full report content.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(markdown_file), exist_ok=True)

    # Write the report to the markdown file
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(report)

    return f"Report saved to {markdown_file}\n\n{report}"


def write_markdown(text: str, file_path: str):
    """
    Writes a markdown-formatted string to a .md file.

    Args:
        text (str): The markdown content to write.
        file_path (str): Path to the markdown file (e.g., 'output.md').
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

async def write_report(summary_for_papers,model,user_research_brief):
    critique_manifest = rt.ToolManifest(
        description=CRITIQUE_AGENT_DESCRIPTION,
        parameters=[
            rt.llm.Parameter(
                name="report_and_brief",
                description="This parameter contains both the research report generated by the agent and the user's research brief, including the topic, scope, and goals that guide the report's content and structure.",
                param_type="string",
            )
        ]
    )
    critique_agent = rt.agent_node(name="CRITIQUE AGENT",llm=model,system_message=CRITIQUE_AGENT_SYSTEM_PROMPT,manifest=critique_manifest)
    write_agent = rt.agent_node(name="Writing Agent ",llm=model,system_message=WRITING_AGENT_SYSTEM_PROMPT,tool_nodes=[generate_report,critique_agent,think_tool])
    writing_agent_response = await rt.call(write_agent,WRITING_AGENT_USER_PROMPT.format(user_research_brief=user_research_brief,summaries=summary_for_papers))
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
    reading_agent = rt.agent_node(name="note-taking agent", llm=model, system_message=NOTE_TAKING_SYSTEM_PROMPT,
                                  output_schema=NotesSchema)
    summarizing_agent = rt.agent_node(name="summarization-agent", llm=model, system_message=SUMMARIZATION_SYSTEM_PROMPT,
                                      output_schema=SummarizationSchema)
    vfs = rt.context.get("vfs")
    print(user_research_brief)
    directories = vfs.get("directories")
    virtual_directory = directories.get(directory)
    granular_summaries = {
    }
    summary_for_papers = []
    rt.context.put("granular_summaries", granular_summaries)
    rt.context.put("summary_for_papers", summary_for_papers)
    for file in virtual_directory:
        paragraphs = load_pdf_paragraphs(file[1])
        granular_summaries.setdefault(file[0], [])
        notes_list = granular_summaries.get(file[0])
        sentences_list = []
        for paragraph in paragraphs:
            USER_PROMPT = f"""
            Take notes for the following paragraph making sure its relevant to the research brief.
            ## Paragraph
            {paragraph}
            ## Research brief.
            {user_research_brief}
            """

            reading_agent_response = await rt.call(reading_agent, USER_PROMPT)
            notes_list.append(reading_agent_response.structured.notes)
            sentences = reading_agent_response.structured.important_sentences
            sentences_list.extend(sentences)
        highlight_sentences_in_pdf(file[1], file[0] + ".pdf", sentences_list)
        SUMMARIZATION_USER_PROMPT = f"""
        This is the user research brief.
        ## Research brief.
        {user_research_brief}
        ## Notes
        {notes_list}
        """
        summarising_agent_response = await rt.call(summarizing_agent, SUMMARIZATION_USER_PROMPT)
        summary_for_papers.append((file[0], summarising_agent_response.structured.summary))
    await write_report(summary_for_papers,model,user_research_brief)
    return f"Finished reading all papers and done writing the report "

def read_papers_and_articles(directory:str, user_research_brief:str):

