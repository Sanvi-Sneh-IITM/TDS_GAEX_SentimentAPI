from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ✅ CORS support (fixes OPTIONS 405)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentencesRequest(BaseModel):
    sentences: List[str]

# ✅ Expanded lexicons (150+ words)
positive_words = set([
    "love","like","awesome","amazing","great","good","happy","excellent","fantastic",
    "wonderful","best","beautiful","brilliant","cool","delight","enjoy","epic","excited",
    "positive","cheerful","superb","perfect","success","win","winning","enjoyable",
    "nice","friendly","fun","fabulous","lovely","celebrate","optimistic","impressive",
    "outstanding","top","victory","satisfied","bright","celebration","progress",
    "sweet","encourage","strong","helpful","support","lucky","peace","glad","awesome",
    "incredible","valuable","amused","amazing","praise","accomplished","motivated",
    "blessed","calm","charming","confident","creative","cute","eager","efficient",
    "elegant","energetic","enthusiastic","exciting","fascinating","genius","gifted",
    "glowing","golden","graceful","grateful","healthy","hero","honest","inspired",
    "joy","kind","lively","marvelous","merry","miracle","neat","noble","passion",
    "peaceful","pleasure","pretty","productive","prosper","relaxed","reliable",
    "respect","safe","savior","shine","smart","smile","sparkle","splendid","stable",
    "strong","success","sunny","talent","thankful","thrilled","unique","victory",
    "vibrant","wise","wonder","yay","yes"
])

negative_words = set([
    "sad","bad","terrible","hate","angry","horrible","awful","upset","worst","pain",
    "disappoint","depress","ugly","annoy","fail","failed","failure","broke","cry",
    "fear","scared","broken","suck","stupid","negative","hurt","terrifying",
    "disgusting","mad","ruin","boring","boring","lazy","evil","problem","danger",
    "dangerous","stress","stressful","struggle","sorrow","jealous","guilty","lonely",
    "nervous","panic","pitiful","poor","sick","angry","anxious","arrogant","ashamed",
    "beaten","betray","blame","bloody","chaos","cheat","complain","confused","crisis",
    "cruel","crying","damage","dark","dead","death","defeat","denied","dirty","doubt",
    "dread","embarrass","enemy","error","evil","fail","fake","fearful","fight","fool",
    "fright","furious","greedy","gross","guilt","hate","harm","helpless","horrid",
    "hostile","hurtful","idiot","ill","impossible","insecure","insult","jealousy",
    "judgment","kill","loneliness","loss","lost","mean","mess","miserable","nasty",
    "nightmare","no","painful","paranoid","pathetic","regret","reject","resent",
    "risk","scam","scared","selfish","shame","shock","sin","smash","sorry","stressed",
    "stupid","suffer","toxic","tragic","trouble","ugly","unhappy","upset","useless",
    "victim","weak","weep","worry","worthless"
])

def analyze_sentiment(sentence: str) -> str:
    s = sentence.lower()

    # Keyword match counts
    pos = sum(1 for w in positive_words if w in s)
    neg = sum(1 for w in negative_words if w in s)

    if pos > neg:
        return "happy"
    elif neg > pos:
        return "sad"
    else:
        return "neutral"

@app.post("/sentiment")
def sentiment_analyze(req: SentencesRequest):
    results = []
    for text in req.sentences:
        results.append({
            "sentence": text,
            "sentiment": analyze_sentiment(text)
        })
    return {"results": results}
