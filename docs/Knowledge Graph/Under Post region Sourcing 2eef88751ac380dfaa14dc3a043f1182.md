# Under Post region Sourcing

# Sourcing

1. Comments 
2. Replies 
3. Links 
    1. Hidden Replies (tag a post but not visible)
    2. Semantic Textual Similarity 
    3. High Impact Account within SimCluster

# b and c cost reduction Approach

## SimCluster

[https://dl.acm.org/doi/10.1145/3394486.3403370](https://dl.acm.org/doi/10.1145/3394486.3403370)

It’s a method of clustering Users and Posts together into communities of interest. It works by graph relations [Terminology](../Terminology%202d2f88751ac380828890f4d63c4b303b.md).

SimClusters lies in the heart of X’s (aka twitter) recommendation engine. 

Structure of a SimCluster: a SimCluster contains impactful accounts in the centre surrounded by less impactful accounts that follow and engage with the former’s content. The posts made by all the accounts are included in a cluster if it has high engagement by the users in that cluster. 

SimCluster are updated once every week.

### Problem with SimClusters

It creates small communities where people only engagement with the content of that community. Twitter tries to create a mix by using random walk algorithms and BERT embeddings (small percent of content) but is fails to achieve a broadcasting news environment and in many ways similar to how a reddit feed works. 

People are reserved to their own communities - 

Democrats receive their own community posts and never get access to the republican content. 

## Underpost Region b and c

We can make use of SimCluster as a way to reduce the load on our STS. 

Ideally we would want to embed all the content on our platform and get related content but this approach has 2 major problems 

1. Cost: Embedding all the content is a very costly affair and would not be feasible initially. 
2. Quality: just like twitter, our platform is likely to receive many factually inaccurate posts. Factually inaccurate posts can be highly engaging and can make their way to recommendation.
    
    If our underpost sourcing algorithms is purely based on STS of whole of twitter, then underpost regions can contains a lot of factually inaccurate content just being engaging and the people who preferred to only see posts from credible sources can feel that our platform is full inaccuracies. 
    

None of the social media platforms perform factual check on their content. 

Doing factual test is virtually and impossible because of the news is shaped by the mainstream media houses. 

Even if we manage find a way fact-check content, we may end offending some community. 

Solution

Fact inaccuracies coming from influential people is still a news, the problem is mainly the factual inaccuracies that come from smaller, newer spam accounts. 

Assuming that we SimCluster for Tat-Sat, we use these clusters to identify influential accounts and vector embed the content of only the influential accounts. 

We then form clustering of the vector embeddings made by these influential accounts and use it to source “link” for the underpost region. 

Problem with the solution : the (b) and  (c) based link we be available only for the high influential account post and will only be from other influential accounts. But other forms of links will be available for smaller accounts and they will still have an opportunity to place make themselves visible in the underpost region by using comments replies and hidden replies (link).