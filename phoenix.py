#!/usr/bin/env python3
"""
Phoenix AI - Intelligent E2E Testing & Automation Platform
Startup Script
"""

import os
import sys
from pathlib import Path

# ASCII Art Banner with Professional Grey & White theme
BANNER = """
\033[90m╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              🔥   \033[1;97mPHOENIX AI\033[0;90m   🔥                                ║
║                                                                       ║
║          \033[1;37mIntelligent E2E Testing & Automation Platform\033[0;90m           ║
║                                                                       ║
║           \033[1;97m✓\033[0;90m PR Testing & Code Review                             ║
║           \033[1;97m✓\033[0;90m API Integration Testing                              ║
║           \033[1;97m✓\033[0;90m E2E Browser Automation                               ║
║           \033[1;97m✓\033[0;90m AI-Powered Test Generation                           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝\033[0m
"""

def main():
    print(BANNER)
    print("\n\033[1m\033[38;5;51m🚀 Starting Phoenix AI...\033[0m\n")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("\033[38;5;226m⚠️  Warning: .env file not found!\033[0m")
        print("\033[38;5;248m   Create .env file from .env.example for full functionality\033[0m\n")
    
    # Import and run the webui
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import argparse
        from src.webui.interface import theme_map, create_ui
        
        parser = argparse.ArgumentParser(description="Phoenix AI - Intelligent Testing Platform")
        parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address to bind to")
        parser.add_argument("--port", type=int, default=7788, help="Port to listen on")
        parser.add_argument("--theme", type=str, default="Ocean", choices=theme_map.keys(), 
                          help="Theme to use for the UI")
        args = parser.parse_args()
        
        print(f"\033[90m🌐 Platform URL:\033[0m \033[1m\033[4mhttp://{args.ip}:{args.port}\033[0m")
        print(f"\033[90m🎨 Theme:\033[0m \033[1m{args.theme}\033[0m")
        print(f"\033[90m✨ Features:\033[0m \033[97mPR Testing • API Integration • E2E Automation\033[0m\n")
        print("\033[90m" + "═" * 75 + "\033[0m")
        print("\n\033[1;97m📚 Documentation:\033[0m")
        print("   \033[90m•\033[0m PR Testing:    \033[37mdocs/PR_TESTING_TOOL.md\033[0m")
        print("   \033[90m•\033[0m API Testing:   \033[37mdocs/API_TESTING.md\033[0m")
        print("   \033[90m•\033[0m Azure DevOps:  \033[37mdocs/AZURE_DEVOPS_SETUP.md\033[0m")
        print("\n\033[90m" + "═" * 75 + "\033[0m\n")
        print("\033[90m🔥\033[0m \033[1;97mPhoenix AI is ready to revolutionize your testing!\033[0m \033[90m🔥\033[0m\n")
        
        demo = create_ui(theme_name=args.theme)
        demo.queue().launch(server_name=args.ip, server_port=args.port)
        
    except ImportError as e:
        print(f"❌ Error: Missing dependencies - {e}")
        print("\n💡 Solution:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Phoenix AI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
