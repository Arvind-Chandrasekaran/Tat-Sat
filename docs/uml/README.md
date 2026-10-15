# TatSat UML and architecture diagrams

These files are Mermaid source diagrams. GitHub and most Markdown viewers
render `.mmd` files when they are embedded or copied into a Mermaid code
block.

| Diagram | Answers |
| --- | --- |
| [`system-architecture.mmd`](system-architecture.mmd) | What services exist and which boundaries are implemented? |
| [`post-submission-sequence.mmd`](post-submission-sequence.mmd) | How does an authenticated client submit a post? |
| [`post-verification-sequence.mmd`](post-verification-sequence.mmd) | How should queued posts be verified and persisted? |
| [`feed-sequence.mmd`](feed-sequence.mmd) | How does the public feed paginate active posts? |
| [`topic-model-batch.mmd`](topic-model-batch.mmd) | How are active posts assigned batch topics? |
| [`domain-data-model.mmd`](domain-data-model.mmd) | Which domain entities and relationships are defined in SQL? |

Solid edges represent implemented or directly wired behavior. Dashed edges
represent scaffolding or planned services. Keep these diagrams synchronized
with the service READMEs and [`schema_unified.sql`](../../schema_unified.sql).

## Diagram maintenance TODO

- [ ] Add a deployment diagram once environments, domains, and managed
      services are finalized.
- [ ] Add a queue state diagram after consumer groups, retries, and
      dead-letter behavior are implemented.
- [ ] Add a feed/ranking component diagram when ranking is implemented.
- [ ] Add an authentication/session sequence diagram when the frontend session
      flow is wired.
