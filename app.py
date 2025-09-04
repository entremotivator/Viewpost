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

# Enhanced CSS styling combining clean design with rich features
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
    
    .main-header {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Calendar styling */
    .calendar-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .calendar-day-button {
        width: 100%;
        min-height: 80px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        background: white;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 2px;
        padding: 8px;
    }
    
    .calendar-day-button:hover {
        border-color: #3498db;
        background: #f8f9fa;
        transform: translateY(-2px);
    }
    
    .calendar-day-with-posts {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-color: #3498db;
        border-width: 3px;
    }
    
    .calendar-day-today {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-color: #ff9800;
        border-width: 3px;
    }
    
    /* Clean post cards */
    .post-card-clean {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .post-card-clean:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .post-meta-info {
        color: #666;
        font-size: 12px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .post-content {
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 15px;
        color: var(--text-dark);
    }
    
    .status-badge-clean {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    
    .status-scheduled {
        background: #4caf50;
        color: white;
    }
    
    .status-queued {
        background: #ff9800;
        color: white;
    }
    
    .status-draft {
        background: #9e9e9e;
        color: white;
    }
    
    /* Enhanced post cards for rich view */
    .post-card-enhanced {
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
    
    .post-card-enhanced:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(52, 152, 219, 0.2);
    }
    
    .post-card-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-blue), var(--accent-blue));
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
    
    /* Edit form styling */
    .edit-form-container {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid #e0e0e0;
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
        .post-card-clean, .post-card-enhanced {
            padding: 16px;
            margin: 10px 0;
        }
        
        .calendar-day-button {
            min-height: 60px;
            padding: 6px;
        }
    }
</style>
""", unsafe_allow_html=True)

class UltimateSocialMediaManager:
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
    
    def analyze_post_performance(self, message):
        """Analyze post performance and provide feedback"""
        score = 0
        feedback = []
        
        # Length analysis
        msg_len = len(message)
        if 50 <= msg_len <= 200:
            score += 25
            feedback.append("✅ Perfect length for engagement")
        elif 20 <= msg_len <= 300:
            score += 15
            feedback.append("📏 Good length, could be optimized")
        else:
            score += 5
            feedback.append("⚠️ Length needs adjustment for better engagement")
        
        # Hashtag analysis
        hashtag_count = message.count('#')
        if 3 <= hashtag_count <= 7:
            score += 20
            feedback.append("✅ Good hashtag usage")
        elif hashtag_count > 0:
            score += 10
            feedback.append("📈 Consider optimizing hashtag count (3-7 recommended)")
        else:
            feedback.append("🏷️ Add hashtags to increase discoverability")
        
        # Emoji analysis
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        if emoji_pattern.search(message):
            score += 15
            feedback.append("✅ Great use of emojis for visual appeal")
        else:
            feedback.append("😊 Consider adding emojis for better engagement")
        
        # Call to action analysis
        cta_words = ['click', 'visit', 'learn', 'discover', 'try', 'get', 'download', 'sign up', 'join', 'follow', 'share', 'comment']
        if any(word in message.lower() for word in cta_words):
            score += 20
            feedback.append("✅ Strong call-to-action detected")
        else:
            feedback.append("📢 Add a call-to-action to drive engagement")
        
        # Question analysis
        if '?' in message:
            score += 10
            feedback.append("✅ Questions encourage engagement")
        else:
            feedback.append("❓ Consider adding a question to spark conversation")
        
        # Engagement words
        engagement_words = ['amazing', 'incredible', 'exciting', 'new', 'exclusive', 'limited', 'free', 'tips', 'secrets']
        if any(word in message.lower() for word in engagement_words):
            score += 10
            feedback.append("✅ Using engaging language")
        
        return min(score, 100), feedback
    
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
    
    def display_enhanced_post_card(self, row, index, view_mode="enhanced"):
        """Display post card with both clean and enhanced modes"""
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
        
        if view_mode == "clean":
            # Clean card display
            st.markdown('<div class="post-card-clean">', unsafe_allow_html=True)
            
            # Status badge
            st.markdown(f'<div class="status-badge-clean {status_class}">📅 {status}</div>', unsafe_allow_html=True)
            
            # Time info
            if status == "Scheduled":
                try:
                    time_str = f"{hour}:{minute:02d}" if hour else "No time set"
                    schedule_info = f"{month}/{day}/{year} at {time_str}"
                except:
                    schedule_info = f"{month}/{day}/{year} (time format error)"
                
                st.markdown(f'<div class="post-meta-info">⏰ {schedule_info}</div>', unsafe_allow_html=True)
            
            # Category
            category = self.safe_str_conversion(row.get('Category', ''))
            if category:
                st.markdown(f'<div class="post-meta-info">🏷️ {category}</div>', unsafe_allow_html=True)
            
            # Full message content
            st.markdown(f'<div class="post-content">{message}</div>', unsafe_allow_html=True)
            
            # Links and media
            link = self.safe_str_conversion(row.get('Link', ''))
            if link:
                st.markdown(f"🔗 [Link]({link})")
            
            image_url = self.safe_str_conversion(row.get('ImageURL', ''))
            if image_url:
                st.markdown(f"🖼️ [Image]({image_url})")
            
            video_url = self.safe_str_conversion(row.get('VideoURL', ''))
            if video_url:
                st.markdown(f"🎥 [Video]({video_url})")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Enhanced card display with AI features
            performance_score = self.calculate_performance_score(message, row)
            feedback = self.generate_ai_feedback(message, row)
            
            st.markdown('<div class="post-card-enhanced">', unsafe_allow_html=True)
            
            # Status and performance
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'<div class="status-badge-clean {status_class}">📅 {status}</div>', unsafe_allow_html=True)
            
            with col2:
                score_color = "#4caf50" if performance_score >= 80 else "#ff9800" if performance_score >= 60 else "#f44336"
                st.markdown(f"""
                <div style="text-align: center; background: {score_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;">
                    {performance_score}/100
                </div>
                """, unsafe_allow_html=True)
            
            # Message content
            st.markdown(f'<div class="post-content">{message[:200]}{"..." if len(message) > 200 else ""}</div>', unsafe_allow_html=True)
            
            # Scheduling info
            if status == "Scheduled":
                try:
                    time_str = f"{hour}:{minute:02d}" if hour else "No time set"
                    schedule_info = f"{month}/{day}/{year} at {time_str}"
                except:
                    schedule_info = f"{month}/{day}/{year} (time format error)"
                
                st.markdown(f'<div class="post-meta-info">📅 {schedule_info}</div>', unsafe_allow_html=True)
            
            # Category and links
            category = self.safe_str_conversion(row.get('Category', ''))
            if category:
                st.markdown(f'<div class="post-meta-info">🏷️ {category}</div>', unsafe_allow_html=True)
            
            link = self.safe_str_conversion(row.get('Link', ''))
            if link:
                st.markdown(f'<div class="post-meta-info">🔗 <a href="{link}" target="_blank">Link attached</a></div>', unsafe_allow_html=True)
            
            # Platform compatibility
            st.markdown('<div style="margin: 12px 0;">')
            for platform, info in self.platform_limits.items():
                char_count = len(message)
                if char_count <= info['limit']:
                    st.markdown(f'<span class="platform-indicator" style="background: {info["color"]};">{platform}</span>', unsafe_allow_html=True)
            st.markdown('</div>')
            
            # Character count analysis
            st.markdown('<div class="character-count">')
            for platform, info in list(self.platform_limits.items())[:4]:
                char_count = len(message)
                if char_count <= info['optimal']:
                    color_class = 'char-count-good'
                elif char_count <= info['limit']:
                    color_class = 'char-count-warning'
                else:
                    color_class = 'char-count-error'
                st.markdown(f'<div class="{color_class}">{platform}: {char_count}/{info["limit"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>')
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # AI Feedback
            if feedback:
                with st.expander("🤖 AI Performance Analysis"):
                    for item in feedback:
                        st.write(item)
            
            # Display media
            if image_url:
                image = self.load_image_from_url(image_url)
                if image:
                    st.image(image, caption="Post Image", use_column_width=True)
                else:
                    st.info(f"🖼️ Image URL: {image_url}")
            
            if video_url:
                if video_url.endswith('.mp4'):
                    try:
                        st.video(video_url)
                    except:
                        st.info(f"🎥 Video URL: {video_url}")
                else:
                    st.info(f"🎥 Video URL: {video_url}")

def show_calendar_view(manager, df, client):
    """Clean calendar view with clickable date buttons"""
    st.markdown('<div class="main-header"><h2>📅 Interactive Calendar</h2></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = datetime.now().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = datetime.now().year
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    
    # Navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("◀ Previous"):
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
        if st.button("📝 Edit Dates"):
            st.session_state.page = "edit_dates"
            st.rerun()
    
    # Filter posts for current month/year
    scheduled_posts = df[
        (df['Month(1-12)'].astype(str) == str(st.session_state.calendar_month)) &
        (df['Year'].astype(str) == str(st.session_state.calendar_year)) &
        (df['Month(1-12)'] != '') &
        (df['Day(1-31)'] != '') &
        (df['Year'] != '')
    ].copy()
    
    # Group posts by day
    posts_by_day = {}
    if not scheduled_posts.empty:
        for _, post in scheduled_posts.iterrows():
            try:
                day = int(post['Day(1-31)'])
                if day not in posts_by_day:
                    posts_by_day[day] = []
                posts_by_day[day].append(post)
            except (ValueError, TypeError):
                continue
    
    # Display calendar
    st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
    
    # Calendar grid
    cal_matrix = calendar.monthcalendar(st.session_state.calendar_year, st.session_state.calendar_month)
    
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
                    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
                else:
                    posts_today = posts_by_day.get(day, [])
                    is_today = (day == today.day and 
                               st.session_state.calendar_month == today.month and 
                               st.session_state.calendar_year == today.year)
                    
                    # Create clickable date button
                    button_key = f"date_{st.session_state.calendar_year}_{st.session_state.calendar_month}_{day}"
                    
                    if st.button(
                        f"{day}\n{len(posts_today)} post{'s' if len(posts_today) != 1 else ''}" if posts_today else str(day),
                        key=button_key,
                        help=f"Click to view posts for {calendar.month_name[st.session_state.calendar_month]} {day}"
                    ):
                        st.session_state.selected_date = {
                            'day': day,
                            'month': st.session_state.calendar_month,
                            'year': st.session_state.calendar_year,
                            'posts': posts_today
                        }
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show posts for selected date
    if st.session_state.selected_date:
        show_posts_for_date(manager, st.session_state.selected_date, df, client)

def show_posts_for_date(manager, date_info, df, client):
    """Show posts for selected date with full functionality"""
    day = date_info['day']
    month = date_info['month']
    year = date_info['year']
    posts = date_info['posts']
    
    st.markdown("---")
    st.markdown(f"### 📅 Posts for {calendar.month_name[month]} {day}, {year}")
    
    if not posts:
        st.info("No posts scheduled for this date.")
        return
    
    # Sort posts by time
    posts_sorted = sorted(posts, key=lambda x: (
        manager.safe_int_conversion(x.get('Hour', ''), 0),
        manager.safe_int_conversion(x.get('Minute(0-59)', ''), 0)
    ))
    
    # View mode toggle
    view_mode = st.radio("View Mode", ["Clean", "Enhanced"], horizontal=True, key="date_view_mode")
    
    for i, post in enumerate(posts_sorted):
        # Find the original index in the dataframe
        original_index = df[df['Message'] == post['Message']].index[0] if not df[df['Message'] == post['Message']].empty else i
        
        # Display post card
        if view_mode == "Clean":
            manager.display_enhanced_post_card(post, original_index, view_mode="clean")
        else:
            manager.display_enhanced_post_card(post, original_index, view_mode="enhanced")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit", key=f"edit_{original_index}"):
                st.session_state.editing_post = original_index
                st.rerun()
        
        with col2:
            if st.button("📅 Change Date", key=f"change_date_{original_index}"):
                st.session_state.editing_post_date = original_index
                st.session_state.page = "edit_dates"
                st.rerun()
        
        with col3:
            if st.button("📋 Duplicate", key=f"duplicate_{original_index}"):
                duplicate_post(manager, df, client, original_index)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{original_index}"):
                if st.button("Confirm Delete", key=f"confirm_delete_{original_index}"):
                    delete_post(manager, df, client, original_index)
        
        # Handle inline editing
        if 'editing_post' in st.session_state and st.session_state.editing_post == original_index:
            show_inline_edit_form(manager, df, client, original_index, post)

def show_inline_edit_form(manager, df, client, index, post):
    """Show inline editing form for a post"""
    st.markdown("---")
    st.markdown("### ✏️ Edit Post")
    
    with st.form(f"edit_form_{index}"):
        # Message
        new_message = st.text_area("Message", value=post['Message'], height=100)
        
        # Basic fields
        col1, col2 = st.columns(2)
        with col1:
            new_category = st.text_input("Category", value=post.get('Category', ''))
            new_link = st.text_input("Link", value=post.get('Link', ''))
        
        with col2:
            new_image_url = st.text_input("Image URL", value=post.get('ImageURL', ''))
            new_video_url = st.text_input("Video URL", value=post.get('VideoURL', ''))
        
        # Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes", type="primary"):
                # Update the dataframe
                df.loc[index, 'Message'] = new_message
                df.loc[index, 'Category'] = new_category
                df.loc[index, 'Link'] = new_link
                df.loc[index, 'ImageURL'] = new_image_url
                df.loc[index, 'VideoURL'] = new_video_url
                
                # Update Google Sheets
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

def show_edit_dates_page(manager, df, client):
    """Separate page for editing posting dates and times"""
    st.markdown('<div class="main-header"><h2>📅 Edit Posting Dates & Times</h2></div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Calendar"):
        st.session_state.page = "calendar"
        if 'editing_post_date' in st.session_state:
            del st.session_state.editing_post_date
        st.rerun()
    
    # Show all posts with date/time editing
    if df.empty:
        st.info("No posts available to edit.")
        return
    
    st.markdown("### All Posts - Click to Edit Date & Time")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_option = st.selectbox("Filter Posts", ["All Posts", "Scheduled Posts", "Unscheduled Posts"])
    
    with col2:
        search_term = st.text_input("Search in messages", placeholder="Type to search...")
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_option == "Scheduled Posts":
        filtered_df = filtered_df[
            (filtered_df['Month(1-12)'] != '') & 
            (filtered_df['Day(1-31)'] != '') & 
            (filtered_df['Year'] != '')
        ]
    elif filter_option == "Unscheduled Posts":
        filtered_df = filtered_df[
            (filtered_df['Month(1-12)'] == '') | 
            (filtered_df['Day(1-31)'] == '') | 
            (filtered_df['Year'] == '')
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Message'].str.contains(search_term, case=False, na=False)
        ]
    
    # Show posts
    for index, post in filtered_df.iterrows():
        st.markdown('<div class="post-card-clean">', unsafe_allow_html=True)
        
        # Post info
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Status
            month = manager.safe_str_conversion(post.get('Month(1-12)', ''))
            day = manager.safe_str_conversion(post.get('Day(1-31)', ''))
            year = manager.safe_str_conversion(post.get('Year', ''))
            hour = manager.safe_str_conversion(post.get('Hour', ''))
            minute = manager.safe_int_conversion(post.get('Minute(0-59)', ''), 0)
            
            if month and day and year:
                status = "Scheduled"
                status_class = "status-scheduled"
                time_str = f"{hour}:{minute:02d}" if hour else "No time"
                date_str = f"{month}/{day}/{year} at {time_str}"
            else:
                status = "Unscheduled"
                status_class = "status-queued"
                date_str = "Not scheduled"
            
            st.markdown(f'<div class="status-badge-clean {status_class}">{status}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="post-meta-info">📅 {date_str}</div>', unsafe_allow_html=True)
            
            # Message preview
            message = manager.safe_str_conversion(post.get('Message', ''), 'No message')
            preview = message[:100] + "..." if len(message) > 100 else message
            st.markdown(f'<div class="post-content">{preview}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("📅 Edit Date/Time", key=f"edit_date_{index}"):
                st.session_state.editing_post_date = index
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show edit form if this post is being edited
        if 'editing_post_date' in st.session_state and st.session_state.editing_post_date == index:
            show_date_edit_form(manager, df, client, index, post)

def show_date_edit_form(manager, df, client, index, post):
    """Show date and time editing form"""
    st.markdown('<div class="edit-form-container">', unsafe_allow_html=True)
    st.markdown(f"### 📅 Edit Date & Time for Post {index + 1}")
    
    # Show full message
    message = manager.safe_str_conversion(post.get('Message', ''), 'No message')
    st.markdown(f"**Post Message:** {message}")
    
    with st.form(f"date_edit_form_{index}"):
        st.markdown("#### Set Posting Date & Time")
        
        # Current values
        current_month = manager.safe_int_conversion(post.get('Month(1-12)', ''), 0)
        current_day = manager.safe_int_conversion(post.get('Day(1-31)', ''), 0)
        current_year = manager.safe_int_conversion(post.get('Year', ''), 0)
        current_hour = manager.safe_int_conversion(post.get('Hour', ''), 0)
        current_minute = manager.safe_int_conversion(post.get('Minute(0-59)', ''), 0)
        
        # Date inputs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_month = st.selectbox(
                "Month", 
                options=[0] + list(range(1, 13)),
                index=current_month if current_month <= 12 else 0,
                format_func=lambda x: "Not set" if x == 0 else calendar.month_name[x]
            )
        
        with col2:
            new_day = st.selectbox(
                "Day",
                options=[0] + list(range(1, 32)),
                index=current_day if current_day <= 31 else 0,
                format_func=lambda x: "Not set" if x == 0 else str(x)
            )
        
        with col3:
            current_year_actual = datetime.now().year
            year_options = [0] + list(range(current_year_actual, current_year_actual + 3))
            year_index = 0
            if current_year in year_options:
                year_index = year_options.index(current_year)
            
            new_year = st.selectbox(
                "Year",
                options=year_options,
                index=year_index,
                format_func=lambda x: "Not set" if x == 0 else str(x)
            )
        
        # Time inputs
        col1, col2 = st.columns(2)
        
        with col1:
            new_hour = st.selectbox(
                "Hour",
                options=list(range(0, 24)),
                index=current_hour if current_hour < 24 else 0,
                format_func=lambda x: f"{x:02d}:00"
            )
        
        with col2:
            new_minute = st.selectbox(
                "Minute",
                options=list(range(0, 60, 15)),
                index=min(current_minute // 15, 3) if current_minute < 60 else 0,
                format_func=lambda x: f":{x:02d}"
            )
        
        # Quick set buttons
        st.markdown("#### Quick Set Options")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.form_submit_button("📅 Set to Today"):
                today = datetime.now()
                new_month = today.month
                new_day = today.day
                new_year = today.year
                new_hour = 9  # Default to 9 AM
                new_minute = 0
        
        with col2:
            if st.form_submit_button("📅 Set to Tomorrow"):
                tomorrow = datetime.now() + timedelta(days=1)
                new_month = tomorrow.month
                new_day = tomorrow.day
                new_year = tomorrow.year
                new_hour = 9
                new_minute = 0
        
        with col3:
            if st.form_submit_button("🗑️ Clear Schedule"):
                new_month = 0
                new_day = 0
                new_year = 0
                new_hour = 0
                new_minute = 0
        
        # Submit buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Date & Time", type="primary"):
                # Update the dataframe
                df.loc[index, 'Month(1-12)'] = new_month if new_month > 0 else ''
                df.loc[index, 'Day(1-31)'] = new_day if new_day > 0 else ''
                df.loc[index, 'Year'] = new_year if new_year > 0 else ''
                df.loc[index, 'Hour'] = new_hour if new_month > 0 and new_day > 0 and new_year > 0 else ''
                df.loc[index, 'Minute(0-59)'] = new_minute if new_month > 0 and new_day > 0 and new_year > 0 else ''
                
                # Update Google Sheets
                success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                if success:
                    st.success("✅ Date and time updated successfully!")
                    del st.session_state.editing_post_date
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                del st.session_state.editing_post_date
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def duplicate_post(manager, df, client, index):
    """Duplicate a post"""
    if index < len(df):
        post = df.iloc[index].copy()
        post['Message'] = f"[COPY] {post['Message']}"
        
        # Clear scheduling to avoid conflicts
        post['Month(1-12)'] = ''
        post['Day(1-31)'] = ''
        post['Year'] = ''
        post['Hour'] = ''
        post['Minute(0-59)'] = ''
        
        # Add to dataframe
        new_df = pd.concat([df, pd.DataFrame([post])], ignore_index=True)
        
        success, message = manager.update_sheet(client, st.session_state.sheet_url, new_df)
        if success:
            st.success("✅ Post duplicated successfully!")
            st.rerun()
        else:
            st.error(f"❌ {message}")

def delete_post(manager, df, client, index):
    """Delete a post"""
    if index < len(df):
        df.drop(index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
        if success:
            st.success("✅ Post deleted successfully!")
            st.rerun()
        else:
            st.error(f"❌ {message}")

def show_posts_list(manager, df, client):
    """Show all posts in a clean list format with enhanced features"""
    st.markdown('<div class="main-header"><h2>📋 All Posts</h2></div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("No posts available. Create some posts first!")
        return
    
    # Filters and view options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        categories = ['All'] + list(df['Category'].dropna().unique())
        category_filter = st.selectbox("Filter by Category", categories)
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Unscheduled"])
    
    with col3:
        sort_options = ["Newest First", "Oldest First", "A-Z", "Z-A", "Longest", "Shortest"]
        sort_by = st.selectbox("Sort by", sort_options)
    
    with col4:
        view_mode = st.selectbox("View Mode", ["Clean", "Enhanced"])
    
    # Search
    search_term = st.text_input("🔍 Search", placeholder="Search in messages...")
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    if status_filter == "Scheduled":
        filtered_df = filtered_df[
            (filtered_df['Month(1-12)'] != '') & 
            (filtered_df['Day(1-31)'] != '') & 
            (filtered_df['Year'] != '')
        ]
    elif status_filter == "Unscheduled":
        filtered_df = filtered_df[
            (filtered_df['Month(1-12)'] == '') | 
            (filtered_df['Day(1-31)'] == '') | 
            (filtered_df['Year'] == '')
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Message'].str.contains(search_term, case=False, na=False)
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
    
    st.write(f"Showing {len(filtered_df)} of {len(df)} posts")
    
    # Display posts
    for index, post in filtered_df.iterrows():
        # Display post card based on view mode
        if view_mode == "Clean":
            manager.display_enhanced_post_card(post, index, view_mode="clean")
        else:
            manager.display_enhanced_post_card(post, index, view_mode="enhanced")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit", key=f"edit_list_{index}"):
                st.session_state.editing_post = index
                st.rerun()
        
        with col2:
            if st.button("📅 Schedule", key=f"schedule_list_{index}"):
                st.session_state.editing_post_date = index
                st.session_state.page = "edit_dates"
                st.rerun()
        
        with col3:
            if st.button("📋 Duplicate", key=f"duplicate_list_{index}"):
                duplicate_post(manager, df, client, index)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_list_{index}"):
                if st.button("Confirm", key=f"confirm_list_{index}"):
                    delete_post(manager, df, client, index)

def show_create_post(manager, df, client):
    """Enhanced post creation with AI assistance"""
    st.markdown('<div class="main-header"><h2>➕ Create New Social Media Post</h2></div>', unsafe_allow_html=True)
    
    # Tabs for different creation methods
    tab1, tab2, tab3 = st.tabs(["✍️ Manual Creation", "🤖 AI Generation", "📝 From Template"])
    
    with tab1:
        show_manual_post_creation(manager, df, client)
    
    with tab2:
        show_ai_post_generation(manager, df, client)
    
    with tab3:
        show_template_post_creation(manager, df, client)

def show_manual_post_creation(manager, df, client):
    """Manual post creation form with real-time analysis"""
    with st.form("manual_post_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Post Content")
            
            message = st.text_area(
                "Message *",
                height=120,
                help="Your social media post content",
                placeholder="Write your engaging social media post here..."
            )
            
            # Real-time character count and platform compatibility
            if message:
                st.markdown("**Platform Compatibility:**")
                platform_cols = st.columns(4)
                
                for idx, (platform, info) in enumerate(list(manager.platform_limits.items())[:4]):
                    with platform_cols[idx]:
                        char_count = len(message)
                        if char_count <= info['optimal']:
                            color = "#4caf50"
                            status = "✅ Optimal"
                        elif char_count <= info['limit']:
                            color = "#ff9800"
                            status = "⚠️ Long"
                        else:
                            color = "#f44336"
                            status = "❌ Too Long"
                        
                        st.markdown(f"""
                        <div style="text-align: center; padding: 8px; border-radius: 8px; background: {color}20; border: 1px solid {color};">
                            <div style="font-size: 12px; font-weight: bold; color: {color};">{platform}</div>
                            <div style="font-size: 11px; color: {color};">{char_count}/{info['limit']}</div>
                            <div style="font-size: 10px; color: {color};">{status}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # AI Performance Analysis
                if len(message) > 10:
                    score, feedback = manager.analyze_post_performance(message)
                    
                    st.markdown("**🤖 AI Performance Analysis:**")
                    score_color = "#4caf50" if score >= 80 else "#ff9800" if score >= 60 else "#f44336"
                    
                    st.markdown(f"""
                    <div style="background: {score_color}20; border: 1px solid {score_color}; border-radius: 8px; padding: 12px; margin: 8px 0;">
                        <div style="font-weight: bold; color: {score_color};">Performance Score: {score}/100</div>
                        <div style="font-size: 12px; margin-top: 4px;">
                            {'🎉 Excellent!' if score >= 80 else '👍 Good!' if score >= 60 else '💡 Needs improvement'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📋 Detailed Feedback"):
                        for item in feedback:
                            st.write(item)
            
            # AI Hashtag Suggestions
            if message and len(message) > 20:
                if st.button("🏷️ Get AI Hashtag Suggestions"):
                    with st.spinner("Generating hashtags..."):
                        suggested_hashtags = manager.suggest_hashtags(message)
                        st.success(f"Suggested hashtags: {suggested_hashtags}")
            
            # Additional content fields
            st.subheader("🔗 Additional Content")
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                link = st.text_input("🔗 Link", placeholder="https://example.com")
                image_url = st.text_input("🖼️ Image URL", placeholder="https://example.com/image.jpg")
            
            with col1_2:
                video_url = st.text_input("🎥 Video URL", placeholder="https://example.com/video.mp4")
                category = st.selectbox(
                    "📂 Category",
                    [""] + ["AI Consulting", "Business", "Technology", "Marketing", "Education", "Lifestyle", "Other"]
                )
        
        with col2:
            st.subheader("📅 Scheduling")
            
            schedule_now = st.checkbox("Schedule this post", value=False)
            
            if schedule_now:
                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    month = st.selectbox("Month", [""] + list(range(1, 13)))
                    day = st.selectbox("Day", [""] + list(range(1, 32)))
                
                with col2_2:
                    year = st.selectbox("Year", [""] + list(range(2024, 2030)))
                    hour = st.selectbox("Hour", [""] + list(range(0, 24)))
                
                minute = st.selectbox("Minute", list(range(0, 60, 15)))
            else:
                month = day = year = hour = minute = ""
            
            st.subheader("🏷️ Metadata")
            
            pin_title = st.text_input("📌 Pin Title", placeholder="Title for Pinterest")
            watermark = st.text_input("💧 Watermark", placeholder="Watermark text")
            hashtag_group = st.selectbox(
                "🏷️ Hashtag Group",
                [""] + list(manager.hashtag_groups.keys())
            )
            
            cta_group = st.text_input("📢 CTA Group", placeholder="Call-to-action group")
            first_comment = st.text_area("💬 First Comment", placeholder="Auto-comment text")
            
            col2_3, col2_4 = st.columns(2)
            with col2_3:
                story = st.selectbox("📱 Story Post?", ["N", "Y"])
            
            with col2_4:
                pinterest_board = st.text_input("📌 Pinterest Board")
            
            alt_text = st.text_area("♿ Alt Text", placeholder="Image description for accessibility")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create Post", type="primary", use_container_width=True)
        
        if submitted and message:
            # Create new post
            new_row = {
                'Message': message,
                'Link': link,
                'ImageURL': image_url,
                'VideoURL': video_url,
                'Month(1-12)': month,
                'Day(1-31)': day,
                'Year': year,
                'Hour': hour,
                'Minute(0-59)': minute,
                'PinTitle': pin_title,
                'Category': category,
                'Watermark': watermark,
                'HashtagGroup': hashtag_group,
                'VideoThumbnailURL': '',
                'CTAGroup': cta_group,
                'FirstComment': first_comment,
                'Story(YorN)': story,
                'PinterestBoard': pinterest_board,
                'AltText': alt_text
            }
            
            # Add to dataframe
            new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Update Google Sheets
            success, message_result = manager.update_sheet(client, st.session_state.sheet_url, new_df)
            
            if success:
                st.success("✅ Post created successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Error: {message_result}")
        elif submitted:
            st.error("❌ Please enter a message for your post")

def show_ai_post_generation(manager, df, client):
    """AI-powered post generation"""
    st.subheader("🤖 AI Post Generation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "📝 Topic or Theme",
            placeholder="e.g., AI in healthcare, productivity tips, startup advice"
        )
        
        platform = st.selectbox(
            "📱 Target Platform",
            list(manager.platform_limits.keys())
        )
        
        tone = st.selectbox(
            "🎭 Tone",
            ["Professional", "Casual", "Enthusiastic", "Educational", "Inspirational", "Humorous"]
        )
        
        include_hashtags = st.checkbox("Include hashtags", value=True)
        
        if st.button("🚀 Generate AI Post", type="primary"):
            if topic:
                with st.spinner("🤖 AI is crafting your post..."):
                    generated_post = manager.generate_ai_post(
                        topic, platform, tone.lower(), include_hashtags
                    )
                    
                    st.session_state.generated_post = generated_post
                    st.success("✅ Post generated successfully!")
            else:
                st.error("❌ Please enter a topic")
    
    with col2:
        st.markdown("**💡 AI Generation Tips:**")
        st.markdown("""
        - Be specific with your topic
        - Choose the right platform for optimal length
        - Professional tone works best for B2B
        - Casual tone engages better on Instagram
        - Include relevant keywords in your topic
        """)
    
    # Display generated post
    if 'generated_post' in st.session_state:
        st.markdown("---")
        st.subheader("📝 Generated Post")
        
        generated_content = st.text_area(
            "Edit if needed:",
            value=st.session_state.generated_post,
            height=150
        )
        
        # Performance analysis
        if generated_content:
            score, feedback = manager.analyze_post_performance(generated_content)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**🤖 AI Performance Analysis:**")
                for item in feedback[:3]:  # Show top 3 feedback items
                    st.write(item)
            
            with col2:
                score_color = "#4caf50" if score >= 80 else "#ff9800" if score >= 60 else "#f44336"
                st.markdown(f"""
                <div style="text-align: center; background: {score_color}20; border: 1px solid {score_color}; border-radius: 8px; padding: 16px;">
                    <div style="font-size: 24px; font-weight: bold; color: {score_color};">{score}/100</div>
                    <div style="font-size: 12px; color: {score_color};">Performance Score</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick save options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save as Draft"):
                # Create new post with generated content
                new_row = {
                    'Message': generated_content,
                    'Link': '',
                    'ImageURL': '',
                    'VideoURL': '',
                    'Month(1-12)': '',
                    'Day(1-31)': '',
                    'Year': '',
                    'Hour': '',
                    'Minute(0-59)': '',
                    'PinTitle': '',
                    'Category': 'AI Generated',
                    'Watermark': '',
                    'HashtagGroup': '',
                    'VideoThumbnailURL': '',
                    'CTAGroup': '',
                    'FirstComment': '',
                    'Story(YorN)': 'N',
                    'PinterestBoard': '',
                    'AltText': ''
                }
                
                # Add to dataframe
                new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Update Google Sheets
                success, message_result = manager.update_sheet(client, st.session_state.sheet_url, new_df)
                
                if success:
                    st.success("✅ Post saved as draft!")
                    del st.session_state.generated_post
                    st.rerun()
                else:
                    st.error(f"❌ Error: {message_result}")
        
        with col2:
            if st.button("📅 Schedule Post"):
                st.info("Use the Manual Creation tab to schedule this post with specific timing!")
        
        with col3:
            if st.button("🔄 Generate Another"):
                if 'generated_post' in st.session_state:
                    del st.session_state.generated_post
                st.rerun()

def show_template_post_creation(manager, df, client):
    """Template-based post creation"""
    st.subheader("📝 Create from Template")
    
    # Template selection
    template_name = st.selectbox(
        "Choose Template",
        list(manager.post_templates.keys())
    )
    
    if template_name:
        template = manager.post_templates[template_name]
        
        st.markdown(f"**Template Preview:** {template['template']}")
        
        # Variable inputs
        st.subheader("Fill in the details:")
        
        variables = {}
        cols = st.columns(2)
        
        for i, var in enumerate(template['variables']):
            with cols[i % 2]:
                variables[var] = st.text_input(
                    f"{var.replace('_', ' ').title()}:",
                    key=f"template_var_{var}"
                )
        
        # Generate preview
        if all(variables.values()):
            try:
                preview_post = template['template'].format(**variables)
                
                st.subheader("📋 Preview:")
                st.markdown(f"""
                <div style="background: #f8f9fa; border-radius: 8px; padding: 16px; border-left: 4px solid #3498db;">
                    {preview_post}
                </div>
                """, unsafe_allow_html=True)
                
                # Performance analysis
                score, feedback = manager.analyze_post_performance(preview_post)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    with st.expander("🤖 Performance Analysis"):
                        for item in feedback:
                            st.write(item)
                
                with col2:
                    score_color = "#4caf50" if score >= 80 else "#ff9800" if score >= 60 else "#f44336"
                    st.markdown(f"""
                    <div style="text-align: center; background: {score_color}20; border: 1px solid {score_color}; border-radius: 8px; padding: 12px;">
                        <div style="font-size: 20px; font-weight: bold; color: {score_color};">{score}/100</div>
                        <div style="font-size: 11px; color: {score_color};">Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("✅ Use This Post", type="primary"):
                    # Create new post with template content
                    new_row = {
                        'Message': preview_post,
                        'Link': '',
                        'ImageURL': '',
                        'VideoURL': '',
                        'Month(1-12)': '',
                        'Day(1-31)': '',
                        'Year': '',
                        'Hour': '',
                        'Minute(0-59)': '',
                        'PinTitle': '',
                        'Category': f'Template: {template_name}',
                        'Watermark': '',
                        'HashtagGroup': '',
                        'VideoThumbnailURL': '',
                        'CTAGroup': '',
                        'FirstComment': '',
                        'Story(YorN)': 'N',
                        'PinterestBoard': '',
                        'AltText': ''
                    }
                    
                    # Add to dataframe
                    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Update Google Sheets
                    success, message_result = manager.update_sheet(client, st.session_state.sheet_url, new_df)
                    
                    if success:
                        st.success("✅ Template post created successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {message_result}")
            
            except KeyError as e:
                st.error(f"Missing variable: {e}")

def show_analytics_dashboard(df):
    """Analytics dashboard with comprehensive insights"""
    st.markdown('<div class="main-header"><h2>📊 Analytics Dashboard</h2></div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("📈 No data available for analytics. Create some posts first!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_posts = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_posts}</div>
            <div class="metric-label">Total Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        scheduled_posts = len(df[(df['Month(1-12)'] != '') & (df['Day(1-31)'] != '') & (df['Year'] != '')])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{scheduled_posts}</div>
            <div class="metric-label">Scheduled Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_length = int(df['Message'].str.len().mean()) if not df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_length}</div>
            <div class="metric-label">Avg. Length</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        posts_with_media = len(df[(df['ImageURL'] != '') | (df['VideoURL'] != '')])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{posts_with_media}</div>
            <div class="metric-label">With Media</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Posts by Category")
        if not df['Category'].empty:
            category_counts = df['Category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Distribution of Posts by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    with col2:
        st.subheader("📏 Message Length Distribution")
        df['message_length'] = df['Message'].str.len()
        fig = px.histogram(
            df,
            x='message_length',
            title="Distribution of Message Lengths",
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance analysis
    st.subheader("🎯 Performance Analysis")
    
    if not df.empty:
        manager = UltimateSocialMediaManager()
        
        # Calculate performance scores for all posts
        performance_scores = []
        for _, row in df.iterrows():
            score = manager.calculate_performance_score(row['Message'], row)
            performance_scores.append(score)
        
        df['performance_score'] = performance_scores
        
        # Performance distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df,
                x='performance_score',
                title="Performance Score Distribution",
                nbins=10
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top performing posts
            st.markdown("**🏆 Top Performing Posts:**")
            top_posts = df.nlargest(5, 'performance_score')[['Message', 'performance_score']]
            for _, post in top_posts.iterrows():
                st.markdown(f"**Score: {post['performance_score']}/100**")
                st.write(f"{post['Message'][:100]}...")
                st.markdown("---")

def show_ai_tools(manager, df, client):
    """AI tools and utilities"""
    st.markdown('<div class="main-header"><h2>🤖 AI Tools & Utilities</h2></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Post Optimizer", "🏷️ Hashtag Generator", "📊 Content Analyzer", "🔮 Trend Predictor"])
    
    with tab1:
        st.subheader("🎯 AI Post Optimizer")
        
        if not df.empty:
            post_to_optimize = st.selectbox(
                "Select post to optimize:",
                range(len(df)),
                format_func=lambda x: f"Post {x+1}: {df.iloc[x]['Message'][:50]}..."
            )
            
            if st.button("🚀 Optimize Post"):
                original_post = df.iloc[post_to_optimize]['Message']
                
                with st.spinner("🤖 AI is optimizing your post..."):
                    # Simulate AI optimization
                    optimized_post = manager.generate_ai_post(
                        f"Optimize this post: {original_post}",
                        "Instagram",
                        "professional"
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Original Post:**")
                    st.text_area("", value=original_post, height=150, disabled=True)
                    
                    orig_score, orig_feedback = manager.analyze_post_performance(original_post)
                    st.markdown(f"**Score: {orig_score}/100**")
                
                with col2:
                    st.markdown("**Optimized Post:**")
                    st.text_area("", value=optimized_post, height=150, disabled=True)
                    
                    opt_score, opt_feedback = manager.analyze_post_performance(optimized_post)
                    st.markdown(f"**Score: {opt_score}/100**")
                
                improvement = opt_score - orig_score
                if improvement > 0:
                    st.success(f"🎉 Improvement: +{improvement} points!")
                else:
                    st.info("💡 Consider manual adjustments for better results")
        else:
            st.info("Create some posts first to use the optimizer!")
    
    with tab2:
        st.subheader("🏷️ Smart Hashtag Generator")
        
        hashtag_input = st.text_area(
            "Enter your post content:",
            placeholder="Paste your post content here to get relevant hashtag suggestions..."
        )
        
        category = st.selectbox(
            "Content Category (optional):",
            [""] + list(manager.hashtag_groups.keys())
        )
        
        if st.button("🏷️ Generate Hashtags") and hashtag_input:
            with st.spinner("🤖 Generating relevant hashtags..."):
                suggested_hashtags = manager.suggest_hashtags(hashtag_input, category)
            
            st.success("✅ Hashtag suggestions generated!")
            st.code(suggested_hashtags)
            
            # Show category-specific hashtags
            if category and category in manager.hashtag_groups:
                st.markdown(f"**{category} Hashtags:**")
                st.code(" ".join(manager.hashtag_groups[category]))
    
    with tab3:
        st.subheader("📊 Content Performance Analyzer")
        
        if not df.empty:
            st.markdown("**Analyze all your posts:**")
            
            # Performance analysis for all posts
            performance_data = []
            for idx, row in df.iterrows():
                score, feedback = manager.analyze_post_performance(row['Message'])
                performance_data.append({
                    'Post': f"Post {idx+1}",
                    'Score': score,
                    'Length': len(row['Message']),
                    'Has_Hashtags': '#' in row['Message'],
                    'Has_Media': bool(row.get('ImageURL') or row.get('VideoURL')),
                    'Category': row.get('Category', 'Uncategorized')
                })
            
            perf_df = pd.DataFrame(performance_data)
            
            # Display analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Performance by Category:**")
                if not perf_df.empty:
                    category_performance = perf_df.groupby('Category')['Score'].mean().sort_values(ascending=False)
                    st.bar_chart(category_performance)
            
            with col2:
                st.markdown("**Top Recommendations:**")
                low_performers = perf_df[perf_df['Score'] < 60]
                if not low_performers.empty:
                    st.write(f"📈 {len(low_performers)} posts could be improved")
                    st.write(f"💡 Average score: {perf_df['Score'].mean():.1f}/100")
                    
                    if perf_df['Has_Hashtags'].sum() < len(perf_df) * 0.8:
                        st.write("🏷️ Add more hashtags to posts")
                    
                    if perf_df['Has_Media'].sum() < len(perf_df) * 0.5:
                        st.write("🖼️ Add more visual content")
                else:
                    st.success("🎉 All posts are performing well!")
        else:
            st.info("Create some posts first to analyze performance!")
    
    with tab4:
        st.subheader("🔮 Trend Predictor")
        
        st.markdown("""
        **Coming Soon!** 
        
        This feature will analyze your content patterns and predict:
        - 📈 Best posting times
        - 🎯 Trending topics in your niche
        - 📊 Content performance predictions
        - 🚀 Growth opportunities
        
        Stay tuned for updates!
        """)
        
        # Placeholder for trend analysis
        if not df.empty:
            st.markdown("**Current Trends in Your Content:**")
            
            # Word frequency analysis
            all_text = ' '.join(df['Message'].fillna(''))
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_freq = Counter(words)
            
            # Remove common words
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'a', 'an', 'this', 'that', 'these', 'those'}
            filtered_freq = {word: count for word, count in word_freq.items() if word not in common_words and len(word) > 3}
            
            if filtered_freq:
                top_words = dict(sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[:10])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Most Used Words:**")
                    for word, count in top_words.items():
                        st.write(f"• {word}: {count} times")
                
                with col2:
                    fig = px.bar(
                        x=list(top_words.values()),
                        y=list(top_words.keys()),
                        orientation='h',
                        title="Word Frequency"
                    )
                    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    st.title("🚀 Ultimate AI-Powered Social Media Manager")
    st.markdown("*The complete solution for social media content management with AI insights*")
    
    # Initialize manager
    manager = UltimateSocialMediaManager()
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "calendar"
    
    # Sidebar for credentials and navigation
    with st.sidebar:
        st.header("⚙️ Setup")
        
        # Google Sheets credentials
        uploaded_file = st.file_uploader(
            "Upload Service Account JSON",
            type=['json'],
            help="Upload your Google service account credentials file"
        )
        
        if uploaded_file:
            try:
                credentials_dict = json.load(uploaded_file)
                st.session_state.google_credentials = credentials_dict
                st.success("✅ Credentials loaded!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        # Sheet URL
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL here"
        )
        
        if sheet_url:
            st.session_state.sheet_url = sheet_url
        
        # Navigation
        st.markdown("---")
        st.header("📍 Navigation")
        
        if st.button("📅 Calendar View", use_container_width=True):
            st.session_state.page = "calendar"
            st.rerun()
        
        if st.button("📋 All Posts", use_container_width=True):
            st.session_state.page = "posts"
            st.rerun()
        
        if st.button("➕ Create Post", use_container_width=True):
            st.session_state.page = "create"
            st.rerun()
        
        if st.button("📅 Edit Dates", use_container_width=True):
            st.session_state.page = "edit_dates"
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
        
        if st.button("🤖 AI Tools", use_container_width=True):
            st.session_state.page = "ai_tools"
            st.rerun()
        
        # Quick stats
        if 'google_credentials' in st.session_state and 'sheet_url' in st.session_state:
            st.markdown("---")
            st.subheader("📈 Quick Stats")
            
            # Try to load data for stats
            try:
                client, error = manager.setup_google_sheets()
                if not error:
                    df = manager.get_sheet_data(client, st.session_state.sheet_url)
                    
                    if not df.empty:
                        st.metric("Total Posts", len(df))
                        scheduled = len(df[(df['Month(1-12)'] != '') & (df['Day(1-31)'] != '') & (df['Year'] != '')])
                        st.metric("Scheduled", scheduled)
                        
                        if df['Category'].notna().any():
                            top_category = df['Category'].value_counts().index[0] if not df['Category'].value_counts().empty else "None"
                            st.metric("Top Category", top_category)
            except:
                pass  # Silently fail for sidebar stats
    
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
        
        # Show appropriate page
        if st.session_state.page == "calendar":
            show_calendar_view(manager, df, client)
        elif st.session_state.page == "posts":
            show_posts_list(manager, df, client)
        elif st.session_state.page == "create":
            show_create_post(manager, df, client)
        elif st.session_state.page == "edit_dates":
            show_edit_dates_page(manager, df, client)
        elif st.session_state.page == "analytics":
            show_analytics_dashboard(df)
        elif st.session_state.page == "ai_tools":
            show_ai_tools(manager, df, client)
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to the Ultimate AI-Powered Social Media Manager!
        
        **Get started in 3 easy steps:**
        
        1. **📁 Upload Credentials** - Upload your Google service account JSON file
        2. **🔗 Add Sheet URL** - Paste your Google Sheets URL
        3. **🚀 Start Managing** - Begin organizing your social media content!
        
        ### ✨ Complete Feature Set:
        
        #### 📅 **Calendar Management**
        - Interactive calendar with clickable date buttons
        - Clean post display without HTML clutter
        - Full post content viewing
        - Separate date editing page
        
        #### 🤖 **AI-Powered Features**
        - AI post generation with custom topics and tones
        - Smart hashtag suggestions
        - Performance scoring and feedback
        - Content optimization recommendations
        - Template-based post creation
        
        #### 📊 **Analytics & Insights**
        - Comprehensive analytics dashboard
        - Performance tracking and scoring
        - Content analysis and recommendations
        - Platform compatibility checking
        - Character count optimization
        
        #### 🎯 **Advanced Tools**
        - Post optimizer with AI suggestions
        - Hashtag generator
        - Content analyzer
        - Trend predictor (coming soon)
        - Multi-platform optimization
        
        #### 📱 **User Experience**
        - Clean, modern interface
        - Mobile-responsive design
        - Real-time performance analysis
        - Inline editing capabilities
        - Bulk operations support
        
        **Ready to revolutionize your social media workflow?** Upload your credentials to begin! 🎯
        """)

if __name__ == "__main__":
    main()

