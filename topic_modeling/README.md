# Topic modelling batch job

The batch job assigns topics only to `active` posts that do not already have a
topic. It uses a self-hosted TF-IDF plus KMeans baseline so the model can run
without sending post content to a third-party AI provider.

Run it from the repository root after installing
[`requirements.txt`](../requirements.txt):

```bash
python -m topic_modeling.batch
```

The job stores:

- `topic`: human-readable topic label assembled from cluster keywords
- `topic_confidence`: normalized distance-based confidence
- `topic_keywords`: top five terms
- `topic_model_version`: reproducibility identifier
- `topic_updated_at`: update timestamp

This is a cold-start baseline, not the final taxonomy system. It should later
be replaced or supplemented with a versioned taxonomy and evaluation set.
