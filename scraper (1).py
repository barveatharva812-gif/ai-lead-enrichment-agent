"""
Handles fetching pages with a headless browser (Playwright), including
JS-rendered content, and discovering likely-useful subpages.
"""
import re
from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Subpage keywords we look for when crawling internal links
SUBPAGE_KEYWORDS = ["about", "team", "company", "contact", "leadership", "pricing"]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _normalize_domain(domain: str) -> str:
    domain = domain.strip()
    if not domain.startswith("http"):
        domain = f"https://{domain}"
    return domain.rstrip("/")


def discover_subpage_links(html: str, base_url: str) -> List[str]:
    """Very lightweight href scan for links matching our keywords."""
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    found = set()
    for href in hrefs:
        low = href.lower()
        if any(kw in low for kw in SUBPAGE_KEYWORDS):
            if href.startswith("http"):
                found.add(href.split("#")[0])
            elif href.startswith("/"):
                found.add(base_url + href.split("#")[0])
    return list(found)[:5]  # cap so we don't crawl the whole site


def fetch_page(page, url: str, timeout_ms: int = 45000) -> str:
    """Fetch a single page, return rendered HTML. Raises on failure."""
    page.goto(url, timeout=timeout_ms, wait_until="networkidle")
    return page.content()


def scrape_domain(domain: str, max_subpages: int = 4) -> Dict[str, str]:
    """
    Returns a dict of {url: raw_html} for the homepage + discovered subpages.
    Never raises — failures are swallowed and just mean fewer pages returned.
    Caller should check the returned dict; empty dict means total failure.
    """
    base_url = _normalize_domain(domain)
    pages: Dict[str, str] = {}
    errors: List[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        # 1. Homepage
        try:
            html = fetch_page(page, base_url)
            pages[base_url] = html
        except PlaywrightTimeout:
            errors.append(f"Timeout fetching homepage: {base_url}")
        except Exception as e:
            errors.append(f"Failed to fetch homepage {base_url}: {e}")

        # 2. Discover + fetch subpages (only if homepage worked)
        if base_url in pages:
            subpage_links = discover_subpage_links(pages[base_url], base_url)
            for link in subpage_links[:max_subpages]:
                try:
                    pages[link] = fetch_page(page, link)
                except PlaywrightTimeout:
                    errors.append(f"Timeout fetching subpage: {link}")
                except Exception as e:
                    errors.append(f"Failed to fetch subpage {link}: {e}")

        browser.close()

    pages["_errors"] = errors  # smuggled through; caller pops this off
    return pages
