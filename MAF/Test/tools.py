from agent_framework import Agent, tool
from playwright.sync_api import sync_playwright

from ..config import AzureConfig


# @tool(approval_mode="never_require")
def get_website_dom(url: str, config: AzureConfig = AzureConfig()) -> str:
    """Return the DOM structure of interactable elements in a given website."""
    dom_data = None
    with sync_playwright() as sp:
        os_name = "linux"
        # browser_url = f"{config.secrets.pw_browser_url}?os={os_name}&runId={service_run_id}&api-version=2025-09-01"

        browser_url = f"{config.secrets.pw_browser_url}?os={os_name}"

        browser = sp.chromium.connect(
            ws_endpoint=browser_url,
            headers={
                "Authorization": f"Bearer {config.secrets.pw_agent_token}",
            },
            timeout=30_000,
            # expose_network="<loopback>",
        )
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        dom_data = page.evaluate(config.pw_dom.js_new)
        browser.close()

    return dom_data


print(get_website_dom("https://www.aicamp.ai/login"))
print(get_website_dom("https://white-cliff-0bca3ed00.1.azurestaticapps.net/login"))
