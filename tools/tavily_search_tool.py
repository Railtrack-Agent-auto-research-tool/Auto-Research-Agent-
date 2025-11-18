import railtracks as rt
from tavily import TavilyClient
import fitz  # PyMuPDF
import asyncio
import os

TAVILY_API_KEY = "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"


# -------------------------------
# Function: Web Search
# -------------------------------
@rt.function_node
def agent_websearch(query_sentence, max_result):
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    response = tavily_client.search(
        query=query_sentence,
        max_results=max_result
    )
    #print(response)
    agent_webextract(response)

    #print(response)
    #return response


# -------------------------------
# Function: Web Extract and Save PDF
# -------------------------------
@rt.function_node
def agent_webextract(search_result):
    #print("in webextract")
    #print(search_result)
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    output_dir = "/Users/yifanzhang/Desktop/pdf_output"
    os.makedirs(output_dir, exist_ok=True)
    for r in search_result.get('results', []):
        #print("in for loop")
        #print(r)
        if r.get('score', 0) >= 0.8:
            #print("erererererererererererereerererererere")
            #print(r)
            page_result = tavily_client.extract(urls=r['url'])#urls=r['url']
            #print(page_result)
            first_result = page_result["results"][0]
            raw_text = first_result["raw_content"]
            #print(raw_text)
  
            if not raw_text:
                continue

            print(raw_text[:500])

            pdf = fitz.open()
            page = pdf.new_page()
            y_pos = 50
            page.insert_text((50, y_pos), f"URL: {r['url']}", fontsize=12, color=(0, 0, 1))
            y_pos += 30

            lines = raw_text.split("\n")
            for line in lines:
                page.insert_text((50, y_pos), line, fontsize=11)
                y_pos += 15
                if y_pos > 750:
                    page = pdf.new_page()
                    y_pos = 50

            filename = r["url"].replace("https://", "").replace("/", "_") + ".pdf"
            full_path = os.path.join(output_dir, filename)
            pdf.save(full_path)
            pdf.close()
            print(f"Saved PDF: {filename}")


# -------------------------------
# Main function
# -------------------------------
async def main():
    # Create MCP server
    #mcp = rt.create_mcp_server([agent_websearch, agent_webextract], server_name="My MCP Server")

    # Run MCP server
    #mcp.run(transport="streamable-http")

    
    response = await rt.call(agent_websearch, "how many fingers do monkeys have?",
       10)

    print(response)



# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())
