import os
from dotenv import load_dotenv
import isodate
import googleapiclient.discovery

load_dotenv()

API_KEY = os.getenv("API_KEY")

def main():
    api_service_name = "youtube"
    api_version = "v3"

    # Get API key 
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY
    )
    
    playlist_id = "PLXZBc7tmmYhdP6O8PJH1yZ6wepAAKCNrD"
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"Total video IDs fetched: {len(video_ids)}")
    
    durations = []

    for video_id in video_ids:
        request = youtube.videos().list(
            part="contentDetails",
            id=video_id
        )
        response = request.execute()

        for item in response["items"]:
            durations.append(item["contentDetails"]["duration"])

    total_seconds = sum(isodate.parse_duration(d).total_seconds() for d in durations)

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    print(f"Total time needed to finish the playlist: {hours:02}:{minutes:02}:{seconds:02}")

if __name__ == "__main__":
    main()
