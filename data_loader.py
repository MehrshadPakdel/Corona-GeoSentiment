from datetime import datetime
from datetime import timedelta

import pandas as pd
import sqlite3

def get_query_date_range(date_text: str):
    '''Function to convert a date string to range of -1 and + 1 days in 
    datetime format to limit sql search query date ranges for input date.
    
    Parameters
    ----------
    date_text : str
        date string as input. Allowed to following formats:
        ('%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y')

    Raises
    ------
    ValueError
        Value error if date format was not found.

    Returns
    -------
    query_date_min : datetime object
        input date -1 days
    query_date_max : datetime object
        input date +1 days

    '''
    # Controls for different datetime formats and converts to sqlite3 database
    # format '%Y-%m-%d'
    for fmt in ('%Y-%m-%d','%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y'):
        try:
            query_date = datetime.strptime(date_text, fmt).date()
            query_date.strftime('%Y-%m-%d')
            
            # calculates date ranges required for sql query
            query_date_min = query_date
            query_date_max = query_date + timedelta(days=1)

            return "'" + str(query_date_min) + "'", "'" + str(query_date_max) + "'"
        
        except ValueError:
            pass
        
    raise ValueError('no valid date format found')

def load_tweets_from_db(**kwargs):
    '''Function to retrieve twitter data from sqlite3 database with optional
    argument for 
    

    Parameters
    ----------
    **kwargs : query_date str.
        Use query_date argument to add date string for desired date of tweet 
        data.

    Returns
    -------
    df : pandas DataFrame object.
        Returns the dataframe object for the data base or query date.

    '''
    # connect to sqlite3 db and cursor
    conn = sqlite3.connect("geo_tweets_germany.db")
    c = conn.cursor()
    
    # get optional arguments for query_date
    query_date = kwargs.get('query_date', None)
    
    # if query_date is True, get query_date_min and query_date_max range from
    # the get_query_date_range function from utils
    if query_date:
        query_date_min, query_date_max = get_query_date_range(query_date)
        df = pd.read_sql_query(f'''SELECT
                               created,
                               user_name,
                               user_location,
                               text,
                               id_str,
                               retweet_count,
                               user_followers
                               FROM tweets WHERE created >
                               {query_date_min} AND created <
                               {query_date_max}''', conn)
    elif not query_date:
        df = pd.read_sql_query('''SELECT
                               created,
                               user_name,
                               user_location,
                               text,
                               id_str,
                               retweet_count,
                               user_followers
                               FROM tweets WHERE date(created) != "2020-05-06"''', conn) # removes 2020-05-06 data from db
    
    # close connection and return dataframe filtered for date
    c.close()
    conn.close()
    # easy way to remove duplicats based on twitter id_str 
    df.drop_duplicates(subset='id_str', keep="first", inplace=True)
    return df

if __name__ == '__main__':
    df = load_tweets_from_db()

