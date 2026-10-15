import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from supabase import acreate_client

load_dotenv()

MODEL_VERSION = "tfidf-kmeans-v1"


def _keywords(vectorizer: TfidfVectorizer, centers, cluster_index: int) -> list[str]:
    terms = vectorizer.get_feature_names_out()
    ranked = centers[cluster_index].argsort()[::-1]
    return [terms[index] for index in ranked[:5]]


def model_topics(rows: list[dict], requested_topics: int = 8) -> list[dict]:
    if not rows:
        return []
    if len(rows) == 1:
        return [
            {
                "id": rows[0]["id"],
                "topic": "General",
                "confidence": 0.0,
                "keywords": [],
            }
        ]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([row["text"] for row in rows])
    topic_count = max(2, min(requested_topics, len(rows)))
    model = KMeans(n_clusters=topic_count, random_state=42, n_init=10)
    labels = model.fit_predict(matrix)
    distances = model.transform(matrix)
    results = []

    for index, row in enumerate(rows):
        cluster = int(labels[index])
        cluster_distance = float(distances[index][cluster])
        confidence = 1.0 / (1.0 + cluster_distance)
        words = _keywords(vectorizer, model.cluster_centers_, cluster)
        results.append(
            {
                "id": row["id"],
                "topic": " / ".join(words) if words else "General",
                "confidence": round(confidence, 4),
                "keywords": words,
            }
        )
    return results


async def run_batch(batch_size: int = 500) -> int:
    url = os.environ["SUPABASE_PROJECT_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    client = await acreate_client(url, key)
    response = await (
        client.schema("domain")
        .table("posts")
        .select("id,text")
        .eq("post_status", "active")
        .is_("topic", "null")
        .limit(batch_size)
        .execute()
    )
    rows = response.data or []
    updates = model_topics(rows)
    now = datetime.now(timezone.utc).isoformat()
    for update in updates:
        await (
            client.schema("domain")
            .table("posts")
            .update(
                {
                    "topic": update["topic"],
                    "topic_confidence": update["confidence"],
                    "topic_keywords": update["keywords"],
                    "topic_model_version": MODEL_VERSION,
                    "topic_updated_at": now,
                }
            )
            .eq("id", update["id"])
            .execute()
        )
    return len(updates)


if __name__ == "__main__":
    print(f"Updated {asyncio.run(run_batch())} posts")
