import os

import pandas as pd
import numpy as np

from textblob import TextBlob
import re

from utils import resources_dir

from data_loader import load_tweets_from_db

def add_coordinates_to_location(df):
    
    # load twitter data. Assign longitude and latitude columns to data frame
    # cleanup user_location column for data processing
    #df = pd.read_csv(os.path.join(resources_dir, '200506_geo_tweets_germany.csv'))
    #df['longitude'] = np.nan
    #df['latitude'] = np.nan
    df.loc[:, 'user_location'].replace(' ', np.nan, inplace=True)
    df.loc[:, 'user_location'] = df.loc[:, 'user_location'].astype(str)
    df = df.copy()
    
    # cleanup strings in user_location column. Split the strings and use first
    # city name and convert it to uppercase. Save new column as a new column
    # user_location_cleaned containing only the city names
    df_loc_split = df.loc[:, 'user_location'].str.split(",", expand=True)
    df_loc_split = df_loc_split[0].str.upper()
    df.loc[:, 'user_location_cleaned'] = df_loc_split
    df = df.copy()
    
    # load df_geo as data frame containing all german city data with longitude
    # and latitude and filter twitter data frame against german cities found 
    # in the geodata_german_cities.csv, save as df_loc_cleaned
    df_geo = pd.read_csv(os.path.join(resources_dir, 'geodata_german_cities.csv'))
    df_loc_cleaned = df.loc[df.loc[:, 'user_location_cleaned'].isin(df_geo.loc[:, 'City'])]
    df_loc_cleaned = df_loc_cleaned.copy()
    
    # create lists of city, long and lat data to create dicts for city:long or 
    # city: lat for filtering longitude, latitude data against city name 
    city_list = df_geo.loc[:, 'City'].tolist()
    longitude_list = df_geo.loc[:, 'longitude'].tolist() 
    latitude_list = df_geo.loc[:, 'latitude'].tolist()
    city_dict_longitude = dict(zip(city_list, longitude_list))
    city_dict_latitude = dict(zip(city_list, latitude_list))
    
    # map against city_dict_longitude and city_dict_latitude to add to
    # these columns the long, lat information based on city name
    df_loc_cleaned.loc[:, 'longitude'] = df_loc_cleaned.loc[:, 'user_location_cleaned'].map(city_dict_longitude)
    df_loc_cleaned = df_loc_cleaned.copy()
    df_loc_cleaned.loc[:, 'latitude'] = df_loc_cleaned.loc[: ,'user_location_cleaned'].map(city_dict_latitude)
    df_loc_cleaned = df_loc_cleaned.copy()
    #df_loc_cleaned.to_csv(os.path.join(resources_dir, '200506_geo_tweets_germany.csv'), header=True, index=True)
    
    return df_loc_cleaned

def sentiment_analysis(df):
    
    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        text = re.sub(': ', '', text)
        text = re.sub('_[A-Za-z0–9]+', '', text)
        text = re.sub(' +', ' ', text)
        text = re.sub('U+[A-Za-z0–9]+', '', text)
        
        emoj = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030""]+", re.UNICODE)
        
        text = re.sub(emoj, '', text)
        text = re.sub('\n', ' ', text)
        text = re.sub('\t', ' ', text)
        text = re.sub('"', ' ', text)
        text = re.sub('„', ' ', text)
        text = re.sub('“', ' ', text)
        text = text.strip()
        
        return text
    
    # Clean the tweets
    df['text'] = df['text'].apply(cleanTxt)

    # Create a function to get the subjectivity
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    # Create a function to get the polarity
    def getPolarity(text):
       return  TextBlob(text).sentiment.polarity

    # Create two new columns 'subjectivity' & 'polarity'
    df['subjectivity'] = df['text'].apply(getSubjectivity)
    df['polarity'] = df['text'].apply(getPolarity)
    
    # return the new dataframe with columns 'Subjectivity' & 'Polarity'
    
    return df

def filter_day_range(df):
    # format timestamps to datetime objects and assign to new column 
    # date_created as dates only
    df['created'] = pd.to_datetime(df['created'])
    df['date_created'] = df['created'].dt.date
    
    # get da pd series of unique dates and convert them to list
    date_range = df['date_created'].drop_duplicates().sort_values().to_list()
    
    # create a dict with key dates and values day number of this series
    # assigned to it
    day_range_list = [x+1 for x in range(len(date_range))]
    date_range_dict = dict(zip(date_range, day_range_list))
    
    # map day ranges to dataframe to day_range column
    df.loc[:, 'day_range'] = df.date_created.map(date_range_dict)
    
    # distribute range of 6 fixed data points distributed over the day range
    # of the data
    selection_day_range = np.linspace(min(day_range_list),
                                      max(day_range_list), 
                                      6,
                                      dtype='int').tolist()
    
    # based on selection_day_range: Assign the respective date strings to list
    # that correspond to day range list. Required for dropdown option list
    # in the figure
    selection_dates = [key.strftime('%d.%m.%Y') for (key, value) in date_range_dict.items() if value in selection_day_range]
    selection_dates.insert(len(selection_dates), 'Full dataset')
    
    # format time stamps for visualization
    df['created'] = pd.to_datetime(df['created'])
    df['created'] = df['created'].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    return df, selection_day_range, selection_dates

if __name__ == '__main__':
    df = load_tweets_from_db()
    df = add_coordinates_to_location(df)
    df, day_range_list, selection_dates = filter_day_range(df)
    