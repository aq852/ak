import re
from difflib import get_close_matches

class FuzzySearch:
    """Fuzzy search and typo tolerance"""
    
    # Common typos mapping
    TYPO_MAP = {
        "batman": ["batman", "btman", "batmen", "bat man"],
        "spiderman": ["spiderman", "spderman", "spider man", "spidy"],
        "avengers": ["avengers", "avenger", "avngers", "avengers endgame"],
        "ironman": ["ironman", "iron man", "ironmann"],
        "thor": ["thor", "thr", "thor ragnarok"],
        "harry potter": ["harry potter", "hary potter", "harry poter"],
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for better matching"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove special chars
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        return text
    
    @staticmethod
    def parse_filters(query: str) -> tuple:
        """Parse advanced filters from query
        
        Example: "/search avengers quality:1080p language:hindi"
        Returns: ("avengers", {"quality": "1080p", "language": "hindi"})
        """
        filters = {}
        words = []
        
        # Pattern for key:value filters
        filter_pattern = r'(\w+):(\S+)'
        
        # Extract filters
        for match in re.finditer(filter_pattern, query):
            key, value = match.groups()
            filters[key.lower()] = value.lower()
        
        # Get remaining words as search query
        query_clean = re.sub(filter_pattern, '', query)
        words = [w for w in query_clean.split() if w.strip()]
        
        return ' '.join(words), filters
    
    @staticmethod
    def suggest_correction(query: str, options: list, cutoff: float = 0.6) -> list:
        """Suggest corrections for typos"""
        normalized = FuzzySearch.normalize_text(query)
        
        # Check typo map
        for correct_word, variations in FuzzySearch.TYPO_MAP.items():
            if any(normalized in var or var in normalized for var in variations):
                return [correct_word]
        
        # Use difflib for fuzzy matching
        suggestions = get_close_matches(normalized, options, n=3, cutoff=cutoff)
        return suggestions
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return FuzzySearch.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def is_similar(query: str, target: str, threshold: float = 0.7) -> bool:
        """Check if query is similar to target"""
        q = FuzzySearch.normalize_text(query)
        t = FuzzySearch.normalize_text(target)
        
        # Exact match
        if q == t:
            return True
        
        # Partial match
        if q in t or t in q:
            return True
        
        # Levenshtein similarity
        max_len = max(len(q), len(t))
        if max_len == 0:
            return True
        
        distance = FuzzySearch.levenshtein_distance(q, t)
        similarity = 1 - (distance / max_len)
        
        return similarity >= threshold
