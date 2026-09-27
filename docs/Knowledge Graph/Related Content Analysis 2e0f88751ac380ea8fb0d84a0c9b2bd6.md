# Related Content Analysis

# Sourcing

Aim is to source all the labels within each label type specified [Labels of a Related Content](Labels%20of%20a%20Related%20Content%202ddf88751ac3800abdc8f3bba1156373.md) 

Multi-level Clustering

Mid and High impact account Content : Re-do clustering once a week. Classify new content, within this gap, into lvl3 clusters using cosine similarity. 

Low-impact account content : Source using SimCluster Embeddings 

The semantic sourcing will be available only for high impact account posts’ underpost region. The semantically sources content will be from other high impact accounts. 

 

Example 

High impact Account @POTUS : He carried an operation in Venezuela yesterday night. 

High impact Account @Jimmy Kimmel (self assigned stance is against, hidden reply, self assigned topics - #ViolationofFreedom, #DictatorTrump) : Whatever u say US has violated the sovereignty of Venezuela for its own interests. 

High Impact Account @CNBCTV (hidden reply, self assigned label - NUANCE, self assigned present additional info, self assigned neutral stance) : Find out more about how USA carried this secret mission within 6 hours : https://….. 

High Impact Account 

786 dimensions semantic match for high impact lvl 2.

243 dimensions for semantic match medium impact for lvl 2.

Graph based sourcing for low impact / new clusters impact for lvl 2. 

Hight impact level 2 clusters, use decoder llms for classification and DQS. 

Low impact, classification taxonomy labels [Innate Traits of a Content](Innate%20Traits%20of%20a%20Content%202def88751ac38049a937ccffd79e8840.md) used to classify posts. 

# Labelling

User given label (if a user gives false, label they can be reported and their right to self assign a label will be revoked)

## 

# Ranking of the Related Content within Classes

(classed created using the labels)

1. Default - DQS + Engagement + Relevance 
2. Latest
3. Engagement
4. DQS
5. Relevance

(combinations of above)