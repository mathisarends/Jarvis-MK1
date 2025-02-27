from typing import List, Optional
from rapidfuzz import process, fuzz

class StringMatcher:
    """Hilfsklasse zur unscharfen Suche nach ähnlichen Strings in einer Liste."""

    def __init__(self, candidates: List[str], score_cutoff: int = 60):
        self.candidates = candidates
        self.score_cutoff = score_cutoff

    def find_best_match(self, query: str) -> Optional[str]:
        if not self.candidates:
            return None

        match = process.extractOne(query, self.candidates, scorer=fuzz.partial_ratio, score_cutoff=self.score_cutoff)
        return match[0] if match else None