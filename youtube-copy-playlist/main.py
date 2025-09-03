import csv
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/youtube"]

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
    return playlist_id

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
            print(f"Added video: {video_id}")
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

    # 🔹 Replace with your CSV file path
    takeout_file = "Watch later-videos.csv"
    video_ids = parse_takeout_csv(takeout_file)
    print(f"Found {len(video_ids)} videos in Watch Later export.")

    if video_ids:
        new_playlist_id = create_playlist(youtube, "Copied from Watch Later", "Imported via Google Takeout CSV")
        add_videos_to_playlist(youtube, new_playlist_id, video_ids)
        print("✅ All videos copied successfully!")

