#!/usr/bin/env python3
"""Test YouTube API key"""

import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_api_key(api_key):
    """Test if the YouTube API key is valid"""
    print("=" * 60)
    print("Testing YouTube Data API v3 Key")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}..." if len(api_key) > 20 else f"API Key: {api_key}")
    print()
    
    try:
        # Build YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Try a simple search
        print("Testing: Searching for 'python tutorial'...")
        request = youtube.search().list(
            part='snippet',
            q='python tutorial',
            type='video',
            maxResults=1
        )
        response = request.execute()
        
        print("✅ SUCCESS! API key is valid and working!")
        print()
        print("Response received:")
        if 'items' in response and len(response['items']) > 0:
            item = response['items'][0]
            print(f"  Title: {item['snippet']['title']}")
            print(f"  Channel: {item['snippet']['channelTitle']}")
            print(f"  Video ID: {item['id']['videoId']}")
        
        print()
        print("=" * 60)
        print("✅ Your YouTube API is ready to collect course data!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python collector.py 5")
        print("     (This will collect 5 courses per category)")
        print()
        print("  2. Import to database: python import_data.py data/courses_*.jsonl")
        print()
        print("  3. View in browser: http://localhost:3000/browse.html")
        print()
        
        return True
        
    except HttpError as e:
        print(f"❌ ERROR: {e}")
        print()
        
        if e.resp.status == 400:
            print("API key is invalid or malformed.")
            print("Please check that you copied the entire key correctly.")
        elif e.resp.status == 403:
            print("API key is valid but YouTube Data API v3 is not enabled.")
            print()
            print("To fix this:")
            print("  1. Go to: https://console.cloud.google.com/")
            print("  2. Select your project")
            print("  3. Go to: APIs & Services → Library")
            print("  4. Search for: YouTube Data API v3")
            print("  5. Click 'Enable'")
        elif e.resp.status == 401:
            print("Authentication error. This might be an OAuth Client ID instead of an API Key.")
            print()
            print("You need an API KEY, not OAuth Client ID!")
            print()
            print("To create an API Key:")
            print("  1. Go to: https://console.cloud.google.com/")
            print("  2. Select your project")
            print("  3. Go to: APIs & Services → Credentials")
            print("  4. Click: Create Credentials → API Key")
            print("  5. Copy the API Key (starts with 'AIza...')")
            print("  6. Update your .env file with: YOUTUBE_API_KEY=AIza...")
        else:
            print(f"Unexpected error (status {e.resp.status})")
        
        print()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    load_dotenv()
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("=" * 60)
        print("❌ ERROR: No API key found")
        print("=" * 60)
        print()
        print("Please set YOUTUBE_API_KEY in your .env file")
        print()
        print("Steps to get an API key:")
        print("  1. Go to: https://console.cloud.google.com/")
        print("  2. Create a project (or select existing)")
        print("  3. Enable YouTube Data API v3")
        print("  4. Go to: APIs & Services → Credentials")
        print("  5. Create Credentials → API Key")
        print("  6. Copy the key and add to .env:")
        print()
        print("     YOUTUBE_API_KEY=AIzaSy...your_key_here")
        print()
        sys.exit(1)
    
    test_api_key(api_key)
