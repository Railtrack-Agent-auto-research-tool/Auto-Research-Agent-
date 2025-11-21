import railtracks as rt
from tavily import TavilyClient
import fitz  # PyMuPDF
import asyncio
import os

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')


def agent_webextract(search_result, directory):
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "pdf_output")
    os.makedirs(output_dir, exist_ok=True)

    saved_paths = []

    for r in search_result.get('results', []):
        if r.get('score', 0) < 0.8:
            continue

        page_result = tavily_client.extract(urls=r['url'])
        first_result = page_result["results"][0]
        raw_text = first_result.get("raw_content")

        if not raw_text:
            continue

        pdf = fitz.open()
        page = pdf.new_page()
        y_pos = 50

        page.insert_text((50, y_pos), f"URL: {r['url']}", fontsize=12, color=(0, 0, 1))
        y_pos += 30

        for line in raw_text.split("\n"):
            page.insert_text((50, y_pos), line, fontsize=11)
            y_pos += 15
            if y_pos > 750:
                page = pdf.new_page()
                y_pos = 50

        filename = (
            r["url"]
            .replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
        ) + ".pdf"

        full_path = os.path.join(output_dir, filename)
        pdf.save(full_path)
        pdf.close()

        saved_paths.append(full_path)

    return saved_paths


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

    # 📄 extract pages + get saved file paths
    saved_paths = agent_webextract(response, directory)

    # 📦 update VFS inside the function
    vfs = rt.context.get("vfs", {})
    directories = vfs.setdefault("directories", {})

    # Store inside a stable key
    directories.setdefault(directory, [])
    directories[directory].extend(saved_paths)

    rt.context.put("vfs", vfs)

    return f"Downloaded {len(saved_paths)} extracted pages from Tavily results."



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



