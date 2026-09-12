"""
Pydantic schemas for the structured data we want the LLM to extract.
Keeping this separate makes it easy to tweak fields later without
touching the scraping or LLM-calling logic.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str
    role: Optional[str] = None
    linkedin_url: Optional[str] = None


class CompanyIntel(BaseModel):
    domain: str
    company_overview: str = Field(..., description="2-sentence summary of what the company does")
    target_audience: str = Field(..., description="Who the product/service is built for")
    contact_emails: List[str] = Field(default_factory=list)
    team_members: List[TeamMember] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)

    # filled in by our own code, not the LLM
    pages_scraped: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
