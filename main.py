from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI(title="Batch Sentiment API")

class SentencesIn(BaseModel):
    sentences: List[str]

# Simple lexicons (small, extend as needed)
POSITIVE = {
    "love","loved","loving","like","liked","awesome","great","good","wonderful",
    "fantastic","amazing","happy","glad","pleased","enjoy","enjoyed","yay","yay!",
    "excellent","best","nice","delightful","brilliant","amazing"
}
NEGATIVE = {
    "hate","hated","hating","dislike","disliked","terrible","bad","awful","horrible",
    "sad","angry","upset","worse","worst","disappoint","disappointed","annoyed",
    "sucks","sucked","problem","issue","unhappy","tragic","poor"
}

# common negation words
NEGATIONS = {"not","never","no","n't","cannot","can't","dont","don't","hardly","rarely"}

EMOTICONS_POS = {":)", ":-)", ":D", ":-D", "<3", "😊", "🙂", "😄"}
EMOTICONS_NEG = {":(", ":-(", ":'(", "😢", "😞", "😠", "😡"}

WORD_RE = re.compile(r"[a-zA-Z']+")

def simple_sentiment(sentence: str) -> str:
    """
    Rule-based sentiment scoring:
      + Count positive and negative tokens.
      + If a positive/negative word appears immediately after a negation (within a window), flip its sign.
      + Count emoticons separately.
      + Small heuristic adjustments for punctuation/exclamation.
    Returns "happy", "sad", or "neutral".
    """
    s = sentence or ""
    s_lower = s.lower()

    # quick emoticon check
    em_pos = sum(1 for e in EMOTICONS_POS if e in s)
    em_neg = sum(1 for e in EMOTICONS_NEG if e in s)

    tokens = WORD_RE.findall(s_lower)
    score = 0
    i = 0
    while i < len(tokens):
        w = tokens[i]
        # handle contractions like "don't" -> "do", "n't"
        if w in NEGATIONS:
            # lookahead window for next 3 words to flip
            for j in range(i+1, min(i+4, len(tokens))):
                tw = tokens[j]
                if tw in POSITIVE:
                    score -= 1  # flipped positive becomes negative
                elif tw in NEGATIVE:
                    score += 1  # flipped negative becomes positive
            i += 1
            continue

        if w in POSITIVE:
            score += 1
        elif w in NEGATIVE:
            score -= 1
        i += 1

    # incorporate emoticons
    score += em_pos * 2
    score -= em_neg * 2

    # punctuation heuristic: exclamation increases intensity slightly
    if "!" in s:
        # if sentence is short and positive words exist, boost positive
        if score > 0:
            score += 1
        elif score < 0:
            score -= 1

    # final mapping to labels
    if score >= 2:
        return "happy"
    elif score <= -2:
        return "sad"
    else:
        return "neutral"


@app.post("/sentiment")
async def batch_sentiment(payload: SentencesIn) -> Dict[str, List[Dict[str, str]]]:
    if payload.sentences is None:
        raise HTTPException(status_code=400, detail="Missing 'sentences' array in JSON body.")
    results = []
    for s in payload.sentences:
        # ensure we maintain exact provided sentence in output
        label = simple_sentiment(s)
        results.append({"sentence": s, "sentiment": label})
    return {"results": results}


# health check
@app.get("/")
def root():
    return {"service": "batch-sentiment", "status": "ok"}
