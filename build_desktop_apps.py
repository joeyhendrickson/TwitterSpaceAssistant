#!/usr/bin/env python3
"""
Build Standalone Desktop Apps for Mac
Creates .app files that can be downloaded and run independently
"""

import os
import subprocess
import sys
import shutil

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")

def build_app(app_name, main_file, icon=None):
    """Build a standalone .app file"""
    print(f"\n🔨 Building {app_name}...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", app_name,
        "--add-data", f"{main_file}:.",
        "--hidden-import", "streamlit",
        "--hidden-import", "sounddevice",
        "--hidden-import", "whisper",
        "--hidden-import", "openai",
        "--hidden-import", "pinecone",
        "--hidden-import", "keyring",
        "--hidden-import", "PyPDF2",
        "--hidden-import", "numpy",
        "--hidden-import", "librosa",
        "--collect-all", "streamlit",
        "--collect-all", "whisper",
        "--collect-all", "sounddevice"
    ]
    
    if icon:
        cmd.extend(["--icon", icon])
    
    # Add the main file
    cmd.append(main_file)
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {app_name} built successfully!")
            
            # Move the .app file to the current directory
            app_path = f"dist/{app_name}.app"
            if os.path.exists(app_path):
                shutil.move(app_path, f"./{app_name}.app")
                print(f"📱 {app_name}.app created in current directory")
            else:
                print(f"⚠️  {app_name}.app not found in dist folder")
        else:
            print(f"❌ Error building {app_name}:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Exception building {app_name}: {e}")

def create_installer_script(app_name):
    """Create an installer script for the app"""
    installer_content = f"""#!/bin/bash

echo "🎤 Installing {app_name}..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    read -p "Press Enter to continue..."
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install streamlit openai pinecone-client keyring PyPDF2 numpy

# Create desktop shortcut
echo "🖥️  Creating desktop shortcut..."
cp "{app_name}.app" ~/Desktop/

echo "✅ {app_name} installed successfully!"
echo "🚀 You can now double-click {app_name}.app on your Desktop"
echo ""
echo "📋 First time setup:"
echo "   1. Double-click {app_name}.app"
echo "   2. Enter your API keys when prompted"
echo "   3. Keys are stored securely on your Mac"
echo ""
read -p "Press Enter to continue..."
"""
    
    with open(f"install_{app_name}.sh", "w") as f:
        f.write(installer_content)
    
    # Make installer executable
    os.chmod(f"install_{app_name}.sh", 0o755)
    print(f"📋 Created installer script: install_{app_name}.sh")

def main():
    """Main build function"""
    print("🔨 Building Standalone Desktop Apps")
    print("===================================")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build each app
    apps = [
        ("Twitter_Spaces_Assistant", "twitter_spaces_app.py"),
        ("LinkedIn_Calls_Assistant", "linkedin_calls_app.py"),
        ("In_Person_Meeting_Assistant", "in_person_meeting_app.py")
    ]
    
    for app_name, main_file in apps:
        if os.path.exists(main_file):
            build_app(app_name, main_file)
            create_installer_script(app_name)
        else:
            print(f"❌ {main_file} not found, skipping {app_name}")
    
    print("\n🎉 Build complete!")
    print("\n📱 Your standalone apps:")
    for app_name, _ in apps:
        if os.path.exists(f"{app_name}.app"):
            print(f"   ✅ {app_name}.app")
        else:
            print(f"   ❌ {app_name}.app (build failed)")
    
    print("\n📋 Next steps:")
    print("1. Copy the .app files to your Desktop")
    print("2. Double-click to run")
    print("3. Enter your API keys on first run")
    print("4. Apps will work independently")

if __name__ == "__main__":
    main()



