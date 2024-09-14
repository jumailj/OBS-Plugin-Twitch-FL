# #author: jumail-j
# #date: 2024-08-27

#third-party
import obspython as obs 
import requests 
#system-lib
import threading 
import sys 
import os 
import time
from datetime import datetime 

# absolute-scriptfile-dir 
script_dir = os.path.dirname(os.path.abspath(__file__))

#utility helper functions
from app_utils import read_usernames, calculate_Expire_Time, write_json, read_json, isTokenExpired
from twitch_utils import ValidateToken, isUserLive
from circular_list import CircularList
from source_utils import create_browser_source, show_source, add_source_below, delete_source

#global-variables
userlist = None
circular_user = None
twitchConfig = None
authData = None
scriptEnabled = None
watchTime = 1
sourceIndex = 0

browserWidth = None
browserHeight = None

#browser-source-config
browserSourcePosX= None
browserSourcePosY = None
scaleFactor = None


def script_description():
    return "Twitch Automation"

# Define script properties
def script_properties():
    props = obs.obs_properties_create()

    #enable and disable script
    obs.obs_properties_add_bool(props, "enable_script", "Enable Script")

    #how much time to watch a each stream.
    obs.obs_properties_add_int(props, "watch_time", "Watch Time (s)", 1,  100, 1)

    #browser scale
    obs.obs_properties_add_float(props, "scale_factor", "Scale", 0, 1, 0.1)

    #browser-windows-size
    obs.obs_properties_add_int(props, "browser_width", "Browser Width", 0, 3000, 1)
    obs.obs_properties_add_int(props, "browser_height", "Browser Height", 0, 3000, 1)

    #browser-windows-position
    obs.obs_properties_add_int(props, "browser_pos_x", "Position X", 0, 2000, 1)
    obs.obs_properties_add_int(props, "browser_pos_y", "Position Y", 0, 2000, 1)



    return props

# Update script properties based on user input
def script_update(settings):

    #enable script, if it's enabled start the user list from index 0
    #only need to check enable script property, only it's enabled reset the userslist.
    global scriptEnabled
    global sourceIndex
    global watchTime
    global scaleFactor
    global browserWidth
    global browserHeight
    global browserSourcePosX
    global browserSourcePosY

    scriptEnabled = obs.obs_data_get_bool(settings, "enable_script")
    obs.obs_data_set_bool(settings, "enable_script", scriptEnabled)

    watchTimeInSeconds = obs.obs_data_get_int(settings, "watch_time")
    obs.obs_data_set_int(settings, "watch_time",watchTimeInSeconds )

    watchTime = watchTimeInSeconds * 1000
    print('script Updated: watchtime: ', watchTime)

    #update scale factor.
    scaleFactor = obs.obs_data_get_double(settings, "scale_factor")

    #browser-window-size
    browserWidth = obs.obs_data_get_int(settings, "browser_width")
    obs.obs_data_set_int(settings, "browser_width", browserWidth)

    browserHeight = obs.obs_data_get_int(settings, "browser_height")
    obs.obs_data_set_int(settings, "browser_height", browserHeight)

    #update browser position
    browserSourcePosX = obs.obs_data_get_int(settings, "browser_pos_x")
    browserSourcePosY = obs.obs_data_get_int(settings, "browser_pos_y")

    if(scriptEnabled):
        circular_user.reset()
        sourceIndex = 0




def validateAndUpdateBrowser():
    #if app is not validate, script will exit,
    #auth data shoudl be update, because once the auth is updated, need to change on the authData variable
    global authData
    global sourceIndex

    authData = read_json(os.path.join(script_dir, 'config/authdata.json'))
    token = ValidateToken(twitchConfig,authData)
    
    currentUser = None

    while True:

        #TODO one problme is when the users all offline. it can makes problmes.
        
        currentUser = circular_user.next()
        print('current user')
        print(currentUser)
        isCurrentUserLive = isUserLive(currentUser, token, twitchConfig['client_id'])

        if isCurrentUserLive:
            print(f"user{currentUser} is live. stopping the check.")
            break
        else:
            print(f"user {currentUser} is offline")
            time.sleep(0.4)

    #generate link for the current user
    streamerLink = f"https://www.twitch.tv/{currentUser}"
    
    sourceIndex +=1

    if (sourceIndex <= 1): #for initail startup we have to create a browser-1 source.
        create_browser_source( str(sourceIndex) , streamerLink,browserWidth, browserHeight, scaleFactor, browserSourcePosX ,browserSourcePosY)
    else:
        target = sourceIndex -1 
        # add_source_below(str(target), str(sourceIndex), "browser_source", streamerLink, 1920, 1080)
        add_source_below(str(target), str(sourceIndex), streamerLink,browserWidth, browserHeight, scaleFactor, browserSourcePosX ,browserSourcePosY)

        #give a safe seconds,for loading time.
        time.sleep(5)
        delete_source(str(target))
    
def run_task():
    #script will not work once the user is enabled the script
    if scriptEnabled:
        #start a new thread for validate and update the browser.
        thread = threading.Thread(target=validateAndUpdateBrowser) # argument example (target=fetch, args=(url, etc,))
        thread.start()

# Function to initialize script
def script_load(settings):
    scriptEnabled = obs.obs_data_get_bool( settings, "enable_script")

    watchTimeInSeconds = obs.obs_data_get_int(settings, "watch_time") * 1000
    print('watch time when script loaded', watchTimeInSeconds)
    watchTime = watchTimeInSeconds

    #call back all the value back to the global vairables;
    #load all the default value
    scaleFactor = obs.obs_data_get_double(settings, "scale_factor")
    browserWidth = obs.obs_data_get_int(settings, "browser_width")
    browserHeight = obs.obs_data_get_int(settings, "browser_height")
    browserSourcePosX = obs.obs_data_get_int(settings, "browser_pos_x")
    browserSourcePosY = obs.obs_data_get_int(settings, "browser_pos_y")


    #it will update the global, instead of taking it as a local varable.
    global userlist, circular_user, twitchConfig, authData

    #load all the user data
    userlist = read_usernames(os.path.join(script_dir, 'userlist.txt'))
    twitchConfig = read_json(os.path.join(script_dir, 'config/twitchconfig.json'))
    authData = read_json(os.path.join(script_dir, 'config/authdata.json'))

    # add it to a global circular user list.
    circular_user = CircularList(userlist)


    # #token shoud be read from file each time.
    print(userlist)
    print(twitchConfig)
    print(authData)

    # run_task(circular_user.next)

    print('watch time ' + str(watchTime))
    if ( watchTime <= 10000):
        watchTime = 10000

    obs.timer_add(run_task, watchTime)
    
    # Retrieve and apply the boolean value from script settings

def script_tick(seconds):
    pass
    # print(seconds)

# Function to clean up when the script is unloaded
def script_unload():
    obs.timer_remove(run_task)
    pass
