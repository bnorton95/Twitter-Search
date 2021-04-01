# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 21:35:12 2019

Author : Brian Norton
"""

import xlsxwriter as xl
import xlrd
import requests
from requests_oauthlib import OAuth1
import json
import os
from textblob import TextBlob
import matplotlib.pyplot as plt
from statistics import mean
import time
import sys



credentials = { # Replace these with credentials
    'CONSUMER_KEY': 'XXXXXX',
    'CONSUMER_SECRET': 'XXXXXX',
    'TOKEN_KEY': 'XXXXXX',
    'TOKEN_SECRET': 'XXXXXX',
}
tampa =    ('-82.475013, 27.827240, -82.391423, 28.171345')
lakeland = ('-81.879508, 28.098964, -81.013072, 29.098964')
orlando =  ('-81.503789, 28.446720, -81.292904, 28.627188')

#Authentication
def authenticate(credentials):
    #Authenticates the Twitter API with the given credentials
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
    """ Returns the Twitter data in the following format:
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
        try:
            text = line['extended_tweet']['full_text']
            returnData.append("Retweet")
        except:
            text = line['text']
            if (text.split())[0] == "RT":
                returnData.append("Retweet")
            else:
                returnData.append("Tweet")
    
    try:
        if TextBlob(text).detect_language() != 'en':
            text = TextBlob(text).translate(to='en')
            text = str(TextBlob("EN ")+text)
    except:
        {}
    returnData.append(text)
    
    
    return returnData


def prepareWorksheet(worksheet):
    #Used once to add in the tags above the data
    worksheet.write(0,0,"User ID")
    worksheet.write(0,1,"Screen Name")
    worksheet.write(0,2,"User Followers")
    worksheet.write(0,3,"User Friends")
    worksheet.write(0,4,"Tweet ID")
    worksheet.write(0,5,"Tweet Status")
    worksheet.write(0,6,"Text")
    
    

closeProgram = False


while not closeProgram:
    choiceRange = [0,2]
    print("1. Save a number of tweets from a local twitter stream")
    print("2. Analyze a saved twitter set")
    print("0. Exit")
    
    choice = -1
    
    
    while 1:
        try:
            choice = int(input("Please enter an option: "))
            if choice < choiceRange[0] or choice > choiceRange[1]:
                continue
            break
        except:
            continue  
    
    
    
    
    #Capture tweets
    if choice == 1:
        
        #Location of search
        print("1. Tampa")
        print("2. Lakeland")
        print("3. Orlando")
        while 1:
            try:
                tweetLoc = int(input("Enter the location you want to search: "))
                if tweetLoc == 1:
                    location = tampa
                    break
                elif tweetLoc == 2:
                    location = lakeland
                    break
                elif tweetLoc == 3:
                    location = orlando
                    break
                else:
                    continue
                break
            except:
                continue
        
        #Search term
        tweetSearch = input("Enter the term you want to collect related tweets to: ")
        
        #Number of tweets to search
        while 1:
            try:
                tweetNum = int(input("Enter the number of tweets to collect: "))
                if tweetNum < 1:
                    continue
                break
            except:
                continue
        
        #Authentication
        url = 'https://stream.twitter.com/1.1/statuses/filter.json'
        
        client = authenticate(credentials)
        try:
            response = client.get(url, stream=True, params={'track': tweetSearch, 'locations': location})
        except:
            print("Error: Twitter API connection could not be established. Ending program...")
            sys.exit()
        
        #File name creation
        j = 1;
        while True:
            fileName = os.getcwd()+'\\Stream_'+tweetSearch+'_'+str(j)+'.xlsx'
            if os.path.isfile(fileName): 
                break;
            j += 1
        print("Creating file at: "+fileName)
        
        
        
        if response.ok:
            tweetCounter = 0
            statuses = []
            
            workbook = xl.Workbook(fileName)
            worksheet = workbook.add_worksheet()
            prepareWorksheet(worksheet)
            
            then = time.time()
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
                        worksheet.write(i+1,j,data)
            except KeyboardInterrupt:
                {}
            finally:
                print('\nSuccess! Collected {} tweets.'.format(tweetCounter))
                workbook.close()
                now = time.time()
                print('Total search time: '+str(round(now-then,4))+" seconds")
        else:
            print('Connection failed. Error: {}'.format(response.status_code))
            
        
    #Analyze saved tweets 
    if choice == 2:
    
        #Creating the file directory to load
        fileArray = []
        for file in os.listdir(os.getcwd()):
            if file.endswith(".xlsx"):
                #print(os.path.join("/mydir", file))
                fileArray.append(file)
        
        
        if len(fileArray) == 0:
            print("No files found.")
        else:
            for index, value in enumerate(fileArray):
                print(str(index+1)+". "+str(value))
        print("0. Go to main menu")
        while 1:
            try:
                fileInput = int(input("Enter the file name in the current directory that you want to analyze: "))
                if fileInput <= len(fileArray)+1 and fileInput >= 0:
                    break;
            except:
                continue
        if fileInput == 0:
            print("\n\n\n")
            continue
        else:
            filePath = os.getcwd()+"\\"+fileArray[fileInput-1]
            print(filePath)
        
        #Opening the file
        try:
            workbook = xlrd.open_workbook(filePath)
            sheet = workbook.sheet_by_index(0) 
            rows = sheet.nrows
            columns = sheet.ncols            
            
            dataCollect = []
            for x in range(0,rows):
                val = []
                if x == 0:
                    continue
                for y in range(0,columns):
                    val.append(sheet.cell_value(x,y))
                dataCollect.append(val)
        except:
            print("Error: File not found.")
            
        #Manipulating the data
        polarity = []
        subjectivity = []
        for x in range(0,len(dataCollect)):
            polarity.append(TextBlob(dataCollect[x][6]).sentiment.polarity)
            subjectivity.append(TextBlob(dataCollect[x][6]).sentiment.subjectivity)
            
        #Sentiment analysis graph
        plt.xlabel('Polarity')
        plt.ylabel('Subjectivity')
        plt.plot(polarity,subjectivity,'ro')
        plt.plot(mean(polarity),mean(subjectivity),'ro',color='green')
        print("Sentiment analysis for the given set of tweets. Green = averages ")
        plt.show()
        
        #Friends/followers graph
        plt.clf()
        plt.xlabel('Friends')
        plt.ylabel('Followers')
        plt.xscale('log')
        plt.yscale('log')
        for x in range(0,len(dataCollect)):
            if dataCollect[x][5] == "Retweet":
                plt.plot(dataCollect[x][3],dataCollect[x][2],'ro',color='red')
            else:
                plt.plot(dataCollect[x][3],dataCollect[x][2],'ro',color='blue')
        print("User friends and followers. Red = Retweet, Blue = Tweet")
        plt.show()
        
        

    #Exit
    if choice == 0:
        closeProgram = True
