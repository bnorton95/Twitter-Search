# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 21:35:12 2019

Author : Brian Norton
"""

import xlsxwriter as xl
import requests
from requests_oauthlib import OAuth1
import json
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
        
def extractData(line):
    """ Returned in the following format:
    [   User ID,
        Screen Name,
        User Followers,
        User Friends,
        Tweet ID,
        Tweet/Retweet Status,
        Text   ] """
    
    returnData = []
    returnData.append(line['user']['id'])
    returnData.append(line['user']['screen_name'])
    returnData.append(line['user']['followers_count'])
    returnData.append(line['user']['friends_count'])
    returnData.append(line['id'])
    try:
        text = line['retweeted_status']['extended_tweet']['full_text']
        returnData.append("Retweet")
    except:
        returnData.append("Tweet")
        try:
            text = line['extended_tweet']['full_text']
        except:
            text = line['text']
    returnData.append(text)
    
    return returnData

def prepareWorksheet(worksheet):
    worksheet.write(0,0,"User ID")
    worksheet.write(0,1,"Screen Name")
    worksheet.write(0,2,"User Followers")
    worksheet.write(0,3,"User Friends")
    worksheet.write(0,4,"Tweet ID")
    worksheet.write(0,5,"Tweet Status")
    worksheet.write(0,6,"Text")
    
    

closeProgram = False

while not closeProgram:
    choiceRange = [0,21]
    print("1. Save a number of tweets from a local twitter stream")
    print("2. Analyze a saved twitter set")
    print("0. Exit")
    
    choice = -1
    
    choice = int(input("Please enter an option: "))
    while choice < choiceRange[0] or choice > choiceRange[1]:
        choice = int(input("Please enter an option between {} and {}: ".format(choiceRange[0],choiceRange[1])))
    
    #Capture tweets
    if choice == 1:
        
        tweetSearch = input("Enter the term you want to collect related tweets to: ")
        tweetNum = int(input("Enter the number of tweets to collect: "))
        
        url = 'https://stream.twitter.com/1.1/statuses/filter.json'
        client = authenticate(credentials)
        response = client.get(url, stream=True, params={'track': tweetSearch, 'locations': tampa})
        
        fileName = 'TweetSearch.xlsx'
        
        if response.ok:
            tweetCounter = 0
            statuses = []
            
            workbook = xl.Workbook(fileName)
            worksheet = workbook.add_worksheet()
            prepareWorksheet(worksheet)
            
            try:
                for line in response.iter_lines():
                    if tweetCounter == tweetNum:
                        break
                    if line:
                        statuses.append(extractData(json.loads(line)))
                        tweetCounter += 1
                        print(".", end='', flush=True)
                for i, status in enumerate(statuses):
                    for j, data in enumerate(status):
                        worksheet.write(i+2,j,data)
                        #print("{} {} {} {}".format(status,i,data,j))
            except KeyboardInterrupt:
                {}
            finally:
                print()
                print('Success! Collected {} tweets.'.format(tweetCounter))
            workbook.close()
        else:
            print('Connection failed. Error: {}'.format(response.status_code))
            
        
    #Analyze saved tweets 
    if choice == 2:
        print("TODO")
    
    #Exit
    if choice == 0:
        closeProgram = True
    
    

