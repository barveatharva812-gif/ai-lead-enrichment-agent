"""
Strips raw HTML down to clean, readable text so we don't burn LLM tokens
feeding it scripts/CSS/SVGs/nav boilerplate.
"""
from bs4 import BeautifulSoup

# Tags that carry no useful text content for our extraction task
STRIP_TAGS = ["script", "style", "svg", "noscript", "iframe", "nav", "footer", "head"]

MAX_CHARS_PER_PAGE = 6000  # rough token-budget guard per page


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    text = soup.get_text(separator="\n")

    # Collapse excessive blank lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)

    return cleaned[:MAX_CHARS_PER_PAGE]


def clean_all_pages(pages: dict) -> str:
    """Combine cleaned text from multiple pages into one context block."""
    parts = []
    for url, html in pages.items():
        if url == "_errors":
            continue
        parts.append(f"=== PAGE: {url} ===\n{clean_html(html)}")
    return "\n\n".join(parts)
