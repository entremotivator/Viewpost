import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime, timedelta
import requests
from PIL import Image
import io
import re
from typing import Optional
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import openai
import hashlib
import time
from collections import Counter
import numpy as np

# Page configuration
st.set_page_config(
    page_title="AI-Powered Social Media Manager Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling with light blue theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #3498db;
        --light-blue: #e3f2fd;
        --accent-blue: #2196f3;
        --success-green: #4caf50;
        --warning-orange: #ff9800;
        --error-red: #f44336;
        --text-dark: #2c3e50;
        --text-light: #7f8c8d;
        --background-light: #f8f9fa;
    }
    
    /* Enhanced post cards */
    .post-card {
        background: linear-gradient(135deg, #ffffff 0%, var(--light-blue) 100%);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.1);
        padding: 24px;
        margin: 15px 0;
        border-left: 5px solid var(--primary-blue);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .post-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(52, 152, 219, 0.2);
    }
    
    .post-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-blue), var(--accent-blue));
    }
    
    .post-message {
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 16px;
        color: var(--text-dark);
        font-weight: 400;
    }
    
    .post-meta {
        font-size: 13px;
        color: var(--text-light);
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .post-actions {
        display: flex;
        gap: 12px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    
    .action-button {
        padding: 8px 16px;
        border-radius: 20px;
        border: none;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .action-button.primary {
        background: var(--primary-blue);
        color: white;
    }
    
    .action-button.secondary {
        background: var(--background-light);
        color: var(--text-dark);
        border: 1px solid #ddd;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 25px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
        gap: 6px;
    }
    
    .status-scheduled {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
    }
    
    .status-queued {
        background: linear-gradient(135deg, #ff9800, #ffb74d);
        color: white;
    }
    
    .status-draft {
        background: linear-gradient(135deg, #9e9e9e, #bdbdbd);
        color: white;
    }
    
    /* Analytics cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, var(--light-blue) 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(52, 152, 219, 0.1);
        border-top: 4px solid var(--primary-blue);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
        color: var(--primary-blue);
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--text-light);
        font-weight: 500;
    }
    
    /* Enhanced Calendar styling */
    .calendar-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding: 16px;
        background: linear-gradient(135deg, var(--primary-blue), var(--accent-blue));
        border-radius: 12px;
        color: white;
    }
    
    .calendar-nav-button {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .calendar-nav-button:hover {
        background: rgba(255,255,255,0.3);
        transform: scale(1.05);
    }
    
    .calendar-day {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 12px;
        margin: 4px;
        min-height: 100px;
        background: white;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .calendar-day:hover {
        background: var(--light-blue);
        border-color: var(--primary-blue);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    }
    
    .calendar-day.has-posts {
        background: linear-gradient(135deg, var(--light-blue), #bbdefb);
        border-color: var(--primary-blue);
        border-width: 3px;
    }
    
    .calendar-day.today {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-color: var(--warning-orange);
        border-width: 3px;
    }
    
    .calendar-day-number {
        font-size: 18px;
        font-weight: bold;
        color: var(--text-dark);
        margin-bottom: 8px;
    }
    
    .calendar-post-indicator {
        background: var(--primary-blue);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin: 2px 0;
        display: inline-block;
    }
    
    .calendar-post-preview {
        font-size: 11px;
        color: var(--text-light);
        margin-top: 4px;
        line-height: 1.2;
        max-height: 40px;
        overflow: hidden;
    }
    
    /* Template cards */
    .template-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .template-card:hover {
        border-color: var(--primary-blue);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.15);
    }
    
    .template-card.selected {
        border-color: var(--primary-blue);
        background: var(--light-blue);
    }
    
    /* AI suggestions */
    .ai-suggestion {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        border-left: 4px solid #9c27b0;
    }
    
    .ai-suggestion-header {
        font-weight: 600;
        color: #6a1b9a;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Platform indicators */
    .platform-indicator {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
    }
    
    .platform-facebook { background: #1877f2; color: white; }
    .platform-instagram { background: #e4405f; color: white; }
    .platform-twitter { background: #1da1f2; color: white; }
    .platform-linkedin { background: #0077b5; color: white; }
    .platform-tiktok { background: #000000; color: white; }
    .platform-pinterest { background: #bd081c; color: white; }
    
    /* Character count indicators */
    .character-count {
        font-size: 12px;
        text-align: right;
        margin-top: 8px;
        padding: 8px;
        background: var(--background-light);
        border-radius: 8px;
    }
    
    .char-count-good { color: var(--success-green); }
    .char-count-warning { color: var(--warning-orange); }
    .char-count-error { color: var(--error-red); }
    
    /* Sidebar styling */
    .sidebar-section {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Success/Error messages */
    .success-message {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid var(--success-green);
        margin: 10px 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid var(--error-red);
        margin: 10px 0;
    }
    
    /* Loading animations */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-blue);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .post-card {
            padding: 16px;
            margin: 10px 0;
        }
        
        .post-actions {
            flex-direction: column;
        }
        
        .action-button {
            width: 100%;
            justify-content: center;
        }
        
        .calendar-day {
            min-height: 80px;
            padding: 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

class EnhancedSocialMediaManager:
    def __init__(self):
        self.column_names = [
            'Message', 'Link', 'ImageURL', 'VideoURL', 'Month(1-12)', 
            'Day(1-31)', 'Year', 'Hour', 'Minute(0-59)', 'PinTitle', 
            'Category', 'Watermark', 'HashtagGroup', 'VideoThumbnailURL',
            'CTAGroup', 'FirstComment', 'Story(YorN)', 'PinterestBoard', 'AltText'
        ]
        
        self.platform_limits = {
            'Facebook': {'limit': 63206, 'optimal': 40, 'color': '#1877f2'},
            'Instagram': {'limit': 2200, 'optimal': 125, 'color': '#e4405f'},
            'Twitter/X': {'limit': 280, 'optimal': 100, 'color': '#1da1f2'},
            'LinkedIn': {'limit': 3000, 'optimal': 150, 'color': '#0077b5'},
            'TikTok': {'limit': 150, 'optimal': 100, 'color': '#000000'},
            'Pinterest': {'limit': 500, 'optimal': 200, 'color': '#bd081c'},
            'YouTube': {'limit': 5000, 'optimal': 125, 'color': '#ff0000'},
            'Snapchat': {'limit': 250, 'optimal': 80, 'color': '#fffc00'}
        }
        
        self.post_templates = {
            'AI Consulting': {
                'template': "🤖 {topic}! {main_message} Our AI solutions have helped {client_type} achieve {result}. Ready to transform your {business_area}? #AI #Consulting #BusinessTransformation",
                'variables': ['topic', 'main_message', 'client_type', 'result', 'business_area']
            },
            'Educational': {
                'template': "📚 {learning_topic}: {key_insight}! {explanation} What's your experience with {topic}? Share below! #Education #Learning #Tips",
                'variables': ['learning_topic', 'key_insight', 'explanation', 'topic']
            },
            'Product Launch': {
                'template': "🚀 EXCITING NEWS! Introducing {product_name} - {product_description}. {key_benefit} Available now! {cta} #ProductLaunch #Innovation #NewProduct",
                'variables': ['product_name', 'product_description', 'key_benefit', 'cta']
            },
            'Customer Success': {
                'template': "🌟 SUCCESS STORY: {customer_name} achieved {achievement} using our {solution}! '{testimonial}' Ready for similar results? {cta} #CustomerSuccess #Testimonial",
                'variables': ['customer_name', 'achievement', 'solution', 'testimonial', 'cta']
            },
            'Industry Insights': {
                'template': "📊 INDUSTRY INSIGHT: {statistic} in {industry}! {analysis} What trends are you seeing? #Industry #Insights #Trends #Data",
                'variables': ['statistic', 'industry', 'analysis']
            },
            'Behind the Scenes': {
                'template': "🎬 BEHIND THE SCENES: {activity_description} {personal_insight} What would you like to see more of? #BehindTheScenes #TeamLife #Culture",
                'variables': ['activity_description', 'personal_insight']
            }
        }
        
        self.hashtag_groups = {
            'AI & Technology': ['#AI', '#MachineLearning', '#TechInnovation', '#DigitalTransformation', '#FutureOfWork', '#Automation'],
            'Business Growth': ['#BusinessGrowth', '#Entrepreneurship', '#StartupLife', '#BusinessStrategy', '#Leadership', '#Innovation'],
            'Marketing': ['#DigitalMarketing', '#ContentMarketing', '#SocialMediaMarketing', '#MarketingStrategy', '#BrandBuilding', '#CustomerEngagement'],
            'Productivity': ['#Productivity', '#TimeManagement', '#WorkflowOptimization', '#Efficiency', '#WorkSmarter', '#LifeHacks'],
            'Education': ['#Learning', '#Education', '#SkillDevelopment', '#ProfessionalDevelopment', '#Training', '#Knowledge'],
            'Industry Specific': ['#Healthcare', '#Finance', '#Retail', '#Manufacturing', '#RealEstate', '#Consulting']
        }
    
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            if 'google_credentials' not in st.session_state:
                return None, "Please upload Google service account credentials"
            
            credentials_dict = st.session_state.google_credentials
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            
            client = gspread.authorize(credentials)
            return client, None
        except Exception as e:
            return None, f"Error connecting to Google Sheets: {str(e)}"
    
    def get_sheet_data(self, client, sheet_url):
        """Fetch data from Google Sheets"""
        try:
            sheet = client.open_by_url(sheet_url).sheet1
            data = sheet.get_all_records()
            
            if not data:
                sheet.append_row(self.column_names)
                return pd.DataFrame(columns=self.column_names)
            
            df = pd.DataFrame(data)
            
            for col in self.column_names:
                if col not in df.columns:
                    df[col] = ''
            
            return df[self.column_names]
        except Exception as e:
            st.error(f"Error reading sheet: {str(e)}")
            return pd.DataFrame(columns=self.column_names)
    
    def update_sheet(self, client, sheet_url, df):
        """Update Google Sheets with DataFrame"""
        try:
            sheet = client.open_by_url(sheet_url).sheet1
            sheet.clear()
            
            data_to_upload = [self.column_names] + df.fillna('').values.tolist()
            sheet.update(f'A1:S{len(data_to_upload)}', data_to_upload)
            return True, "Sheet updated successfully!"
        except Exception as e:
            return False, f"Error updating sheet: {str(e)}"
    
    def safe_int_conversion(self, value, default=0):
        """Safely convert value to integer with fallback"""
        try:
            if value == '' or value is None or pd.isna(value):
                return default
            return int(float(str(value)))
        except (ValueError, TypeError):
            return default
    
    def safe_str_conversion(self, value, default=''):
        """Safely convert value to string with fallback"""
        try:
            if value is None or pd.isna(value):
                return default
            return str(value)
        except:
            return default
    
    def display_enhanced_post_card(self, row, index):
        """Display enhanced post card with proper error handling"""
        message = self.safe_str_conversion(row.get('Message', ''), 'No message')
        
        # Determine status with safe conversions
        month = self.safe_str_conversion(row.get('Month(1-12)', ''))
        day = self.safe_str_conversion(row.get('Day(1-31)', ''))
        year = self.safe_str_conversion(row.get('Year', ''))
        hour = self.safe_str_conversion(row.get('Hour', ''))
        minute = self.safe_int_conversion(row.get('Minute(0-59)', ''), 0)
        
        # Determine post status
        if month and day and year:
            status = "Scheduled"
            status_class = "status-scheduled"
        else:
            status = "Queued"
            status_class = "status-queued"
        
        # Calculate performance score
        performance_score = self.calculate_performance_score(message, row)
        
        # Generate AI feedback
        feedback = self.generate_ai_feedback(message, row)
        
        # Create enhanced card HTML
        card_html = f"""
        <div class="post-card">
            <div class="status-badge {status_class}">
                {'📅' if status == 'Scheduled' else '📝'} {status}
            </div>
        """
        
        # Performance score
        score_color = "#4caf50" if performance_score >= 80 else "#ff9800" if performance_score >= 60 else "#f44336"
        card_html += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 12px; color: #666;">Performance Score</div>
                <div style="background: {score_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;">
                    {performance_score}/100
                </div>
            </div>
        """
        
        # Message content
        card_html += f'<div class="post-message">{message[:200]}{"..." if len(message) > 200 else ""}</div>'
        
        # Scheduling info with proper error handling
        if status == "Scheduled":
            # Format schedule info safely
            try:
                schedule_info = f"{month}/{day}/{year}"
                if hour:
                    schedule_info += f" at {hour}:{minute:02d}"
                else:
                    schedule_info += " (time not set)"
            except:
                schedule_info = f"{month}/{day}/{year} (time format error)"
            
            card_html += f'<div class="post-meta">📅 {schedule_info}</div>'
        
        # Category and other meta info
        category = self.safe_str_conversion(row.get('Category', ''))
        if category:
            card_html += f'<div class="post-meta">🏷️ {category}</div>'
        
        link = self.safe_str_conversion(row.get('Link', ''))
        if link:
            card_html += f'<div class="post-meta">🔗 <a href="{link}" target="_blank">Link attached</a></div>'
        
        # Platform compatibility
        card_html += '<div style="margin: 12px 0;">'
        for platform, info in self.platform_limits.items():
            char_count = len(message)
            if char_count <= info['limit']:
                card_html += f'<span class="platform-indicator" style="background: {info["color"]};">{platform}</span>'
        card_html += '</div>'
        
        # Character count analysis
        card_html += '<div class="character-count">'
        for platform, info in list(self.platform_limits.items())[:4]:  # Show top 4 platforms
            char_count = len(message)
            if char_count <= info['optimal']:
                color_class = 'char-count-good'
            elif char_count <= info['limit']:
                color_class = 'char-count-warning'
            else:
                color_class = 'char-count-error'
            card_html += f'<div class="{color_class}">{platform}: {char_count}/{info["limit"]}</div>'
        card_html += '</div>'
        
        card_html += "</div>"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(card_html, unsafe_allow_html=True)
            
            # AI Feedback
            if feedback:
                with st.expander("🤖 AI Performance Analysis"):
                    for item in feedback:
                        st.write(item)
            
            # Display media
            image_url = self.safe_str_conversion(row.get('ImageURL', ''))
            if image_url:
                image = self.load_image_from_url(image_url)
                if image:
                    st.image(image, caption="Post Image", use_column_width=True)
                else:
                    st.info(f"🖼️ Image URL: {image_url}")
            
            video_url = self.safe_str_conversion(row.get('VideoURL', ''))
            if video_url:
                if video_url.endswith('.mp4'):
                    try:
                        st.video(video_url)
                    except:
                        st.info(f"🎥 Video URL: {video_url}")
                else:
                    st.info(f"🎥 Video URL: {video_url}")
        
        with col2:
            st.markdown("**Actions:**")
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("✏️", key=f"edit_{index}", help="Edit post"):
                    st.session_state.editing_post = index
                    st.rerun()
                
                if st.button("📋", key=f"duplicate_{index}", help="Duplicate post"):
                    st.session_state.duplicate_post = index
                    st.rerun()
            
            with col2_2:
                if st.button("🗑️", key=f"delete_{index}", help="Delete post"):
                    st.session_state.delete_post = index
                    st.rerun()
                
                if st.button("📊", key=f"analyze_{index}", help="Analyze post"):
                    st.session_state.analyze_post = index
                    st.rerun()
    
    def calculate_performance_score(self, message, row):
        """Calculate post performance score"""
        score = 0
        
        # Message length (30 points)
        msg_len = len(message)
        if 50 <= msg_len <= 200:
            score += 30
        elif 20 <= msg_len <= 300:
            score += 20
        else:
            score += 10
        
        # Has scheduling info (20 points)
        if row.get('Month(1-12)') and row.get('Day(1-31)') and row.get('Year'):
            score += 20
        
        # Has media (20 points)
        if row.get('ImageURL') or row.get('VideoURL'):
            score += 20
        
        # Has category (10 points)
        if row.get('Category'):
            score += 10
        
        # Has hashtags (10 points)
        if '#' in message:
            score += 10
        
        # Has call to action (10 points)
        cta_words = ['click', 'visit', 'learn', 'discover', 'try', 'get', 'download', 'sign up', 'join', 'follow']
        if any(word in message.lower() for word in cta_words):
            score += 10
        
        return min(score, 100)
    
    def generate_ai_feedback(self, message, row):
        """Generate AI feedback for post improvement"""
        feedback = []
        
        # Length feedback
        msg_len = len(message)
        if msg_len < 50:
            feedback.append("📝 Consider expanding your message for better engagement")
        elif msg_len > 300:
            feedback.append("✂️ Consider shortening your message for better readability")
        
        # Hashtag feedback
        if '#' not in message:
            feedback.append("🏷️ Add relevant hashtags to increase discoverability")
        
        # Media feedback
        if not row.get('ImageURL') and not row.get('VideoURL'):
            feedback.append("🖼️ Adding visual content can significantly boost engagement")
        
        # Scheduling feedback
        if not (row.get('Month(1-12)') and row.get('Day(1-31)') and row.get('Year')):
            feedback.append("📅 Schedule this post for optimal timing")
        
        # Engagement feedback
        if '?' not in message:
            feedback.append("❓ Consider adding a question to encourage engagement")
        
        return feedback
    
    def load_image_from_url(self, url):
        """Load image from URL with error handling"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except:
            return None
    
    def generate_ai_post(self, topic, platform, tone="professional", include_hashtags=True):
        """Generate AI-powered social media post"""
        try:
            client = openai.OpenAI()
            
            platform_info = self.platform_limits.get(platform, {'limit': 280, 'optimal': 100})
            char_limit = platform_info['optimal']
            
            prompt = f"""
            Create an engaging social media post about {topic} for {platform}.
            
            Requirements:
            - Tone: {tone}
            - Character limit: approximately {char_limit} characters
            - Include relevant emojis
            - Make it engaging and actionable
            - Include a call-to-action
            {'- Include 3-5 relevant hashtags' if include_hashtags else '- Do not include hashtags'}
            
            The post should be compelling, professional, and encourage engagement.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating AI post: {str(e)}"
    
    def suggest_hashtags(self, message, category=None):
        """AI-powered hashtag suggestions"""
        try:
            client = openai.OpenAI()
            
            prompt = f"""
            Based on this social media post: "{message}"
            {f"Category: {category}" if category else ""}
            
            Suggest 8-10 relevant hashtags that would help this post reach the right audience.
            Return only the hashtags, separated by spaces, starting with #.
            Focus on popular, relevant hashtags that aren't too generic.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "#socialmedia #content #marketing"

def show_enhanced_calendar_view(df):
    """Enhanced calendar view with better functionality"""
    st.header("📅 Enhanced Calendar View")
    
    # Calendar navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    # Initialize session state for calendar navigation
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = datetime.now().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = datetime.now().year
    
    with col1:
        if st.button("◀ Prev"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    
    with col2:
        if st.button("Today"):
            st.session_state.calendar_month = datetime.now().month
            st.session_state.calendar_year = datetime.now().year
            st.rerun()
    
    with col3:
        month_name = calendar.month_name[st.session_state.calendar_month]
        st.markdown(f"<h3 style='text-align: center; color: #3498db;'>{month_name} {st.session_state.calendar_year}</h3>", 
                   unsafe_allow_html=True)
    
    with col4:
        if st.button("Next ▶"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    
    with col5:
        view_type = st.selectbox("View", ["Month", "Week"], key="calendar_view_type")
    
    # Filter posts for the current month/year
    scheduled_posts = df[
        (df['Month(1-12)'].astype(str) == str(st.session_state.calendar_month)) &
        (df['Year'].astype(str) == str(st.session_state.calendar_year)) &
        (df['Month(1-12)'] != '') &
        (df['Day(1-31)'] != '') &
        (df['Year'] != '')
    ].copy()
    
    if view_type == "Month":
        show_month_calendar(scheduled_posts, st.session_state.calendar_month, st.session_state.calendar_year)
    else:
        show_week_calendar(scheduled_posts, st.session_state.calendar_month, st.session_state.calendar_year)

def show_month_calendar(posts_df, month, year):
    """Enhanced month calendar view"""
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    cal_matrix = cal.monthcalendar(year, month)
    
    # Group posts by day
    posts_by_day = {}
    if not posts_df.empty:
        for _, post in posts_df.iterrows():
            try:
                day = int(post['Day(1-31)'])
                if day not in posts_by_day:
                    posts_by_day[day] = []
                posts_by_day[day].append(post)
            except (ValueError, TypeError):
                continue
    
    # Calendar container
    st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
    
    # Day headers
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: #3498db; padding: 10px;'>{day[:3]}</div>", 
                       unsafe_allow_html=True)
    
    # Calendar weeks
    today = datetime.now()
    for week in cal_matrix:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
                else:
                    posts_today = posts_by_day.get(day, [])
                    is_today = (day == today.day and month == today.month and year == today.year)
                    
                    # Determine day styling
                    day_class = "calendar-day"
                    if posts_today:
                        day_class += " has-posts"
                    if is_today:
                        day_class += " today"
                    
                    # Create day content
                    day_html = f"""
                    <div class="{day_class}">
                        <div class="calendar-day-number">{day}</div>
                    """
                    
                    if posts_today:
                        day_html += f'<div class="calendar-post-indicator">{len(posts_today)} post{"s" if len(posts_today) > 1 else ""}</div>'
                        
                        # Show preview of first post
                        first_post = posts_today[0]
                        message_preview = first_post['Message'][:50] + "..." if len(first_post['Message']) > 50 else first_post['Message']
                        hour = first_post.get('Hour', '')
                        minute = int(first_post.get('Minute(0-59)', 0)) if first_post.get('Minute(0-59)', '') != '' else 0
                        
                        time_str = f"{hour}:{minute:02d}" if hour else "No time"
                        day_html += f'<div class="calendar-post-preview"><strong>{time_str}</strong><br>{message_preview}</div>'
                    
                    day_html += "</div>"
                    
                    st.markdown(day_html, unsafe_allow_html=True)
                    
                    # Show detailed posts in expander
                    if posts_today:
                        with st.expander(f"📅 {len(posts_today)} post{'s' if len(posts_today) > 1 else ''} on {calendar.month_name[month]} {day}"):
                            for post in posts_today:
                                hour = post.get('Hour', '')
                                minute = int(post.get('Minute(0-59)', 0)) if post.get('Minute(0-59)', '') != '' else 0
                                time_str = f"{hour}:{minute:02d}" if hour else "No time set"
                                
                                st.markdown(f"**⏰ {time_str}**")
                                st.write(post['Message'][:150] + "..." if len(post['Message']) > 150 else post['Message'])
                                
                                if post.get('Category'):
                                    st.markdown(f"🏷️ *{post['Category']}*")
                                
                                st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_week_calendar(posts_df, month, year):
    """Enhanced week calendar view"""
    st.subheader("📅 Week View")
    
    # Get current week
    today = datetime.now()
    if month == today.month and year == today.year:
        current_date = today
    else:
        current_date = datetime(year, month, 1)
    
    # Calculate week start (Monday)
    days_since_monday = current_date.weekday()
    week_start = current_date - timedelta(days=days_since_monday)
    
    # Generate week days
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    
    # Group posts by day
    posts_by_date = {}
    if not posts_df.empty:
        for _, post in posts_df.iterrows():
            try:
                post_day = int(post['Day(1-31)'])
                post_date = datetime(year, month, post_day)
                if post_date in week_days:
                    if post_date not in posts_by_date:
                        posts_by_date[post_date] = []
                    posts_by_date[post_date].append(post)
            except (ValueError, TypeError):
                continue
    
    # Display week
    for day_date in week_days:
        day_posts = posts_by_date.get(day_date, [])
        day_name = day_date.strftime("%A")
        day_num = day_date.strftime("%d")
        
        is_today = day_date.date() == today.date()
        
        # Day header
        header_style = "background: linear-gradient(135deg, #3498db, #2980b9); color: white;" if is_today else "background: #f8f9fa; color: #2c3e50;"
        
        st.markdown(f"""
        <div style="{header_style} padding: 12px; border-radius: 8px; margin: 8px 0;">
            <h4 style="margin: 0;">{day_name}, {day_num}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if day_posts:
            # Sort posts by time
            day_posts.sort(key=lambda x: (
                int(x.get('Hour', 0)) if x.get('Hour', '') != '' else 0,
                int(x.get('Minute(0-59)', 0)) if x.get('Minute(0-59)', '') != '' else 0
            ))
            
            for post in day_posts:
                hour = post.get('Hour', '')
                minute = int(post.get('Minute(0-59)', 0)) if post.get('Minute(0-59)', '') != '' else 0
                time_str = f"{hour}:{minute:02d}" if hour else "No time"
                
                st.markdown(f"""
                <div style="
                    background: white;
                    border-left: 4px solid #3498db;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="font-weight: bold; color: #3498db; margin-bottom: 8px;">⏰ {time_str}</div>
                    <div style="margin-bottom: 8px;">{post['Message'][:200]}{"..." if len(post['Message']) > 200 else ""}</div>
                    {f"<div style='font-size: 12px; color: #666;'>🏷️ {post['Category']}</div>" if post.get('Category') else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                border-radius: 8px;
                margin: 8px 0;
                border: 2px dashed #dee2e6;
            ">
                No posts scheduled for this day
            </div>
            """, unsafe_allow_html=True)

def show_posts_view(manager, df, client):
    """Enhanced posts view with better filtering and display"""
    st.header("📋 Manage Your Posts")
    
    # Enhanced filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        categories = ['All'] + list(df['Category'].dropna().unique())
        category_filter = st.selectbox("📂 Category", categories)
    
    with col2:
        status_filter = st.selectbox("📊 Status", ["All", "Scheduled", "Queued"])
    
    with col3:
        sort_options = ["Newest First", "Oldest First", "A-Z", "Z-A", "Longest", "Shortest"]
        sort_by = st.selectbox("🔄 Sort by", sort_options)
    
    with col4:
        search_term = st.text_input("🔍 Search", placeholder="Search in messages...")
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Message'].str.contains(search_term, case=False, na=False)
        ]
    
    if status_filter != "All":
        if status_filter == "Scheduled":
            filtered_df = filtered_df[
                (filtered_df['Month(1-12)'] != '') | 
                (filtered_df['Day(1-31)'] != '') | 
                (filtered_df['Year'] != '')
            ]
        else:  # Queued
            filtered_df = filtered_df[
                (filtered_df['Month(1-12)'] == '') & 
                (filtered_df['Day(1-31)'] == '') & 
                (filtered_df['Year'] == '')
            ]
    
    # Apply sorting
    if not filtered_df.empty:
        if sort_by == "Newest First":
            filtered_df = filtered_df.iloc[::-1]
        elif sort_by == "A-Z":
            filtered_df = filtered_df.sort_values('Message')
        elif sort_by == "Z-A":
            filtered_df = filtered_df.sort_values('Message', ascending=False)
        elif sort_by == "Longest":
            filtered_df['msg_len'] = filtered_df['Message'].str.len()
            filtered_df = filtered_df.sort_values('msg_len', ascending=False)
        elif sort_by == "Shortest":
            filtered_df['msg_len'] = filtered_df['Message'].str.len()
            filtered_df = filtered_df.sort_values('msg_len')
    
    # Results summary
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"📊 Showing **{len(filtered_df)}** of **{len(df)}** posts")
    
    with col2:
        view_mode = st.radio("View Mode", ["Cards", "Table"], horizontal=True)
    
    # Display posts
    if not filtered_df.empty:
        if view_mode == "Cards":
            # Enhanced card view
            for i in range(0, len(filtered_df), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    if i + j < len(filtered_df):
                        with col:
                            manager.display_enhanced_post_card(filtered_df.iloc[i + j], i + j)
        else:
            # Table view
            display_columns = ['Message', 'Category', 'Month(1-12)', 'Day(1-31)', 'Year', 'Hour']
            table_df = filtered_df[display_columns].copy()
            table_df['Message'] = table_df['Message'].str[:100] + '...'
            
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("🔍 No posts found matching your filters.")
    
    # Handle post actions
    handle_post_actions(manager, df, client)

def handle_post_actions(manager, df, client):
    """Handle various post actions"""
    # Handle editing
    if 'editing_post' in st.session_state:
        st.subheader("✏️ Edit Post")
        index = st.session_state.editing_post
        
        if index < len(df):
            post = df.iloc[index]
            
            with st.form("edit_post_form"):
                new_message = st.text_area("Message", value=post['Message'], height=100)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_category = st.text_input("Category", value=post.get('Category', ''))
                with col2:
                    new_link = st.text_input("Link", value=post.get('Link', ''))
                with col3:
                    new_image_url = st.text_input("Image URL", value=post.get('ImageURL', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        df.loc[index, 'Message'] = new_message
                        df.loc[index, 'Category'] = new_category
                        df.loc[index, 'Link'] = new_link
                        df.loc[index, 'ImageURL'] = new_image_url
                        
                        success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                        if success:
                            st.success("✅ Post updated successfully!")
                            del st.session_state.editing_post
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state.editing_post
                        st.rerun()
    
    # Handle deletion
    if 'delete_post' in st.session_state:
        index = st.session_state.delete_post
        
        if index < len(df):
            post = df.iloc[index]
            st.warning(f"🗑️ Are you sure you want to delete this post?")
            st.write(f"**Message:** {post['Message'][:100]}...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Yes, Delete"):
                    df.drop(index, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    
                    success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                    if success:
                        st.success("✅ Post deleted successfully!")
                        del st.session_state.delete_post
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            with col2:
                if st.button("❌ Cancel"):
                    del st.session_state.delete_post
                    st.rerun()

def main():
    """Main application function"""
    st.title("🚀 AI-Powered Social Media Manager Pro")
    st.markdown("*Streamline your social media workflow with AI-powered insights and automation*")
    
    # Initialize manager
    manager = EnhancedSocialMediaManager()
    
    # Sidebar for credentials and settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Google Sheets credentials
        st.subheader("🔐 Google Sheets Setup")
        uploaded_file = st.file_uploader(
            "Upload Service Account JSON",
            type=['json'],
            help="Upload your Google service account credentials file"
        )
        
        if uploaded_file:
            try:
                credentials_dict = json.load(uploaded_file)
                st.session_state.google_credentials = credentials_dict
                st.success("✅ Credentials loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading credentials: {str(e)}")
        
        # Sheet URL
        sheet_url = st.text_input(
            "📊 Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL here"
        )
        
        if sheet_url:
            st.session_state.sheet_url = sheet_url
    
    # Main content
    if 'google_credentials' in st.session_state and 'sheet_url' in st.session_state:
        # Setup Google Sheets connection
        client, error = manager.setup_google_sheets()
        
        if error:
            st.error(f"❌ {error}")
            return
        
        # Load data
        with st.spinner("📊 Loading your social media data..."):
            df = manager.get_sheet_data(client, st.session_state.sheet_url)
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Posts", "📅 Calendar", "➕ Create", "📊 Analytics", "🤖 AI Tools"
        ])
        
        with tab1:
            show_posts_view(manager, df, client)
        
        with tab2:
            show_enhanced_calendar_view(df)
        
        with tab3:
            st.header("➕ Create New Post")
            st.info("Post creation functionality would be implemented here")
        
        with tab4:
            st.header("📊 Analytics Dashboard")
            st.info("Analytics functionality would be implemented here")
        
        with tab5:
            st.header("🤖 AI Tools")
            st.info("AI tools functionality would be implemented here")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to AI-Powered Social Media Manager Pro!
        
        To get started:
        1. **Upload your Google service account credentials** in the sidebar
        2. **Paste your Google Sheets URL** 
        3. **Start managing your social media content!**
        
        ### ✨ Features:
        - 📋 **Smart Post Management** - View, edit, and organize your posts
        - 📅 **Enhanced Calendar View** - Visualize your content schedule
        - 🤖 **AI-Powered Insights** - Get performance scores and suggestions
        - 📊 **Analytics Dashboard** - Track your content performance
        - 🎯 **Multi-Platform Optimization** - Optimize for different social platforms
        """)

if __name__ == "__main__":
    main()


