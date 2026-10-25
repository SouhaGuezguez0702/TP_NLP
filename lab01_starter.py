"""
NLP Lab 1 - Preprocessing pipeline - STARTER FILE (student)
Polytechnic Engineering High School - 5th-year Engineering, Data Science & AI
Standard library only. Run from this folder:  python lab01_starter.py
Complete every block marked TODO. The file runs as-is: unfinished functions
are reported as FAIL (not implemented yet) instead of crashing.
"""
import re
import unicodedata
from collections import Counter

# ---------------------------------------------------------------- data (synthetic, written for this lab)
CORPUS = [
    "The cat sat on the mat.",
    "The cat, the dog, and the bird ran.",
    "Dr. Smith isn't home; call https://x.io later!",
]
ARABIC = [
    "الْعَرَبِيَّةُ",    # with diacritics (harakat)
    "أحمد إلى آسيا",     # alef variants with hamza / madda
    "محـــمد",           # tatweel (kashida) U+0640
]

# ---------------------------------------------------------------- Exercise 1

def normalize(text, lower=True):
    # 1. Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Case folding (optional)
    if lower:
        text = text.casefold()

    # 3. Collapse consecutive whitespace
    text = re.sub(r"\s+", " ", text)

    # 4. Remove whitespace at both ends
    text = text.strip()

    return text


# ---------------------------------------------------------------- Exercise 2

def word_tokenize(text):
    pattern = r"\b\w+(?:'\w+)?\b|[^\w\s]"
    return re.findall(pattern, text)

# ---------------------------------------------------------------- Exercise 3

def sentence_tokenize(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def buggy_sentence_tokenize(text):
    # Given for Exercise 3.4 (diagnosis) - do NOT fix this one, explain it.
    return [s for s in re.split(r"[.!?]\s+", text) if s]

# ---------------------------------------------------------------- Exercise 4
DIAC = re.compile(r"[\u064B-\u0652\u0670]")
def normalize_arabic(text):
    text = unicodedata.normalize("NFC", text)   # (1) forme Unicode unique
    text = DIAC.sub("", text)                   # (2a) supprime les harakat
    text = text.replace("\u0640", "")           # (2b) supprime le tatwil
    for c in ("\u0623", "\u0625", "\u0622"):    # (3) أ إ آ -> ا
        text = text.replace(c, "\u0627")
    return text

# ---------------------------------------------------------------- Exercise 5
def token_stats(tokens):
    n = len(tokens)
    v = len(set(tokens))
    return {
        "tokens": n,
        "types": v,
        "type_token_ratio": round(v / n, 3) if n else 0.0,
        "top5": Counter(tokens).most_common(5),
    }

def corpus_tokens(corpus, lower=True):
    return [tok for sent in corpus for tok in word_tokenize(normalize(sent, lower))]

# ---------------------------------------------------------------- tests (do not modify)
TESTS = [
    ("T1 normalize lower",   lambda: normalize("  Héllo   WORLD  ") == "héllo world"),
    ("T2 normalize keep case", lambda: normalize("CaFé", lower=False) == "CaFé"),
    ("T3 word_tokenize",     lambda: word_tokenize("Dr. Smith isn't home.") == ['Dr', '.', 'Smith', "isn't", 'home', '.']),
    ("T4 sentence_tokenize", lambda: sentence_tokenize("Hi there. How are you? I'm fine!") == ["Hi there.", "How are you?", "I'm fine!"]),
    ("T5 normalize_arabic",  lambda: normalize_arabic("أحمد") == normalize_arabic("احمد")),
    ("T6 token_stats",       lambda: token_stats(['a', 'b', 'a', 'c'])["type_token_ratio"] == 0.75),
]

def run_tests():
    passed = 0
    for name, test in TESTS:
        try:
            ok = bool(test())
        except NotImplementedError:
            ok = False; name += " (not implemented yet)"
        except Exception as e:
            ok = False; name += f" (error: {type(e).__name__}: {e})"
        print(("PASS  " if ok else "FAIL  ") + name)
        passed += ok
    print(f"{passed}/{len(TESTS)} tests passed")
    return passed == len(TESTS)

if __name__ == "__main__":
    print("Python environment OK")
    run_tests()
    # Uncomment progressively as you finish the exercises:
    print("stats (lower=True): ", token_stats(corpus_tokens(CORPUS, lower=True)))
    print("stats (lower=False):", token_stats(corpus_tokens(CORPUS, lower=False)))
    print("arabic:", [normalize_arabic(w) for w in ARABIC])
    print("buggy splitter:", buggy_sentence_tokenize("Hi there. How are you? I'm fine!"))
