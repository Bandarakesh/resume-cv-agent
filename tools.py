from langchain.tools import tool
import trafilatura

@tool
def web_scrapping_tool(url: str) -> str:
    "This tool takes url provides scrapped website data"
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return "Failed to fetch URL"

    text = trafilatura.extract(downloaded)

    return text if text else "No content extracted"
