 #!/usr/bin/env python3

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sqlite3
from pathlib import Path

# Load environment variables
load_dotenv()

class SimpleDataCollector:
    """Simplified data collector for testing"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.db_path = "data/youtube_analytics.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with basic tables"""
        # Create data directory if it doesn't exist
        Path("data").mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                channel_id TEXT UNIQUE NOT NULL,
                channel_name TEXT NOT NULL,
                subscriber_count INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                video_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create video_analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_analytics (
                id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                title TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                published_at TIMESTAMP,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def get_channel_info(self, channel_id):
        """Get channel information from YouTube API"""
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                info = {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                    'view_count': int(channel['statistics'].get('viewCount', 0)),
                    'video_count': int(channel['statistics'].get('videoCount', 0)),
                }
                print(f"✅ Retrieved info for channel: {info['title']}")
                return info
            return None
        except HttpError as e:
            print(f"❌ Error getting channel info: {e}")
            return None
    
    def get_channel_videos(self, channel_id, max_results=10):
        """Get videos from a channel"""
        try:
            # Get channel uploads playlist
            channels_response = self.youtube.channels().list(
                id=channel_id,
                part='contentDetails'
            ).execute()
            
            if not channels_response['items']:
                return []
            
            playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=max_results
            ).execute()
            
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
            
            # Get detailed video statistics
            videos_response = self.youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics,contentDetails'
            ).execute()
            
            videos = []
            for video in videos_response['items']:
                videos.append({
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'views': int(video['statistics'].get('viewCount', 0)),
                    'likes': int(video['statistics'].get('likeCount', 0)),
                    'comments': int(video['statistics'].get('commentCount', 0)),
                    'published_at': video['snippet']['publishedAt']
                })
            
            print(f"✅ Retrieved {len(videos)} videos")
            return videos
            
        except HttpError as e:
            print(f"❌ Error getting videos: {e}")
            return []
    
    def store_channel_data(self, channel_info):
        """Store channel data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update channel
            cursor.execute('''
                INSERT OR REPLACE INTO channels 
                (id, channel_id, channel_name, subscriber_count, view_count, video_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                channel_info['channel_id'],
                channel_info['channel_id'],
                channel_info['title'],
                channel_info['subscriber_count'],
                channel_info['view_count'],
                channel_info['video_count'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Stored channel data: {channel_info['title']}")
            
        except Exception as e:
            print(f"❌ Error storing channel data: {e}")
    
    def store_video_data(self, video, channel_id):
        """Store video data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate engagement rate
            views = video['views']
            likes = video['likes']
            comments = video['comments']
            engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO video_analytics 
                (id, video_id, channel_id, title, views, likes, comments_count, engagement_rate, published_at, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video['video_id'],
                video['video_id'],
                channel_id,
                video['title'],
                views,
                likes,
                comments,
                engagement_rate,
                video['published_at'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Stored video: {video['title'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error storing video data: {e}")
    
    def collect_channel_data(self, channel_id):
        """Collect all data for a channel"""
        print(f"🔍 Starting data collection for channel: {channel_id}")
        
        # Get channel info
        channel_info = self.get_channel_info(channel_id)
        if not channel_info:
            return False
        
        # Store channel info
        self.store_channel_data(channel_info)
        
        # Get videos
        videos = self.get_channel_videos(channel_id, max_results=5)  # Limit for testing
        
        # Store videos
        for video in videos:
            self.store_video_data(video, channel_id)
            time.sleep(0.1)  # Rate limiting
        
        print(f"✅ Completed data collection for {channel_info['title']}")
        print(f"📊 Collected {len(videos)} videos")
        return True
    
    def show_database_stats(self):
        """Show database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count channels
            cursor.execute("SELECT COUNT(*) FROM channels")
            channel_count = cursor.fetchone()[0]
            
            # Count videos
            cursor.execute("SELECT COUNT(*) FROM video_analytics")
            video_count = cursor.fetchone()[0]
            
            # Get latest data
            cursor.execute("SELECT channel_name, subscriber_count FROM channels ORDER BY updated_at DESC LIMIT 5")
            latest_channels = cursor.fetchall()
            
            conn.close()
            
            print("\n📊 Database Statistics:")
            print(f"   📺 Total channels: {channel_count}")
            print(f"   🎬 Total videos: {video_count}")
            print("\n📈 Latest channels:")
            for name, subs in latest_channels:
                print(f"   • {name}: {subs:,} subscribers")
                
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")

def test_data_collection():
    """Test the data collection system"""
    print("🧪 Testing Simple Data Collection System...")
    print("=" * 50)
    
    try:
        # Initialize collector
        collector = SimpleDataCollector()
        
        # Test with Google Developers channel (known to work)
        test_channel_id = "UCBVjMGOIkavEAhyqpxJ73Dw"
        
        # Collect data
        success = collector.collect_channel_data(test_channel_id)
        
        if success:
            print("\n🎉 Data collection test successful!")
            collector.show_database_stats()
        else:
            print("\n❌ Data collection test failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_data_collection()
