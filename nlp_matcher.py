"""Text similarity between a resume and a job description."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
 
def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
 
 
def calculate_similarity(resume_text: str, job_description: str) -> float:
    """Return similarity as a percentage (0-100), rounded to 2 decimals.
 
    TF-IDF turns each text into a weighted word vector.
    Cosine similarity measures the angle between the two vectors.
    """
    a, b = _clean(resume_text), _clean(job_description)
    if not a or not b:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform([a, b])
    except ValueError:  # e.g. only stop-words
        return 0.0
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score) * 100, 2)
 
