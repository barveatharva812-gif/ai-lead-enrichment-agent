# AI Lead Enrichment Agent

An autonomous Python agent that scrapes company websites (homepage +
about/team/contact/pricing pages), cleans the content, and uses an LLM
with structured tool-calling to extract company intelligence:

- Company overview (2-sentence summary)
- Target audience / ICP
- Public contact emails
- Key leadership / team members
- A data confidence score (0.0–1.0)

Built for the SoftwareBrio AI Engineer Intern take-home assignment.
Tested against `postman.com`, `supabase.com`, and `vapi.ai`.

## How it works

1. **Scrape** (`scraper.py`) — Playwright (headless Chromium) loads the
   homepage, discovers likely subpages (about/team/contact/pricing) via
   link scanning, and fetches each one. Failures on individual pages are
   caught so one bad page never crashes the whole run.
2. **Clean** (`cleaner.py`) — Strips scripts, styles, SVGs, and nav/footer
   boilerplate with BeautifulSoup, leaving plain readable text and
   capping length per page to keep LLM token usage low.
3. **Extract** (`extractor.py`) — Sends the cleaned text to an LLM using
   forced tool-calling (a strict JSON schema), so the response is always
   valid structured data rather than free-form text to parse.
4. **Orchestrate** (`main.py`) — Loops over all target domains, wraps
   every domain in error handling, and writes results to `output.json`.

## Tech stack

- **Scraping:** Playwright (Chromium, headless)
- **Cleaning:** BeautifulSoup4
- **LLM:** [Groq](https://console.groq.com) (free tier, OpenAI-compatible
  API) running `openai/gpt-oss-120b`, called via the `openai` Python SDK
  pointed at Groq's endpoint
- **Structured output validation:** Pydantic

## Setup

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Create a `.env` file (see `.env.example`) with a free Groq API key from
[console.groq.com](https://console.groq.com):
