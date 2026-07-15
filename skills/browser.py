"""
Browser automation — JARVIS drives a real browser.
Uses Playwright (pip install playwright && playwright install chromium).

Capabilities:
- fetch & summarize a page's text (feed to the brain)
- fill simple search boxes
- take a screenshot of any site

Safety: never auto-submits forms with personal data;
purchases/logins are intentionally NOT automated.
"""


def _get_browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "Playwright not installed. Run: pip install playwright && playwright install chromium"
    return sync_playwright, None


def read_page(url: str, max_chars: int = 4000) -> str:
    """Open a page and return its visible text (for the brain to summarize)."""
    sp, err = _get_browser()
    if err:
        return err
    try:
        with sp() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            text = page.inner_text("body")
            browser.close()
        text = " ".join(text.split())
        return text[:max_chars]
    except Exception as e:
        return f"Couldn't read that page: {e}"


def screenshot_page(url: str) -> str:
    """Screenshot a webpage to the Pictures folder."""
    sp, err = _get_browser()
    if err:
        return err
    import os
    from datetime import datetime
    try:
        with sp() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            filename = f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(os.path.expanduser("~"), "Pictures", filename)
            page.screenshot(path=path, full_page=True)
            browser.close()
        return f"Page captured to Pictures as {filename}, sir."
    except Exception as e:
        return f"Screenshot failed: {e}"


def research(query: str, brain=None) -> str:
    """
    Light research agent: search DuckDuckGo, read the top result,
    and (if a brain is provided) summarize it.
    """
    sp, err = _get_browser()
    if err:
        return err
    try:
        with sp() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                      timeout=20000, wait_until="domcontentloaded")
            page.wait_for_selector("a[data-testid='result-title-a']", timeout=8000)
            first = page.locator("a[data-testid='result-title-a']").first
            href = first.get_attribute("href")
            browser.close()

        if not href:
            return "No results found, sir."

        content = read_page(href)
        if brain:
            return brain.think(f"Summarize this in 3 sentences: {content[:3000]}")
        return f"Top result ({href}):\n{content[:800]}..."
    except Exception as e:
        return f"Research failed: {e}"
