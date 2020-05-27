import os
import json

project_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(project_dir, 'resources')
docs_dir = os.path.join(project_dir, 'docs')

def dump_twitter_credentials_json():
# enter your twitter keys/secrets as strings in the following fields

    credentials = {}
    credentials['CONSUMER_KEY'] = 'YOUR CONSUMER KEY'
    credentials['CONSUMER_SECRET'] = 'YOUR CONSUMER SECRET'
    credentials['ACCESS_TOKEN'] = 'YOUR ACCESS TOKEN'
    credentials['ACCESS_SECRET'] = 'YOUR ACCESS SECRET'
    
    # Save the twitter API credentials as a json file to the resources folder
    with open(os.path.join(resources_dir, "twitter_credentials.json"), "w") as file:
        json.dump(credentials, file)

if __name__ == '__main__':
    dump_twitter_credentials_json()
