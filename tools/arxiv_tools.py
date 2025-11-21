import asyncio
import os
from typing import Any

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