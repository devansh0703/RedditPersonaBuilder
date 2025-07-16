"""Reddit scraper module for collecting user posts and comments."""

import praw
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    MAX_POSTS, MAX_COMMENTS, REQUEST_DELAY
)
from utils import rate_limit_delay, clean_reddit_text, format_timestamp


class RedditScraper:
    """Handles Reddit API interactions and data collection."""
    
    def __init__(self):
        """Initialize Reddit API client."""
        self.reddit = None
        self.setup_reddit_client()
        
    def setup_reddit_client(self) -> None:
        """Set up Reddit API client with credentials."""
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            raise ValueError(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID "
                "and REDDIT_CLIENT_SECRET environment variables."
            )
        
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            # Test authentication
            self.reddit.user.me()
        except Exception as e:
            logging.error(f"Failed to authenticate with Reddit API: {e}")
            raise
    
    def get_user_profile(self, username: str) -> Optional[praw.models.Redditor]:
        """Get Reddit user profile object."""
        try:
            user = self.reddit.redditor(username)
            # Test if user exists by accessing an attribute
            _ = user.created_utc
            return user
        except Exception as e:
            logging.error(f"Failed to get user profile for {username}: {e}")
            return None
    
    def scrape_user_posts(self, username: str) -> List[Dict[str, Any]]:
        """Scrape posts from a Reddit user profile."""
        user = self.get_user_profile(username)
        if not user:
            return []
        
        posts = []
        try:
            submissions = user.submissions.new(limit=MAX_POSTS)
            
            for submission in submissions:
                rate_limit_delay(REQUEST_DELAY)
                
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'body': clean_reddit_text(submission.selftext),
                    'subreddit': str(submission.subreddit),
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'permalink': submission.permalink,
                    'url': submission.url,
                    'is_self': submission.is_self,
                    'over_18': submission.over_18,
                    'stickied': submission.stickied,
                    'locked': submission.locked
                }
                
                posts.append(post_data)
                
            logging.info(f"Scraped {len(posts)} posts for user {username}")
            return posts
            
        except Exception as e:
            logging.error(f"Error scraping posts for {username}: {e}")
            return []
    
    def scrape_user_comments(self, username: str) -> List[Dict[str, Any]]:
        """Scrape comments from a Reddit user profile."""
        user = self.get_user_profile(username)
        if not user:
            return []
        
        comments = []
        try:
            user_comments = user.comments.new(limit=MAX_COMMENTS)
            
            for comment in user_comments:
                rate_limit_delay(REQUEST_DELAY)
                
                comment_data = {
                    'id': comment.id,
                    'body': clean_reddit_text(comment.body),
                    'subreddit': str(comment.subreddit),
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'permalink': comment.permalink,
                    'parent_id': comment.parent_id,
                    'is_submitter': comment.is_submitter,
                    'stickied': comment.stickied,
                    'locked': getattr(comment, 'locked', False)
                }
                
                # Try to get parent post title for context
                try:
                    if hasattr(comment, 'submission'):
                        comment_data['parent_title'] = comment.submission.title
                except:
                    comment_data['parent_title'] = ""
                
                comments.append(comment_data)
                
            logging.info(f"Scraped {len(comments)} comments for user {username}")
            return comments
            
        except Exception as e:
            logging.error(f"Error scraping comments for {username}: {e}")
            return []
    
    def scrape_user_data(self, username: str) -> Dict[str, Any]:
        """Scrape all available data for a Reddit user."""
        logging.info(f"Starting data scrape for user: {username}")
        
        user = self.get_user_profile(username)
        if not user:
            raise ValueError(f"User {username} not found or profile is private")
        
        # Get basic profile info
        profile_info = {
            'username': username,
            'created_utc': user.created_utc,
            'comment_karma': user.comment_karma,
            'link_karma': user.link_karma,
            'is_gold': user.is_gold,
            'is_mod': user.is_mod,
            'has_verified_email': user.has_verified_email,
            'account_age_days': (time.time() - user.created_utc) / (24 * 3600)
        }
        
        # Scrape posts and comments
        posts = self.scrape_user_posts(username)
        comments = self.scrape_user_comments(username)
        
        # Calculate activity statistics
        total_posts = len(posts)
        total_comments = len(comments)
        
        # Get subreddit activity
        subreddit_activity = {}
        for post in posts:
            subreddit = post['subreddit']
            subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1
        
        for comment in comments:
            subreddit = comment['subreddit']
            subreddit_activity[subreddit] = subreddit_activity.get(subreddit, 0) + 1
        
        # Sort subreddits by activity
        top_subreddits = sorted(subreddit_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'profile': profile_info,
            'posts': posts,
            'comments': comments,
            'statistics': {
                'total_posts': total_posts,
                'total_comments': total_comments,
                'total_activity': total_posts + total_comments,
                'top_subreddits': top_subreddits
            }
        }
