"""Configuration settings for the Reddit Persona Generator.

Required Environment Variables:
- REDDIT_CLIENT_ID: Your Reddit API client ID
- REDDIT_CLIENT_SECRET: Your Reddit API client secret  
- GEMINI_API_KEY: Your Google Gemini API key

Get Reddit credentials at: https://www.reddit.com/prefs/apps
Get Gemini API key at: https://aistudio.google.com/app/apikey
"""

import os

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "PersonaGenerator/1.0"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Scraping Configuration
MAX_POSTS = None if os.getenv("MAX_POSTS") == "None" else int(os.getenv("MAX_POSTS", "1000"))  # High default limit
MAX_COMMENTS = None if os.getenv("MAX_COMMENTS") == "None" else int(os.getenv("MAX_COMMENTS", "2000"))  # High default limit
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))  # Reduced delay

# Output Configuration
OUTPUT_DIR = "personas"
CITATION_LIMIT = 5  # Maximum citations per characteristic
