import requests
import json
import os
from pathlib import Path

def deploy_to_streamlit():
    """Deploy the app to Streamlit Cloud using their API"""
    
    # Streamlit Cloud API endpoint
    url = "https://share.streamlit.io/api/v1/apps"
    
    # App configuration
    app_config = {
        "repository": "joeyhendrickson/TwitterSpaceAssistant",
        "branch": "main",
        "mainModule": "dashboard.py",
        "appId": "ai-conversation-assistant",
        "appName": "AI Conversation Assistant Hub",
        "environmentVariables": {
            "OPENAI_API_KEY": "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",
            "PINECONE_API_KEY": "pcsk_5vv1EY_EZhAHDyXU7ZY7QrRsAuBANV32bGPD5LNHmhuvwTMKs3GYNQEw6Vgo1UnCHUGm1o",
            "PINECONE_ENV": "us-east-1"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_STREAMLIT_TOKEN"  # This would need to be set
    }
    
    try:
        response = requests.post(url, json=app_config, headers=headers)
        if response.status_code == 200:
            print("✅ App deployed successfully!")
            print(f"URL: https://ai-conversation-assistant.streamlit.app")
        else:
            print(f"❌ Deployment failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Deploying to Streamlit Cloud...")
    deploy_to_streamlit()

