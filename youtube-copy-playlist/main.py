import csv
import os
import pickle
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/youtube"]

PLAYLIST_ID_FILE = "synced_playlist_id.txt"

def get_authenticated_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def create_playlist(youtube, title, description=""):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "unlisted"}
        }
    )
    response = request.execute()
    playlist_id = response["id"]
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"✅ Created playlist: {playlist_url}")
    time.sleep(2)
    return playlist_id

def get_or_create_synced_playlist(youtube):
    if os.path.exists(PLAYLIST_ID_FILE):
        with open(PLAYLIST_ID_FILE, "r") as f:
            playlist_id = f.read().strip()
        print(f"🔗 Using existing synced playlist: https://www.youtube.com/playlist?list={playlist_id}")
        return playlist_id
    else:
        playlist_id = create_playlist(youtube, "Synced Watch Later", "Semi-automatic sync from Takeout CSV")
        with open(PLAYLIST_ID_FILE, "w") as f:
            f.write(playlist_id)
        return playlist_id

def get_videos_in_playlist(youtube, playlist_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            vid = item["snippet"]["resourceId"]["videoId"]
            video_ids.append(vid)
        request = youtube.playlistItems().list_next(request, response)
    return video_ids

def add_videos_to_playlist(youtube, playlist_id, video_ids):
    for video_id in video_ids:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()
            print(f"➕ Added video: {video_id}")
        except Exception as e:
            print(f"❌ Failed to add {video_id}: {e}")

def parse_takeout_csv(filepath):
    video_ids = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Video ID column usually exists
            vid = row.get("Video ID")
            if vid:
                video_ids.append(vid.strip())
    return video_ids

if __name__ == "__main__":
    youtube = get_authenticated_service()

    # Path to your latest Takeout CSV
    takeout_file = "Watch later-videos.csv"
    exported_video_ids = parse_takeout_csv(takeout_file)
    print(f"📂 Found {len(exported_video_ids)} videos in Takeout export.")

    # 🔹 Get (or create) the synced playlist
    target_playlist_id = get_or_create_synced_playlist(youtube)

    # Get what’s already in the target playlist
    existing_videos = set(get_videos_in_playlist(youtube, target_playlist_id))
    print(f"🎞️ Playlist currently has {len(existing_videos)} videos.")

    # Find new videos not already in the playlist
    new_videos = [vid for vid in exported_video_ids if vid not in existing_videos]

    if new_videos:
        print(f"🔄 Adding {len(new_videos)} new videos...")
        add_videos_to_playlist(youtube, target_playlist_id, new_videos)
    else:
        print("✅ No new videos to add. Already up to date!")
