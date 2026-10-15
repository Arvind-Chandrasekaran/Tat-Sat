from topic_modeling.batch import model_topics


def test_model_topics_returns_primary_topic_metadata():
    rows = [
        {"id": "1", "text": "Postgres vector databases and indexes"},
        {"id": "2", "text": "Database query performance and indexes"},
        {"id": "3", "text": "Football match strategy and team training"},
        {"id": "4", "text": "Football coach prepares the team for a match"},
    ]

    results = model_topics(rows, requested_topics=2)

    assert len(results) == len(rows)
    assert all(result["topic"] for result in results)
    assert all(result["keywords"] for result in results)
    assert all(0 <= result["confidence"] <= 1 for result in results)


def test_model_topics_handles_cold_start():
    assert model_topics([{"id": "1", "text": "A single post"}]) == [
        {
            "id": "1",
            "topic": "General",
            "confidence": 0.0,
            "keywords": [],
        }
    ]
