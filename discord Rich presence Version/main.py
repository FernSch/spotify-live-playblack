from types import NoneType
import requests
import time
from pypresence import Presence
from pprint import pprint


SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'

#access token intents must include "user-read-playback-position" in addition to default intent in order to include "progress_ms"

ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
client_id = "YOUR-DISCORD-APP-CLIENT-ID"

RPC = Presence(client_id)  # Initialize the Presence class
RPC.connect()  # Start the handshake loop

wait_time = 0
#i suggest at least 1 second wait time as it seems updating it too much will cause rate limit

def get_current_track(access_token):
    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    json_resp = response.json()

    #track_id = json_resp['item']['id']
    track_name = json_resp['item']['name']
    artists = [artist for artist in json_resp['item']['artists']]

    link = json_resp['item']['external_urls']['spotify']

    artist_names = ', '.join([artist['name'] for artist in artists])

    #converting duration of song and user progress into minutes and seconds

    progress = json_resp['progress_ms']
    progress = progress / 1000
    progress_minutes = 0

    while progress > 60:
        progress_minutes += 1
        progress -= 60

    duration = json_resp['item']['duration_ms']
    duration = duration / 1000
    duration_minutes = 0

    while duration > 60:
        duration_minutes += 1
        duration -= 60


    image = json_resp['item']['album']['images'][0]['url']

    current_track_info = {
    	#"id": track_id,
    	"track_name": track_name,
    	"artists": artist_names,
    	"link": link,
        "album+image": image,
        #[minutes, seconds]
        "progress": {"minutes": progress_minutes, "seconds": int(progress)},
        "duration": {"minutes": duration_minutes, "seconds": int(duration)}
    }

    return current_track_info

old_info = None
old_song = None
while True:
    try:
        if old_song != get_current_track(ACCESS_TOKEN)['track_name']:
            old_song = get_current_track(ACCESS_TOKEN)['track_name']
            #RPC.update(details=f"Now playing {get_current_track(ACCESS_TOKEN)['track_name']} by {get_current_track(ACCESS_TOKEN)['artists']}", state=f"{track_info['progress']['minutes']}:{track_info['progress']['seconds']:02} - {track_info['duration']['minutes']}:{track_info['duration']['seconds']:02} \r")
            #print(f"Now playing {get_current_track(ACCESS_TOKEN)['track_name']} by {get_current_track(ACCESS_TOKEN)['artists']}")
        if old_info != get_current_track(ACCESS_TOKEN):
            old_info = get_current_track(ACCESS_TOKEN)
            track_info = get_current_track(ACCESS_TOKEN)
            #print(f"{track_info['progress']['minutes']}:{track_info['progress']['seconds']:02} / {track_info['duration']['minutes']}:{track_info['duration']['seconds']:02} \r")
        #time.sleep(1)
            RPC.update(details=f"Now playing {get_current_track(ACCESS_TOKEN)['track_name']} by {get_current_track(ACCESS_TOKEN)['artists']}", state=f"{track_info['progress']['minutes']}:{track_info['progress']['seconds']:02} - {track_info['duration']['minutes']}:{track_info['duration']['seconds']:02} \r")
            #print("updated")
            #RPC.update(buttons=[{"label": "Listen", "url": link}])
        time.sleep(wait_time)
    except get_current_track(ACCESS_TOKEN) == Nonetype:
        RPC.update(details="No song playing", state="⛔🎧")
        #print("Now playing ad")
       # time.sleep(1)
    #will show "No song playing" if no song is playing or if ad is playing
        time.sleep(wait_time)
