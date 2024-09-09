# Import necessary functions and classes
from app_utils import  read_json
from twitch_utils import authenticate_and_return_oauthToken

# Load configurations and token
twitchConfig = read_json('./config/twitchconfig.json')
authToken = read_json('./config/authdata.json')

# Initialize token and streamer list
token = ''
token =  authenticate_and_return_oauthToken(twitchConfig)      