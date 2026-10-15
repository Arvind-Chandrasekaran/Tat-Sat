# System design

The original visual architecture is preserved in
[`readme/system_design.jpg`](readme/system_design.jpg).

The maintained, reviewable source diagrams are Mermaid files:

- [`docs/uml/system-architecture.mmd`](docs/uml/system-architecture.mmd)
- [`docs/uml/post-submission-sequence.mmd`](docs/uml/post-submission-sequence.mmd)
- [`docs/uml/post-verification-sequence.mmd`](docs/uml/post-verification-sequence.mmd)
- [`docs/uml/domain-data-model.mmd`](docs/uml/domain-data-model.mmd)

The current implementation ends at Redis enqueueing. The verifier, feed,
knowledge graph, moderation, and recommendation services remain TODOs.