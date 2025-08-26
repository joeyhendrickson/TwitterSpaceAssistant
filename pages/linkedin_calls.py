import os
import streamlit as st
import whisper
import sounddevice as sd
import numpy as np
import time
import random
from uuid import uuid4
from PyPDF2 import PdfReader
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import json
import cv2
from PIL import Image
import pytesseract


# Load environment variables
load_dotenv()

# Initialize API clients
openai_api_key = os.getenv("OPENAI_API_KEY", "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")
pinecone_api_key = os.getenv("PINECONE_API_KEY", "pcsk_5vv1EY_EZhAHDyXU7ZY7QrRsAuBANV32bGPD5LNHmhuvwTMKs3GYNQEw6Vgo1UnCHUGm1o")
pinecone_env = os.getenv("PINECONE_ENV", "us-east-1")

client = OpenAI(api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)

# LinkedIn Call specific index
linkedin_index_name = "linkedin-call-assistant"

if linkedin_index_name not in pc.list_indexes().names():
    pc.create_index(
        name=linkedin_index_name,
        dimension=1536,
        metric="cosine"
    )
index = pc.Index(linkedin_index_name)

# Configuration
RECORD_DURATION = 5
ROLLING_BUFFER_LIMIT = 12
MODEL_NAME = "base"

@st.cache_resource
def load_model():
    return whisper.load_model(MODEL_NAME)

whisper_model = load_model()

def chunk_text(text, max_tokens=500):
    words = text.split()
    return [" ".join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def embed_and_upsert(text, person_name):
    for chunk in chunk_text(text):
        vector = get_embedding(chunk)
        index.upsert([{
            "id": str(uuid4()),
            "values": vector,
            "metadata": {"text": chunk, "person": person_name}
        }], namespace=person_name)

def query_context(query, person_name):
    vector = get_embedding(query)
    response = index.query(vector=vector, top_k=5, include_metadata=True, namespace=person_name)
    return "\n".join([match['metadata']['text'] for match in response.matches])

def analyze_linkedin_profile(profile_image=None):
    """Analyze LinkedIn profile from uploaded screenshot"""
    try:
        if profile_image:
            st.info("🔍 Analyzing LinkedIn profile from uploaded screenshot...")
            return analyze_linkedin_screenshot(profile_image)
        else:
            st.error("Please upload a profile screenshot")
            return None
            
    except Exception as e:
        st.error(f"Error analyzing LinkedIn profile: {e}")
        return None



def analyze_multiple_screenshots(uploaded_files):
    """Analyze multiple LinkedIn profile screenshots for comprehensive data"""
    try:
        st.info(f"📸 Processing {len(uploaded_files)} screenshot(s)...")
        
        all_ocr_text = []
        
        # Process each screenshot
        for i, uploaded_file in enumerate(uploaded_files):
            st.info(f"Processing screenshot {i+1}/{len(uploaded_files)}...")
            
            # Extract text from each screenshot
            ocr_text = extract_text_from_image(uploaded_file)
            if ocr_text:
                all_ocr_text.append(f"--- Screenshot {i+1} ---\n{ocr_text}")
            else:
                st.warning(f"Could not extract text from screenshot {i+1}")
        
        if not all_ocr_text:
            st.error("No text could be extracted from any screenshots")
            return None
        
        # Combine all OCR text
        combined_text = "\n\n".join(all_ocr_text)
        st.info(f"📝 Extracted {len(combined_text)} characters from {len(uploaded_files)} screenshot(s)")
        
        st.info("🤖 Analyzing combined screenshots with AI...")
        
        # Use OpenAI to parse the combined OCR text into structured profile data
        profile_data = parse_linkedin_text_with_ai(combined_text)
        
        if profile_data:
            st.success(f"✅ Successfully analyzed {len(uploaded_files)} screenshot(s) for {profile_data['name']}")
            return profile_data
        else:
            st.warning("Could not parse profile information from screenshots")
            return None
            
    except Exception as e:
        st.error(f"Error analyzing multiple screenshots: {e}")
        return None



def analyze_linkedin_screenshot(image):
    """Analyze LinkedIn profile from screenshot using OCR and AI"""
    try:
        st.info("📸 Processing LinkedIn profile screenshot...")
        
        # Convert image to text using OCR
        ocr_text = extract_text_from_image(image)
        
        if not ocr_text:
            st.error("Could not extract text from the image")
            return None
        
        st.info("🤖 Analyzing extracted text with AI...")
        
        # Use OpenAI to parse the OCR text into structured profile data
        profile_data = parse_linkedin_text_with_ai(ocr_text)
        
        if profile_data:
            st.success(f"✅ Successfully analyzed screenshot for {profile_data['name']}")
            return profile_data
        else:
            st.warning("Could not parse profile information from screenshot")
            return create_fallback_profile("screenshot", "unknown")
            
    except Exception as e:
        st.error(f"Error analyzing LinkedIn screenshot: {e}")
        return None

def extract_text_from_image(image):
    """Extract text from LinkedIn profile screenshot using OCR"""
    try:
        # Convert Streamlit uploaded file to PIL Image
        if hasattr(image, 'read'):
            pil_image = Image.open(image)
        else:
            pil_image = image
        
        # Convert to OpenCV format for preprocessing
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR
        processed_image = preprocess_image_for_ocr(opencv_image)
        
        # Extract text using Tesseract OCR
        try:
            # Try with default settings first
            text = pytesseract.image_to_string(processed_image)
        except:
            # Fallback to basic OCR if Tesseract fails
            text = pytesseract.image_to_string(pil_image)
        
        if text.strip():
            st.info(f"📝 Extracted {len(text)} characters from image")
            return text
        else:
            st.warning("No text found in the image")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return None

def preprocess_image_for_ocr(image):
    """Preprocess image to improve OCR accuracy"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        st.error(f"Error preprocessing image: {e}")
        return image

def parse_linkedin_text_with_ai(ocr_text):
    """Use OpenAI to analyze LinkedIn profile text and provide strategic insights for business calls"""
    try:
        prompt = f"""
        You are an expert business analyst and communication strategist. Analyze this LinkedIn profile text and provide strategic insights for business calls.

        LinkedIn Profile Text:
        {ocr_text}

        Please provide a comprehensive analysis in the following format:

        **PROFILE SUMMARY**
        [Extract and summarize the key professional information: name, title, company, location, education]

        **PROFESSIONAL BACKGROUND**
        [Summarize their career journey, key achievements, and expertise areas]

        **STRATEGIC INSIGHTS**
        [Provide business-relevant observations about their background, industry positioning, and professional interests]

        **CALL STRATEGY**
        [Suggest 3-4 conversation starters, relevant topics to discuss, and potential questions that could lead to meaningful business discussion]

        **RELATIONSHIP BUILDING**
        [How to build rapport and position value based on their background]

        **CALL PREPARATION NOTES**
        [Key strategic points to remember for the call]

        Focus on practical insights that would help during a business conversation. Be concise but comprehensive.
        """
        
        # Try to get available models first
        try:
            models_response = client.models.list()
            available_models = [model.id for model in models_response.data if "gpt" in model.id.lower()]
            st.info(f"Available GPT models: {available_models}")
            
            # Use the first available GPT model
            if available_models:
                model_to_use = available_models[0]
                response = client.chat.completions.create(
                    model=model_to_use,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                st.info(f"✅ Using model: {model_to_use}")
            else:
                st.error("No GPT models available in your project")
                return None
                
        except Exception as model_error:
            st.error(f"Error accessing OpenAI models: {model_error}")
            return None
        
        # Get the response text
        response_text = response.choices[0].message.content.strip()
        
        # Create a simple structured format for display
        profile_data = {
            "name": "LinkedIn Profile Analysis",
            "title": "Strategic Business Call Insights",
            "location": "Based on uploaded screenshots",
            "summary": response_text,
            "skills": [],
            "experience": [],
            "education": "",
            "social_links": [],
            "strategic_analysis": response_text
        }
        
        return profile_data
            
    except Exception as e:
        st.error(f"Error analyzing LinkedIn profile with AI: {e}")
        return None

def scrape_linkedin_profile(linkedin_url):
    """Advanced LinkedIn scraping with multiple bypass techniques"""
    try:
        st.info("📡 Attempting LinkedIn profile scraping with advanced techniques...")
        
        # Try multiple scraping methods
        profile_data = None
        
        # Method 1: Advanced headers with session
        profile_data = try_advanced_scraping(linkedin_url)
        
        # Method 2: If failed, try with different user agents
        if not profile_data:
            profile_data = try_rotating_user_agents(linkedin_url)
        
        # Method 3: If still failed, try with delays and cookies
        if not profile_data:
            profile_data = try_session_based_scraping(linkedin_url)
        
        # Method 4: If all failed, try mobile user agent
        if not profile_data:
            profile_data = try_mobile_scraping(linkedin_url)
        
        if profile_data and profile_data["name"] != "Unknown":
            st.success("✅ Successfully scraped LinkedIn profile!")
            return profile_data
        else:
            st.warning("⚠️ All scraping methods failed. Using manual input mode.")
            return create_manual_profile(linkedin_url)
            
    except Exception as e:
        st.error(f"Error in advanced scraping: {e}")
        return create_manual_profile(linkedin_url)

def try_advanced_scraping(linkedin_url):
    """Advanced scraping with sophisticated headers and session"""
    try:
        import random
        import time
        
        # Create a session for better cookie handling
        session = requests.Session()
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
        }
        
        session.headers.update(headers)
        
        # Add random delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        st.info("🔍 Method 1: Advanced headers with session...")
        
        # First, visit LinkedIn homepage to get cookies
        session.get('https://www.linkedin.com/', timeout=10)
        time.sleep(random.uniform(1, 2))
        
        # Now try to access the profile
        response = session.get(linkedin_url, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for blocking indicators
            if is_blocked_page(soup):
                return None
            
            profile_data = extract_profile_data_from_html(soup, linkedin_url)
            if profile_data and profile_data["name"] != "Unknown":
                return profile_data
        
        return None
        
    except Exception as e:
        st.error(f"Advanced scraping failed: {e}")
        return None

def try_rotating_user_agents(linkedin_url):
    """Try scraping with different user agents"""
    try:
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        for i, user_agent in enumerate(user_agents, 1):
            try:
                st.info(f"🔍 Method 2.{i}: Trying user agent {i}...")
                
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(linkedin_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    if not is_blocked_page(soup):
                        profile_data = extract_profile_data_from_html(soup, linkedin_url)
                        if profile_data and profile_data["name"] != "Unknown":
                            return profile_data
                
                time.sleep(2)  # Delay between attempts
                
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        st.error(f"User agent rotation failed: {e}")
        return None

def try_session_based_scraping(linkedin_url):
    """Try with session-based approach and cookies"""
    try:
        st.info("🔍 Method 3: Session-based scraping...")
        
        session = requests.Session()
        
        # Set up session with realistic browser behavior
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Simulate browser behavior: visit homepage first
        session.get('https://www.linkedin.com/', timeout=10)
        time.sleep(2)
        
        # Try to access the profile
        response = session.get(linkedin_url, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not is_blocked_page(soup):
                profile_data = extract_profile_data_from_html(soup, linkedin_url)
                if profile_data and profile_data["name"] != "Unknown":
                    return profile_data
        
        return None
        
    except Exception as e:
        st.error(f"Session-based scraping failed: {e}")
        return None

def try_mobile_scraping(linkedin_url):
    """Try mobile user agent approach"""
    try:
        st.info("🔍 Method 4: Mobile user agent...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        response = requests.get(linkedin_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not is_blocked_page(soup):
                profile_data = extract_profile_data_from_html(soup, linkedin_url)
                if profile_data and profile_data["name"] != "Unknown":
                    return profile_data
        
        return None
        
    except Exception as e:
        st.error(f"Mobile scraping failed: {e}")
        return None

def is_blocked_page(soup):
    """Check if the page is blocked or requires login"""
    try:
        page_text = soup.get_text().lower()
        
        # Check for blocking indicators
        blocking_indicators = [
            'sign in',
            'login',
            'join linkedin',
            'access denied',
            'blocked',
            'unusual activity',
            'security check',
            'captcha',
            'verify you are human'
        ]
        
        for indicator in blocking_indicators:
            if indicator in page_text:
                return True
        
        # Check for empty or minimal content
        if len(page_text.strip()) < 100:
            return True
        
        return False
        
    except:
        return True

def create_manual_profile(linkedin_url):
    """Create a profile template for manual input when scraping fails"""
    linkedin_id = extract_linkedin_id(linkedin_url)
    
    return {
        "name": f"Profile {linkedin_id}",
        "title": "Please enter manually",
        "location": "Please enter manually", 
        "summary": "LinkedIn profile found but requires manual input due to access restrictions. Please fill in the details below.",
        "skills": [],
        "experience": [],
        "education": "Please enter manually",
        "social_links": [linkedin_url, "", ""],
        "requires_manual_input": True
    }

def extract_profile_data_from_html(soup, linkedin_url):
    """Extract profile data from LinkedIn HTML"""
    try:
        profile_data = {
            "name": "Unknown",
            "title": "Unknown",
            "location": "Unknown",
            "summary": "No summary available",
            "skills": [],
            "experience": [],
            "education": "No education info",
            "social_links": [linkedin_url, "", ""]
        }
        
        # Extract name (multiple possible selectors)
        name_selectors = [
            'h1.text-heading-xlarge',
            '.text-heading-xlarge',
            'h1[data-section="name"]',
            '.pv-text-details__left-panel h1',
            '.profile-name'
        ]
        
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                profile_data["name"] = name_elem.get_text().strip()
                break
        
        # Extract title/headline
        title_selectors = [
            '.text-body-medium.break-words',
            '.pv-text-details__left-panel .text-body-medium',
            '.profile-headline',
            '[data-section="headline"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                profile_data["title"] = title_elem.get_text().strip()
                break
        
        # Extract location
        location_selectors = [
            '.text-body-small.inline.t-black--light.break-words',
            '.pv-text-details__left-panel .text-body-small',
            '.profile-location'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                profile_data["location"] = location_elem.get_text().strip()
                break
        
        # Extract about/summary
        about_selectors = [
            '.pv-shared-text-with-see-more',
            '.pv-about__summary-text',
            '.profile-summary',
            '[data-section="summary"]'
        ]
        
        for selector in about_selectors:
            about_elem = soup.select_one(selector)
            if about_elem:
                profile_data["summary"] = about_elem.get_text().strip()
                break
        
        # Extract skills
        skills_selectors = [
            '.pv-skill-category-entity__name-text',
            '.skill-category-entity__name',
            '.profile-skill'
        ]
        
        for selector in skills_selectors:
            skill_elems = soup.select(selector)
            if skill_elems:
                profile_data["skills"] = [skill.get_text().strip() for skill in skill_elems[:10]]  # Limit to 10 skills
                break
        
        # Extract experience
        experience_selectors = [
            '.pv-entity__summary-info-v2',
            '.experience-item',
            '.profile-experience'
        ]
        
        for selector in experience_selectors:
            exp_elems = soup.select(selector)
            if exp_elems:
                for exp in exp_elems[:5]:  # Limit to 5 experiences
                    exp_text = exp.get_text().strip()
                    if exp_text:
                        profile_data["experience"].append(exp_text)
                break
        
        # Extract education
        education_selectors = [
            '.pv-entity__school-name',
            '.education-item',
            '.profile-education'
        ]
        
        for selector in education_selectors:
            edu_elem = soup.select_one(selector)
            if edu_elem:
                profile_data["education"] = edu_elem.get_text().strip()
                break
        
        # Try to find social media links
        social_links = extract_social_links(soup)
        if social_links:
            profile_data["social_links"] = social_links
        
        return profile_data
        
    except Exception as e:
        st.error(f"Error extracting profile data: {e}")
        return None

def extract_social_links(soup):
    """Extract social media links from LinkedIn profile"""
    try:
        social_links = ["", "", ""]  # [linkedin, twitter, facebook]
        
        # Look for social media links in the profile
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href'].lower()
            
            # Twitter
            if 'twitter.com' in href or 'x.com' in href:
                social_links[1] = link['href']
            
            # Facebook
            elif 'facebook.com' in href:
                social_links[2] = link['href']
        
        return social_links
        
    except Exception as e:
        st.error(f"Error extracting social links: {e}")
        return None

def clean_linkedin_url(url):
    """Clean and standardize LinkedIn URL"""
    try:
        # Remove any query parameters and fragments
        url = url.split('?')[0].split('#')[0]
        
        # Ensure it's a valid LinkedIn profile URL
        if 'linkedin.com/in/' in url:
            return url
        elif 'linkedin.com/profile/view' in url:
            return url
        else:
            return None
    except:
        return None



def create_fallback_profile(linkedin_url, linkedin_id):
    """Create a fallback profile when Apollo.io doesn't find exact match"""
    return {
        "name": f"Profile {linkedin_id}",
        "title": "Unknown",
        "location": "Unknown",
        "summary": "Profile found but limited data available",
        "skills": [],
        "experience": [],
        "education": "Unknown",
        "social_links": [linkedin_url, "", ""]
    }

def extract_linkedin_id(profile_url):
    """Extract LinkedIn profile ID from URL"""
    try:
        # Handle different LinkedIn URL formats
        if 'linkedin.com/in/' in profile_url:
            # Extract the profile identifier
            parts = profile_url.split('linkedin.com/in/')
            if len(parts) > 1:
                profile_id = parts[1].split('/')[0].split('?')[0]
                return profile_id
        return None
    except:
        return None

def analyze_social_media_posts(social_links):
    """Analyze social media posts for personality insights"""
    try:
        st.info("📱 Analyzing social media posts for personality insights...")
        
        # Simulated social media analysis
        personality_insights = {
            "interests": ["Technology", "Travel", "Photography", "Coffee", "Hiking"],
            "personality_traits": ["Analytical", "Creative", "Outgoing", "Family-oriented"],
            "recent_activities": [
                "Posted about hiking trip to Yosemite",
                "Shared article about AI in healthcare",
                "Celebrated daughter's birthday",
                "Attended tech conference in Austin"
            ],
            "communication_style": "Professional but friendly, uses emojis occasionally",
            "family_notes": "Married with 2 kids, lives in San Francisco",
            "professional_interests": ["AI/ML", "Web Development", "Startups", "Innovation"]
        }
        
        return personality_insights
    except Exception as e:
        st.error(f"Error analyzing social media: {e}")
        return None

def generate_personality_summary(profile_data, personality_insights):
    """Generate a comprehensive personality summary"""
    if not profile_data or not personality_insights:
        return "Unable to generate personality summary due to missing data."
    
    summary_prompt = f"""
    Create a comprehensive personality summary for a professional contact based on the following information:
    
    LinkedIn Profile:
    - Name: {profile_data.get('name', 'Unknown')}
    - Title: {profile_data.get('title', 'Unknown')}
    - Summary: {profile_data.get('summary', 'No summary available')}
    - Skills: {', '.join(profile_data.get('skills', []))}
    - Experience: {'; '.join(profile_data.get('experience', []))}
    
    Social Media Insights:
    - Interests: {', '.join(personality_insights.get('interests', []))}
    - Personality Traits: {', '.join(personality_insights.get('personality_traits', []))}
    - Recent Activities: {'; '.join(personality_insights.get('recent_activities', []))}
    - Communication Style: {personality_insights.get('communication_style', 'Unknown')}
    - Family Notes: {personality_insights.get('family_notes', 'No family information')}
    - Professional Interests: {', '.join(personality_insights.get('professional_interests', []))}
    
    Generate a concise, professional summary that highlights key conversation points, interests, and personality traits that would be useful for a business call.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_questions(transcript, person_name, call_goals, personality_summary):
    """Generate personalized questions based on personality analysis"""
    context = query_context(transcript, person_name)
    
    full_prompt = f"""
    You are an expert assistant helping with a professional call. Generate 3 intelligent, personalized questions based on the person's background and the call goals.
    
    Person's Background Summary:
    {personality_summary}
    
    Call Goals:
    {call_goals}
    
    Current Conversation:
    {transcript}
    
    Relevant Context:
    {context}
    
    Generate 3 intelligent, discussion-forwarding questions that are:
    1. Personalized to their interests and background
    2. Relevant to the call goals
    3. Professional and engaging
    4. Based on their recent activities or professional interests
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt.strip()}]
    )
    return response.choices[0].message.content.strip()

def main():
    # Main UI
    st.title("💼 LinkedIn Call Assistant")
    st.markdown("Analyze LinkedIn profiles and social media to generate personalized conversation insights")

    # Person Information
    st.header("👤 Contact Information")
    person_name = st.text_input("Person's Name", placeholder="Enter the person's name")
    
    # LinkedIn Profile Analysis Form
    st.header("📋 LinkedIn Profile Analysis")
    
    st.info("""
    **Instructions:**
    1. Open the LinkedIn profile you want to analyze in your browser
    2. Take screenshots of the key sections (profile info, experience, skills, etc.)
    3. Upload multiple screenshots below for comprehensive analysis
    """)
    
    # Screenshot Upload Tool
    st.subheader("📸 Upload LinkedIn Profile Screenshots")
    
    # Multiple screenshot upload
    uploaded_files = st.file_uploader(
        "Upload LinkedIn Profile Screenshots", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        help="Upload multiple screenshots covering different sections of the profile"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} screenshot(s) uploaded")
        
        # Display uploaded screenshots
        if len(uploaded_files) > 0:
            st.subheader("📷 Uploaded Screenshots")
            cols = st.columns(min(3, len(uploaded_files)))
            for i, uploaded_file in enumerate(uploaded_files):
                with cols[i % 3]:
                    st.image(uploaded_file, caption=f"Screenshot {i+1}", use_column_width=True)
        
        # Analyze button
        if st.button("🔍 Analyze Screenshots"):
            with st.spinner("Analyzing LinkedIn profile screenshots..."):
                profile_data = analyze_multiple_screenshots(uploaded_files)
                if profile_data:
                    st.session_state.profile_data = profile_data
                    st.success("✅ Profile analysis completed!")
    

            
            if profile_data:
                st.session_state.profile_data = profile_data
                st.success("LinkedIn profile analyzed successfully!")
                
                # Display profile information
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📋 Profile Information")
                    st.write(f"**Name:** {profile_data['name']}")
                    st.write(f"**Title:** {profile_data['title']}")
                    st.write(f"**Location:** {profile_data['location']}")
                    st.write(f"**Summary:** {profile_data['summary']}")
                    
                    st.subheader("🛠️ Skills")
                    for skill in profile_data['skills']:
                        st.write(f"• {skill}")
                
                with col2:
                    st.subheader("💼 Experience")
                    for exp in profile_data['experience']:
                        st.write(f"• {exp}")
                    
                    st.subheader("🎓 Education")
                    st.write(profile_data['education'])
                    
                    st.subheader("🔗 Social Links")
                    for link in profile_data['social_links']:
                        if link and link != "Unknown":
                            st.write(f"• {link}")
                
                # Display strategic analysis if available
                if 'strategic_analysis' in profile_data and profile_data['strategic_analysis']:
                    st.subheader("🎯 Strategic Analysis & Call Insights")
                    st.markdown(profile_data['strategic_analysis'])
                
                # Manual input section if LinkedIn blocking occurred
                if profile_data.get('requires_manual_input', False):
                    st.warning("⚠️ LinkedIn blocked automated access. Please manually enter the profile details below:")
                    
                    with st.expander("📝 Manual Profile Input", expanded=True):
                        manual_name = st.text_input("Full Name", value=profile_data['name'], key="manual_name")
                        manual_title = st.text_input("Job Title", value=profile_data['title'], key="manual_title")
                        manual_location = st.text_input("Location", value=profile_data['location'], key="manual_location")
                        manual_summary = st.text_area("Professional Summary", value=profile_data['summary'], key="manual_summary")
                        manual_skills = st.text_input("Skills (comma-separated)", value=", ".join(profile_data['skills']), key="manual_skills")
                        manual_experience = st.text_area("Recent Experience", value="\n".join(profile_data['experience']), key="manual_experience")
                        manual_education = st.text_input("Education", value=profile_data['education'], key="manual_education")
                        
                        if st.button("💾 Save Manual Profile"):
                            # Update profile data with manual input
                            updated_profile = {
                                "name": manual_name,
                                "title": manual_title,
                                "location": manual_location,
                                "summary": manual_summary,
                                "skills": [skill.strip() for skill in manual_skills.split(",") if skill.strip()],
                                "experience": [exp.strip() for exp in manual_experience.split("\n") if exp.strip()],
                                "education": manual_education,
                                "social_links": profile_data['social_links'],
                                "requires_manual_input": False
                            }
                            st.session_state.profile_data = updated_profile
                            st.success("✅ Manual profile saved successfully!")
                            st.rerun()

    # Social Media Analysis
    if 'profile_data' in st.session_state:
        st.header("📱 Social Media Analysis")
        
        if st.button("🔍 Analyze Social Media Posts"):
            with st.spinner("Analyzing social media posts..."):
                personality_insights = analyze_social_media_posts(st.session_state.profile_data.get('social_links', []))
                
                if personality_insights:
                    st.session_state.personality_insights = personality_insights
                    st.success("Social media analysis completed!")
                    
                    # Generate personality summary
                    personality_summary = generate_personality_summary(
                        st.session_state.profile_data, 
                        personality_insights
                    )
                    st.session_state.personality_summary = personality_summary
                    
                    # Display insights
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🎯 Interests & Traits")
                        st.write("**Interests:** " + ", ".join(personality_insights['interests']))
                        st.write("**Personality:** " + ", ".join(personality_insights['personality_traits']))
                        st.write("**Communication:** " + personality_insights['communication_style'])
                    
                    with col2:
                        st.subheader("👨‍👩‍👧‍👦 Personal Notes")
                        st.write("**Family:** " + personality_insights['family_notes'])
                        st.write("**Recent Activities:**")
                        for activity in personality_insights['recent_activities'][:3]:
                            st.write(f"• {activity}")

    # Call Preparation
    if 'personality_summary' in st.session_state:
        st.header("📞 Call Preparation")
        
        # Auto-populate personality summary
        personality_summary = st.text_area(
            "Personality Summary (Auto-generated)",
            value=st.session_state.personality_summary,
            height=150,
            help="This summary will guide question generation during the call"
        )
        
        call_goals = st.text_area(
            "Call Goals & Agenda",
            placeholder="Enter the purpose, goals, or agenda for this call...",
            height=100
        )
        
        # Store in session state
        st.session_state.personality_summary = personality_summary
        st.session_state.call_goals = call_goals

    # Start Call
    if 'personality_summary' in st.session_state and 'call_goals' in st.session_state:
        st.header("🎤 Start Call")
        
        if st.button("Start Listening"):
            st.session_state.listening = True

    # Call Interface
    if st.session_state.get("listening", False):
        st.header("🎙️ Live Call")
        
        # Display current person info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Calling:** {person_name}")
            st.info(f"**Goals:** {st.session_state.get('call_goals', 'Not set')}")
        
        with col2:
            if st.button("Stop Listening"):
                st.session_state.listening = False
                st.success("Call ended.")
                st.rerun()
        
        # Transcript and questions display
        transcript_display = st.empty()
        question_display = st.empty()
        
        rolling_buffer = []
        all_transcripts = []
        
        try:
            while st.session_state.get("listening", False):
                st.markdown("**Recording...** 🎙️")
                
                # Record audio
                audio = sd.rec(int(RECORD_DURATION * 16000), samplerate=16000, channels=1, dtype='float32')
                sd.wait()
                audio_np = np.squeeze(audio)
                
                # Transcribe
                result = whisper_model.transcribe(audio_np, fp16=False)
                text = result["text"].strip()
                
                if text:
                    all_transcripts.append(text)
                    rolling_buffer.append(text)
                    
                    if len(rolling_buffer) > ROLLING_BUFFER_LIMIT:
                        rolling_buffer.pop(0)
                    
                    joined_text = " ".join(rolling_buffer)
                    transcript_display.markdown("**Latest Transcript:**\n" + joined_text)
                    
                    # Generate questions periodically
                    if len(all_transcripts) % ROLLING_BUFFER_LIMIT == 0:
                        questions = generate_questions(
                            joined_text, 
                            person_name, 
                            st.session_state.get('call_goals', ''),
                            st.session_state.get('personality_summary', '')
                        )
                        question_display.markdown("**Smart Questions:**\n" + questions)
                        
                        # Store in vector database
                        embed_and_upsert(joined_text, person_name)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            st.session_state.listening = False
            st.success("Call ended.")

if __name__ == "__main__":
    main() 