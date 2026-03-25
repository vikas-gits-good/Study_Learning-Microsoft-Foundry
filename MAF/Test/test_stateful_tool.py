import uuid
from dataclasses import dataclass
from typing import Dict

from agent_framework import tool
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from ..config import AzureConfig


@dataclass
class SessionState:
    sp: Playwright
    browser: Browser
    page: Page
    url: str


_sessions: Dict[str, SessionState] = {}


@tool
def start_session(url: str, config: AzureConfig = AzureConfig()) -> str:
    """Start a new browser session, navigate to url, return session id."""
    session_id = str(uuid.uuid4())

    sp = sync_playwright().start()
    os_name = "linux"
    browser_url = f"{config.secrets.pw_browser_url}?os={os_name}"
    browser = sp.chromium.connect(
        ws_endpoint=browser_url,
        headers={"Authorization": f"Bearer {config.secrets.pw_agent_token}"},
        timeout=30_000,
    )
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    _sessions[session_id] = SessionState(sp=sp, browser=browser, page=page, url=url)
    return session_id


# def _run_action(session_id: str, js_action: str) -> None:
#     """Internal: run a single action JS snippet in the page."""
#     state = _sessions.get(session_id)
#     if not state:
#         raise RuntimeError(f"Session not found: {session_id}")
#     state.page.evaluate(js_action)


@tool
def run_test(session_id: str, js_code: str, config: AzureConfig = AzureConfig()):
    """Run js_code in the page and return the DOM snapshot."""
    state = _sessions.get(session_id)
    if not state:
        raise RuntimeError(f"Session not found: {session_id}")
    if js_code:
        state.page.evaluate(js_code)
    return state.page.evaluate(config.pw_dom.js_new)


@tool
def close_session(session_id: str) -> None:
    """Close and remove a session."""
    state = _sessions.pop(session_id, None)
    if not state:
        return
    state.browser.close()
    state.sp.stop()


if __name__ == "__main__":
    cfg = AzureConfig()
    sid = start_session("https://www.aicamp.ai/login", cfg)
    dom = run_test(sid, "", cfg)
    print(dom)
    close_session(sid)
