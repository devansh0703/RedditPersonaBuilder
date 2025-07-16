"""Utility functions for the Reddit Persona Generator."""

import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any


def create_output_directory(directory: str) -> None:
    """Create output directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    # Limit length
    return sanitized[:100]


def extract_username_from_url(url: str) -> str:
    """Extract username from Reddit user profile URL."""
    patterns = [
        r'reddit\.com/user/([^/]+)',
        r'reddit\.com/u/([^/]+)',
        r'www\.reddit\.com/user/([^/]+)',
        r'www\.reddit\.com/u/([^/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract username from URL: {url}")


def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to readable date."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def rate_limit_delay(delay: float = 1.0) -> None:
    """Add delay between requests to respect rate limits."""
    time.sleep(delay)


def validate_reddit_data(data: Dict[str, Any]) -> bool:
    """Validate that Reddit data contains required fields."""
    required_fields = ['posts', 'comments']
    return all(field in data for field in required_fields)


def clean_reddit_text(text: str) -> str:
    """Clean Reddit text by removing markdown and formatting."""
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
    text = re.sub(r'&gt;', '>', text)             # Quote markers
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&amp;', '&', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def format_citation(post_data: Dict[str, Any], citation_type: str = "post") -> str:
    """Format a citation for a Reddit post or comment."""
    title = post_data.get('title', '')
    body = post_data.get('body', '')
    subreddit = post_data.get('subreddit', '')
    timestamp = post_data.get('created_utc', 0)
    url = post_data.get('permalink', '')
    
    # Truncate content for citation
    content = title if title else body
    content = truncate_text(content, 100)
    
    formatted_time = format_timestamp(timestamp)
    
    return f"[{citation_type.upper()}] r/{subreddit} - {formatted_time}\n\"{content}\"\nSource: reddit.com{url}"
