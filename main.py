from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI(title="Batch Sentiment API")

# ✅ Enable CORS so browser tests & tools can call API without errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (update if needed)
    allow_credentials=True,
    allow_methods=["*"],  # ✅ handles OPTIONS
    allow_headers=["*"],
)


class SentencesIn(BaseModel):
    sentences: List[str]


POSITIVE = {
    "love", "loved", "loving", "like", "liked", "awesome", "great", "good",
    "wonderful", "fantastic", "amazing", "happy", "glad", "pleased", "enjoy",
    "enjoyed", "yay", "excellent", "best", "nice", "delightful", "brilliant"
}

NEGATIVE = {
    "hate", "hated", "hating", "dislike", "disliked", "terrible", "bad",
    "awful", "horrible", "sad", "angry", "upset", "worse", "worst",
    "disappoint", "disappointed", "annoyed", "sucks", "problem", "unhappy",
    "tragic", "poor"
}

NEGATIONS = {"not", "never", "no", "n't", "cannot", "can't", "dont", "don't"}

EMOTICONS_POS = {":)", ":-)", ":D", ":-D", "<3", "😊", "🙂", "😄"}
EMOTICONS_NEG = {":(", ":-(", ":'(", "😢", "😞", "😠", "😡"}

WORD_RE = re.compile(r"[a-zA-Z']+")


def simple_sentiment(sentence: str) -> str:
    s = sentence or ""
    s_lower = s.lower()

    em_pos = sum(1 for e in EMOTICONS_POS if e in s)
    em_neg = sum(1 for e in EMOTICONS_NEG if e in s)

    tokens = WORD_RE.findall(s_lower)
    score = 0
    i = 0

    while i < len(tokens):
        w = tokens[i]
        if w in NEGATIONS:
            for j in range(i + 1, min(i + 4, len(tokens))):
                tw = tokens[j]
                if tw in POSITIVE:
                    score -= 1
                elif tw in NEGATIVE:
                    score += 1
            i += 1
            continue

        if w in POSITIVE:
            score += 1
        elif w in NEGATIVE:
            score -= 1

        i += 1

    score += em_pos * 2
    score -= em_neg * 2

    if "!" in s:
        if score > 0:
            score += 1
        elif score < 0:
            score -= 1

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
    results = [{"sentence": s, "sentiment": simple_sentiment(s)} for s in payload.sentences]
    return {"results": results}


@app.get("/")
def root():
    return {"service": "batch-sentiment", "status": "ok"}
