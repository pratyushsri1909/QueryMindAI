"""
Text Preprocessor for QueryMind AI (Member 1 - NLP Engine).
Handles tokenization, case normalization, stop-word filtering with keyword
preservation, lemmatization, and rule-based POS tagging.
"""

import re
from typing import List, Tuple, Dict, Any

# Conversational stop words to remove (notice operators like "greater", "than", "top" are EXCLUDED from stop-words)
STOP_WORDS = {
    "a", "an", "the", "please", "kindly", "can", "you", "could", "would",
    "i", "want", "to", "see", "get", "give", "me", "tell", "fetch", "display",
    "show", "list", "of", "for", "in", "from", "with", "whose", "details",
    "information", "record", "records", "data", "all"
}

# Preserve words critical to SQL clauses and operators even if conversational
PRESERVED_KEYWORDS = {
    "greater", "less", "more", "fewer", "than", "equal", "above", "below",
    "not", "top", "bottom", "highest", "lowest", "count", "average", "avg",
    "sum", "min", "max", "between", "like", "order", "by", "sort", "asc", "desc"
}

# Suffix rules for simple lemmatization
LEMMA_SUFFIXES = [
    ("sses", "ss"),
    ("ies", "y"),
    ("s", ""),
    ("ed", ""),
    ("ing", "")
]


class Preprocessor:
    """Performs lexical and linguistic preprocessing on query text."""

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Sanitizes text and unifies symbols."""
        if not text:
            return ""
        # Normalize quotes
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        # Ensure spacing around comparison symbols
        for sym in [">=", "<=", "!=", "=", ">", "<"]:
            text = text.replace(sym, f" {sym} ")
        # Condense multiple whitespaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Splits normalized text into tokens."""
        cleaned = self.clean_text(text)
        # Tokenize by words, numbers, and operator symbols
        tokens = re.findall(r"[A-Za-z0-9_.]+|>=|<=|!=|=|>|<", cleaned)
        return tokens

    def lemmatize_token(self, token: str) -> str:
        """Lemmatizes a single token to its base form."""
        token_lower = token.lower()
        if len(token_lower) <= 3:
            return token_lower
        for suffix, replacement in LEMMA_SUFFIXES:
            if token_lower.endswith(suffix) and len(token_lower) - len(suffix) >= 3:
                return token_lower[:-len(suffix)] + replacement
        return token_lower

    def pos_tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """
        Rule-based POS tagger.
        Tags:
        - CD: Cardinal number
        - JJR: Comparative adjective
        - JJS: Superlative adjective
        - NN: Noun / Entity
        - VB: Action verb
        - IN: Preposition / Conjunction
        - SYM: Symbol / Operator
        """
        tagged = []
        for tok in tokens:
            lower = tok.lower()
            if re.match(r"^-?\d+(\.\d+)?$", tok):
                tagged.append((tok, "CD"))
            elif tok in {">", "<", ">=", "<=", "=", "!="}:
                tagged.append((tok, "SYM"))
            elif lower in {"greater", "less", "more", "fewer", "higher", "lower", "better", "worse"}:
                tagged.append((tok, "JJR"))
            elif lower in {"top", "bottom", "highest", "lowest", "best", "worst", "maximum", "minimum"}:
                tagged.append((tok, "JJS"))
            elif lower in {"count", "average", "avg", "sum", "min", "max"}:
                tagged.append((tok, "AGG"))
            elif lower in {"show", "display", "list", "get", "find", "fetch", "sort", "order"}:
                tagged.append((tok, "VB"))
            elif lower in {"having", "where", "than", "and", "or", "in", "by"}:
                tagged.append((tok, "IN"))
            else:
                tagged.append((tok, "NN"))
        return tagged

    def preprocess(self, query: str) -> Dict[str, Any]:
        """
        Executes full preprocessing pipeline.
        Returns cleaned text, original tokens, filtered tokens, lemmas, and POS tags.
        """
        cleaned = self.clean_text(query)
        raw_tokens = self.tokenize(cleaned)
        
        # Filtered tokens (keeping preserved keywords)
        filtered_tokens = []
        for t in raw_tokens:
            t_low = t.lower()
            if t_low not in STOP_WORDS or t_low in PRESERVED_KEYWORDS:
                filtered_tokens.append(t)
                
        lemmas = [self.lemmatize_token(t) for t in raw_tokens]
        pos_tags = self.pos_tag(raw_tokens)

        return {
            "original_query": query,
            "cleaned_query": cleaned,
            "tokens": raw_tokens,
            "filtered_tokens": filtered_tokens,
            "lemmas": lemmas,
            "pos_tags": pos_tags
        }
