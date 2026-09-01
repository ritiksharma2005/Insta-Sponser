from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Lead(BaseModel):
    """Pydantic model representing a potential sponsor lead."""
    lead_id: str
    date_found: str = Field(default_factory=lambda: date.today().isoformat())
    business_name: str
    category: str = Field(default="General")
    subcategory: str = Field(default="General")
    city: str = Field(default="Not Available")
    state: str = Field(default="Not Available")
    country: str = Field(default="India")
    website: str = Field(default="Not Available")
    instagram: str = Field(default="Not Available")
    followers: str = Field(default="Not Available")
    linkedin: str = Field(default="Not Available")
    email: str = Field(default="Not Available")
    phone: str = Field(default="Not Available")
    description: str = Field(default="Not Available")
    target_audience: str = Field(default="Not Available")
    student_relevance: str = Field(default="High")
    youth_relevance: str = Field(default="High")
    geographic_relevance: str = Field(default="India / Gujarat")
    social_activity: str = Field(default="Active")
    growth_signal: str = Field(default="None detected")
    discovery_source: str = Field(default="Web Search API")
    research_date: str = Field(default_factory=lambda: date.today().isoformat())
    lead_score: int = Field(default=50, ge=0, le=100)
    lead_tier: str = Field(default="MEDIUM")  # HOT, HIGH, MEDIUM, LOW
    why_suitable: str = Field(default="")
    suggested_collaboration: str = Field(default="")
    personalized_message: str = Field(default="")
    status: str = Field(default="APPROVAL_PENDING")
    last_contacted: str = Field(default="Not Contacted")
    next_followup: str = Field(default="None")
    response: str = Field(default="No Response")
    notes: str = Field(default="")

    def to_sheets_row(self) -> list:
        """Serializes Lead model to a flat row array matching Google Sheets LEADS schema."""
        return [
            self.lead_id,
            self.date_found,
            self.business_name,
            self.category,
            self.subcategory,
            self.city,
            self.state,
            self.country,
            self.website,
            self.instagram,
            self.followers,
            self.linkedin,
            self.email,
            self.phone,
            self.description,
            self.target_audience,
            self.student_relevance,
            self.youth_relevance,
            self.geographic_relevance,
            self.social_activity,
            self.growth_signal,
            self.discovery_source,
            self.research_date,
            self.lead_score,
            self.lead_tier,
            self.why_suitable,
            self.suggested_collaboration,
            self.personalized_message,
            self.status,
            self.last_contacted,
            self.next_followup,
            self.response,
            self.notes
        ]

class Candidate(BaseModel):
    """Raw unresearched candidate discovered during daily search."""
    business_name: str
    category: str
    city: str = "Not Available"
    website: str = "Not Available"
    instagram: str = "Not Available"
    snippet: str = ""
    source: str = "Web Search"

class SearchHistoryRecord(BaseModel):
    """Search query history record."""
    date: str = Field(default_factory=lambda: date.today().isoformat())
    category: str
    keyword: str
    location: str
    source: str
    candidates_found: int
    qualified_leads: int
    rejected_leads: int

    def to_sheets_row(self) -> list:
        return [
            self.date,
            self.category,
            self.keyword,
            self.location,
            self.source,
            self.candidates_found,
            self.qualified_leads,
            self.rejected_leads
        ]

class OutreachRecord(BaseModel):
    """Outreach action record."""
    lead_id: str
    business: str
    message: str
    generated_date: str = Field(default_factory=lambda: date.today().isoformat())
    approved: bool = False
    sent_date: str = "Not Sent"
    response: str = "Pending"
    followup_date: str = "None"
    status: str = "APPROVAL_PENDING"

    def to_sheets_row(self) -> list:
        return [
            self.lead_id,
            self.business,
            self.message,
            self.generated_date,
            "TRUE" if self.approved else "FALSE",
            self.sent_date,
            self.response,
            self.followup_date,
            self.status
        ]
