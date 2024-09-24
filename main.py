import os
import time
from steam_web_api import Steam
from dotenv import load_dotenv
from datetime import datetime

try:
    load_dotenv()
    KEY = os.getenv("STEAM_API_KEY")
    steam = Steam(KEY)
    steam_id = os.getenv("STEAM_ACCOUNT_ID")
    file_path = "game_stats.txt"
    if not KEY or not steam_id:
        raise ValueError("Missing Steam API Key or Steam ID.")
except Exception as e:
    print(e, "Key and Steam ID not found.")
    raise SystemExit("Critical Error: Could not load API Key or Steam ID.")
#Initial API call data. 
try:
    initial_api_call = steam.users.get_user_recently_played_games(steam_id)

    initial_playtime = {}
    for game in initial_api_call['games']:
        initial_playtime[game['name']] =  game['playtime_forever']

    start_date_time = datetime.now().strftime("%A, %d-%m-%Y, %H:%M:%S")
    print(initial_playtime)
except:
    raise SystemExit("Critical Error: Initial API call failed.")

#Storing the time the initial api call was made to compare it to the update times.
start_time = datetime.now()

#Variable to store total time played.
total_playtime = 0

def api_calls():
    global initial_playtime, start_time, total_playtime, start_date_time

    #Get updated info from the API call.
    #Current data updates every 30 mins or when you quit the game.
    while True:
        current_data = steam.users.get_user_recently_played_games(steam_id)
        current_playtime  = {}
        older_than_2weeks_playtime= {}
        for game in current_data['games']:
            current_playtime[game['name']] =  game['playtime_forever']
            older_than_2weeks_playtime[game['name']] =  game['playtime_2weeks']
        with open(file_path, 'a') as file_object:
            for name in current_playtime:
                if name in initial_playtime:
                    previous_playtime = initial_playtime[name]
                    recent_playtime = current_playtime[name]
                    if recent_playtime > previous_playtime:
                        playtime_approx = recent_playtime - previous_playtime
                        total_playtime += playtime_approx

                        #Timestamps between each increase in playtime.
                        update_time = datetime.now()
                        time_diff = update_time - start_time
                        print(f"time_diff: {time_diff.total_seconds()} seconds\n")

                        #if diferenta end_date_time de la ultimul update este mai mica de 30' atunci scrii in fisier
                        if (time_diff.total_seconds() < 1800):
                            end_date_time = update_time.strftime("%A, %d-%m-%Y, %H:%M:%S")
                            file_object.write(f"Game: {name}, Playtime today: {total_playtime} minutes\n")
                            file_object.write(f"Start time: {start_date_time}\n")
                            file_object.write(f"End time: {end_date_time}\n")
                            file_object.write(f"Not playing {name} anymore.\n")

                            #After quitting a game, reset the start time.
                            start_date_time = end_date_time

                        else:
                            start_time = update_time

                        initial_playtime[name] = recent_playtime
                else:
                    playtime_approx = older_than_2weeks_playtime[name]
                    if playtime_approx > 0 :
                        file_object.write(f"Game: {name}, Playtime today: {playtime_approx} minutes\n")
                        file_object.write(f"Start time: {start_date_time}\n")
                        file_object.write(f"End time: {end_date_time}\n")
                        file_object.write("Playtime has been recorded for a new game\n")
                        initial_playtime[name] = playtime_approx
        time.sleep(60)

api_calls()