import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv('API_KEY')
PLAYLIST_ID = 'WL'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_durations(playlist_id):
    total_seconds = 0
    video_ids = []

    # Fetch videos in the playlist
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        # Debug: Print response
        print("Playlist Response:", playlist_response)

        # Collect video IDs
        for item in playlist_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    print("Collected Video IDs:", video_ids)

    # Fetch durations for all video IDs in batches
    for i in range(0, len(video_ids), 50):
        video_request = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids[i:i + 50])
        )
        video_response = video_request.execute()

        # Debug: Print response
        print("Video Response:", video_response)

        for item in video_response['items']:
            duration = item['contentDetails']['duration']
            total_seconds += parse_duration(duration)

    return total_seconds

def parse_duration(duration):
    import isodate  # For parsing ISO 8601 duration
    parsed_duration = isodate.parse_duration(duration)
    return int(parsed_duration.total_seconds())

# Fetch and calculate total duration
total_seconds = get_video_durations(PLAYLIST_ID)

# Convert total seconds to hours, minutes, seconds
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

print(f"Total Playlist Duration: {hours} hours, {minutes} minutes, {seconds} seconds")
