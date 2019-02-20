# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 21:35:12 2019

Author : Brian Norton
"""


import requests
from requests_oauthlib import OAuth1
#import json
#import networkx as nx
#import sys


credentials = {
    'CONSUMER_KEY': 'p5oC7sS9IkH3s8LwzJiMqEDPF',
    'CONSUMER_SECRET': 'zSfzEBN3KRb53RwOJsaXDdDJiIpnxYLHgs1BvRjxfkgwb7CM8J',
    'TOKEN_KEY': '1032328784270254080-zPVukJRIWQInVuufzGPwEEXT9nAMwA',
    'TOKEN_SECRET': 'EIlItnR79j1JqGI7eFIPKFIVeF1rJVHD82Ja9VavzLB8S',
}
tampa = ('-82.475013,27.827240,-82.391423,28.171345')

#Authentication
def authenticate(credentials):
    try:
        oauth = OAuth1(client_key=credentials['CONSUMER_KEY'],
                      client_secret=credentials['CONSUMER_SECRET'],
                      resource_owner_key=credentials['TOKEN_KEY'],
                      resource_owner_secret=credentials['TOKEN_SECRET'],
                      signature_type='auth_header')
        client = requests.session()
        client.auth = oauth
        return client
    except (KeyError, TypeError):
        print('Error setting auth credentials.')
        raise

closeProgram = False

while not closeProgram:
    choiceRange = [1,3]
    print("1. Save a number of tweets from a local twitter stream")
    print("2. Analyze a saved twitter set")
    print("3. Exit")
    
    choice = 0
    
    choice = int(input("Please enter an option: "))
    while choice < choiceRange[0] or choice > choiceRange[1]:
        choice = int(input("Please enter an option between {} and {}: ".format(choiceRange[0],choiceRange[1])))
    
    #Capture tweets
    if choice == 1:
        print("Authenticating Twitter credentials")
        
        
        tweetSearch = input("Enter the keyword you want to search for: ")
        tweetNum = int(input("Enter the number of tweets to collect: "))
        
        
        url = 'https://stream.twitter.com/1.1/statuses/filter.json'

        client = authenticate(credentials)
        response = client.get(url, stream=True, params={'track': tweetSearch, 'locations': tampa})
        statuses = []
        
        if response.ok:
            print(tweetSearch)
            #f = open(fileName,"wb")
            num_tweets = 0
            try:
                for line in response.iter_lines():
                    if num_tweets == tweetNum:
                        break
                    if line:
                        #f.write(line + b'\n')
                        num_tweets += 1
                        print(".", end='', flush=True)
            except KeyboardInterrupt:
                # User pressed the 'Stop' button
                print()
                print('Data collection interrupted by user!')
            finally:
                # Cleanup -- close file and report number of tweets collected 
                #f.close()
                print()
                print('Collected {} tweets.'.format(num_tweets))
        else:
            print('Connection failed with status: {}'.format(response.status_code))
        
    #Analyze saved tweets 
    if choice == 2:
        print("TODO")
    
    #Exit
    if choice == 3:
        closeProgram = True
    
    

