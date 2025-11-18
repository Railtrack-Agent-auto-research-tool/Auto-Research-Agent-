import asyncio
import os
from typing import Any

import arxiv
import railtracks as rt


@rt.function_node
async def search_and_download_papers(query:str,directory:str) -> str:
    os.makedirs(directory,exist_ok=True)
    results = arxiv.Search(
        query=query,
        max_results=20,
        sort_by=arxiv.SortCriterion.Relevance
    )
    vfs = rt.context.get("vfs",{})
    vfs["directory"] = []
    titles = []
    for paper in results.results():
        print("Downloading:", paper.title,)
        abstract = paper.summary
        print(abstract)
        titles.append(paper.title+"-"+abstract)
        path = paper.download_pdf(dirpath=directory)
        vfs["directory"].append(path)
    rt.context.put("vfs",vfs)
    return f"Downloaded {len(titles)} papers. The papers are : titles"

@rt.function_node
async def get_arxiv_query(query:str):
    return

@rt.session(context={"vfs": {}})
async def main():
    response = await rt.call(search_and_download_papers,"transformers","test")


if __name__ == "__main__":
    asyncio.run(main())