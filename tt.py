import re
import time
import sys
import tweepy
import os
from json import dumps, dump, loads
from tweepy import OAuthHandler
from py2neo import authenticate, Graph
from textblob import TextBlob
from json import dumps, dump, loads

consumer_key = 'yjD9RIXnknpmWfUzZWGRmZ0lV'
consumer_secret = 'H2HIWAAAahh2vjXDvkAzgJ7JXWbRVRoMWsTMXs4tlTUHc0zSQo'
access_token = '1106948527-CE97yEn5mJx2bn2SsfsllYqIM3Ydz3wOmYIkUtr'
access_secret = 'kfqvkn8K6fLLMMHa0knxdIbBF3LFI11zsqtfa7ztqCMe2'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
auth.secure = True


#api = tweepy.API(auth)
#public_tweets = api.home_timeline()
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True, parser=tweepy.parsers.JSONParser())

authenticate("localhost:7474", "neo4j", "1234")
db = Graph("http://localhost:7474/db/data")

#def clean_tweet(tweet):
#
#    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
#
#def get_tweet_sentiment(tweet):
#
#    analysis = TextBlob(clean_tweet(tweet))
#    # set sentiment
#    if analysis.sentiment.polarity > 0:
#        return 'positive'
#    elif analysis.sentiment.polarity == 0:
#        return 'neutral'
#    else:
#        return 'negative'

key_word = 'EPN'
tweets = api.search(q = key_word,rpp = 100, count=100, show_user=True)["statuses"]

def post_tweets(keyword_string):

    try:
        db.run("""
            CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE
            CREATE CONSTRAINT ON (u:User) ASSERT u.screen_name IS UNIQUE
            CREATE CONSTRAINT ON (s:Source) ASSERT s.name IS UNIQUE
        """)
    except:
        pass

    tweets = api.search(q = key_word,rpp = 100, count=100)["statuses"]

    print(tweets)

    query_string = """
    UNWIND {tweets} AS t
    WITH t
    ORDER BY t.id

    WITH t,
        t.entities AS e,
        t.user AS u,
        t.retweeted_status AS retweet
    MERGE (tweet:Tweet {id:t.id})
    SET tweet.text = t.text,
        tweet.created_at = t.created_at,
        tweet.favorites = t.favorites_count

    MERGE (user:User {screen_name:u.screen_name})
    SET user.name = u.name,
        user.location = u.location,
        user.followers = u.followers_count,
        user.statuses = u.statusus_count

    MERGE (user)-[:POSTS]->(tweet)

    MERGE (source:Source {name:t.source})
    MERGE (tweet)-[:USING]->(source)

    FOREACH (r IN [r IN [t.in_reply_to_status_id] WHERE r IS NOt NULL] |
        MERGE (reply_tweet:Tweet {id:r})
        MERGE (tweet)-[:REPLY_TO]->(reply_tweet)
    )

    FOREACH (retweet_id IN [x IN [retweet.id] WHERE x IS NOt NULL] |
        MERGE (reply_tweet:Tweet {id:retweet_id})
        MERGE (tweet)-[:RETWEETS]->(retweet_tweet)
    )
    """
    db.run(query_string, {'tweets':tweets})

def get_JSON(key_word):

    users_tweets_query= """
    MATCH (n:User)-[r:POSTS]->(m:Tweet) where  NOT (m)-[:RETWEETS]->()
    MATCH (p:Keyword {name:'"""+key_word.lower()+"""'})-[:TAGS]->(m)
    RETURN type(r) as type, m.id as tweet_id,  m.text as tweet_text, n.screen_name as screen_name, n.name as name, n.followers as followers, n.following as following LIMIT 100
    """

    query_user = db.run(users_tweets_query).data()

    query_user_string = dumps(query_user, sort_keys=True, indent=2, separators=(',', ': '))

#public_tweets = api.home_timeline()

for tweet in tweets:
    print (tweet)