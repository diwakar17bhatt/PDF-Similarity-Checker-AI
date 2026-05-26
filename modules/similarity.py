from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(doc1, doc2):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([doc1, doc2])

    similarity = cosine_similarity(vectors)

    return round(similarity[0][1] * 100, 2)