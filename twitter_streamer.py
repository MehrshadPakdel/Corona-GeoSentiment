import os
import json

import tweepy
import dataset
from textblob import TextBlob

from utils import resources_dir

class StreamListener(tweepy.StreamListener):
    
    def on_status(self, status):
        description = status.user.description
        loc = status.user.location
        text = status.text
        coords = status.coordinates
        geo = status.geo
        name = status.user.screen_name
        user_created = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        created = status.created_at
        retweets = status.retweet_count
        
        blob = TextBlob(text)
        sent = blob.sentiment
        polarity = sent.polarity
        subjectivity = sent.subjectivity
   
        if coords is not None:
            coords = json.dumps(coords)
        
        if geo is not None:
            geo = json.dumps(geo)
        
        if geo or coords or loc is not None:
            table = db["tweets"]
            table.insert(dict(
                user_description=description,
                user_location=loc,
                coordinates=coords,
                geo=geo,
                text=text,
                user_name=name,
                user_created=user_created,
                user_followers=followers,
                id_str=id_str,
                created=created,
                retweet_count=retweets,
                polarity=sent.polarity,
                subjectivity=sent.subjectivity,))
        
    def on_error(self, status_code):
        if status_code == 420:
            return False
        
if __name__ == '__main__':
    
    with open(os.path.join(resources_dir, 'twitter_credentials.json'), "r") as file:
       creds = json.load(file)

    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit = True)
    db = dataset.connect("sqlite:///geo_tweets.db")
    
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=["Corona", "Coronavirus", "COVID", "COVID19", "COVID-19", "SARS-CoV-2", "CoronaCrisis", "SARSCoV2", "SARS-CoV2"])
   
   