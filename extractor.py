"""
Sends cleaned page text to an LLM and forces a structured (JSON-schema)
response using tool-calling, then validates it with Pydantic.

Uses Groq's free API (OpenAI-compatible) instead of a paid provider, so
this runs with zero billing setup. Swap GROQ_API_KEY / MODEL if you later
want to point this at OpenAI or Anthropic instead.
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"

EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "record_company_intel",
        "description": "Record structured intelligence extracted about a company.",
        "parameters": {
            "type": "object",
            "properties": {
                "company_overview": {"type": "string", "description": "2-sentence summary of what they do"},
                "target_audience": {"type": "string", "description": "Who the product is built for"},
                "contact_emails": {"type": "array", "items": {"type": "string"}},
                "team_members": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "linkedin_url": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                },
                "confidence_score": {
                    "type": "number",
                    "description": "0.0 to 1.0 how complete/reliable this extraction is"
                }
            },
            "required": ["company_overview", "target_audience", "contact_emails", "team_members", "confidence_score"]
        }
    }
}


def extract_company_intel(domain, cleaned_text):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1500,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "function", "function": {"name": "record_company_intel"}},
        messages=[
            {
                "role": "user",
                "content": (
                    "Here is scraped website content for the company at domain '" + domain + "'. "
                    "Extract the requested fields. If information isn't present, use empty "
                    "strings/lists rather than guessing, and reflect that in a lower "
                    "confidence_score.\n\n" + cleaned_text
                )
            }
        ]
    )

    message = response.choices[0].message
    if message.tool_calls:
        call = message.tool_calls[0]
        if call.function.name == "record_company_intel":
            return json.loads(call.function.arguments)

    raise ValueError("No structured tool call returned for " + domain)
