# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from dotenv import load_dotenv

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

load_dotenv()

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.getenv("CLIENT_SECRET")
    API_KEY = os.getenv("API_KEY")

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube_auth = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )

    youtube_key = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY
    )

    video_ids = []
    next_page_token = None

    while True:
        request = youtube_auth.playlistItems().list(
            part="contentDetails",
            maxResults=50,
            playlistId="PLXZBc7tmmYhdP6O8PJH1yZ6wepAAKCNrD",
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
        request = youtube_key.videos().list(
            part="contentDetails",
            id=video_id
        )
        response = request.execute()

        for item in response["items"]:
            durations.append(item["contentDetails"]["duration"])

    print(durations)

if __name__ == "__main__":
    main()
