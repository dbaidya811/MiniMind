import urllib.parse
import urllib.request
import json
from duckduckgo_search import DDGS

class WebSearchTool:
    @staticmethod
    def search_web(query: str, max_results: int = 5) -> str:
        """
        Deep RAG search combining direct Wikipedia summary extraction
        and DuckDuckGo deep context retrieval.
        """
        aggregated_intel = []

        # 1. Direct Wikipedia API Search for factual background
        try:
            wiki_query = query.replace("list", "").replace("table", "").replace("complete", "").strip()
            encoded_query = urllib.parse.quote(wiki_query)
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            
            req = urllib.request.Request(
                wiki_url, 
                headers={'User-Agent': 'MiniMindAI/1.0 (academic research; contact: dev@minimind.local)'}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if "extract" in data:
                    aggregated_intel.append(f"[Wikipedia Fact Sheet: {data.get('title')}]\n{data.get('extract')}")
        except Exception:
            pass

        # 2. DuckDuckGo Search for detailed listings & real-time snippets
        try:
            enhanced_query = f"{query} details list"
            with DDGS() as ddgs:
                results = list(ddgs.text(enhanced_query, max_results=max_results))
                for idx, r in enumerate(results, 1):
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if body:
                        aggregated_intel.append(f"[Source {idx}: {title}]\n{body}")
        except Exception:
            pass

        return "\n\n".join(aggregated_intel)[:2500] if aggregated_intel else ""