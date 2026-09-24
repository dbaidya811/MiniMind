from duckduckgo_search import DDGS
from typing import List, Dict

class WebSearchTool:
    @staticmethod
    def search_web(query: str, max_results: int = 3) -> str:
        """
        Searches DuckDuckGo and formats the top snippets into a compact context block.
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return ""

                context_blocks = []
                for idx, item in enumerate(results, start=1):
                    title = item.get("title", "Source")
                    body = item.get("body", "").strip()
                    if body:
                        context_blocks.append(f"[{idx}] {title}: {body}")

                return "\n\n".join(context_blocks)
        except Exception:
            return ""