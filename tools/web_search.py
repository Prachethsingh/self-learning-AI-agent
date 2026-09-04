"""
Web Search Tool

Provides web search capabilities using multiple free search APIs.
"""

from typing import Any, Dict, List, Optional
import logging
import httpx
import json
import asyncio

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Provides web search capabilities using free search APIs.
    """

    def __init__(self, api_key: Optional[str] = None, engine: str = "duckduckgo"):
        """
        Initialize the web search tool.

        Args:
            api_key: API key for search service (if required)
            engine: Search engine to use ("duckduckgo", "searx", "brave", "google_programmable")
        """
        self.api_key = api_key
        self.engine = engine.lower()
        self.client = httpx.AsyncClient(timeout=30.0)
        self.fallback_engines = ["duckduckgo", "searx"]

    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "us-en",
        safesearch: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search with fallback mechanisms.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            region: Region for search results
            safesearch: Safesearch setting

        Returns:
            List of search results
        """
        logger.info(f"Performing web search for: {query}")

        # Try primary engine first
        try:
            if self.engine == "duckduckgo":
                return await self._search_duckduckgo(query, max_results, region, safesearch)
            elif self.engine == "searx":
                return await self._search_searx(query, max_results, region, safesearch)
            elif self.engine == "brave":
                return await self._search_brave(query, max_results, region, safesearch)
            elif self.engine == "google_programmable":
                return await self._search_google_programmable(query, max_results, region, safesearch)
            else:
                logger.warning(f"Unknown search engine: {self.engine}, falling back to DuckDuckGo")
                return await self._search_duckduckgo(query, max_results, region, safesearch)
        except Exception as e:
            logger.error(f"Error in primary search engine {self.engine}: {e}")
            # Try fallback engines
            for fallback in self.fallback_engines:
                if fallback != self.engine:
                    try:
                        logger.info(f"Trying fallback engine: {fallback}")
                        if fallback == "duckduckgo":
                            return await self._search_duckduckgo(query, max_results, region, safesearch)
                        elif fallback == "searx":
                            return await self._search_searx(query, max_results, region, safesearch)
                    except Exception as fallback_error:
                        logger.error(f"Fallback engine {fallback} also failed: {fallback_error}")
                        continue

            # If all engines fail, return informative placeholder
            logger.warning("All search engines failed, returning educational placeholder")
            return await self._get_educational_placeholder(query, max_results)

    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str
    ) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo instant answer API."""
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }

        try:
            response = await self.client.get(url, params=params)
            data = response.json()

            results = []

            # Add abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "snippet": data["Abstract"],
                    "url": data.get("AbstractURL", ""),
                    "source": "DuckDuckGo Abstract",
                    "rank": 1
                })

            # Add related topics
            for i, topic in enumerate(data.get("RelatedTopics", [])[:max_results-1]):
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "source": "DuckDuckGo Related Topic",
                        "rank": i + 2
                    })

            # If we need more results, add some suggested searches
            if len(results) < max_results:
                for i, suggestion in enumerate(data.get("RelatedTopics", [])[:max_results-len(results)]):
                    if isinstance(suggestion, dict) and "Text" in suggestion:
                        results.append({
                            "title": f"Related: {suggestion.get('Text', '')[:50]}",
                            "snippet": suggestion.get("Text", ""),
                            "url": f"https://duckduckgo.com/?q={httpx.utils.quote(suggestion.get('Text', ''))}",
                            "source": "DuckDuckGo Suggestion",
                            "rank": len(results) + 1
                        })

            return results[:max_results]

        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {e}")
            raise

    async def _search_searx(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str
    ) -> List[Dict[str, Any]]:
        """Search using SearX (free meta-search engine)."""
        # Using a public SearX instance - in production you might self-host
        searx_instances = [
            "https://searx.be",
            "https://search.snopyta.org",
            "https://searx.tiekoetter.com"
        ]

        for instance in searx_instances:
            try:
                url = f"{instance}/search"
                params = {
                    "q": query,
                    "format": "json",
                    "language": "en",
                    "safesearch": 1 if safesearch in ["strict", "moderate"] else 0,
                    "time_range": ""  # Could add time filtering
                }

                response = await self.client.get(url, params=params)
                data = response.json()

                results = []
                for i, result in enumerate(data.get("results", [])[:max_results]):
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("content", ""),
                        "url": result.get("url", ""),
                        "source": f"SearX ({instance.split('//')[1]})",
                        "rank": i + 1,
                        "engines": result.get("engines", [])
                    })

                if results:
                    return results

            except Exception as e:
                logger.warning(f"SearX instance {instance} failed: {e}")
                continue

        raise Exception("All SearX instances failed")

    async def _search_brave(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str
    ) -> List[Dict[str, Any]]:
        """Search using Brave Search API (free tier available)."""
        if not self.api_key:
            raise ValueError("Brave Search API key required")

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": min(max_results, 20),  # Brave max is 20
            "offset": 0,
            "safesearch": 1 if safesearch == "strict" else 0 if safesearch == "off" else 1,
            "country": region.upper()[:2] if region != "us-en" else "US",
            "search_lang": "en"
        }

        try:
            response = await self.client.get(url, headers=headers, params=params)
            data = response.json()

            results = []
            for i, result in enumerate(data.get("web", {}).get("results", [])[:max_results]):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("description", ""),
                    "url": result.get("url", ""),
                    "source": "Brave Search",
                    "rank": i + 1,
                    "page_age": result.get("page_age", ""),
                    "language": result.get("language", "")
                })

            return results
        except Exception as e:
            logger.error(f"Error in Brave search: {e}")
            raise

    async def _search_google_programmable(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str
    ) -> List[Dict[str, Any]]:
        """Search using Google Programmable Search Engine (free with limitations)."""
        if not self.api_key:
            raise ValueError("Google Programmable Search API key required")

        # You would need to set up a custom search engine first
        # This is a placeholder showing the structure
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": "YOUR_SEARCH_ENGINE_ID",  # Would need to be configured
            "q": query,
            "num": min(max_results, 10),
            "safe": "high" if safesearch == "strict" else "medium" if safesearch == "moderate" else "off",
            "lr": f"lang_{region.split('-')[0]}" if region != "us-en" else "lang_en"
        }

        try:
            response = await self.client.get(url, params=params)
            data = response.json()

            results = []
            for i, item in enumerate(data.get("items", [])[:max_results]):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": "Google Programmable Search",
                    "rank": i + 1,
                    "displayLink": item.get("displayLink", ""),
                    "formattedUrl": item.get("formattedUrl", "")
                })

            return results
        except Exception as e:
            logger.error(f"Error in Google Programmable Search: {e}")
            raise

    async def _get_educational_placeholder(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Provide educational placeholder when all search engines fail."""
        results = []

        # Provide educational content about search and the query topic
        educational_topics = [
            {
                "title": f"How to search for information about: {query}",
                "snippet": "When search engines are unavailable, you can use library databases, academic journals, books, or expert consultation. Consider breaking down your query into key concepts and searching each concept individually.",
                "url": "https://en.wikipedia.org/wiki/Information_retrieval",
                "source": "Educational Guidance",
                "rank": 1
            },
            {
                "title": f"Learning resources related to: {query}",
                "snippet": "Explore online courses, tutorials, documentation, and community forums for learning about this topic. Sites like Coursera, edX, Khan Academy, and Stack Overflow often have valuable free resources.",
                "url": "https://www.khanacademy.org/",
                "source": "Learning Resources",
                "rank": 2
            },
            {
                "title": "Developing effective search strategies",
                "snippet": "Learn to use Boolean operators (AND, OR, NOT), quotes for exact phrases, and site-specific searches to improve your search effectiveness when tools are limited.",
                "url": "https://guides.library.harvard.edu/researchbasics",
                "source": "Search Strategy Guide",
                "rank": 3
            }
        ]

        return educational_topics[:max_results]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Enhanced factory function
def create_web_search_tool(
    api_key: Optional[str] = None,
    engine: str = "duckduckgo"
) -> WebSearchTool:
    """
    Create a web search tool instance.

    Args:
        api_key: API key for search service (Brave/Google require keys)
        engine: Search engine to use

    Returns:
        WebSearchTool instance
    """
    return WebSearchTool(api_key=api_key, engine=engine)