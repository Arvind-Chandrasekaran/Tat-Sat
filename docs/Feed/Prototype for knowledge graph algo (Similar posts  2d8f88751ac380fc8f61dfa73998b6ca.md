# Prototype for knowledge graph algo (Similar posts and NOT main feed algo)

Based on the code provided, the recommendation logic in **TatSat** is a **hybrid system** that combines **Semantic Vector Search** (via embeddings) with a deterministic **Heuristic Quality Algorithm** (Discourse Quality Score or DQS).

Unlike traditional social media algorithms that optimize for engagement (clicks/time-spent), this system optimizes for **constructive argumentation** and **semantic relevance**.

Here is the technical breakdown:

### 1. Feature Engineering (Ingestion Phase)

When a post is created (services/backend.ts -> createPost), three distinct feature sets are generated via the Gemini API before the data hits the database:

- **Content Embeddings:** The raw text is passed to text-embedding-004 to generate a high-dimensional vector (likely 768 dimensions) representing the semantic meaning of the post.
- **Topic Embeddings:** The system extracts a categorical topic (e.g., "Neuroscience",
"Urbanism") and generates a separate vector embedding for that specific
label. This allows for "Topic Space" comparisons separate from "Content
Space."
- **Discourse Quality Score (DQS):** This is the core differentiator. The system analyzes the text structure using a specific heuristic (services/geminiService.ts -> calculateDQS). It is **not** a black-box LLM rating, but a weighted sum of specific rhetorical components:
    - **Argument Structure Quality (ASQ - 35%):** Checks for Toulmin model components (Claim, Grounds, Warrant, Backing, Rebuttal).
    - **Fallacy Score (FS - 25%):** Penalizes logical fallacies (Ad Hominem, Strawman).
    - **Cooperative Principle Score (CPS - 25%):** Measures adherence to Grice’s Maxims (Quality, Quantity, Relevance, Manner).
    - **Emotional Tone Score (ETS - 15%):** Penalizes high emotional intensity to favor neutrality.

### 2. Retrieval Strategy A: The Main Feed (PLACEHOLDER)

The main feed (backend.getFeed) is currently rudimentary but includes a **Quality Gate**:

1. **Chronological Fetch:** It pulls posts ordered by created_at.
2. **Client-Side Quality Filter:** If the user is in EXPLORE mode (HIGH_QUALITY), the client strictly filters out any post with a post.analysis.score < 70.
    - *Implication:* Content with poor argumentation structure is invisibly suppressed, regardless of how "viral" or emotional it might be.

### 3. Retrieval Strategy B: The Knowledge Graph (Related Posts)

This is the advanced recommendation engine (backend.getRelatedPosts). It uses a Remote Procedure Call (RPC) to Supabase (TatSat_hybrid_search) to perform a similarity search in vector space.

It uses a **Hybrid Vector Search** approach:

**Input:**

- query_embedding: The vector of the current post's content.
- query_topic_embedding: The vector of the current post's topic.

**The Algorithm (TatSat_hybrid_search logic inferred from arguments):**

It calculates **Cosine Similarity** between the active post and all other posts in the database.

- **Discovery (match_threshold: 0.5)**
    - Performs a Nearest Neighbor search (ANN or KNN).
    - Retrieves posts where the semantic distance is within a moderate range.
    - This encourages serendipity by finding loosely related concepts (e.g., linking "Urban Noise" to "Cortisol Levels").

### 4. Taxonomy of Recommendations

The frontend categorizes the recommendations returned by the vector search into three buckets (logic in components/PostInteractionPanel.tsx and inferred RPC return types):

1. **TOPIC:** High similarity in topic_embedding but lower in content_embedding. (Same field of study, different specific argument).
2. **CONTENT:** High similarity in content_embedding. (Directly related subject matter).
3. **HYBRID:** High similarity in both.

### Summary

The system implements a **Content-Based Filtering** recommendation engine utilising v**ector space models**.

1. **Vectorization:** Model(Content) -> R^n.
2. **Indexing:** Postgres pgvector (HNSW or IVFFlat index implicitly used).
3. **Ranking Function:**  where  is the current post vector.
4. **Filtering Function:** , where  is the quality threshold.

The "Magic" isn't in a collaborative filtering matrix (User-Item interactions), but in the **pre-computation of the DQS scalar**, which acts as a static weight or filter to enforce the platform's ethos of quality over popularity.

[https://unsw-my.sharepoint.com/:v:/g/personal/z5384798_ad_unsw_edu_au/IQBvsKw3g9RJQ7L9lLMpheEPARqntWhTAfIkK426JJy1txk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=gtEUv6](https://unsw-my.sharepoint.com/:v:/g/personal/z5384798_ad_unsw_edu_au/IQBvsKw3g9RJQ7L9lLMpheEPARqntWhTAfIkK426JJy1txk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=gtEUv6)