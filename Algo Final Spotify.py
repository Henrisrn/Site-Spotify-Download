import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
import pytube
import time
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
CLIENT_ID = '5e445ca58b10405ba49a353f8e52e83d'
CLIENT_SECRET = "64642b9ac87e428dbf7d0a3b1bf38788"
Playlistcreator = "Unity Records"
Playlistid = "3tfKhtLN08PQcIH6nk6qk0"
#You can recup the id with the link to the playlist after /playlist/

CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)
downloadtype = 1

def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]


def call_playlist(creator, playlist_id):
    playlist_features_list = ["artist","album","track_name",  "track_id","danceability","energy","key","loudness","mode", "speechiness","instrumentalness","liveness","valence","tempo", "duration_ms","time_signature"]

    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    #step2
    #playlist = SP.playlist_tracks(playlist_id)["items"]

    playlist = SP.user_playlist_tracks(creator, playlist_id)["items"]
    for track in playlist:
        try:
            # Create empty dict
            playlist_features = {}
            # Get metadata
            print(track["track"]["album"]["artists"][0]["name"])
            print(track["track"]["name"])
            playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]
            
            # Get audio features
            audio_features = SP.audio_features(playlist_features["track_id"])[0]
            for feature in playlist_features_list[4:]:
                try:
                    playlist_features[feature] = audio_features[feature]
                except:
                    print("error")        
            # Concat the dfs
            track_df = pd.DataFrame(playlist_features, index = [0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)
        except:
            print("Error with : ",track) 

    #Step 3
        
    return playlist_df


#driver=webdriver.Chrome("C://Users//henri//Downloads//chromedriver_win32 (5)//chromedriver.exe")  
def normalise(string):
    res = ""
    for i in range(len(string)):
        if(string[i] == " " and string[i+1] != " " and string[i-1] != " "):
            res += '+'
        if(string[i] != " "):
            res += string[i]
    return res


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-playlist-info", methods=["POST"])
def submit_playlist_info():
    playlist_link = request.form["playlist_link"]
    creator_name = request.form["creator_name"]
    output = process_playlist_info(playlist_link, creator_name)
    return render_template("output.html", output="End of the process")

def process_playlist_info(playlist_link, creator_name):
    # Your code here to process the playlist information
    global dfplaylist
    Playlistcreator =creator_name
    Playlistid = str(playlist_link).split("/")[-1]
    dfplaylist = call_playlist(Playlistcreator,Playlistid)
    render_template("output.html", output="Titre de la playlist récupéré")
    uridespages = []
    titreplaylist = []
    print(dfplaylist["track_name"])
    for i in range(len(dfplaylist["track_name"])):
        titre = normalise(str(dfplaylist["track_name"][i])).replace(" ","+")+'+'+ normalise(str(dfplaylist["artist"][i])).replace(" ","+")
        #driver.get("https://www.youtube.com/results?search_query="+titre)
        try:
            #soup = BeautifulSoup(driver.page_source, 'lxml')
            #link = soup.find_all('a',class_="yt-simple-endpoint style-scope ytd-video-renderer",href=True)
            #uridespages.append(link[0]["href"])
            #print(link[0]["href"])
            # envoi de la requête et récupération des données sous forme de JSON
            response = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&q="+str(titre)+"&type=video&key=AIzaSyAuz6HCelEoLHELYGFA6HeNC9CAMB3XKmE")
            data = json.loads(response.text)
            # boucle à travers les résultats de recherche et récupération des liens vidéo
            video_link = 'https://www.youtube.com/watch?v=' + data['items'][0]['id']['videoId']
            uridespages.append(video_link)
            time.sleep(1)
        except:
            print("Probleme avec la lecture du titre : "+str(titre))
        
    print(titreplaylist)
    print(uridespages)
    # where to save 
    render_template("output.html", output="Lien récupéré")
    # link of the video to be downloaded 
    for i in uridespages:
        try:
            render_template("output.html", output="Téléchargement du titre liée à : "+str(i))
            print(i)
            yt = pytube.YouTube(str(i))
            stream = yt.streams.get_audio_only()
            #stream = yt.streams.first()
            stream.download()
        except:
            print("Problem avec : "+str(i))
        time.sleep(2)
    print("Playlist link:", playlist_link)
    print("Creator name:", creator_name)

if __name__ == "__main__":
    app.run(debug=True)
    



#driver.close()

