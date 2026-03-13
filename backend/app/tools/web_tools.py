"""Web-related tools for internet operations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timezone
import logging

from app.tools.base import BaseTool, ToolMetadata, ToolCategory, ToolError


# ========== Web Search Tool ==========

class WebSearchInput(BaseModel):
    """Web search input model."""

    query: str = Field(..., description="Search query string")
    num_results: int = Field(default=10, ge=1, le=100, description="Number of results")
    language: str = Field(default="en", description="Language code")
    country: str = Field(default="us", description="Country code")
    safe_search: bool = Field(default=True, description="Enable safe search")


class WebSearchResult(BaseModel):
    """Web search result item."""

    title: str
    url: str
    snippet: str
    display_url: Optional[str] = None
    date_published: Optional[datetime] = None


class WebSearchOutput(BaseModel):
    """Web search output model."""

    query: str
    results: List[WebSearchResult]
    total_results: Optional[int] = None
    search_time_ms: Optional[float] = None


class WebSearchTool(BaseTool[WebSearchInput, WebSearchOutput]):
    """Tool for performing web searches.

    Supports multiple search engines (Google, Bing) via API.
    """

    metadata = ToolMetadata(
        name="web_search",
        description="Search the web using search engine APIs",
        category=ToolCategory.WEB,
        version="1.0.0",
        tags=["search", "web", "research"],
        requires_auth=True,
        rate_limit_per_minute=60,
        timeout_seconds=30.0,
    )

    InputModel = WebSearchInput
    OutputModel = WebSearchOutput

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize web search tool.

        Args:
            config: Configuration with API keys.
        """
        super().__init__(config)
        self.search_engine = self.config.get("search_engine", "google")
        self.api_key = self.config.get("api_key")
        self.cse_id = self.config.get("cse_id")  # For Google Custom Search

    async def _execute(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Execute web search.

        Args:
            input_data: Search parameters.

        Returns:
            WebSearchOutput: Search results.
        """
        if self.search_engine == "google":
            return await self._google_search(input_data)
        elif self.search_engine == "bing":
            return await self._bing_search(input_data)
        else:
            raise ToolError(f"Unsupported search engine: {self.search_engine}")

    async def _google_search(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Perform Google Custom Search.

        Args:
            input_data: Search parameters.

        Returns:
            WebSearchOutput: Search results.
        """
        import httpx

        if not self.api_key or not self.cse_id:
            # Return mock results for development
            return self._mock_search_results(input_data)

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": input_data.query,
            "num": min(input_data.num_results, 10),
            "lr": f"lang_{input_data.language}",
            "safe": "active" if input_data.safe_search else "off",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("items", []):
            results.append(
                WebSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    display_url=item.get("displayLink"),
                )
            )

        return WebSearchOutput(
            query=input_data.query,
            results=results,
            total_results=int(data.get("searchInformation", {}).get("totalResults", 0)),
            search_time_ms=float(data.get("searchInformation", {}).get("searchTime", 0)) * 1000,
        )

    async def _bing_search(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Perform Bing Search.

        Args:
            input_data: Search parameters.

        Returns:
            WebSearchOutput: Search results.
        """
        import httpx

        if not self.api_key:
            return self._mock_search_results(input_data)

        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": input_data.query,
            "count": min(input_data.num_results, 50),
            "mkt": f"{input_data.language}-{input_data.country.upper()}",
            "safeSearch": "Moderate" if input_data.safe_search else "Off",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append(
                WebSearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    display_url=item.get("displayUrl"),
                )
            )

        return WebSearchOutput(
            query=input_data.query,
            results=results,
            total_results=data.get("webPages", {}).get("totalEstimatedMatches"),
        )

    def _mock_search_results(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Generate mock search results for development.

        Args:
            input_data: Search parameters.

        Returns:
            WebSearchOutput: Mock results.
        """
        self._logger.warning("Using mock search results (no API key configured)")
        return WebSearchOutput(
            query=input_data.query,
            results=[
                WebSearchResult(
                    title=f"Result {i} for {input_data.query}",
                    url=f"https://example.com/result-{i}",
                    snippet=f"This is a mock search result for query: {input_data.query}",
                )
                for i in range(1, min(input_data.num_results + 1, 6))
            ],
            total_results=100,
        )


# ========== Web Scraper Tool ==========

class WebScraperInput(BaseModel):
    """Web scraper input model."""

    url: HttpUrl = Field(..., description="URL to scrape")
    extract_text: bool = Field(default=True, description="Extract main text content")
    extract_links: bool = Field(default=False, description="Extract all links")
    extract_images: bool = Field(default=False, description="Extract image URLs")
    extract_metadata: bool = Field(default=True, description="Extract page metadata")
    css_selector: Optional[str] = Field(default=None, description="CSS selector for targeted extraction")


class WebScraperOutput(BaseModel):
    """Web scraper output model."""

    url: str
    title: Optional[str] = None
    text_content: Optional[str] = None
    links: List[Dict[str, str]] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status_code: int = 200


class WebScraperTool(BaseTool[WebScraperInput, WebScraperOutput]):
    """Tool for scraping web page content."""

    metadata = ToolMetadata(
        name="web_scraper",
        description="Extract content from web pages",
        category=ToolCategory.WEB,
        version="1.0.0",
        tags=["scraping", "web", "extraction"],
        rate_limit_per_minute=30,
        timeout_seconds=60.0,
    )

    InputModel = WebScraperInput
    OutputModel = WebScraperOutput

    async def _execute(self, input_data: WebScraperInput) -> WebScraperOutput:
        """Execute web scraping.

        Args:
            input_data: Scraping parameters.

        Returns:
            WebScraperOutput: Scraped content.
        """
        import httpx
        from bs4 import BeautifulSoup

        url = str(input_data.url)
        self._logger.info(f"Scraping URL: {url}")

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        output = WebScraperOutput(
            url=url,
            status_code=response.status_code,
        )

        # Extract metadata
        if input_data.extract_metadata:
            output.metadata = self._extract_metadata(soup)

        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            output.title = title_tag.get_text(strip=True)

        # Extract text content
        if input_data.extract_text:
            if input_data.css_selector:
                elements = soup.select(input_data.css_selector)
                output.text_content = "\n".join(
                    elem.get_text(strip=True) for elem in elements
                )
            else:
                # Remove script and style tags
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                output.text_content = soup.get_text(separator="\n", strip=True)

        # Extract links
        if input_data.extract_links:
            output.links = [
                {"text": link.get_text(strip=True), "href": link.get("href", "")}
                for link in soup.find_all("a", href=True)
            ][:100]  # Limit to 100 links

        # Extract images
        if input_data.extract_images:
            output.images = [
                img.get("src", "")
                for img in soup.find_all("img", src=True)
            ][:50]  # Limit to 50 images

        return output

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata.

        Args:
            soup: BeautifulSoup object.

        Returns:
            Dict: Metadata dictionary.
        """
        metadata = {}

        # Meta description
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            metadata["description"] = desc["content"]

        # Meta keywords
        keywords = soup.find("meta", attrs={"name": "keywords"})
        if keywords and keywords.get("content"):
            metadata["keywords"] = keywords["content"]

        # Author
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["author"] = author["content"]

        # Open Graph tags
        for og_tag in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            property_name = og_tag.get("property", "")
            content = og_tag.get("content", "")
            if property_name and content:
                metadata[property_name] = content

        return metadata


# ========== API Client Tool ==========

class APIClientInput(BaseModel):
    """API client input model."""

    url: HttpUrl = Field(..., description="API endpoint URL")
    method: str = Field(default="GET", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    json_body: Optional[Dict[str, Any]] = Field(default=None, description="JSON request body")
    timeout_seconds: float = Field(default=30.0, description="Request timeout")
    follow_redirects: bool = Field(default=True, description="Follow redirects")


class APIClientOutput(BaseModel):
    """API client output model."""

    status_code: int
    headers: Dict[str, str]
    body: Any
    elapsed_ms: float
    url: str


class APIClientTool(BaseTool[APIClientInput, APIClientOutput]):
    """Generic HTTP client tool for API interactions."""

    metadata = ToolMetadata(
        name="api_client",
        description="Make HTTP requests to APIs",
        category=ToolCategory.WEB,
        version="1.0.0",
        tags=["http", "api", "rest"],
        rate_limit_per_minute=100,
        timeout_seconds=60.0,
    )

    InputModel = APIClientInput
    OutputModel = APIClientOutput

    async def _execute(self, input_data: APIClientInput) -> APIClientOutput:
        """Execute API request.

        Args:
            input_data: Request parameters.

        Returns:
            APIClientOutput: Response data.
        """
        import httpx

        self._logger.info(f"{input_data.method} {input_data.url}")

        async with httpx.AsyncClient(
            follow_redirects=input_data.follow_redirects,
            timeout=input_data.timeout_seconds,
        ) as client:
            start_time = datetime.now(timezone.utc)

            response = await client.request(
                method=input_data.method.upper(),
                url=str(input_data.url),
                headers=input_data.headers,
                params=input_data.params if input_data.params else None,
                json=input_data.json_body if input_data.json_body else None,
            )

            elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            # Try to parse JSON response
            try:
                body = response.json()
            except Exception:
                body = response.text

            return APIClientOutput(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
                elapsed_ms=elapsed_ms,
                url=str(response.url),
            )


# ========== RSS Feed Tool ==========

class RSSFeedInput(BaseModel):
    """RSS feed input model."""

    feed_url: HttpUrl = Field(..., description="RSS feed URL")
    num_items: int = Field(default=20, ge=1, le=100, description="Number of items to retrieve")
    include_content: bool = Field(default=False, description="Include full content")


class RSSFeedItem(BaseModel):
    """RSS feed item."""

    title: str
    link: str
    published: Optional[datetime] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None


class RSSFeedOutput(BaseModel):
    """RSS feed output model."""

    feed_title: Optional[str] = None
    feed_link: Optional[str] = None
    feed_description: Optional[str] = None
    items: List[RSSFeedItem] = Field(default_factory=list)


class RSSFeedTool(BaseTool[RSSFeedInput, RSSFeedOutput]):
    """Tool for parsing RSS/Atom feeds."""

    metadata = ToolMetadata(
        name="rss_feed",
        description="Parse and extract content from RSS/Atom feeds",
        category=ToolCategory.WEB,
        version="1.0.0",
        tags=["rss", "feed", "news"],
        timeout_seconds=30.0,
    )

    InputModel = RSSFeedInput
    OutputModel = RSSFeedOutput

    async def _execute(self, input_data: RSSFeedInput) -> RSSFeedOutput:
        """Execute RSS feed parsing.

        Args:
            input_data: Feed parameters.

        Returns:
            RSSFeedOutput: Parsed feed data.
        """
        import httpx
        import feedparser

        self._logger.info(f"Parsing RSS feed: {input_data.feed_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(input_data.feed_url))
            response.raise_for_status()

        feed = feedparser.parse(response.text)

        items = []
        for entry in feed.entries[: input_data.num_items]:
            item = RSSFeedItem(
                title=entry.get("title", ""),
                link=entry.get("link", ""),
                summary=entry.get("summary", ""),
            )

            # Parse published date
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                item.published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            # Get author
            if hasattr(entry, "author"):
                item.author = entry.author

            # Get full content
            if input_data.include_content:
                item.content = entry.get("content", [{}])[0].get("value") or entry.get("description")

            items.append(item)

        return RSSFeedOutput(
            feed_title=feed.feed.get("title"),
            feed_link=feed.feed.get("link"),
            feed_description=feed.feed.get("description"),
            items=items,
        )
