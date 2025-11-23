from typing import List

import railtracks as rt
from tavily import TavilyClient
import fitz  # PyMuPDF
import asyncio
import os

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')


def write_text_to_pdf(text: str, output_path: str):
    pdf = fitz.open()        # new empty PDF
    page = pdf.new_page()    # create a page

    y = 50
    for line in text.split("\n"):
        page.insert_text((50, y), line, fontsize=12)
        y += 15
        if y > 750:
            page = pdf.new_page()
            y = 50

    pdf.save(output_path)
    pdf.close()

def extract(urls):
    tavily_client = TavilyClient(TAVILY_API_KEY)
    response = tavily_client.extract(urls)
    for result in response["results"]:
        print(f"URL: {result['url']}")
        print(f"Raw Content: {result['raw_content']}")

@rt.function_node
def download_articles(urls: List[str], directory: str):
    """
    Downloads articles from the given list of web search URLs and saves them to the specified directory.

    Args:
        urls (List[str]): A list of URLs pointing to the articles to be downloaded.
        directory (str): The directory path where the downloaded articles will be saved.

    Returns:
        str: A message indicating which articles are being downloaded and the target directory.
    """
    os.makedirs(directory, exist_ok=True)
    vfs = rt.context.get("vfs")
    directories = vfs.get("directories")
    directories.setdefault(directory, [])
    virtual_directory = directories.get(directory)
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.extract(urls=urls, include_images=False)
    results = response.get("results", [])
    saved_paths = []
    for idx, item in enumerate(results):
        url = item.get("url", f"unknown_{idx}")
        title = item.get("title")
        content = item.get("raw_content", "")
        if not content:
            content = f"(No raw_content extracted from {url})"
        safe_title = (
            title.lower()
            .strip()
            .replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
        )
        output_path = os.path.join(directory, f"{safe_title}.pdf")
        write_text_to_pdf(content, output_path)
        saved_paths.append((safe_title,output_path))
    virtual_directory.extend(saved_paths)
    return f"Downloaded {len(saved_paths)} articles into {directory}, this is state of the directory: {virtual_directory} which has the name of the file and its location."


@rt.function_node
def execute_web_search(query:str):
    """
    Executes a web search using the Tavily API and returns a summary of results.

    This function initializes a Tavily client with a provided API key, performs a search
    for the given query, and collects up to 5 results. Each result includes the title,
    content snippet, and URL. The results are printed to the console and returned as a
    formatted string.

    Args:
        query (str): The search query string to be submitted to the Tavily API.

    Returns:
        str: A formatted string summarizing the search results, including title, content,
        and URL for each entry.
    """
    tavily_client = TavilyClient(TAVILY_API_KEY)
    response = tavily_client.search(
        query=query,
        max_results=5
    )
    test_result = []
    for result in response["results"]:
        entry_dict = {
            "title": result["title"],
            "content": result["content"],
            "url": result["url"],
        }
        test_result.append(entry_dict)
    return f"These are the initial results: {test_result}"

@rt.function_node
def execute_web_search_main(query:str):
    """
    Executes a web search using the Tavily API and returns a summary of results.

    This function initializes a Tavily client with a provided API key, performs a search
    for the given query, and collects up to 5 results. Each result includes the title,
    content snippet, and URL. The results are printed to the console and returned as a
    formatted string.

    Args:
        query (str): The search query string to be submitted to the Tavily API.

    Returns:
        str: A formatted string summarizing the search results, including title, content,
        and URL for each entry.
    """
    tavily_client = TavilyClient(TAVILY_API_KEY)
    response = tavily_client.search(
        query=query,
        max_results=5
    )
    test_result = []
    for result in response["results"]:
        entry_dict = {
            "title": result["title"],
            "content": result["content"],
            "url": result["url"],
        }
        test_result.append(entry_dict)
    return f"These are the initial results: {test_result}"


@rt.function_node
def download_web_articles(query: str, directory: str) -> str:
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    response = tavily_client.search(
        query=query,
        max_results=20
    )
    results = response["results"]
    test_results = []
    if results:
        for result in results:
            if result["score"] > 0.8:
                test_results.append(result["url"])
        extract(test_results)
    return "Downloaded articles"








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



