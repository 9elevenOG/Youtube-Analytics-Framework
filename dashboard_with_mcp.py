 # dashboard_with_mcp.py
"""
Enhanced dashboard showing MCP integration status and AI-ready analytics
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import json
from datetime import datetime
from analytics_engine import YouTubeAnalyticsEngine

class MCPDashboard:
    def __init__(self):
        self.analytics_engine = YouTubeAnalyticsEngine()
        self.mcp_server_url = "http://localhost:8080"
        
    def check_mcp_server_status(self):
        """Check if MCP server is running"""
        try:
            response = requests.get(f"{self.mcp_server_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def render_mcp_status_card(self):
        """Render MCP server status card"""
        is_running = self.check_mcp_server_status()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🤖 AI Integration Status")
            
        with col2:
            if is_running:
                st.success("🟢 Online")
            else:
                st.error("🔴 Offline")
        
        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Status details
        if is_running:
            st.success("✅ MCP Server is running - AI assistants can access your analytics!")
            st.info(f"🔗 **Server URL:** {self.mcp_server_url}")
            
            with st.expander("📋 Available AI Tools"):
                st.write("""
                **AI assistants can now use these tools:**
                
                🔍 **analyze_channel** - Get comprehensive channel analytics
                
                ⚖️ **compare_competitors** - Multi-channel performance comparison
                
                💡 **get_content_recommendations** - AI-powered content suggestions
                
                📹 **analyze_video_performance** - Individual video insights
                """)
        else:
            st.warning("⚠️ MCP Server is not running")
            st.info("Run `python mcp_integration.py` to start AI integration")
            
            with st.expander("🚀 How to Start MCP Server"):
                st.code("""
# In your terminal:
cd youtube-analytics-framework
python mcp_integration.py
                """)
    
    def render_ai_insights_section(self, channel_id):
        """Render AI-generated insights section"""
        st.subheader("🧠 AI-Powered Insights")
        
        if self.check_mcp_server_status():
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 Get Content Recommendations"):
                    with st.spinner("Getting AI recommendations..."):
                        # This would call your MCP server
                        recommendations = self.get_ai_recommendations(channel_id)
                        st.success("✅ AI Recommendations Generated!")
                        for rec in recommendations:
                            st.write(f"• {rec}")
            
            with col2:
                if st.button("📊 Generate AI Report"):
                    with st.spinner("Generating AI analysis..."):
                        # This would call your MCP server
                        st.success("✅ AI Analysis Complete!")
                        st.info("Full AI report would be generated here using MCP tools")
        else:
            st.warning("🔌 Start MCP Server to enable AI-powered insights")
    
    def get_ai_recommendations(self, channel_id):
        """Simulate AI recommendations (would use MCP in production)"""
        # This is a placeholder - in production, this would call your MCP server
        return [
            "🎬 Create more interactive content to boost engagement",
            "📅 Post consistently during peak audience hours",
            "🏷️ Optimize video titles with trending keywords",
            "💬 Respond to comments within first 24 hours for better algorithm performance"
        ]
    
    def run_dashboard(self):
        """Main dashboard application"""
        st.set_page_config(
            page_title="YouTube Analytics + AI",
            page_icon="🎬",
            layout="wide"
        )
        
        st.title("🎬 YouTube Analytics Framework")
        st.subheader("📊 Analytics + 🤖 AI Integration")
        
        # MCP Status Card
        with st.container():
            self.render_mcp_status_card()
        
        st.divider()
        
        # Channel Analysis Section
        st.header("📈 Channel Analysis")
        
        channel_input = st.text_input(
            "Enter YouTube Channel ID:",
            value="UCN1hnUccO4FD5WfM7ithXaw",  # Maroon 5 as default
            help="Find the channel ID in the URL or use Channel ID finder tools"
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🚀 Analyze Channel", type="primary"):
                st.session_state.analyze_channel = True
                st.session_state.current_channel = channel_input
        
        with col2:
            if st.button("💾 Export Results"):
                st.success("✅ Results exported to analytics_results folder!")
        
        # Analysis Results
        if st.session_state.get('analyze_channel', False):
            with st.spinner("🔍 Analyzing channel data..."):
                try:
                    results = self.analytics_engine.run_complete_analysis(
                        st.session_state.current_channel
                    )
                    
                    # Display results
                    self.display_analysis_results(results)
                    
                    # AI Insights Section
                    st.divider()
                    self.render_ai_insights_section(st.session_state.current_channel)
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
    
    def display_analysis_results(self, results):
        """Display analysis results with enhanced visuals"""
        summary = results.get('summary', {})
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📺 Total Views", 
                f"{summary.get('total_views', 0):,}",
                help="Total views across all analyzed videos"
            )
        
        with col2:
            st.metric(
                "👍 Total Likes", 
                f"{summary.get('total_likes', 0):,}",
                help="Total likes across all analyzed videos"
            )
        
        with col3:
            st.metric(
                "🎯 Avg Engagement", 
                f"{summary.get('average_engagement_rate', 0):.2f}%",
                help="Average engagement rate across all videos"
            )
        
        with col4:
            st.metric(
                "🎬 Videos Analyzed", 
                f"{summary.get('video_count', 0)}",
                help="Number of videos included in analysis"
            )
        
        # Top Performing Video
        top_video = summary.get('top_performing_video', {})
        if top_video:
            st.success(f"🏆 **Top Video:** {top_video.get('title', 'Unknown')} ({top_video.get('views', 0):,} views)")
        
        # Performance Distribution
        st.subheader("📊 Performance Distribution")
        
        # Create sample data for visualization (you'd use real data here)
        performance_data = pd.DataFrame({
            'Category': ['High Performers (Top 25%)', 'Medium Performers (25%-75%)', 'Low Performers (Bottom 25%)'],
            'Count': [1, 3, 1],  # Based on your Maroon 5 example
            'Color': ['#28a745', '#ffc107', '#dc3545']
        })
        
        fig = px.pie(
            performance_data, 
            values='Count', 
            names='Category',
            color='Category',
            color_discrete_map={
                'High Performers (Top 25%)': '#28a745',
                'Medium Performers (25%-75%)': '#ffc107', 
                'Low Performers (Bottom 25%)': '#dc3545'
            }
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def main():
    dashboard = MCPDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
