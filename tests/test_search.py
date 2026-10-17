"""Offline tests use the real graph, LangChain tools and MCP HTTP client.

Only HTTP responses and model decisions are scripted; no Ollama server is used.
"""

import asyncio
import json
import os
import unittest
from unittest.mock import patch

import httpx
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import ToolException

from app import build_agent
from search_provider import (
    MCP_URL, USER_AGENT, DisabledSearch, ParallelSearch, create_search,
)
import tool


SOURCE = "Ada Lovelace biography https://example.org/ada"
REAL_CLIENT = httpx.AsyncClient


class ScriptedModel:
    """Request Alfred's real tool, then consume its ToolMessage."""

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, messages):
        if isinstance(messages[-1], ToolMessage):
            return AIMessage(content="From search: " + messages[-1].content)
        return AIMessage(content="", tool_calls=[{
            "name": "web_search_tool", "args": {"query": "Ada Lovelace biography"},
            "id": "search-1", "type": "tool_call",
        }])


class MCPServer:
    """Wire-level MCP fixture consumed by the SDK's Streamable HTTP transport."""

    def __init__(self, mode="success"):
        self.mode = mode
        self.requests = []
        self.clients = []
        self.started = asyncio.Event()
        self.cancelled = asyncio.Event()

    def client(self, **kwargs):
        client = REAL_CLIENT(transport=httpx.MockTransport(self.respond), **kwargs)
        self.clients.append(client)
        return client

    async def respond(self, request):
        self.requests.append(request)
        data = json.loads(request.content)
        method = data["method"]
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "initialize":
            result = {
                "protocolVersion": data["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fixture", "version": "1"},
            }
        elif method == "tools/list":
            result = {"tools": [{
                "name": "web_search", "description": "Search the web",
                "inputSchema": {"type": "object", "properties": {
                    "objective": {"type": "string"},
                    "search_queries": {"type": "array", "items": {"type": "string"}},
                }, "required": ["objective", "search_queries"]},
            }]}
        elif method == "tools/call":
            self.started.set()
            if self.mode == "wait":
                try:
                    await asyncio.Event().wait()
                finally:
                    self.cancelled.set()
            if self.mode == "network":
                raise httpx.ConnectError("connection unavailable", request=request)
            result = {
                "content": [{"type": "text", "text": (
                    "Search quota exceeded" if self.mode == "error" else SOURCE
                )}],
                "isError": self.mode == "error",
            }
        else:
            raise AssertionError("Unexpected MCP method: " + method)
        return httpx.Response(200, json={
            "jsonrpc": "2.0", "id": data["id"], "result": result,
        })


def graph():
    return build_agent(ScriptedModel(), [tool.web_search_tool])


def request_state():
    return {"messages": [HumanMessage(content="Tell me about Ada Lovelace")]}


def thread_config():
    return {"configurable": {"thread_id": "test-thread"}}


class SearchTests(unittest.TestCase):
    def test_fresh_default_and_explicit_duckduckgo(self):
        from langchain_community.tools import DuckDuckGoSearchRun

        for env in ({}, {"ALFRED_SEARCH_PROVIDER": "duckduckgo"}):
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True):
                backend = create_search()
                self.assertIsInstance(backend, DuckDuckGoSearchRun)
                with patch.object(tool, "search", backend), patch.object(
                    DuckDuckGoSearchRun, "run", return_value="DuckDuckGo result"
                ) as run:
                    result = graph().invoke(request_state(), thread_config())
                run.assert_called_once_with("Ada Lovelace biography")
                self.assertEqual(result["messages"][-1].content,
                                 "From search: DuckDuckGo result")

    def test_explicit_selection_and_invalid_setting(self):
        with patch.dict(os.environ, {"ALFRED_SEARCH_PROVIDER": "parallel"}, clear=True):
            self.assertIsInstance(create_search(), ParallelSearch)
            self.assertIsInstance(create_search("disabled"), DisabledSearch)
        with self.assertRaisesRegex(ValueError, "must be"):
            create_search("paralell")

    def test_disabled_search_never_connects(self):
        with patch.dict(os.environ, {"ALFRED_SEARCH_PROVIDER": "disabled"}, clear=True):
            with patch.object(tool, "search", create_search()), patch(
                "httpx.AsyncClient", side_effect=AssertionError("network forbidden")
            ):
                result = graph().invoke(request_state(), thread_config())
        self.assertIn("disabled", result["messages"][-1].content)

    def test_sync_graph_consumes_parallel_result(self):
        server = MCPServer()
        with patch.dict(os.environ, {"ALFRED_SEARCH_PROVIDER": "parallel"}, clear=True):
            with patch.object(tool, "search", create_search()), patch(
                "httpx.AsyncClient", side_effect=server.client
            ):
                result = graph().invoke(request_state(), thread_config())
        self.assertEqual(result["messages"][-1].content, "From search: " + SOURCE)
        self.assertEqual(result["messages"][-2].name, "web_search_tool")
        self.assert_requests(server)

    def assert_requests(self, server):
        self.assertTrue(server.requests)
        methods = []
        for request in server.requests:
            self.assertEqual(str(request.url), MCP_URL)
            self.assertEqual(request.headers["user-agent"], USER_AGENT)
            self.assertNotIn("authorization", request.headers)
            data = json.loads(request.content)
            methods.append(data["method"])
            if data["method"] == "tools/call":
                self.assertEqual(data["params"]["name"], "web_search")
                self.assertEqual(data["params"]["arguments"], {
                    "objective": "Ada Lovelace biography",
                    "search_queries": ["Ada Lovelace biography"],
                })
        self.assertIn("initialize", methods)
        self.assertIn("tools/list", methods)
        self.assertIn("tools/call", methods)
        self.assertTrue(all(c.is_closed for c in server.clients))

    def test_server_and_network_errors_reach_agent_without_fallback(self):
        for mode in ("error", "network"):
            with self.subTest(mode=mode):
                server = MCPServer(mode)
                with patch.object(tool, "search", create_search("parallel")), patch(
                    "httpx.AsyncClient", side_effect=server.client
                ), patch("search_provider.create_search", side_effect=AssertionError("fallback")):
                    result = graph().invoke(request_state(), thread_config())
                self.assertIn("Parallel search failed", result["messages"][-1].content)
                if mode == "error":
                    self.assertIn("Search quota exceeded", result["messages"][-1].content)
                else:
                    self.assertIn("connection unavailable", result["messages"][-1].content)
                self.assertEqual(result["messages"][-2].status, "error")

    def test_tool_allowlist_prevents_search(self):
        with patch("httpx.AsyncClient", side_effect=AssertionError("network forbidden")):
            agent = build_agent(ScriptedModel(), [tool.get_weather_tool])
            result = agent.invoke(request_state(), thread_config())
        self.assertIn("not a valid tool", result["messages"][-1].content)

    def test_timeout_reaches_agent_and_closes_transport(self):
        server = MCPServer("wait")
        with patch.object(tool, "search", ParallelSearch(timeout=0.1)), patch(
            "httpx.AsyncClient", side_effect=server.client
        ):
            result = graph().invoke(request_state(), thread_config())
        self.assertIn("timed out", result["messages"][-1].content)
        self.assertTrue(server.cancelled.is_set())
        self.assertTrue(all(c.is_closed for c in server.clients))

    def test_blank_query_makes_no_request(self):
        with patch("httpx.AsyncClient", side_effect=AssertionError("network forbidden")):
            with self.assertRaisesRegex(ToolException, "must not be empty"):
                ParallelSearch().run("  ")

    def test_existing_search_override_and_news_query(self):
        class Override:
            def run(self, query):
                return "Override: " + query

        with patch.object(tool, "search", Override()):
            self.assertEqual(tool.web_search_tool.invoke({"query": "Ada"}), "Override: Ada")
            self.assertEqual(tool.latest_news_tool.invoke({"topic": "Ada"}),
                             "Override: latest news about Ada")


class AsyncSearchTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_graph_consumes_result(self):
        server = MCPServer()
        with patch.object(tool, "search", create_search("parallel")), patch(
            "httpx.AsyncClient", side_effect=server.client
        ):
            result = await graph().ainvoke(request_state(), thread_config())
        self.assertEqual(result["messages"][-1].content, "From search: " + SOURCE)
        SearchTests().assert_requests(server)

    async def test_cancellation_reaches_transport(self):
        server = MCPServer("wait")
        with patch.object(tool, "search", create_search("parallel")), patch(
            "httpx.AsyncClient", side_effect=server.client
        ):
            task = asyncio.create_task(graph().ainvoke(request_state(), thread_config()))
            await asyncio.wait_for(server.started.wait(), timeout=5)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertTrue(server.cancelled.is_set())
        self.assertTrue(all(c.is_closed for c in server.clients))


if __name__ == "__main__":
    unittest.main()
