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
- **LLM:** Groq (free tier, OpenAI-compatible API) running `openai/gpt-oss-120b`, called via the `openai` Python SDK pointed at Groq's endpoint
- **Structured output validation:** Pydantic

## Setup

python -m pip install -r requirements.txt
python -m playwright install chromium

Create a `.env` file (see `.env.example`) with a free Groq API key from console.groq.com:

GROQ_API_KEY=your_key_here

## Run

python main.py

This scrapes the 3 test domains and writes results to `output.json` (a sample run is included in this repo).

## Project structure

| File | Purpose |
|---|---|
| `scraper.py` | Playwright-based headless browsing, subpage discovery |
| `cleaner.py` | Strips HTML down to clean text to save LLM tokens |
| `extractor.py` | Calls the LLM with a forced-tool-use JSON schema |
| `models.py` | Pydantic schema for the final structured output |
| `main.py` | Orchestrates the pipeline across all domains, with error handling |
| `output.json` | Sample output from a real run against the 3 test domains |

## Design notes

- **Resilience:** every domain is wrapped in try/except in `main.py`, and scraping failures per-page are caught inside `scraper.py`, so one broken subpage or a bot-blocked site never kills the whole run — it just shows up in that domain's `errors` list with a lower `confidence_score`.
- **Token savings:** `cleaner.py` strips scripts/styles/nav/footer and caps each page's text before it ever reaches the LLM.
- **Structured output:** `extractor.py` forces the model to respond via a single tool call matching a strict JSON schema, so there's no free-form text parsing involved.

## Known limitations / next steps

- Subpage discovery is a simple href/keyword scan — could be made smarter with sitemap.xml lookups.
- No external search (SerpAPI/Tavily) yet for finding LinkedIn URLs not on the site itself.
- No cost/token logging yet — could be added by reading `response.usage` from the Groq/OpenAI response in `extractor.py`.

## Operations question answer



**Answer:** Yes

I confirm I have read and understood that this role involves approximately 40% of working hours dedicated to manual lead prospecting, email discovery, and account handling, alongside AI engineering tasks. I'm comfortable with this split — while working on this assignment, I genuinely enjoyed the hands-on process, from debugging scraping issues to getting the structured output working end-to-end, so I'm confident I'll enjoy the mix of manual prospecting work and AI engineering tasks in this role.

**LinkedIn:** https://www.linkedin.com/in/atharva-barve-824764271/


