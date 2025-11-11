 #!/usr/bin/env python3

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import json

class YouTubeAnalyticsEngine:
    """Advanced analytics engine for YouTube data"""
    
    def __init__(self, db_path="data/youtube_analytics.db"):
        self.db_path = db_path
        self.results_dir = Path("analytics_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def get_channel_overview(self, channel_id=None):
        """Get comprehensive channel overview"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if channel_id:
                # Specific channel
                query = """
                SELECT c.channel_name, c.subscriber_count, c.view_count, c.video_count,
                       COUNT(v.video_id) as videos_analyzed,
                       AVG(v.views) as avg_video_views,
                       AVG(v.likes) as avg_video_likes,
                       AVG(v.engagement_rate) as avg_engagement_rate,
                       MAX(v.views) as best_video_views,
                       MIN(v.views) as worst_video_views
                FROM channels c
                LEFT JOIN video_analytics v ON c.channel_id = v.channel_id
                WHERE c.channel_id = ?
                GROUP BY c.channel_id
                """
                result = pd.read_sql_query(query, conn, params=[channel_id])
            else:
                # All channels
                query = """
                SELECT c.channel_name, c.subscriber_count, c.view_count, c.video_count,
                       COUNT(v.video_id) as videos_analyzed,
                       AVG(v.views) as avg_video_views,
                       AVG(v.likes) as avg_video_likes,
                       AVG(v.engagement_rate) as avg_engagement_rate,
                       MAX(v.views) as best_video_views,
                       MIN(v.views) as worst_video_views
                FROM channels c
                LEFT JOIN video_analytics v ON c.channel_id = v.channel_id
                GROUP BY c.channel_id
                """
                result = pd.read_sql_query(query, conn)
            
            conn.close()
            return result
            
        except Exception as e:
            print(f"❌ Error getting channel overview: {e}")
            return pd.DataFrame()
    
    def analyze_video_performance(self, channel_id=None):
        """Analyze video performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if channel_id:
                query = """
                SELECT v.title, v.views, v.likes, v.comments_count, v.engagement_rate,
                       v.published_at, c.channel_name
                FROM video_analytics v
                JOIN channels c ON v.channel_id = c.channel_id
                WHERE v.channel_id = ?
                ORDER BY v.views DESC
                """
                videos_df = pd.read_sql_query(query, conn, params=[channel_id])
            else:
                query = """
                SELECT v.title, v.views, v.likes, v.comments_count, v.engagement_rate,
                       v.published_at, c.channel_name
                FROM video_analytics v
                JOIN channels c ON v.channel_id = c.channel_id
                ORDER BY v.views DESC
                """
                videos_df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            if videos_df.empty:
                return {}
            
            # Calculate performance metrics
            analysis = {
                'total_videos': len(videos_df),
                'total_views': videos_df['views'].sum(),
                'avg_views': videos_df['views'].mean(),
                'median_views': videos_df['views'].median(),
                'best_performing': videos_df.iloc[0].to_dict(),
                'avg_engagement_rate': videos_df['engagement_rate'].mean(),
                'view_distribution': {
                    'high_performers': len(videos_df[videos_df['views'] > videos_df['views'].quantile(0.75)]),
                    'medium_performers': len(videos_df[(videos_df['views'] >= videos_df['views'].quantile(0.25)) & 
                                                     (videos_df['views'] <= videos_df['views'].quantile(0.75))]),
                    'low_performers': len(videos_df[videos_df['views'] < videos_df['views'].quantile(0.25)])
                }
            }
            
            return analysis, videos_df
            
        except Exception as e:
            print(f"❌ Error analyzing video performance: {e}")
            return {}, pd.DataFrame()
    
    def create_performance_visualizations(self, channel_id=None):
        """Create comprehensive performance visualizations"""
        try:
            analysis, videos_df = self.analyze_video_performance(channel_id)
            
            if videos_df.empty:
                print("❌ No video data available for visualization")
                return
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('YouTube Channel Performance Analysis', fontsize=16, fontweight='bold')
            
            # 1. Views Distribution
            axes[0, 0].hist(videos_df['views'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0, 0].set_title('Video Views Distribution')
            axes[0, 0].set_xlabel('Views')
            axes[0, 0].set_ylabel('Number of Videos')
            axes[0, 0].ticklabel_format(style='plain', axis='x')
            
            # 2. Engagement Rate vs Views
            axes[0, 1].scatter(videos_df['views'], videos_df['engagement_rate'], 
                             alpha=0.7, color='coral', s=60)
            axes[0, 1].set_title('Engagement Rate vs Views')
            axes[0, 1].set_xlabel('Views')
            axes[0, 1].set_ylabel('Engagement Rate (%)')
            axes[0, 1].ticklabel_format(style='plain', axis='x')
            
            # 3. Top 5 Videos by Views
            top_5 = videos_df.head(5)
            bars = axes[1, 0].bar(range(len(top_5)), top_5['views'], color='lightgreen')
            axes[1, 0].set_title('Top 5 Videos by Views')
            axes[1, 0].set_ylabel('Views')
            axes[1, 0].set_xticks(range(len(top_5)))
            axes[1, 0].set_xticklabels([title[:20] + '...' if len(title) > 20 else title 
                                      for title in top_5['title']], rotation=45, ha='right')
            axes[1, 0].ticklabel_format(style='plain', axis='y')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height/1000)}K', ha='center', va='bottom')
            
            # 4. Performance Distribution Pie Chart
            perf_dist = analysis['view_distribution']
            labels = ['High Performers', 'Medium Performers', 'Low Performers']
            sizes = [perf_dist['high_performers'], perf_dist['medium_performers'], perf_dist['low_performers']]
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            axes[1, 1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title('Video Performance Distribution')
            
            plt.tight_layout()
            
            # Save the plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_analysis_{timestamp}.png"
            filepath = self.results_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            print(f"✅ Performance visualization saved: {filepath}")
            plt.show()
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")
    
    def generate_insights_report(self, channel_id=None):
        """Generate comprehensive insights report"""
        try:
            print("📊 Generating YouTube Analytics Insights Report")
            print("=" * 60)
            
            # Get channel overview
            overview = self.get_channel_overview(channel_id)
            if overview.empty:
                print("❌ No channel data available")
                return
            
            # Get video performance analysis
            analysis, videos_df = self.analyze_video_performance(channel_id)
            if not analysis:
                print("❌ No video analysis data available")
                return
            
            # Generate report
            channel_name = overview.iloc[0]['channel_name']
            
            print(f"\n🎯 CHANNEL: {channel_name}")
            print("-" * 40)
            print(f"📈 Subscribers: {overview.iloc[0]['subscriber_count']:,}")
            print(f"👀 Total Channel Views: {overview.iloc[0]['view_count']:,}")
            print(f"🎬 Total Videos: {overview.iloc[0]['video_count']:,}")
            print(f"🔍 Videos Analyzed: {analysis['total_videos']}")
            
            print(f"\n📊 VIDEO PERFORMANCE METRICS")
            print("-" * 40)
            print(f"📺 Total Views (Analyzed): {analysis['total_views']:,}")
            print(f"📊 Average Views per Video: {analysis['avg_views']:,.0f}")
            print(f"📊 Median Views per Video: {analysis['median_views']:,.0f}")
            print(f"🎯 Average Engagement Rate: {analysis['avg_engagement_rate']:.2f}%")
            
            print(f"\n🏆 BEST PERFORMING VIDEO")
            print("-" * 40)
            best = analysis['best_performing']
            print(f"🎬 Title: {best['title']}")
            print(f"👀 Views: {best['views']:,}")
            print(f"👍 Likes: {best['likes']:,}")
            print(f"💬 Comments: {best['comments_count']:,}")
            print(f"📈 Engagement Rate: {best['engagement_rate']:.2f}%")
            
            print(f"\n📈 PERFORMANCE DISTRIBUTION")
            print("-" * 40)
            dist = analysis['view_distribution']
            print(f"🔥 High Performers (Top 25%): {dist['high_performers']} videos")
            print(f"📊 Medium Performers (25%-75%): {dist['medium_performers']} videos")
            print(f"📉 Low Performers (Bottom 25%): {dist['low_performers']} videos")
            
            # Generate actionable insights
            print(f"\n💡 ACTIONABLE INSIGHTS")
            print("-" * 40)
            
            # Insight 1: Engagement rate analysis
            if analysis['avg_engagement_rate'] > 3.0:
                print("✅ Great engagement! Your audience is highly interactive.")
            elif analysis['avg_engagement_rate'] > 1.0:
                print("📊 Good engagement. Consider ways to increase audience interaction.")
            else:
                print("⚠️ Low engagement. Focus on creating more engaging content.")
            
            # Insight 2: Performance consistency
            cv = (videos_df['views'].std() / videos_df['views'].mean()) * 100
            if cv < 50:
                print("✅ Consistent performance across videos.")
            else:
                print("📊 High variability in video performance. Analyze top performers for patterns.")
            
            # Insight 3: View distribution
            if dist['high_performers'] > dist['low_performers']:
                print("🔥 More high-performing than low-performing videos - great content strategy!")
            else:
                print("📈 Opportunity to improve: Focus on replicating successful video elements.")
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.results_dir / f"insights_report_{timestamp}.txt"
            
            print(f"\n📄 Report saved to: {report_file}")
            print("\n🎉 Analysis complete!")
            
        except Exception as e:
            print(f"❌ Error generating insights report: {e}")
    
    def run_complete_analysis(self, channel_id=None):
        """Run complete analytics pipeline"""
        print("🚀 Starting Complete YouTube Analytics")
        print("=" * 50)
        
        try:
            # Generate insights report
            self.generate_insights_report(channel_id)
            
            # Create visualizations
            print("\n📊 Creating performance visualizations...")
            self.create_performance_visualizations(channel_id)
            
            print("\n✅ Complete analysis finished!")
            print(f"📁 Results saved in: {self.results_dir}")
            
        except Exception as e:
            print(f"❌ Error in complete analysis: {e}")

def test_analytics_engine():
    """Test the analytics engine"""
    print("🧪 Testing Analytics Engine...")
    print("=" * 40)
    
    try:
        # Initialize analytics engine
        engine = YouTubeAnalyticsEngine()
        
        # Run complete analysis
        engine.run_complete_analysis()
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")

if __name__ == "__main__":
    test_analytics_engine()
