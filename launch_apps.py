#!/usr/bin/env python3
"""
Audio Assistant Apps Launcher
Simple launcher for the three desktop apps
"""

import subprocess
import sys
import os

def main():
    print("🎤 Audio Assistant Desktop Apps")
    print("=" * 40)
    print()
    print("Choose an app to launch:")
    print("1. 🐦 Twitter Spaces Assistant")
    print("2. 💼 LinkedIn Calls Assistant") 
    print("3. 🤝 In-Person Meeting Assistant")
    print("4. 🔧 Run Setup Script")
    print("5. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                print("🚀 Launching Twitter Spaces Assistant...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "twitter_spaces_app.py"])
                break
                
            elif choice == "2":
                print("🚀 Launching LinkedIn Calls Assistant...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "linkedin_calls_app.py"])
                break
                
            elif choice == "3":
                print("🚀 Launching In-Person Meeting Assistant...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "in_person_meeting_app.py"])
                break
                
            elif choice == "4":
                print("🔧 Running setup script...")
                subprocess.run(["./setup_mac.sh"])
                print("\nSetup complete! Choose an app to launch:")
                continue
                
            elif choice == "5":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()



