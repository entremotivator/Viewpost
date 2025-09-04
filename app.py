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
    """Enhanced month calendar view with fixed calendar import"""
    cal_matrix = calendar.monthcalendar(year, month)  # Use module directly
    
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
    
    # Group posts by date
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
    
    # Handle duplication
    if 'duplicate_post' in st.session_state:
        index = st.session_state.duplicate_post
        
        if index < len(df):
            post = df.iloc[index].copy()
            post['Message'] = f"[COPY] {post['Message']}"
            
            # Add to dataframe
            new_df = pd.concat([df, pd.DataFrame([post])], ignore_index=True)
            
            success, message = manager.update_sheet(client, st.session_state.sheet_url, new_df)
            if success:
                st.success("✅ Post duplicated successfully!")
                del st.session_state.duplicate_post
                st.rerun()
            else:
                st.error(f"❌ {message}")

def show_create_post(manager, df, client):
    """Enhanced post creation with AI assistance"""
    st.header("➕ Create New Social Media Post")
    
    # Tabs for different creation methods
    tab1, tab2, tab3 = st.tabs(["✍️ Manual Creation", "🤖 AI Generation", "📝 From Template"])
    
    with tab1:
        show_manual_post_creation(manager, df, client)
    
    with tab2:
        show_ai_post_generation(manager, df, client)
    
    with tab3:
        show_template_post_creation(manager, df, client)

def show_manual_post_creation(manager, df, client):
    """Manual post creation form"""
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
    """Analytics dashboard with insights"""
    st.header("📊 Analytics Dashboard")
    
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
        manager = EnhancedSocialMediaManager()
        
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
    st.header("🤖 AI Tools & Utilities")
    
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
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Posts", "📅 Calendar", "➕ Create", "📊 Analytics", "🤖 AI Tools"
        ])
        
        with tab1:
            show_posts_view(manager, df, client)
        
        with tab2:
            show_enhanced_calendar_view(df)
        
        with tab3:
            show_create_post(manager, df, client)
        
        with tab4:
            show_analytics_dashboard(df)
        
        with tab5:
            show_ai_tools(manager, df, client)
    
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
        - ✍️ **AI Content Generation** - Create posts with AI assistance
        - 📝 **Template System** - Use pre-built templates for consistency
        - 🏷️ **Smart Hashtag Suggestions** - AI-powered hashtag recommendations
        
        ### 🚀 Getting Started:
        1. Create a Google Cloud Project
        2. Enable the Google Sheets API
        3. Create a service account and download credentials
        4. Create a Google Sheet for your posts
        5. Upload credentials and sheet URL in the sidebar
        
        **Ready to revolutionize your social media workflow?** 🎯
        """)

if __name__ == "__main__":
    main()

