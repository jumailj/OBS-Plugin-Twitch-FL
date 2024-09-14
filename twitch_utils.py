#author: jumail-j
#data : 2024-08-25

import requests
import os
from datetime import datetime

from app_utils import calculate_Expire_Time, write_json, read_json, isTokenExpired

# absolute-scriptfile-dir 
script_dir = os.path.dirname(os.path.abspath(__file__))


def authenticate_and_return_oauthToken(configData):
    authorization_code = ''
    #permission for read and edit chat
    authorization_url = f"https://id.twitch.tv/oauth2/authorize?client_id={configData['client_id']}&redirect_uri={configData['redirect_uri']}&response_type=code&scope={configData['scope']}"

    #todo change method to automate it.
    print("Please go to the following URL and authorize the application:")
    print(authorization_url)

    authorization_code = input("Enter the authorization code from the callback URL: ")

    token_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': configData['client_id'],
        'client_secret': configData['client_secret'],
        'code' : authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri' : configData['redirect_uri']
    }

    #todo set expire-time, auto autho later.
    response = requests.post(token_url, params=params)
    #get the expire time and refresh token.
    data = response.json()
    del data['scope']
    del data['token_type']

    #reduce 60 seconds from actual expiry time:
    data['expires_in'] -= 60

    # convert expires_in, int time format.datatime object to string object, for adding it on json
    # using utc time.
    exp_time = calculate_Expire_Time(data['expires_in']).isoformat()
    data['expires_in'] = exp_time

    #write it to token file
    #TODO, CHANGE THE FILE NAME TO THE ABSOLUTE PATH.
    write_json(os.path.join(script_dir, 'config/authdata.json'),data)


    #if the access_token present, then return
    if 'access_token' in data:
        oauth_token = data['access_token']
        return oauth_token # return the new auth token
    else:
        print('Failed to obtain OAuth token:', data)
        return 0

def authenticate_with_refresh_token_and_return_oauthToken(configData,authToken):
    print('########################################')
    print(configData)
    print(authToken)
    #construct the request parameters
    print("generating new token!")
    print('---------------refresh token')
    print(authToken['refresh_token'])

    params = {
        "grant_type": 'refresh_token', 
        'client_id': configData['client_id'] ,
        'client_secret': configData['client_secret'],
        'refresh_token': authToken['refresh_token'] ,
    }

    headers = {
        'Content-Type':'application/x-www-form-urlencoded'
    }

     # Send the token exchange request
    response = requests.post('https://id.twitch.tv/oauth2/token',headers=headers, params=params)

    #get the expire time and refresh token.
    data = response.json()
    print('-----------------------------response data---------------------------------')
    print(data)
    del data['scope']
    del data['token_type']

    #reduce 60 seconds from actual expiry time:
    data['expires_in'] -= 60

    # convert expires_in, int time format.datatime object to string object, for adding it on json
    # using utc time.
    exp_time = calculate_Expire_Time(data['expires_in']).isoformat()
    data['expires_in'] = exp_time


    #TODO, CHANGE FILE PATH TO ABSOLUTE
    # write_json('./config/token.json',data)
    write_json(os.path.join(script_dir, 'config/authdata.json'),data)


    if 'access_token' in data:
        oauth_token = data['access_token']
        return oauth_token # return the new auth token
    else:
        print('Failed to obtain OAuth token:', data)
        return 0

def ValidateToken(twitchConfig,authToken):
    if(len(authToken) == 0):
        print('Please Authinticate with twitch')
        sys.exit()
        
    # check if the authtoken present and the time expired!
    ExpireTime = authToken['expires_in']
    ExpireTime = datetime.strptime(ExpireTime,"%Y-%m-%dT%H:%M:%S.%f")

    if(len(authToken)!= 0 and isTokenExpired(ExpireTime)):
        print('time expired')
        newToken = authenticate_with_refresh_token_and_return_oauthToken(twitchConfig, authToken)
        print('new token ===')
        print(newToken)
        return newToken
        
    if ( authToken['access_token']):
        return authToken['access_token']

def isUserLive(userName, token, client_id):
        # Define the URL of the Twitch Helix API endpoint to check if a user is live
    stream_info_url = 'https://api.twitch.tv/helix/streams'

    # Define the parameters for the specific user you want to check
    params = {
        'user_login': userName 
    }

    # Define the headers with the client ID 
    headers = {
        'Authorization': f'Bearer {token}', 
        'Client-Id': client_id 
    }
    

    # Send a GET request to the Twitch API to fetch stream information for the specific user
    response = requests.get(stream_info_url, headers=headers, params=params)

    # Parse the response as JSON
    stream_data = response.json()

    # Check if the user is live
    if 'data' in stream_data and len(stream_data['data']) > 0:     
        return True #it's true when user is live
    else:    
        return False #it's not true when user is not live

#game this is the develo