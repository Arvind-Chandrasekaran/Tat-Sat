# Temporal Relevancy

# Intro

Tat-Sat is fundamentally a news discussion and news opinion-sharing platform. If a user open’s Tat-Sat feed, he would expect to see the news that is relevant to them and the people’s opinion in the form and discussions on this news. 

News comprises of factual information and opinions both. 

Factual Information includes, updates, announcements and 

### Example

(hypothetical examples)

- Post by the President of the US: I’m gonna increase the tariffs on China, they’ve been profiting of American money and we get nothing is in return.

- Comment by an high school teacher: I wonder how it’s gonna the electronics prices in the US, guess i’ll buy the new iphone before this happens.

- Reply by a political scientist: The tariff is gonna destroy  our relationship with Beijing, we are headed towards another cold war.

- Reply by a economist: This is gonna have huge impact on the tech sector, especially companies like Apple are gonna have find other location replace China, not gonna be easy for them. Might as well see them crippling.

- Link by a news-outlet: Almost 45% manufacturing of electronics by american companies takes place in China, read this article for more: https:…….

- Reply by a political spokes person to the economist: Apple has already shifted its ipad manufacturing to India, they’ve be planning this exit for quite sometime now.

Tat-sat will be filled with these kinds of micro-discussions. Each micro-discussion belongs to a topic cluster and add up to a greater discussion representing a greater trend in that topic. Political cluster usually end show greater debate associated with political spectrum (left vs right, top vs down). 

A micro-discussion starts with a seed News content , followed by reaction posts. Reactions can posts can further serve as seeds for more micro-discussions. 

 

# Feed

When opening the feed, a suer would expect to see the news that is relevant to them and the people’s opinion in the form and discussions on this news. 

One of the metrics of relevancy is temporal relevancy, and we discuss how this will decide the content on the platform. 

## 1. User expects to receive recent news when they open the feed

Certain News can lose their relevancy with time for a particular user. 

### Example

User A: Normal citizen who uses tat-sat for govt announcements and follows govt handles and media outlets on tat-sat.

Person B: Follows vaccine news and updates. Interested in public health related measures. 

Person C: Researcher, who is tracking vaccine news from Covid era for academic purposes. 

In 27 Dec 2025, 

Post 1 from 12 feb 2022 : “covid vaccine certificate is mandatory to travel inter-state” 

Post 2 post from 26 dec 2025 “covid vaccine certificate is mandatory to travel inter-state” 

1. Post 1 is irrelevant to user A and would not be recommended in topic + graph based recommendation.
2. Post 2 is relevant to user A and would be recommended in topic + graph based recommendation assuming he follows the right accounts. 
3. Post 1 is irrelevant to user B, since he only follows vaccine updates and seeing this old update in their feed would confuse them more (making them check the date of the post and other sources to verify whether there is mandate in dec 2025 : confusing and cumbersome).
4. Post 2 is relevant to user B and would be recommended in topic + graph based recommendation ranking pretty high. 
5. Post 1 is relevant to user C in one sense that they researching on the topic, but usually when user C opens their feed it is to gain general national and international news and not probably not their work related data.
6. Post 2 is relevant to user C and would be recommended in topic + graph based recommendation assuming he follows the right accounts. 

### News Cycle Theory

In a fast paced urban lifestyle, news is consumed on a daily basis and is relevant only for 24 hours. 

News is thus realtime and is constant updated through the day. 

[https://en.wikipedia.org/wiki/24-hour_news_cycle](https://en.wikipedia.org/wiki/24-hour_news_cycle) (references) 

### Solution

Feed should only recommend posts that are not older than yesterday morning. This allows recent information to be present in the feed. 

A researcher can use the search feature to look all the old posts and perform a observe trends if needed for their research. 

(be careful for bots stealing the data)

Existing news related platforms like twitter have a very similar approach. 

But other platforms like YouTube, (which more is less towards realtime news and opinion) and more towards learning and infotainment can recommend posts as old as 13 years. 

Tat-Sat is more inclined towards realtime news. 

## 2. Did not open tat-sat for a short period

A user may sometimes not open tat-sat for short periods like 3 to 7 days and may end up missing news that highly relevant to them despite the news cycle theory.  (in some cases news can be relevant for more than 48 hours and can be missed)

Problem 1

I am a cricket followers and usually get the squad announcements from BCCI’s official twitter handle. India’s t20 world cup squad announcement happened 3 days ago and will not get this high relevance news on my feed. 

Solution

Majority of the high relevance news are debated and discussed in their clusters for a some period. 

These debates and discussion content will be present in the user feed (since the post was high relevance and related posts will be highly recommended on both graph + topic based recommendation). 

When user clicks on a discussion, they would be able to see the news posts as a topic within links in the under-post region. 

In this case, there could be Harsha Bhogle talking about Jitesh Sharma’s exclusion and the underpost region should present the squad announcement by BCCI (since I follow it) within a News topic within the underpost region. 

Tat-Sat provides realtime news and opinions and the all the relevant info to understand and enhance this realtime news + opinion consumption experience. 

Problem 2

Important but low relevance posts may still be missed. 

A user may follow a govt account to get important alerts on mask mandates and public health related to info. 

But if the user does not consume public health related posts regularly, then related discussion posts will be ranked higher in topic + graph recommendation. Since a user follows the account the post should be present in the feed if they open the Tat-Sat within 48 hours of the posts but if they do not they are likely miss it forever. 

Solution

We allow accounts to create a alert posts (for importance announcements) with a flair for their posts. 

These flairs will make this posts get a red alert siren animation, when scrolling through the feed (ensuring that it catches the attention of the user if they have their feed open within news cycle timeframe). 
Moreover, user can choose to get all these alert posts from specific accounts accumulated from in an inbox feature (on the top right corner of the screen) with notification on and these alert posts. 

If the click on inbox all alert posts will be present there in single window. 

The red siren will also be displayed only of user chooses to accept the alert content from the account. 

This feature could also be used by companies that sell limited edition sneakers that last only for a few hours allows them to make announcements to a wide audience. 

Question? what is accounts end mis using this feature and create too many alert posts. The user can opt out of it and by default they will be opted out of all accounts.

Municipal corporations and other agencies and let people know to activate the alert feature and these accounts will not misuse this feature. (govt bodies using tat-sat becuase it will be the only platform that his feature). 

Social media usually do not have obligations to share alert posts on the top by govt bodies. No social media does anything for it. But we at Tat-Sat are concerned about the user and their news consuming pattern. (this USP has to marketed correctly to govt body and they end up asking people download it and keep the alert on) (council of randwick asking people to do it) 

Tat-Sat hence is an all in platform for news. 

 

### 3. Old Relevant News

Old relevant news includes news that provides details that are either necessary to consume or enhance the consumption of recent news. 

This includes 

1. Old Factual information: that is valid for a very long time. 
    
    Ex - Republic News 2025: Ind and Pak are in the brink of a war. 
    Republic News 2025: India has 3 posts in Kashmir that become relevant in future conflict with Pak. 
    

1. Old Contextual information: This also includes old news that has become relevant now due to the link with the recent news. 
    
    Ex - Trump 2025: I dont care about India. 
    Trump 2015: India is best ally. 
    

By having the 48 hours filter we may never receive these old relevant news. 

Solution 

The correct place if this information is the not the feed but the under post region:

Firstly, even if we receive this old relevant news in our feed, we have do our own inferences associated with recognising an old post and looking at the new one and inferring the hypocrisy or evolution of Trump. This cumbersome. 

Secondly, most of users have multiple interests 

It could something like Indian army, and knowing the indian army bases’ location in pak front is something that the user would love to do. 

But they have many interests. They follow AI, football, cricket and American India politics and there is too much information that they can learn from every one of these topics. Their feed can be keep be on  bombarded with a lot of information posts and their minds can be clogged with this. (Information fatigue syndrome) 
Ideally the user would want the info only when it is relevant to them, The information becomes relevant to them when there is a relevant recent news update associated with it. 

If there is going to be a war soon and I am interested in the knowing updates, I click on a recent news post and receive the relevant military bases information in the under-post region.  

If a user really needs an info without any realtime association with it, the user can search for it.

Usually this is the expectation from YouTube but  it would not be from micro-blogging platform like Twitter. 

So the solution, having a category for old contextual information within the links in the underpost region. (other representation ways can be explored but should be in underpost region)

What happens if you click an old post : you still a rabbit from that period of time. With possibly the new posts in the underpost region. 

What about evergreen debates like socialism vs capitalism?

Only recent discourses, pertaining to recent news, from these topics will be available in the feed. Old ones can be found in the underpost region. 

People who super passionate about these specific topics usually use Reddits. If a recent news provokes this discussion I see people re-posting old discourse points and also tagging them by manual search. It is also common for people link Reddit.