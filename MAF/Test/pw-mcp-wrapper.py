import os
from typing import Any, Dict

import requests
from agent_framework import tool

from ..config import AzureConfig

_sessions: Dict[str, Dict[str, Any]] = {}


def _mcp_call(base_url: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(
        f"{base_url}/mcp",
        json={"method": method, "params": params},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


@tool
def start_session(url: str, config: AzureConfig = AzureConfig()) -> str:
    """
    Start a Playwright MCP session and navigate to url.
    Requires env var PLAYWRIGHT_MCP_URL (e.g. https://your-mcp-host).
    Returns session_id.
    """
    base_url = os.environ.get("PLAYWRIGHT_MCP_URL")
    if not base_url:
        raise RuntimeError("PLAYWRIGHT_MCP_URL is not set")

    # Create a new MCP session
    session_resp = _mcp_call(base_url, "session.new", {})
    session_id = session_resp.get("result")
    if not session_id:
        raise RuntimeError(f"Failed to create MCP session: {session_resp}")

    _sessions[session_id] = {"base_url": base_url}

    # Navigate
    _mcp_call(
        base_url,
        "page.goto",
        {"session": session_id, "url": url, "waitUntil": "domcontentloaded"},
    )
    return session_id


@tool
def run_test(session_id: str, js_code: str, config: AzureConfig = AzureConfig()):
    """
    Run js_code (actions) then run custom snapshot JS (config.pw_dom.js_new)
    via Playwright MCP and return the snapshot result.
    """
    session = _sessions.get(session_id)
    if not session:
        raise RuntimeError(f"Session not found: {session_id}")
    base_url = session["base_url"]

    if js_code:
        _mcp_call(
            base_url,
            "page.evaluate",
            {"session": session_id, "expression": js_code},
        )

    snap_resp = _mcp_call(
        base_url,
        "page.evaluate",
        {"session": session_id, "expression": config.pw_dom.js_new},
    )
    return snap_resp.get("result")


@tool
def close_session(session_id: str) -> None:
    """
    Close session in Playwright MCP.
    """
    session = _sessions.pop(session_id, None)
    if not session:
        return
    base_url = session["base_url"]
    _mcp_call(base_url, "session.close", {"session": session_id})
