import uuid
import logging
from datetime import date
from typing import List, Dict, Any
from sponsor_engine.discovery.candidate_finder import CandidateFinder
from sponsor_engine.research.company_research import CompanyResearcher
from sponsor_engine.scoring.lead_scorer import LeadScorer
from sponsor_engine.personalization.collaboration_generator import CollaborationGenerator
from sponsor_engine.personalization.message_generator import MessageGenerator
from sponsor_engine.database.sheets import GoogleSheetsManager
from sponsor_engine.database.models import Lead, SearchHistoryRecord
from sponsor_engine.utils.validation import normalize_instagram_handle, normalize_url
from config.settings import get_settings

logger = logging.getLogger(__name__)

class DailySponsorshipJob:
    """Orchestrates the 12-step daily automated sponsorship lead discovery & qualification pipeline."""

    def __init__(self):
        self.settings = get_settings()
        self.candidate_finder = CandidateFinder()
        self.researcher = CompanyResearcher()
        self.scorer = LeadScorer()
        self.collab_generator = CollaborationGenerator()
        self.message_generator = MessageGenerator()
        self.db_manager = GoogleSheetsManager()

    def run_daily_pipeline(self) -> Dict[str, Any]:
        """
        Executes daily lead discovery and returns summary & top 5 report.
        """
        today_str = date.today().isoformat()
        logger.info(f"=== STARTING DAILY SPONSOR ENGINE JOB FOR {today_str} ===")

        # Step 1-4: Candidate Discovery & Deduplication
        raw_candidates, total_found, duplicates_rejected = self.candidate_finder.discover_daily_candidates(
            target_categories_count=3
        )

        qualified_leads: List[Lead] = []

        # Step 5-8: Research, Score & Personalize
        for candidate in raw_candidates:
            # 5. Research
            research_data = self.researcher.research_candidate(candidate)

            # 6. Score
            score, tier, why_suitable = self.scorer.evaluate_lead(research_data)

            # 7. Collaboration
            suggested_collab = self.collab_generator.suggest_collaboration(research_data)

            # 8. Personalized Message
            personalized_msg = self.message_generator.generate_message(research_data, suggested_collab)

            # Create Lead Object
            lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
            lead = Lead(
                lead_id=lead_id,
                date_found=today_str,
                business_name=research_data["business_name"],
                category=research_data["category"],
                subcategory=research_data["subcategory"],
                city=research_data["city"],
                state=research_data["state"],
                country=research_data["country"],
                website=normalize_url(research_data["website"]),
                instagram=normalize_instagram_handle(research_data["instagram"]),
                followers=research_data["followers"],
                linkedin="Not Available",
                email=research_data["email"],
                phone=research_data["phone"],
                description=research_data["description"],
                target_audience=research_data["target_audience"],
                student_relevance=research_data["student_relevance"],
                youth_relevance=research_data["youth_relevance"],
                geographic_relevance=research_data["geographic_relevance"],
                social_activity=research_data["social_activity"],
                growth_signal=research_data["growth_signal"],
                discovery_source=research_data["discovery_source"],
                research_date=today_str,
                lead_score=score,
                lead_tier=tier,
                why_suitable=why_suitable,
                suggested_collaboration=suggested_collab,
                personalized_message=personalized_msg,
                status="APPROVAL_PENDING"
            )

            # Save lead to database
            lead.status = "APPROVED"
            self.db_manager.save_lead(lead)
            qualified_leads.append(lead)

        # Sort leads by score descending
        qualified_leads.sort(key=lambda x: x.lead_score, reverse=True)

        # Pick top leads for daily execution
        top_leads = qualified_leads[:5]

        # Automatically execute DM outreach for top leads
        try:
            from sponsor_engine.outreach.instagram_sender import InstagramSender
            sender = InstagramSender()
            for lead in top_leads:
                sender.send_outreach(lead)
        except Exception as oe:
            logger.warning(f"Outreach dispatch warning: {oe}")

        # Export json history for Vercel Web Dashboard and GitHub sync
        self._export_leads_json()

        # Record search history
        search_record = SearchHistoryRecord(
            date=today_str,
            category="Dynamic Categories",
            keyword="Multi-query exploration",
            location="India / Surat",
            source="Automated Search Engine",
            candidates_found=total_found,
            qualified_leads=len(qualified_leads),
            rejected_leads=duplicates_rejected
        )
        self.db_manager.record_search(search_record)

        # Generate Text Report
        report_text = self.generate_daily_report_text(top_leads, total_found, duplicates_rejected)

        logger.info(f"=== DAILY JOB COMPLETED: {len(top_leads)} Top Prospects Selected ===")
        return {
            "date": today_str,
            "total_discovered": total_found,
            "duplicates_rejected": duplicates_rejected,
            "total_qualified": len(qualified_leads),
            "top_leads": top_leads,
            "report_text": report_text
        }

    def generate_daily_report_text(self, top_leads: List[Lead], total_found: int, duplicates_rejected: int) -> str:
        """Formats the official daily top-5 sponsor report markdown text."""
        today_str = date.today().isoformat()
        lines = [
            "==================================================",
            "NEWS NIT IIT – DAILY SPONSOR LEADS",
            f"Date: {today_str}",
            "==================================================",
            f"Candidates Discovered: {total_found}",
            f"Duplicates Rejected: {duplicates_rejected}",
            f"Qualified Prospects: {len(top_leads)}",
            "--------------------------------------------------\n"
        ]

        if not top_leads:
            lines.append("No suitable new sponsor leads found today.")
            return "\n".join(lines)

        for idx, lead in enumerate(top_leads, 1):
            lines.append(f"LEAD {idx}")
            lines.append(f"Business: {lead.business_name}")
            lines.append(f"Category: {lead.category}")
            lines.append(f"Location: {lead.city}, {lead.state}")
            lines.append(f"Instagram: {lead.instagram}")
            lines.append(f"Followers: {lead.followers}")
            lines.append(f"Score: {lead.lead_score}/100")
            lines.append(f"Tier: {lead.lead_tier}")
            lines.append(f"\nWhy Suitable:\n{lead.why_suitable}")
            lines.append(f"\nSuggested Collaboration:\n{lead.suggested_collaboration}")
            lines.append(f"\nPersonalized Message:\n{lead.personalized_message}")
            lines.append(f"Status: {lead.status}")
            lines.append("--------------------------------------------------\n")

        return "\n".join(lines)

    def _export_leads_json(self):
        """Exports stored leads to data/leads.json for Vercel Web Dashboard and GitHub sync."""
        try:
            import json
            from sponsor_engine.database.sqlite_db import SQLiteDatabase
            db = SQLiteDatabase()
            leads = db.get_all_leads()
            json_path = self.settings.BASE_DIR / "data" / "leads.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            leads_data = [l.model_dump() for l in leads]
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(leads_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully exported {len(leads_data)} client records to {json_path}")
        except Exception as e:
            logger.warning(f"Could not export leads.json: {e}")
