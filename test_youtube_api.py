#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

def test_youtube_api_simple():
    """Simple test of YouTube API connection"""
    print("🔍 Testing YouTube API setup...")
    
    # Get API key from environment
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ YouTube API key not found in .env file")
        print("   Make sure YOUTUBE_API_KEY is set in your .env file")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    try:
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        print("✅ YouTube API client initialized")
        
        # Test with a simple API call
        request = youtube.channels().list(
            part="snippet",
            forUsername="GoogleDevelopers"  # Known channel
        )
        response = request.execute()
        
        print("✅ YouTube API connection test successful!")
        print(f"   Test response received: {len(response.get('items', []))} items")
        
        return True
        
    except HttpError as e:
        print(f"❌ YouTube API HTTP error: {e}")
        if "API_KEY_INVALID" in str(e):
            print("   Check if your API key is correct")
        elif "quotaExceeded" in str(e):
            print("   API quota exceeded, try again later")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_youtube_api_simple()
    if success:
        print("\n🎉 YouTube API setup is working correctly!")
        print("You can now proceed to the next steps.")
    else:
        print("\n❌ YouTube API setup needs attention.")
        print("Please check your API key and try again.")
