import csv
import os
import re
import unicodedata
from pathlib import Path
from typing import Iterable

debug = os.environ.get("DEBUG", "1") == "1"
if debug:
    BADWORDS_CSV = "functions/offensive_word_detection/merged_badwords.csv"
else:
    BADWORDS_CSV = "merged_badwords.csv"

CENSOR_CHAR = "*"

def load_badwords(csv_path: str) -> Iterable[str]:
    with open(csv_path, encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            word = row[0].strip().lower()
            yield word

# ---- NORMALIZATION ----
LEET_MAP = str.maketrans({
    "4": "a", "@": "a",
    "8": "b",
    "3": "e",
    "1": "i", "!": "i",
    "0": "o",
    "$": "s", "5": "s",
    "7": "t"
})

def normalize_text(s: str) -> str:
    """Unicode normalize, lowercase, replace leetspeak, remove zero-width chars."""
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(LEET_MAP)
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)  # remove ZW spaces
    return s.lower()


def find_badwords(text: str, badwords: list[str]) -> Iterable[str]:
    text_norm = normalize_text(text)
    for word in badwords:
        # \b works for Latin scripts; for Persian/Arabic/others we also check raw substring
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, text_norm) or word in text_norm.split():
            yield word


def censor_text(text: str, found_words: list[str]) -> str:
    """Replace bad words with stars."""
    censored = text
    for w in found_words:
        mask = CENSOR_CHAR * len(w)
        censored = re.sub(re.escape(w), mask, censored, flags=re.IGNORECASE)
    return censored


bad_words = list(load_badwords(BADWORDS_CSV))

def handler(event, context=None):
    text = event.get("text", "")
    if text:
        hits = list(find_badwords(text, bad_words))
        if hits:
            words = list(set(hits))  # unique
            censored = censor_text(text, words)
            return {
                "toxic": True,
                "found_words": words,
                "censored": censored
            }
        else:
            return {
                "toxic": False,
                "found_words": [],
                "censored": text
            }
    
    return {
        "error": "No text provided"
    }
