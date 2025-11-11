# mcp_integration.py
"""
Simplified MCP Integration for YouTube Analytics
This creates a bridge between your analytics engine and AI assistants
"""

import sys
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.mcp_server.server import YouTubeAnalyticsMCPServer
    from analytics_engine import YouTubeAnalyticsEngine
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are in place:")
    print("  - src/mcp_server/server.py")
    print("  - src/mcp_server/__init__.py") 
    print("  - analytics_engine.py")
    sys.exit(1)

class SimpleMCPIntegration:
    def __init__(self):
        print("🔧 Initializing MCP Integration...")
        try:
            self.analytics_engine = YouTubeAnalyticsEngine()
            self.mcp_server = YouTubeAnalyticsMCPServer(self.analytics_engine)
            print("✅ MCP Integration initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing MCP integration: {e}")
            raise
    
    def test_mcp_tools(self):
        """Test the MCP tools integration"""
        print("\n🧪 Testing MCP Tools Integration...")
        
        # Test with Maroon 5 channel (from your previous successful test)
        channel_id = "UCN1hnUccO4FD5WfM7ithXaw"  # Maroon 5
        
        print(f"📈 Testing analytics integration for channel: {channel_id}")
        
        try:
            # Test 1: Check available tools
            tools = self.mcp_server.get_available_tools()
            print(f"✅ Found {len(tools)} available MCP tools:")
            for tool in tools:
                print(f"   • {tool['name']} - {tool['description']}")
            
            # Test 2: Test channel analysis tool
            print("\n🔍 Testing channel analysis tool...")
            analysis_result = self.mcp_server.call_tool("analyze_channel", {
                "channel_id": channel_id,
                "max_videos": 5
            })
            
            if analysis_result.get("status") == "success":
                print("✅ Channel analysis tool working correctly")
                summary = analysis_result.get("summary", {})
                print(f"   📊 Found {summary.get('video_count', 0)} videos analyzed")
                print(f"   👁️ Total views: {summary.get('total_views', 0):,}")
                print(f"   🎯 Avg engagement: {summary.get('average_engagement_rate', 0):.2f}%")
            else:
                print(f"❌ Channel analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return False
            
            # Test 3: Test recommendations tool
            print("\n💡 Testing content recommendations tool...")
            recommendations_result = self.mcp_server.call_tool("get_content_recommendations", {
                "channel_id": channel_id,
                "focus_area": "engagement"
            })
            
            if recommendations_result.get("status") == "success":
                print("✅ Content recommendations tool working correctly")
                recs = recommendations_result.get("recommendations", [])
                print(f"   📝 Generated {len(recs)} recommendations")
                for i, rec in enumerate(recs[:3], 1):
                    print(f"   {i}. {rec}")
            else:
                print(f"❌ Recommendations failed: {recommendations_result.get('error', 'Unknown error')}")
            
            print("\n🎯 MCP Integration Test Complete!")
            print("✅ Your analytics engine is now AI-ready!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in MCP integration test: {e}")
            return False
    
    def demonstrate_ai_integration(self):
        """Demonstrate how AI assistants can use your analytics"""
        print("\n🤖 AI Integration Demonstration")
        print("=" * 50)
        
        # Show server info
        server_info = self.mcp_server.get_server_info()
        print(f"🖥️ Server: {server_info['name']} v{server_info['version']}")
        print(f"📊 Available Tools: {server_info['available_tools']}")
        
        print("\n🔌 AI assistants can now:")
        print("   • Analyze any YouTube channel instantly")
        print("   • Get AI-powered content recommendations") 
        print("   • Access real-time performance insights")
        print("   • Generate custom reports and analysis")
        
        print("\n📋 Example AI Assistant Commands:")
        print('   "Analyze the performance of channel UCN1hnUccO4FD5WfM7ithXaw"')
        print('   "Give me content recommendations to improve engagement"')
        print('   "What are the top performing video patterns for this channel?"')
        
        return True

def main():
    print("=" * 60)
    print("🎬 YOUTUBE ANALYTICS MCP INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Initialize integration
        integration = SimpleMCPIntegration()
        
        # Run tests
        if integration.test_mcp_tools():
            integration.demonstrate_ai_integration()
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! MCP Integration is working!")
            print("=" * 60)
            print("\n📝 Next Steps:")
            print("   1. Your analytics engine is now AI-ready")
            print("   2. AI assistants can access your YouTube data")
            print("   3. Ready for Claude integration!")
            
        else:
            print("\n❌ MCP Integration test failed. Please check the errors above.")
            
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Make sure analytics_engine.py is working")
        print("   • Check that all files are in the right directories")
        print("   • Verify your virtual environment is activated")

if __name__ == "__main__":
    main()