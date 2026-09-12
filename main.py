"""
Entry point: run this to scrape + extract intel for a list of domains.

Usage:
    python main.py
"""
import json
from dotenv import load_dotenv

from scraper import scrape_domain
from cleaner import clean_all_pages
from extractor import extract_company_intel
from models import CompanyIntel

load_dotenv()

TARGET_DOMAINS = [
    "postman.com",
    "supabase.com",
    "vapi.ai",
]


def process_domain(domain: str) -> CompanyIntel:
    errors = []

    # Step 1: scrape
    pages = scrape_domain(domain)
    scrape_errors = pages.pop("_errors", [])
    errors.extend(scrape_errors)

    if not pages:
        # Total failure — return a stub record instead of crashing
        return CompanyIntel(
            domain=domain,
            company_overview="",
            target_audience="",
            contact_emails=[],
            team_members=[],
            confidence_score=0.0,
            pages_scraped=[],
            errors=errors + ["Could not fetch any pages for this domain."],
        )

    # Step 2: clean
    cleaned_text = clean_all_pages(pages)

    # Step 3: LLM extraction
    try:
        raw = extract_company_intel(domain, cleaned_text)
        return CompanyIntel(
            domain=domain,
            pages_scraped=list(pages.keys()),
            errors=errors,
            **raw,
        )
    except Exception as e:
        errors.append(f"LLM extraction failed: {e}")
        return CompanyIntel(
            domain=domain,
            company_overview="",
            target_audience="",
            contact_emails=[],
            team_members=[],
            confidence_score=0.0,
            pages_scraped=list(pages.keys()),
            errors=errors,
        )


def main():
    results = []
    for domain in TARGET_DOMAINS:
        print(f"Processing {domain} ...")
        try:
            result = process_domain(domain)
        except Exception as e:
            # last-resort safety net — one bad domain should never kill the run
            print(f"  ! Unexpected failure on {domain}: {e}")
            result = CompanyIntel(
                domain=domain,
                company_overview="",
                target_audience="",
                contact_emails=[],
                team_members=[],
                confidence_score=0.0,
                errors=[f"Unexpected failure: {e}"],
            )
        results.append(result.model_dump())
        print(f"  -> confidence: {result.confidence_score}, errors: {len(result.errors)}")

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nDone. Results written to output.json")


if __name__ == "__main__":
    main()
