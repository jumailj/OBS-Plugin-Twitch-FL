# author: jumail-j
# date:  2024-08-24
import json
import time
import datetime

def read_usernames(file_path):
    try:
        with open(file_path, 'r') as file:
            usernames = [line.strip() for line in file]
            print('[LOG] ' + file_path + ' file Loaded ' )
            return usernames
    except FileNotFoundError:
        print( '[ERROR] ' + file_path + 'file was not found!')
        exit()
    except IOError:
        print( '[ERROR]: An I/O error occurred while trying to read ' + file_path )
        exit()

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print( '[LOG] ' + file_path + ' Loaded ' )
            return data
    except FileNotFoundError:
        print( '[ERROR] ' + file_path + ' was not found!' )
        exit()
    except json.JSONDecodeError:
        print('[ERROR] Failed to decode JSON from ' + file_path )
        exit()
    except IOError:
        print( + '[ERROR] An I/O error occurred while trying to read ' + file_path )
        exit()


def write_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print('[LOG] ' + file_path + ' file Updated ' )
    except FileNotFoundError:
        print( '[ERROR] ' + file_path + ' was not found!' )
    except json.JSONDecodeError:
        print( '[ERROR] Failed to decode JSON from ' + file_path )
    except Exception as e:
        print(f"Error editing JSON file '{file_path}': {e}")


def calculate_Expire_Time(expiration_period):
    current_time_utc = datetime.datetime.utcnow()
    expire_time_utc = current_time_utc + datetime.timedelta(seconds=expiration_period)
    return expire_time_utc  

def isTokenExpired(ExpireTime):
    expireTime = ExpireTime
    currentTime =  datetime.datetime.utcnow()

    if ( currentTime > expireTime):
        return True #token expired
    else:
        return False
