import logging
from typing import List, Tuple
from sponsor_engine.database.models import Candidate
from sponsor_engine.discovery.category_generator import CategoryGenerator
from sponsor_engine.discovery.search_engine import SearchEngine
from sponsor_engine.utils.deduplication import DeduplicationEngine

logger = logging.getLogger(__name__)

class CandidateFinder:
    """Orchestrates category generation and search filtering to discover candidate leads."""

    def __init__(self):
        self.category_generator = CategoryGenerator()
        self.search_engine = SearchEngine()
        self.dedup_engine = DeduplicationEngine()

    def discover_daily_candidates(self, target_categories_count: int = 3) -> Tuple[List[Candidate], int, int]:
        """
        Discovers raw candidate leads across dynamic categories.
        Returns tuple of (unique_candidates, total_found, duplicates_rejected).
        """
        categories = self.category_generator.generate_categories(total_categories=target_categories_count)
        
        all_candidates: List[Candidate] = []
        total_found = 0
        duplicates_rejected = 0

        for cat in categories:
            cat_name = cat["name"]
            queries = cat.get("search_queries", [f"{cat_name} India"])
            
            # Select 1-2 queries per category to stay within search limits
            selected_query = queries[0] if queries else f"{cat_name} Surat India"
            
            raw_candidates = self.search_engine.search_category(
                category_name=cat_name,
                search_query=selected_query,
                max_results=5
            )

            total_found += len(raw_candidates)

            for cand in raw_candidates:
                # Check for duplicate lead in DB
                is_dup, _ = self.dedup_engine.is_duplicate(
                    instagram=cand.instagram,
                    website=cand.website,
                    business_name=cand.business_name
                )

                if is_dup:
                    duplicates_rejected += 1
                else:
                    all_candidates.append(cand)

        logger.info(f"Discovery complete. Found {total_found} total candidates, {duplicates_rejected} duplicates rejected, {len(all_candidates)} new candidate prospects.")
        return all_candidates, total_found, duplicates_rejected
