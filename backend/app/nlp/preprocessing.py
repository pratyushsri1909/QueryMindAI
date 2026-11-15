"""
Preprocessing Module for QueryMind AI (Member 1 - NLP Module).
Handles tokenization, normalization, stop-word filtering with operator preservation,
lemmatization, and POS tagging.
"""

import re
from typing import List, Tuple, Dict, Any

# Conversational stop words to remove
STOP_WORDS = {
    "a", "an", "the", "please", "kindly", "can", "you", "could", "would",
    "i", "want", "to", "see", "get", "give", "me", "tell", "fetch", "display",
    "show", "list", "find", "of", "for", "with", "whose", "details",
    "information", "record", "records", "data", "all"
}

# Preserve tokens critical to SQL intent, operators, and ordering
PRESERVED_KEYWORDS = {
    "greater", "less", "more", "fewer", "than", "equal", "above", "below",
    "not", "top", "bottom", "highest", "lowest", "count", "average", "avg",
    "sum", "min", "max", "between", "like", "order", "by", "sort", "asc", "desc",
    "each", "wise", "department-wise", "course-wise", "enrolled", "in", "from"
}

LEMMA_SUFFIXES = [
    ("sses", "ss"),
    ("ies", "y"),
    ("s", ""),
    ("ed", ""),
    ("ing", "")
]


class TextPreprocessor:
    """Preprocesses natural language text for query parsing."""

    def clean_text(self, text: str) -> str:
        """Sanitizes punctuation and normalizes whitespace."""
        if not text:
            return ""
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        for sym in [">=", "<=", "!=", "=", ">", "<"]:
            text = text.replace(sym, f" {sym} ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text into lexical word and operator tokens."""
        cleaned = self.clean_text(text)
        tokens = re.findall(r"[A-Za-z0-9_.\-]+|>=|<=|!=|=|>|<", cleaned)
        return tokens

    def lemmatize_token(self, token: str) -> str:
        """Lemmatizes a token to its base dictionary root."""
        lower = token.lower()
        if len(lower) <= 3:
            return lower
        for suffix, replacement in LEMMA_SUFFIXES:
            if lower.endswith(suffix) and len(lower) - len(suffix) >= 3:
                return lower[:-len(suffix)] + replacement
        return lower

    def pos_tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Rule-based POS tagger."""
        tagged = []
        for tok in tokens:
            lower = tok.lower()
            if re.match(r"^-?\d+(\.\d+)?$", tok):
                tagged.append((tok, "CD"))
            elif tok in {">", "<", ">=", "<=", "=", "!="}:
                tagged.append((tok, "SYM"))
            elif lower in {"greater", "less", "more", "fewer", "higher", "lower"}:
                tagged.append((tok, "JJR"))
            elif lower in {"top", "bottom", "highest", "lowest", "best", "worst", "maximum", "minimum"}:
                tagged.append((tok, "JJS"))
            elif lower in {"count", "average", "avg", "sum", "min", "max"}:
                tagged.append((tok, "AGG"))
            elif lower in {"show", "display", "list", "get", "find", "fetch", "sort", "order"}:
                tagged.append((tok, "VB"))
            elif lower in {"having", "where", "than", "and", "or", "in", "by", "from"}:
                tagged.append((tok, "IN"))
            else:
                tagged.append((tok, "NN"))
        return tagged

    def process(self, query: str) -> Dict[str, Any]:
        """Executes full preprocessing pipeline."""
        cleaned = self.clean_text(query)
        raw_tokens = self.tokenize(cleaned)
        
        filtered = []
        for t in raw_tokens:
            t_low = t.lower()
            if t_low not in STOP_WORDS or t_low in PRESERVED_KEYWORDS:
                filtered.append(t)

        lemmas = [self.lemmatize_token(t) for t in raw_tokens]
        pos_tags = self.pos_tag(raw_tokens)

        return {
            "original_query": query,
            "cleaned_query": cleaned,
            "tokens": raw_tokens,
            "filtered_tokens": filtered,
            "lemmas": lemmas,
            "pos_tags": pos_tags
        }
