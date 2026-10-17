"""Search backends for Alfred's existing LangChain tools."""

import asyncio
import os

from langchain_core.tools import ToolException


MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = "alfred-ai-agent (https://github.com/dahiya-04/alfred-ai-agent)"


def _error_text(exc: Exception) -> str:
    if isinstance(exc, ExceptionGroup):
        return "; ".join(_error_text(child) for child in exc.exceptions)
    return str(exc)


class DisabledSearch:
    def run(self, query: str) -> str:
        raise ToolException("Web search is disabled by ALFRED_SEARCH_PROVIDER=disabled.")

    async def arun(self, query: str) -> str:
        return self.run(query)


class ParallelSearch:
    """Anonymous Search MCP over Streamable HTTP, with a total request deadline."""

    def __init__(self, timeout: float = 30):
        self.timeout = timeout

    def run(self, query: str) -> str:
        # The CLI is synchronous; async agent callers use arun directly so that
        # cancellation reaches the MCP transport rather than a background thread.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.arun(query))
        raise ToolException("Use web_search_tool.ainvoke() inside an async event loop.")

    async def arun(self, query: str) -> str:
        if not query.strip():
            raise ToolException("Search query must not be empty.")

        import anyio
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        try:
            with anyio.fail_after(self.timeout):
                async with httpx.AsyncClient(
                    headers={"User-Agent": USER_AGENT},
                    timeout=self.timeout,
                    follow_redirects=True,
                ) as client:
                    async with streamable_http_client(
                        MCP_URL, http_client=client
                    ) as (read, write, _):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            result = await session.call_tool(
                                "web_search",
                                {"objective": query, "search_queries": [query]},
                            )
        except TimeoutError as exc:
            raise ToolException("Parallel search timed out. Please try again later.") from exc
        except Exception as exc:
            # MCP's transport task groups can wrap server/connection errors.
            # Cancellation is a BaseException and deliberately propagates.
            raise ToolException(f"Parallel search failed: {_error_text(exc)}") from exc

        text = "\n\n".join(
            block.text for block in result.content if block.type == "text"
        )
        if result.isError:
            raise ToolException(f"Parallel search failed: {text}")
        return text or "No search results found."


def create_search(provider: str | None = None):
    """An explicit choice wins; the unconfigured backend stays DuckDuckGo."""
    selected = provider if provider is not None else os.getenv(
        "ALFRED_SEARCH_PROVIDER", "duckduckgo"
    )
    selected = selected.strip().lower()
    if selected == "parallel":
        return ParallelSearch()
    if selected == "disabled":
        return DisabledSearch()
    if selected == "duckduckgo":
        from langchain_community.tools import DuckDuckGoSearchRun

        return DuckDuckGoSearchRun()
    raise ValueError(
        "ALFRED_SEARCH_PROVIDER must be duckduckgo, parallel or disabled."
    )
