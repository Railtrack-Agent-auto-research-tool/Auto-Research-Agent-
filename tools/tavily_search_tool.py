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

