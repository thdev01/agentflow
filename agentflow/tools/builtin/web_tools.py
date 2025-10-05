"""Web-related tools."""

from typing import Optional

import httpx

from agentflow.tools.base import tool


@tool
def web_search(query: str) -> str:
    """Search the web for information.

    Note: This is a mock implementation. For real web search, integrate
    with services like Google Search API, Bing API, or SerpAPI.

    Args:
        query: Search query

    Returns:
        Search results (mock)
    """
    # This is a placeholder - real implementation would call a search API
    return f"""Web Search Results for: "{query}"

[Mock Results - Integrate with real search API for production use]

1. Title: Understanding {query}
   URL: https://example.com/article1
   Snippet: Comprehensive guide to {query} with examples and best practices...

2. Title: {query} - Wikipedia
   URL: https://wikipedia.org/wiki/{query.replace(' ', '_')}
   Snippet: {query} is an important concept in computer science...

3. Title: Latest news about {query}
   URL: https://news.example.com/{query}
   Snippet: Recent developments in {query} show promising results...

Note: This is a mock response. Configure a real search API for production use.
"""


@tool
def fetch_url(url: str, method: str = "GET") -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch
        method: HTTP method (GET, POST, etc.)

    Returns:
        Response content or error message
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            if method.upper() == "GET":
                response = client.get(url)
            elif method.upper() == "POST":
                response = client.post(url)
            else:
                return f"Error: Unsupported HTTP method '{method}'"

            response.raise_for_status()

            # Get content type
            content_type = response.headers.get("content-type", "")

            # Return appropriate content
            if "application/json" in content_type:
                return f"Status: {response.status_code}\nContent-Type: {content_type}\n\n{response.json()}"
            elif "text/" in content_type:
                # Limit text responses to avoid overwhelming the LLM
                text = response.text[:5000]
                if len(response.text) > 5000:
                    text += "\n\n... (truncated, total length: {} chars)".format(len(response.text))
                return f"Status: {response.status_code}\nContent-Type: {content_type}\n\n{text}"
            else:
                return f"Status: {response.status_code}\nContent-Type: {content_type}\nContent length: {len(response.content)} bytes"

    except httpx.HTTPStatusError as e:
        return f"HTTP Error {e.response.status_code}: {e.response.text[:200]}"
    except httpx.RequestError as e:
        return f"Request Error: {str(e)}"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"
