# Post Rating Tests

Asset includes Post, Comment, Reply, Link 

Aim is to get a scalar score of each post based on it’s content alone. 

Baseline Tests 1

Train a ML to score each post in scale of 1 to 10. 

ML Training - on a dataset that look like this : S no txt likes dislikes no. of comments views user-followers quotes retweets clicks shares reach saves profile visits DQS 

DQS - obtained from another source

Baseline Tests 2

Train a ML score each post in scale of 1 to 10. 

ML Training - on a dataset that look like this : S no txt likes dislikes no. of comments views user-followers quotes retweets clicks shares reach saves profile visits DQS 

DQS - obtained from making an llm score posts after explaining the good argument logic

Test 3

Train a Parent-ML score each post in scale of 1 to 10. 

Having a ML/rule based model extract each of features of a good argument logic for each post. 

And train the parent-ml model on dataset: 

S no features likes dislikes no. of comments views user-followers quotes retweets clicks shares reach saves profile visits DQS 

Test 4

Finetune an llm to completely rate a post on a scale of 1 to 10 and make it rate  each post based on the post.