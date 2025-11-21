import railtracks as rt
from tavily import TavilyClient
import fitz  # PyMuPDF
import asyncio
import os

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')


def agent_webextract(response, directory):
    print(response)
    print(directory)
    return []


@rt.function_node
def agent_websearch(query_sentence: str, directory: str) -> str:
    """
    Search the web using Tavily, extract webpage text content into PDFs,
    save them locally, and update the Railtracks virtual file system (VFS).

    This function performs a Tavily web search using the provided query,
    extracts raw text content from high-scoring results, converts each
    extracted page into a PDF file, saves the PDFs in the specified
    directory, stores the file paths inside the VFS, and returns a
    summary message indicating the number of files downloaded.

    Args:
        query_sentence (str):
            The natural-language search query to send to Tavily.
        directory (str):
            Directory where the generated PDF files should be saved.
            The directory is created if it does not already exist.

    Returns:
        str:
            A message indicating how many extracted pages were saved
            as PDF files. The message follows the pattern:
            `"Downloaded N extracted pages from Tavily results."`

    Side Effects:
        - Calls Tavily’s search API.
        - Calls Tavily’s extraction API for each high-confidence result.
        - Generates one PDF per extracted page.
        - Creates `directory` if missing.
        - Updates `rt.context["vfs"]["directories"][directory]` with
          the list of generated PDF paths.

    Notes:
        - Only results with score >= 0.8 are extracted.
        - PDF filenames are constructed from sanitized URLs.
        - The helper function `agent_webextract()` performs the PDF creation.
    """

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    # 🌐 search
    response = tavily_client.search(
        query=query_sentence,
        max_results=20
    )




@rt.function_node
def generate_websearch_query(query: str) -> str:
    """
    Generate a web search query string.

    This function is used inside an agent workflow to produce a
    standardized search-query payload. The agent should call this
    function whenever it needs to construct a query for a web
    search tool. The returned string is passed directly to the
    search mechanism.

    Parameters
    ----------
    query : str
        The raw user or agent-generated search text.

    Returns
    -------
    str
        A formatted search query string that begins with
        'Search Query Generated:' followed by the original query.
    """
    return f"Search Query Generated: {query}"



