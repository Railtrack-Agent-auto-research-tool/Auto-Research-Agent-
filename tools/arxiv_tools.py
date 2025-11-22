import asyncio
import os
from typing import Any, Dict, List

import arxiv
import railtracks as rt


@rt.function_node
async def search_and_download_papers(query: str, directory: str) -> str:
    """
    Search arXiv for papers matching a query and download their PDFs.

    This function performs an arXiv search using the provided query string,
    downloads up to 20 of the most relevant papers into the specified directory,
    stores the downloaded file paths in the Railtracks virtual file system (VFS),
    and returns a summary message.

    Args:
        query (str): The arXiv search query (e.g., "transformer models").
        directory (str): Path to the directory where the PDFs will be saved.
                         The directory is created if it does not exist. Start directory name with "./"

    Returns:
        str: A message indicating how many papers were downloaded.

    Side Effects:
        - Creates the target directory if missing.
        - Writes PDF files to `directory`.
        - Updates `rt.context["vfs"]["directory"]` with the list of file paths.

    Notes:
        - Up to 20 results are fetched, sorted by arXiv relevance.
        - Each entry added to the VFS corresponds to the local PDF file path.
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)

    # Search arXiv
    results = arxiv.Search(
        query=query,
        max_results=20,
        sort_by=arxiv.SortCriterion.Relevance
    )

    # Load or init VFS
    vfs = rt.context.get("vfs", {})
    directories = vfs.setdefault("directories", {})

    # Ensure this directory key exists
    directories.setdefault(directory, [])

    titles = []
    downloaded_paths = directories[directory]

    # Download papers
    for paper in results.results():
        print("Downloading:", paper.title)
        abstract = paper.summary
        titles.append(paper.title + "-" + abstract)
        print(paper.pdf_url)
        print(paper.get_short_id())
        print(paper.entry_id)

        # Safe filename
        cleaned_title = (
            paper.title.replace("/", "_")
                       .replace("\\", "_")
                       .replace(":", "_")
                       .replace("*", "_")
                       .replace("?", "_")
                       .replace('"', "_")
                       .replace("<", "_")
                       .replace(">", "_")
                       .replace("|", "_")
        ) + ".pdf"

        try:
            path = paper.download_pdf(dirpath=directory, filename=cleaned_title)
            downloaded_paths.append(path)
        except Exception as e:
            print(f"Failed to download {paper.title}: {e}")
            continue

    # Save updated VFS
    rt.context.put("vfs", vfs)

    # 🔥 Return statement untouched
    return f"Downloaded {len(titles)} papers. The papers are : {titles}."


@rt.function_node
def execute_search(query: str) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers matching a query and return a list of metadata dictionaries.

    This function performs an arXiv search using the provided query string and retrieves
    up to 5 of the most relevant results. For each result, it extracts the title and abstract
    and returns them as a dictionary.

    Args:
        query (str): The arXiv search query string (e.g., "transformer models").

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing:
            - "title" (str): The paper's title.
            - "abstract" (str): The paper's abstract.

    Notes:
        - Results are sorted by arXiv relevance.
        - Only the first 5 results are returned.
    """
    results = arxiv.Search(
        query=query,
        max_results=10,
        sort_by=arxiv.SortCriterion.Relevance
    )
    test_results = []
    for result in results.results():
        entry_dict = {
            "title": result.title,
            "abstract": result.summary,
            "paper_id": result.entry_id
        }
        test_results.append(entry_dict)
    return test_results

@rt.function_node
def download_papers(paper_ids: List[str], directory: str):
    """
    Downloads papers from arXiv given a list of paper IDs and saves them to the specified directory.

    Args:
        paper_ids (List[str]): A list of arXiv paper IDs to download (e.g., ["2210.06313v2"]).
        directory (str): The directory path where the downloaded papers will be saved.

    Returns:
        str: A message indicating which papers were downloaded and the target directory.
    """
    return f"Downloaded papers for {paper_ids} in {directory}"

@rt.function_node
def execute_search_main(query: str) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers matching a query and return a list of metadata dictionaries.

    This function performs an arXiv search using the provided query string and retrieves
    up to 10 of the most relevant results. For each result, it extracts the title and abstract
    and returns them as a dictionary.

    Args:
        query (str): The arXiv search query string (e.g., "transformer models").

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing:
            - "title" (str): The paper's title.
            - "abstract" (str): The paper's abstract.

    Notes:
        - Results are sorted by arXiv relevance.
        - Only the first 5 results are returned.
    """
    results = arxiv.Search(
        query=query,
        max_results=10,
        sort_by=arxiv.SortCriterion.Relevance
    )
    test_results = []
    for result in results.results():
        entry_dict = {
            "title": result.title,
            "abstract": result.summary,
            "paper_id": result.entry_id
        }
        test_results.append(entry_dict)
    return f"These are the results {test_results}"

@rt.function_node
async def get_arxiv_query(query:str):
    """
   Return a formatted arXiv query string for agent use.

   This function is used by an agent to prepare the final query that will be
   sent to the arXiv API. The `query` argument should contain the exact search
   expression the agent wants to use (e.g., keywords, author filters, etc.).
   The function simply wraps that raw query into a standardized string format.

   Args:
       query (str): The full arXiv search query provided by the agent.

   Returns:
       str: A formatted query string of the form "arXiv query <query>" that
       downstream tools or nodes can consume.
   """
    return f"arXiv query {query}"

@rt.session(context={"vfs": {}})
async def main():
    response = await rt.call(search_and_download_papers,"transformers","test")


if __name__ == "__main__":
    asyncio.run(main())