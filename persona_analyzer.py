"""AI-powered persona analysis module."""

import json
import logging
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
import os
from pydantic import BaseModel, Field

from config import CITATION_LIMIT
from utils import format_citation, truncate_text


class Demographics(BaseModel):
    """Demographics section of persona analysis."""
    age_estimate: str = Field(description="Age estimate with reasoning")
    occupation_guess: str = Field(description="Occupation guess with reasoning")
    location_hints: str = Field(description="Location hints with reasoning")
    lifestyle: str = Field(description="Lifestyle analysis with reasoning")


class BehaviorHabits(BaseModel):
    """Behavior and habits section of persona analysis."""
    posting_patterns: str = Field(description="Posting patterns analysis")
    interaction_style: str = Field(description="Interaction style analysis")
    content_preferences: str = Field(description="Content preferences analysis")
    activity_level: str = Field(description="Activity level analysis")


class Motivations(BaseModel):
    """Motivations section of persona analysis."""
    primary_drivers: str = Field(description="Primary drivers analysis")
    values: str = Field(description="Values analysis")
    interests: str = Field(description="Interests analysis")


class Personality(BaseModel):
    """Personality section of persona analysis."""
    introversion_extroversion: str = Field(description="Introversion/extroversion analysis")
    thinking_feeling: str = Field(description="Thinking/feeling analysis")
    judging_perceiving: str = Field(description="Judging/perceiving analysis")
    communication_style: str = Field(description="Communication style analysis")


class GoalsNeeds(BaseModel):
    """Goals and needs section of persona analysis."""
    primary_goals: str = Field(description="Primary goals analysis")
    information_needs: str = Field(description="Information needs analysis")
    social_needs: str = Field(description="Social needs analysis")


class Frustrations(BaseModel):
    """Frustrations section of persona analysis."""
    main_frustrations: str = Field(description="Main frustrations analysis")
    pain_points: str = Field(description="Pain points analysis")
    challenges: str = Field(description="Challenges analysis")


class PersonaAnalysis(BaseModel):
    """Complete persona analysis structure."""
    demographics: Demographics
    behavior_habits: BehaviorHabits
    motivations: Motivations
    personality: Personality
    goals_needs: GoalsNeeds
    frustrations: Frustrations


class CitationResponse(BaseModel):
    """Citation response structure."""
    relevant_ids: List[str] = Field(description="List of relevant post/comment IDs")


class PersonaAnalyzer:
    """Handles AI analysis of Reddit data to generate user personas."""
    
    def __init__(self):
        """Initialize Gemini client."""
        self.client = None
        self.setup_gemini_client()
    
    def setup_gemini_client(self) -> None:
        """Set up Gemini API client."""
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            self.client = genai.Client(api_key=gemini_api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def prepare_analysis_data(self, reddit_data: Dict[str, Any]) -> str:
        """Prepare Reddit data for AI analysis."""
        profile = reddit_data['profile']
        posts = reddit_data['posts']
        comments = reddit_data['comments']
        stats = reddit_data['statistics']
        
        # Create summary text for analysis
        analysis_text = f"""
USER PROFILE SUMMARY:
Username: {profile['username']}
Account Age: {profile['account_age_days']:.0f} days
Comment Karma: {profile['comment_karma']}
Link Karma: {profile['link_karma']}
Total Posts: {stats['total_posts']}
Total Comments: {stats['total_comments']}

TOP SUBREDDITS:
{chr(10).join([f"r/{subreddit}: {count} activities" for subreddit, count in stats['top_subreddits']])}

RECENT POSTS:
"""
        
        # Add recent posts
        for i, post in enumerate(posts[:50]):  # Increased for more analysis data
            analysis_text += f"\nPost {i+1}:\n"
            analysis_text += f"Title: {post['title']}\n"
            analysis_text += f"Subreddit: r/{post['subreddit']}\n"
            analysis_text += f"Score: {post['score']}\n"
            if post['body']:
                analysis_text += f"Content: {truncate_text(post['body'], 300)}\n"
            analysis_text += f"---\n"
        
        analysis_text += "\nRECENT COMMENTS:\n"
        
        # Add recent comments
        for i, comment in enumerate(comments[:100]):  # Increased for more analysis data
            analysis_text += f"\nComment {i+1}:\n"
            analysis_text += f"Subreddit: r/{comment['subreddit']}\n"
            analysis_text += f"Score: {comment['score']}\n"
            if comment.get('parent_title'):
                analysis_text += f"Post: {comment['parent_title']}\n"
            analysis_text += f"Content: {truncate_text(comment['body'], 200)}\n"
            analysis_text += f"---\n"
        
        return analysis_text
    
    def generate_persona(self, reddit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user persona using AI analysis."""
        analysis_data = self.prepare_analysis_data(reddit_data)
        
        system_prompt = """
You are an expert user experience researcher and behavioral psychologist specializing in creating detailed user personas from social media data. 
Analyze the provided Reddit user data and create a comprehensive, in-depth persona that includes:

1. DEMOGRAPHICS: Provide detailed analysis with reasoning for:
   - Age estimate (with supporting evidence from language patterns, cultural references, life stage indicators)
   - Occupation guess (based on technical knowledge, work-related posts, time patterns, industry discussions)
   - Location hints (timezone patterns, local references, cultural context clues)
   - Lifestyle analysis (living situation, financial status, social life, hobbies, daily routines)

2. BEHAVIOR & HABITS: Provide extensive analysis of:
   - Posting patterns (frequency, timing, seasonal variations, consistency)
   - Interaction style (how they engage with others, tone, helpfulness, argument style)
   - Content preferences (topics they gravitate toward, types of posts they create/engage with)
   - Activity level (lurker vs active participant, response patterns, community involvement)

3. MOTIVATIONS: Deep dive into:
   - Primary drivers (what motivates their Reddit usage and life decisions)
   - Values (what principles guide their behavior and opinions)
   - Interests (detailed breakdown of hobbies, passions, and areas of expertise)

4. PERSONALITY: Comprehensive psychological profiling:
   - Introversion/extroversion tendencies with specific behavioral evidence
   - Thinking vs feeling decision-making patterns
   - Judging vs perceiving approach to life and planning
   - Communication style (direct/indirect, formal/casual, emotional/logical)

5. GOALS & NEEDS: Detailed analysis of:
   - Primary goals (career, personal, social, learning objectives)
   - Information needs (what they seek to learn or stay updated on)
   - Social needs (community, validation, help, entertainment)

6. FRUSTRATIONS: In-depth exploration of:
   - Main frustrations (recurring themes of annoyance or disappointment)
   - Pain points (specific challenges they face regularly)
   - Challenges (obstacles to achieving their goals)

For each section, provide detailed analysis with multiple paragraphs. Include specific examples and evidence from their posts/comments. 
Be thorough, analytical, and provide insights that would be valuable for UX design, marketing, or product development.
Generate comprehensive, detailed responses - aim for depth and specificity rather than brevity.
"""
        
        try:
            # Note that the newest Gemini model series is "gemini-2.5-flash" or "gemini-2.5-pro"
            # do not change this unless explicitly requested by the user
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=analysis_data)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=PersonaAnalysis,
                    temperature=0.7,
                    max_output_tokens=8000
                )
            )
            
            raw_response = response.text
            
            # Check if response is None
            if raw_response is None:
                logging.error("Received None response from Gemini API")
                return self._create_fallback_persona("No response received from Gemini API")
            
            logging.info(f"Raw Gemini response length: {len(raw_response)}")
            
            # Parse using Pydantic with structured output
            try:
                persona_analysis = PersonaAnalysis.model_validate_json(raw_response)
                logging.info("Successfully parsed structured Gemini response")
                return persona_analysis.model_dump()
            except Exception as e:
                logging.warning(f"Pydantic parsing failed: {e}")
                
                # Try to fix JSON truncation issues
                cleaned_response = raw_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                # Try to fix truncated JSON by adding missing closing braces
                if not cleaned_response.endswith('}'):
                    # Count open braces and add corresponding closing braces
                    open_braces = cleaned_response.count('{')
                    close_braces = cleaned_response.count('}')
                    missing_braces = open_braces - close_braces
                    
                    if missing_braces > 0:
                        # Add missing quotes if the string ends abruptly
                        if cleaned_response.endswith('"') or cleaned_response.endswith("'"):
                            pass  # Already properly quoted
                        elif cleaned_response[-1].isalnum():
                            cleaned_response += '"'
                        
                        # Add missing closing braces
                        cleaned_response += '}' * missing_braces
                        logging.info(f"Added {missing_braces} missing closing braces")
                
                try:
                    import json as json_module
                    raw_data = json_module.loads(cleaned_response)
                    persona_analysis = PersonaAnalysis.model_validate(raw_data)
                    logging.info("Successfully parsed with fallback JSON parsing")
                    return persona_analysis.model_dump()
                except Exception as fallback_error:
                    logging.error(f"Fallback JSON parsing failed: {fallback_error}")
                    logging.error(f"Raw response: {raw_response[:1000]}...")
                    return self._create_fallback_persona(raw_response)
            
        except Exception as e:
            logging.error(f"Failed to generate persona: {e}")
            raise
    
    def _create_fallback_persona(self, raw_response: str) -> Dict[str, Any]:
        """Create a fallback persona when JSON parsing fails."""
        logging.warning("Creating fallback persona due to JSON parsing failure")
        
        # Try to extract some basic info from the raw response
        fallback_text = "Analysis unavailable due to response parsing error"
        if raw_response:
            # Extract any readable text from the response
            import re
            text_fragments = re.findall(r'"([^"]*)"', raw_response)
            if text_fragments:
                fallback_text = " ".join(text_fragments[:3])
        
        return {
            "demographics": {
                "age_estimate": f"Unable to determine from available data. {fallback_text}",
                "occupation_guess": "Unable to determine from available data",
                "location_hints": "Unable to determine from available data", 
                "lifestyle": "Unable to determine from available data"
            },
            "behavior_habits": {
                "posting_patterns": "Unable to determine from available data",
                "interaction_style": "Unable to determine from available data",
                "content_preferences": "Unable to determine from available data",
                "activity_level": "Unable to determine from available data"
            },
            "motivations": {
                "primary_drivers": "Unable to determine from available data",
                "values": "Unable to determine from available data",
                "interests": "Unable to determine from available data"
            },
            "personality": {
                "introversion_extroversion": "Unable to determine from available data",
                "thinking_feeling": "Unable to determine from available data",
                "judging_perceiving": "Unable to determine from available data",
                "communication_style": "Unable to determine from available data"
            },
            "goals_needs": {
                "primary_goals": "Unable to determine from available data",
                "information_needs": "Unable to determine from available data",
                "social_needs": "Unable to determine from available data"
            },
            "frustrations": {
                "main_frustrations": "Unable to determine from available data",
                "pain_points": "Unable to determine from available data",
                "challenges": "Unable to determine from available data"
            }
        }
    
    def generate_citations(self, reddit_data: Dict[str, Any], persona: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate citations linking persona characteristics to specific posts/comments."""
        posts = reddit_data['posts']
        comments = reddit_data['comments']
        
        citations = {}
        
        # Create citation prompt for each persona section
        for section_name, section_data in persona.items():
            section_citations = []
            
            # Analyze each characteristic in the section
            for characteristic, analysis in section_data.items():
                citation_prompt = f"""
Based on this persona characteristic analysis: "{analysis}"

Find the most relevant Reddit posts and comments that support this analysis.
Look for specific examples that directly relate to this characteristic.

Reddit Posts:
{self._format_posts_for_citation(posts[:10])}

Reddit Comments:
{self._format_comments_for_citation(comments[:15])}

Return the IDs of the most relevant posts/comments that support this analysis.
Format as JSON: {{"relevant_ids": ["post_id1", "comment_id2", ...]}}
Limit to maximum 3 most relevant items.
"""
                
                try:
                    # Note that the newest Gemini model series is "gemini-2.5-flash" or "gemini-2.5-pro"
                    # do not change this unless explicitly requested by the user
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            types.Content(role="user", parts=[types.Part(text=citation_prompt)])
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction="You are a citation expert. Find the most relevant source material for the given analysis.",
                            response_mime_type="application/json",
                            response_schema=CitationResponse,
                            temperature=0.3,
                            max_output_tokens=500
                        )
                    )
                    
                    # Parse citation response with better error handling
                    raw_citation_response = response.text
                    if raw_citation_response is None:
                        logging.warning("Received None response from Gemini for citations")
                        continue
                    
                    cleaned_citation_response = raw_citation_response.strip()
                    if cleaned_citation_response.startswith('```json'):
                        cleaned_citation_response = cleaned_citation_response[7:]
                    if cleaned_citation_response.endswith('```'):
                        cleaned_citation_response = cleaned_citation_response[:-3]
                    cleaned_citation_response = cleaned_citation_response.strip()
                    
                    try:
                        # Use Pydantic for structured citation parsing
                        citation_response = CitationResponse.model_validate_json(cleaned_citation_response)
                        relevant_ids = citation_response.relevant_ids
                    except Exception as citation_error:
                        logging.warning(f"Citation parsing error: {citation_error}")
                        # Try fallback JSON parsing
                        try:
                            import json as json_module
                            citation_data = json_module.loads(cleaned_citation_response)
                            relevant_ids = citation_data.get('relevant_ids', [])
                        except Exception:
                            # Try regex extraction for citations
                            import re
                            id_matches = re.findall(r'"([a-zA-Z0-9_]+)"', cleaned_citation_response)
                            relevant_ids = id_matches[:3] if id_matches else []
                    
                    # Format citations
                    for item_id in relevant_ids:
                        citation = self._find_and_format_citation(item_id, posts, comments)
                        if citation:
                            section_citations.append(f"{characteristic}: {citation}")
                    
                except Exception as e:
                    logging.warning(f"Failed to generate citations for {characteristic}: {e}")
                    continue
            
            citations[section_name] = section_citations[:CITATION_LIMIT]
        
        return citations
    
    def _format_posts_for_citation(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts for citation analysis."""
        formatted = ""
        for post in posts:
            formatted += f"POST_ID: {post['id']}\n"
            formatted += f"Title: {post['title']}\n"
            formatted += f"Subreddit: r/{post['subreddit']}\n"
            if post['body']:
                formatted += f"Content: {truncate_text(post['body'], 200)}\n"
            formatted += "---\n"
        return formatted
    
    def _format_comments_for_citation(self, comments: List[Dict[str, Any]]) -> str:
        """Format comments for citation analysis."""
        formatted = ""
        for comment in comments:
            formatted += f"COMMENT_ID: {comment['id']}\n"
            formatted += f"Subreddit: r/{comment['subreddit']}\n"
            formatted += f"Content: {truncate_text(comment['body'], 200)}\n"
            formatted += "---\n"
        return formatted
    
    def _find_and_format_citation(self, item_id: str, posts: List[Dict[str, Any]], comments: List[Dict[str, Any]]) -> Optional[str]:
        """Find and format a citation for a specific post or comment ID."""
        # Check posts
        for post in posts:
            if post['id'] == item_id:
                return format_citation(post, "post")
        
        # Check comments
        for comment in comments:
            if comment['id'] == item_id:
                return format_citation(comment, "comment")
        
        return None
