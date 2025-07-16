"""
Flask web application for Reddit Persona Generator
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge
import traceback
from datetime import datetime

from reddit_scraper import RedditScraper
from persona_analyzer import PersonaAnalyzer
from utils import extract_username_from_url, validate_reddit_data
from config import OUTPUT_DIR

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def index():
    """Main page with input form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_persona():
    """Generate persona from Reddit profile"""
    try:
        data = request.get_json()
        profile_input = data.get('profile_input', '').strip()
        
        if not profile_input:
            return jsonify({'error': 'Please provide a Reddit username or profile URL'}), 400
        
        # Extract username from input
        if profile_input.startswith('http'):
            username = extract_username_from_url(profile_input)
        else:
            # Assume it's just a username
            username = profile_input.replace('u/', '').replace('/u/', '').replace('@', '')
        
        if not username:
            return jsonify({'error': 'Invalid Reddit username or URL'}), 400
        
        logging.info(f"Processing request for username: {username}")
        
        # Initialize components
        scraper = RedditScraper()
        analyzer = PersonaAnalyzer()
        
        # Scrape Reddit data
        logging.info(f"Scraping Reddit data for user: {username}")
        reddit_data = scraper.scrape_user_data(username)
        
        if not validate_reddit_data(reddit_data):
            return jsonify({'error': f'No data found for user {username} or user does not exist'}), 404
        
        total_activities = len(reddit_data.get('posts', [])) + len(reddit_data.get('comments', []))
        logging.info(f"Found {total_activities} total activities for {username}")
        
        # Generate persona
        logging.info("Generating AI persona analysis...")
        persona = analyzer.generate_persona(reddit_data)
        
        # Generate citations
        logging.info("Generating citations...")
        citations = analyzer.generate_citations(reddit_data, persona)
        
        # Format response
        response_data = {
            'username': username,
            'total_activities': total_activities,
            'posts_count': len(reddit_data.get('posts', [])),
            'comments_count': len(reddit_data.get('comments', [])),
            'persona': persona,
            'citations': citations,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        
        logging.info(f"Successfully generated persona for {username}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error generating persona: {error_msg}")
        logging.error(traceback.format_exc())
        
        return jsonify({
            'error': f'Error generating persona: {error_msg}',
            'success': False
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)