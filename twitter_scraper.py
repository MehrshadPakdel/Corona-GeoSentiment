# -*- coding: utf-8 -*-
"""
Created on Fri May  1 15:52:20 2020

@author: mehrs
"""
import os
import json
import time

import tweepy
import dataset

from utils import resources_dir

def collect_tweets():
    with open(os.path.join(resources_dir, 'twitter_credentials.json'), "r") as file:
        creds = json.load(file)
    
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    db = dataset.connect("sqlite:///geo_tweets_germany.db")
    
    
    geocode_germany = "51.163361,10.447683,450km"
    query = "#Corona" or "#Coronavirus" or "#covid19" or "#Coronakrise" or "#sarscov2" or "#SARS-CoV-2" or "#CoronaCrisis" or "#SARS-CoV2" or "Pandemie"
    
    count = 100
    page_count = 0
    try:
        for pages in tweepy.Cursor(api.search, q=query, count=count, geocode=geocode_germany, tweet_mode='extended').pages():
        
            for tweet in pages:
                created = tweet.created_at
                name = tweet.user.screen_name
                
                loc = tweet.user.location
                coords = tweet.coordinates
                
                description = tweet.user.description
                text = tweet.full_text
                
                id_str = tweet.id_str
                followers = tweet.user.followers_count
                retweets = tweet.retweet_count
                user_created = tweet.user.created_at
                
                if coords is not None:
                    coords = json.dumps(coords)
                    
                #if place is not None:
                    #place = json.dumps(place)
                
                if loc or coords is not None:
                    table = db["tweets"]
                    table.insert(dict(
                        created=created,
                        user_name=name,
                        
                        user_location=loc,
                        coordinates=coords,
                        
                        user_description=description,
                        text=text,
                        
                        id_str=id_str,
                        retweet_count=retweets,
                        user_followers=followers,
                        user_created=user_created,))
            
            page_count += 1
            print(page_count)
            if page_count >= 1000:
                break
    except tweepy.TweepError as e:
        if e == "[{u'message': u'Rate limit exceeded', u'code': 88}]":
            time.sleep(60*5) #Sleep for 5 minutes
        else:
            print(e)

collect_tweets()