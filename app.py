# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
from youtube_transcript_api import YouTubeTranscriptApi

# --- Small stopword set (keeps code dependency-free) ---
STOPWORDS = {
    "the","and","is","in","to","of","a","for","that","on","with","as","it","are","this",
    "be","by","from","or","an","at","have","has","was","but","not","they","their","we",
    "you","your","i","my","so","if","will","can"
}

# ------------------ Extraction helpers ------------------
def extract_text_from_url(url):
    """Download a simple article body by collecting <p> tags (basic)."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
        else:
            paragraphs = soup.find_all("p")
        text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        return text or None
    except Exception as e:
        return None


# ------------------ Simple offline summarizer & generators (fallback) ------------------
def simple_summarize(text, max_sentences=3):
    """Naive summarizer: score sentences by word frequencies (no external libs)."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return " ".join(sentences)
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        if w in STOPWORDS: continue
        freq[w] = freq.get(w, 0) + 1
    scores = []
    for i, s in enumerate(sentences):
        s_words = re.findall(r'\w+', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        scores.append((score, i, s))
    top = sorted(scores, reverse=True)[:max_sentences]
    top = sorted(top, key=lambda x: x[1])  # keep original order
    return " ".join(t[2].strip() for t in top)

def simple_tweets(text, n=3):
    """Create short tweet-like lines from the text (fallback)."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    tweets = []
    for i in range(min(n, len(sentences))):
        t = sentences[i]
        if len(t) > 240:
            t = t[:237] + "..."
        tweets.append(t)
    # If not enough sentences, make variations
    while len(tweets) < n:
        tweets.append((tweets[-1] + " Read more.") if tweets else "Interesting take! Read more.")
    return tweets

def simple_linkedin(text):
    """Make a short LinkedIn-style post (fallback)."""
    summary = simple_summarize(text, max_sentences=4)
    linkedin = f"{summary}\n\nKey takeaway: {summary.split('.')[0]}. \n#marketing #content"
    return linkedin

def simple_keywords(text, top_k=8):
    """Pick top frequent words as naive keywords (fallback)."""
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        if w in STOPWORDS or len(w) < 3: continue
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:top_k]]

# ------------------ LLM integration stub ------------------
def llm_generate(prompt_text: str) -> str:
    """
    IMPORTANT: Replace this function with your Gemini (or other LLM) API call.
    For now it returns an empty string so the app will fall back to simple local generators.
    Example replacement strategy:
    - Read API key from env var
    - Call the provider's Python client or REST endpoint with the prompt_text
    - Return the model's raw text response (string)
    """
    return ""  # <-- replace with real API call

def parse_llm_json_response(response_text: str):
    """Attempt to parse LLM JSON output; return None on failure."""
    try:
        data = json.loads(response_text)
        return data
    except Exception:
        return None

def generate_marketing(text):
    """Try LLM first; if it fails, use local fallback."""
    # Build a clear prompt requesting JSON output
    prompt = (
        "You are a helpful marketing assistant. Given the ARTICLE_TEXT below, produce a JSON object exactly "
        "with these keys: summary (string), tweets (array of 3-5 strings), linkedin (string), keywords (array of strings).\n\n"
        f"ARTICLE_TEXT:\n{text[:20000]}"  # limit length for safety
    )
    response = llm_generate(prompt)
    parsed = parse_llm_json_response(response) if response else None
    if parsed:
        return parsed
    # fallback:
    return {
        "summary": simple_summarize(text, max_sentences=3),
        "tweets": simple_tweets(text, n=4),
        "linkedin": simple_linkedin(text),
        "keywords": simple_keywords(text, top_k=8)
    }

# ------------------ Streamlit UI ------------------
st.title("Automated Content → Marketing Assistant")
st.markdown("Give a blog URL, or paste a transcript. App will produce summary, tweets, LinkedIn post, and keywords.")

input_type = st.radio("Input type", ("Blog URL", "Paste transcript"))

input_text = st.text_area("Enter URL or paste transcript here", height=120)

if st.button("Generate marketing assets"):
    with st.spinner("Extracting text..."):
        extracted = None
        if input_type == "Blog URL":
            extracted = extract_text_from_url(input_text.strip())
            if not extracted:
                st.error("Could not extract article from the URL. Try another URL or paste the text.")

        else:
            extracted = input_text.strip() or None
            if not extracted:
                st.error("Please paste a transcript or some text.")
    if extracted:
        st.subheader("Extracted text (preview)")
        st.text_area("Article / Transcript (first 5000 chars)", extracted[:5000], height=200)
        with st.spinner("Generating marketing assets (LLM fallback available)..."):
            out = generate_marketing(extracted)
        st.subheader("Summary")
        st.write(out.get("summary", ""))
        st.subheader("Tweets")
        for i, t in enumerate(out.get("tweets", []), 1):
            st.markdown(f"**Tweet {i}:** {t}")
        st.subheader("LinkedIn Post")
        st.write(out.get("linkedin", ""))
        st.subheader("Suggested SEO keywords")
        st.write(", ".join(out.get("keywords", [])))
        st.success("Done! If you wire in your LLM in llm_generate(), the app will use it automatically.")
