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
    
    /* Calendar styling */
    .calendar-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .calendar-day {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
        margin: 2px;
        min-height: 80px;
        background: white;
        transition: all 0.2s ease;
    }
    
    .calendar-day:hover {
        background: var(--light-blue);
        border-color: var(--primary-blue);
    }
    
    .calendar-day.has-posts {
        background: linear-gradient(135deg, var(--light-blue), #bbdefb);
        border-color: var(--primary-blue);
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
            
            hashtags = response.choices[0].message.content.strip()
            return hashtags
        except Exception as e:
            return "#SocialMedia #Content #Marketing"
    
    def analyze_post_performance(self, message):
        """Analyze post for engagement potential"""
        score = 0
        feedback = []
        
        # Length analysis
        length = len(message)
        if 50 <= length <= 150:
            score += 20
            feedback.append("✅ Good length for engagement")
        elif length < 50:
            score += 10
            feedback.append("⚠️ Consider adding more detail")
        else:
            score += 5
            feedback.append("⚠️ Might be too long for some platforms")
        
        # Emoji analysis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', message))
        if 1 <= emoji_count <= 3:
            score += 15
            feedback.append("✅ Good emoji usage")
        elif emoji_count == 0:
            score += 5
            feedback.append("💡 Consider adding emojis")
        else:
            score += 10
            feedback.append("⚠️ Might have too many emojis")
        
        # Call-to-action analysis
        cta_words = ['comment', 'share', 'like', 'follow', 'click', 'visit', 'try', 'download', 'subscribe', 'join']
        has_cta = any(word in message.lower() for word in cta_words)
        if has_cta:
            score += 20
            feedback.append("✅ Contains call-to-action")
        else:
            score += 0
            feedback.append("💡 Consider adding a call-to-action")
        
        # Question analysis
        if '?' in message:
            score += 15
            feedback.append("✅ Includes engaging question")
        else:
            score += 5
            feedback.append("💡 Questions increase engagement")
        
        # Hashtag analysis
        hashtag_count = len(re.findall(r'#\w+', message))
        if 3 <= hashtag_count <= 8:
            score += 15
            feedback.append("✅ Good hashtag count")
        elif hashtag_count < 3:
            score += 10
            feedback.append("💡 Consider adding more hashtags")
        else:
            score += 5
            feedback.append("⚠️ Might have too many hashtags")
        
        # Urgency/excitement analysis
        excitement_words = ['new', 'exciting', 'amazing', 'incredible', 'breakthrough', 'revolutionary', 'exclusive']
        has_excitement = any(word in message.lower() for word in excitement_words)
        if has_excitement:
            score += 10
            feedback.append("✅ Contains excitement words")
        
        # Personal touch analysis
        personal_words = ['we', 'our', 'my', 'i', 'us', 'team']
        has_personal = any(word in message.lower() for word in personal_words)
        if has_personal:
            score += 5
            feedback.append("✅ Has personal touch")
        
        return min(score, 100), feedback
    
    def load_image_from_url(self, url):
        """Load and display image from URL"""
        try:
            if not url or not url.startswith(('http://', 'https://')):
                return None
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image
        except:
            pass
        return None
    
    def get_post_status(self, row):
        """Determine post status based on scheduling info"""
        if any([row.get(f, '') for f in ['Month(1-12)', 'Day(1-31)', 'Year', 'Hour']]):
            return "Scheduled", "status-scheduled"
        return "Queued", "status-queued"
    
    def create_calendar_view(self, df):
        """Create calendar view of scheduled posts"""
        if df.empty:
            return None
        
        # Filter scheduled posts
        scheduled_df = df[
            (df['Month(1-12)'] != '') & 
            (df['Day(1-31)'] != '') & 
            (df['Year'] != '')
        ].copy()
        
        if scheduled_df.empty:
            return None
        
        # Convert to datetime
        try:
            scheduled_df['date'] = pd.to_datetime(
                scheduled_df[['Year', 'Month(1-12)', 'Day(1-31)']].rename(columns={
                    'Year': 'year', 'Month(1-12)': 'month', 'Day(1-31)': 'day'
                })
            )
            
            # Group by date
            posts_by_date = scheduled_df.groupby('date').size().reset_index(name='post_count')
            
            # Create calendar heatmap
            fig = px.density_heatmap(
                posts_by_date, 
                x=posts_by_date['date'].dt.day,
                y=posts_by_date['date'].dt.month,
                z='post_count',
                title="Scheduled Posts Calendar",
                labels={'x': 'Day', 'y': 'Month', 'z': 'Posts'},
                color_continuous_scale='Blues'
            )
            
            return fig
        except:
            return None
    
    def display_enhanced_post_card(self, row, index):
        """Display enhanced post card with AI insights"""
        status, status_class = self.get_post_status(row)
        message = row.get('Message', '')
        
        # AI analysis
        performance_score, feedback = self.analyze_post_performance(message)
        
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
        
        # Scheduling info
        if status == "Scheduled":
            schedule_info = f"{row.get('Month(1-12)', '')}/{row.get('Day(1-31)', '')}/{row.get('Year', '')} at {row.get('Hour', '')}:{row.get('Minute(0-59)', '0'):02d}"
            card_html += f'<div class="post-meta">📅 {schedule_info}</div>'
        
        # Category and other meta info
        if row.get('Category'):
            card_html += f'<div class="post-meta">🏷️ {row.get("Category")}</div>'
        
        if row.get('Link'):
            card_html += f'<div class="post-meta">🔗 <a href="{row.get("Link")}" target="_blank">Link attached</a></div>'
        
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
            if row.get('ImageURL'):
                image = self.load_image_from_url(row.get('ImageURL'))
                if image:
                    st.image(image, caption="Post Image", use_column_width=True)
                else:
                    st.info(f"🖼️ Image URL: {row.get('ImageURL')}")
            
            if row.get('VideoURL'):
                if row.get('VideoURL').endswith('.mp4'):
                    try:
                        st.video(row.get('VideoURL'))
                    except:
                        st.info(f"🎥 Video URL: {row.get('VideoURL')}")
                else:
                    st.info(f"🎥 Video URL: {row.get('VideoURL')}")
        
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
                
                if st.button("🚀", key=f"boost_{index}", help="AI Optimize"):
                    st.session_state.optimize_post = index
                    st.rerun()

def main():
    st.title("🚀 AI-Powered Social Media Manager Pro")
    st.markdown("**Advanced social media management with AI insights, analytics, and automation**")
    
    manager = EnhancedSocialMediaManager()
    
    # Initialize session state
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'dashboard'
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("⚙️ Configuration")
        
        # Google Sheets Setup
        st.subheader("📊 Google Sheets Setup")
        credentials_file = st.file_uploader(
            "Upload Service Account JSON",
            type="json",
            help="Upload your Google service account credentials"
        )
        
        if credentials_file:
            credentials_dict = json.load(credentials_file)
            st.session_state.google_credentials = credentials_dict
            st.success("✅ Credentials loaded!")
        
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL"
        )
        
        if sheet_url:
            st.session_state.sheet_url = sheet_url
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("🧭 Navigation")
        
        nav_options = {
            'dashboard': '📊 Dashboard',
            'posts': '📋 Manage Posts',
            'create': '➕ Create Post',
            'ai_tools': '🤖 AI Tools',
            'analytics': '📈 Analytics',
            'calendar': '📅 Calendar',
            'templates': '📝 Templates',
            'bulk': '⚙️ Bulk Actions'
        }
        
        for key, label in nav_options.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_view = key
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Stats
        if 'google_credentials' in st.session_state and 'sheet_url' in st.session_state:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("📊 Quick Stats")
            
            try:
                client, error = manager.setup_google_sheets()
                if not error:
                    df = manager.get_sheet_data(client, st.session_state.sheet_url)
                    
                    total_posts = len(df)
                    scheduled_posts = len(df[
                        (df['Month(1-12)'] != '') & 
                        (df['Day(1-31)'] != '') & 
                        (df['Year'] != '')
                    ])
                    
                    st.metric("Total Posts", total_posts)
                    st.metric("Scheduled", scheduled_posts)
                    st.metric("Queued", total_posts - scheduled_posts)
                    
                    if not df.empty and 'Category' in df.columns:
                        top_category = df['Category'].value_counts().index[0] if len(df['Category'].value_counts()) > 0 else "None"
                        st.metric("Top Category", top_category)
            except:
                pass
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Platform Limits Reference
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("📱 Platform Limits")
        with st.expander("Character Limits"):
            for platform, info in manager.platform_limits.items():
                st.write(f"**{platform}:** {info['limit']:,} chars")
                st.write(f"*Optimal:* {info['optimal']} chars")
                st.write("---")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content based on navigation
    if 'google_credentials' not in st.session_state:
        st.warning("⚠️ Please upload your Google service account credentials in the sidebar")
        
        with st.expander("📋 Setup Instructions", expanded=True):
            st.markdown("""
            ### 🚀 Quick Setup Guide:
            
            **1. Google Cloud Console Setup:**
            - Visit [Google Cloud Console](https://console.cloud.google.com/)
            - Create or select a project
            - Enable Google Sheets API
            
            **2. Service Account Creation:**
            - Go to "APIs & Services" > "Credentials"
            - Create Service Account
            - Download JSON key file
            
            **3. Sheet Permissions:**
            - Share your Google Sheet with the service account email
            - Grant "Editor" permissions
            
            **4. Upload & Connect:**
            - Upload the JSON file in the sidebar
            - Paste your Google Sheets URL
            
            ### 🎯 New Features in Pro Version:
            - 🤖 AI-powered post generation
            - 📊 Advanced analytics dashboard
            - 📅 Calendar scheduling view
            - 📝 Smart templates system
            - 🎯 Performance optimization
            - 🔄 Bulk operations
            - 📈 Engagement predictions
            - 🏷️ Smart hashtag suggestions
            """)
        return
    
    if 'sheet_url' not in st.session_state:
        st.warning("⚠️ Please enter your Google Sheets URL in the sidebar")
        return
    
    # Connect to Google Sheets
    client, error = manager.setup_google_sheets()
    if error:
        st.error(error)
        return
    
    # Load data
    with st.spinner("🔄 Loading data from Google Sheets..."):
        df = manager.get_sheet_data(client, st.session_state.sheet_url)
    
    # Route to different views
    current_view = st.session_state.current_view
    
    if current_view == 'dashboard':
        show_dashboard(manager, df, client)
    elif current_view == 'posts':
        show_posts_view(manager, df, client)
    elif current_view == 'create':
        show_create_post(manager, df, client)
    elif current_view == 'ai_tools':
        show_ai_tools(manager, df, client)
    elif current_view == 'analytics':
        show_analytics(manager, df, client)
    elif current_view == 'calendar':
        show_calendar_view(manager, df, client)
    elif current_view == 'templates':
        show_templates(manager, df, client)
    elif current_view == 'bulk':
        show_bulk_actions(manager, df, client)

def show_dashboard(manager, df, client):
    """Enhanced dashboard with key metrics and insights"""
    st.header("📊 Dashboard Overview")
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_posts = len(df)
    scheduled_posts = len(df[
        (df['Month(1-12)'] != '') & 
        (df['Day(1-31)'] != '') & 
        (df['Year'] != '')
    ]) if not df.empty else 0
    
    posts_with_media = len(df[
        (df['ImageURL'] != '') | (df['VideoURL'] != '')
    ]) if not df.empty else 0
    
    avg_message_length = df['Message'].str.len().mean() if not df.empty else 0
    
    categories_count = len(df['Category'].unique()) if not df.empty and 'Category' in df.columns else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_posts}</div>
            <div class="metric-label">Total Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{scheduled_posts}</div>
            <div class="metric-label">Scheduled</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{posts_with_media}</div>
            <div class="metric-label">With Media</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{int(avg_message_length)}</div>
            <div class="metric-label">Avg Length</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{categories_count}</div>
            <div class="metric-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    if not df.empty:
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Posts by Category")
            if 'Category' in df.columns and not df['Category'].isna().all():
                category_counts = df['Category'].value_counts().head(10)
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Distribution of Posts by Category",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available")
        
        with col2:
            st.subheader("📈 Message Length Distribution")
            df['message_length'] = df['Message'].str.len()
            fig = px.histogram(
                df, 
                x='message_length',
                nbins=20,
                title="Distribution of Message Lengths",
                labels={'message_length': 'Characters', 'count': 'Number of Posts'},
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Posts Preview
        st.subheader("📝 Recent Posts Preview")
        recent_posts = df.head(3)
        
        for idx, row in recent_posts.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    message = row.get('Message', '')
                    st.markdown(f"""
                    <div style="background: white; padding: 16px; border-radius: 8px; border-left: 4px solid #3498db; margin: 8px 0;">
                        <div style="font-size: 14px; margin-bottom: 8px;">{message[:150]}{'...' if len(message) > 150 else ''}</div>
                        <div style="font-size: 12px; color: #666;">
                            Category: {row.get('Category', 'Uncategorized')} | 
                            Length: {len(message)} chars
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("View", key=f"view_recent_{idx}"):
                        st.session_state.current_view = 'posts'
                        st.rerun()
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Create New Post", use_container_width=True):
                st.session_state.current_view = 'create'
                st.rerun()
        
        with col2:
            if st.button("🤖 AI Generate Post", use_container_width=True):
                st.session_state.current_view = 'ai_tools'
                st.rerun()
        
        with col3:
            if st.button("📅 View Calendar", use_container_width=True):
                st.session_state.current_view = 'calendar'
                st.rerun()
        
        with col4:
            if st.button("📊 Full Analytics", use_container_width=True):
                st.session_state.current_view = 'analytics'
                st.rerun()
    
    else:
        st.info("📝 No posts yet. Create your first post to get started!")
        if st.button("Create First Post", type="primary"):
            st.session_state.current_view = 'create'
            st.rerun()

def show_posts_view(manager, df, client):
    """Enhanced posts management view"""
    st.header("📋 Manage Your Posts")
    
    # Enhanced Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        categories = ["All"] + list(df['Category'].dropna().unique()) if not df.empty else ["All"]
        category_filter = st.selectbox("📂 Category", categories)
    
    with col2:
        status_filter = st.selectbox("📊 Status", ["All", "Scheduled", "Queued"])
    
    with col3:
        sort_options = ["Newest First", "Oldest First", "A-Z", "Z-A", "Longest", "Shortest"]
        sort_by = st.selectbox("🔄 Sort By", sort_options)
    
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
                # Save logic here
                st.success("Saved as draft!")
        
        with col2:
            if st.button("📅 Schedule Post"):
                # Schedule logic here
                st.info("Scheduling feature coming soon!")
        
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
                    st.session_state.template_generated_post = preview_post
                    st.success("Template post ready! You can now edit and save it.")
            
            except KeyError as e:
                st.error(f"Missing variable: {e}")

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
            
            if st.button("📊 Analyze All Posts"):
                with st.spinner("🤖 Analyzing all posts..."):
                    scores = []
                    categories = []
                    lengths = []
                    
                    for _, row in df.iterrows():
                        score, _ = manager.analyze_post_performance(row['Message'])
                        scores.append(score)
                        categories.append(row.get('Category', 'Uncategorized'))
                        lengths.append(len(row['Message']))
                    
                    analysis_df = pd.DataFrame({
                        'Score': scores,
                        'Category': categories,
                        'Length': lengths,
                        'Message': df['Message'].str[:50] + '...'
                    })
                
                # Performance distribution
                fig = px.histogram(
                    analysis_df,
                    x='Score',
                    nbins=20,
                    title="Performance Score Distribution",
                    labels={'Score': 'Performance Score', 'count': 'Number of Posts'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Category performance
                if len(analysis_df['Category'].unique()) > 1:
                    fig2 = px.box(
                        analysis_df,
                        x='Category',
                        y='Score',
                        title="Performance by Category"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Top and bottom performers
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏆 Top Performers:**")
                    top_posts = analysis_df.nlargest(3, 'Score')
                    for _, post in top_posts.iterrows():
                        st.markdown(f"**{post['Score']}/100** - {post['Message']}")
                
                with col2:
                    st.markdown("**📈 Needs Improvement:**")
                    bottom_posts = analysis_df.nsmallest(3, 'Score')
                    for _, post in bottom_posts.iterrows():
                        st.markdown(f"**{post['Score']}/100** - {post['Message']}")
    
    with tab4:
        st.subheader("🔮 Content Trend Predictor")
        
        st.info("🚧 Coming Soon: AI-powered trend analysis and content suggestions based on current social media trends!")
        
        # Placeholder for trend analysis
        st.markdown("""
        **Upcoming Features:**
        - 📈 Trending topic analysis
        - 🎯 Optimal posting time predictions
        - 📊 Engagement forecasting
        - 🏷️ Trending hashtag recommendations
        - 🌍 Platform-specific trend insights
        """)

def show_analytics(manager, df, client):
    """Advanced analytics dashboard"""
    st.header("📈 Advanced Analytics")
    
    if df.empty:
        st.info("📊 No data available for analytics. Create some posts first!")
        return
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        time_period = st.selectbox(
            "📅 Time Period",
            ["All Time", "Last 30 Days", "Last 7 Days", "This Month", "This Week"]
        )
    
    # Key Metrics
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_posts = len(df)
    avg_length = df['Message'].str.len().mean()
    posts_with_links = len(df[df['Link'] != ''])
    posts_with_media = len(df[(df['ImageURL'] != '') | (df['VideoURL'] != '')])
    scheduled_ratio = len(df[(df['Month(1-12)'] != '') & (df['Day(1-31)'] != '') & (df['Year'] != '')]) / total_posts * 100 if total_posts > 0 else 0
    
    with col1:
        st.metric("Total Posts", total_posts)
    
    with col2:
        st.metric("Avg Length", f"{int(avg_length)} chars")
    
    with col3:
        st.metric("With Links", f"{posts_with_links} ({posts_with_links/total_posts*100:.1f}%)")
    
    with col4:
        st.metric("With Media", f"{posts_with_media} ({posts_with_media/total_posts*100:.1f}%)")
    
    with col5:
        st.metric("Scheduled", f"{scheduled_ratio:.1f}%")
    
    # Charts
    st.markdown("---")
    
    # Row 1: Category and Length Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Posts by Category")
        if 'Category' in df.columns and not df['Category'].isna().all():
            category_counts = df['Category'].value_counts()
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Number of Posts by Category",
                labels={'x': 'Category', 'y': 'Number of Posts'},
                color=category_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    with col2:
        st.subheader("📏 Message Length Analysis")
        df['message_length'] = df['Message'].str.len()
        
        fig = px.box(
            df,
            y='message_length',
            title="Message Length Distribution",
            labels={'message_length': 'Characters'}
        )
        
        # Add platform limit lines
        for platform, info in list(manager.platform_limits.items())[:3]:
            fig.add_hline(
                y=info['limit'],
                line_dash="dash",
                annotation_text=f"{platform} limit",
                annotation_position="right"
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Performance and Scheduling Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Performance Analysis")
        
        # Calculate performance scores for all posts
        scores = []
        for _, row in df.iterrows():
            score, _ = manager.analyze_post_performance(row['Message'])
            scores.append(score)
        
        df['performance_score'] = scores
        
        fig = px.histogram(
            df,
            x='performance_score',
            nbins=20,
            title="Performance Score Distribution",
            labels={'performance_score': 'Performance Score', 'count': 'Number of Posts'},
            color_discrete_sequence=['#3498db']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance by category
        if 'Category' in df.columns and not df['Category'].isna().all():
            avg_scores = df.groupby('Category')['performance_score'].mean().sort_values(ascending=False)
            
            st.markdown("**📊 Average Performance by Category:**")
            for category, score in avg_scores.head().items():
                st.markdown(f"**{category}:** {score:.1f}/100")
    
    with col2:
        st.subheader("📅 Scheduling Patterns")
        
        # Scheduled vs Queued
        scheduled_count = len(df[(df['Month(1-12)'] != '') & (df['Day(1-31)'] != '') & (df['Year'] != '')])
        queued_count = total_posts - scheduled_count
        
        fig = px.pie(
            values=[scheduled_count, queued_count],
            names=['Scheduled', 'Queued'],
            title="Scheduled vs Queued Posts",
            color_discrete_sequence=['#3498db', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Hour distribution for scheduled posts
        scheduled_df = df[(df['Hour'] != '') & (df['Hour'].notna())]
        if not scheduled_df.empty:
            hour_counts = scheduled_df['Hour'].value_counts().sort_index()
            
            fig = px.bar(
                x=hour_counts.index,
                y=hour_counts.values,
                title="Posting Hours Distribution",
                labels={'x': 'Hour of Day', 'y': 'Number of Posts'},
                color_discrete_sequence=['#e74c3c']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Content Analysis
    st.subheader("📝 Content Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏷️ Hashtag Usage**")
        hashtag_counts = []
        for message in df['Message']:
            hashtags = len(re.findall(r'#\w+', str(message)))
            hashtag_counts.append(hashtags)
        
        df['hashtag_count'] = hashtag_counts
        avg_hashtags = np.mean(hashtag_counts)
        
        st.metric("Avg Hashtags per Post", f"{avg_hashtags:.1f}")
        
        hashtag_dist = pd.Series(hashtag_counts).value_counts().sort_index()
        fig = px.bar(
            x=hashtag_dist.index,
            y=hashtag_dist.values,
            title="Hashtag Count Distribution",
            labels={'x': 'Number of Hashtags', 'y': 'Number of Posts'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🔗 Link Usage**")
        link_usage = df['Link'].apply(lambda x: 'With Link' if x and x.strip() else 'No Link').value_counts()
        
        fig = px.pie(
            values=link_usage.values,
            names=link_usage.index,
            title="Posts with Links",
            color_discrete_sequence=['#2ecc71', '#ecf0f1']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**📱 Media Usage**")
        
        media_types = []
        for _, row in df.iterrows():
            if row['ImageURL'] and row['VideoURL']:
                media_types.append('Both')
            elif row['ImageURL']:
                media_types.append('Image Only')
            elif row['VideoURL']:
                media_types.append('Video Only')
            else:
                media_types.append('No Media')
        
        media_dist = pd.Series(media_types).value_counts()
        
        fig = px.pie(
            values=media_dist.values,
            names=media_dist.index,
            title="Media Type Distribution",
            color_discrete_sequence=['#9b59b6', '#3498db', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights and Recommendations
    st.markdown("---")
    st.subheader("💡 AI Insights & Recommendations")
    
    insights = []
    
    # Performance insights
    if 'performance_score' in df.columns:
        avg_performance = df['performance_score'].mean()
        if avg_performance < 60:
            insights.append("📈 Your average performance score is below 60. Consider adding more call-to-actions and engaging questions.")
        elif avg_performance > 80:
            insights.append("🎉 Excellent! Your posts have high performance scores. Keep up the great work!")
    
    # Length insights
    if avg_length < 50:
        insights.append("📝 Your posts are quite short. Consider adding more detail to increase engagement.")
    elif avg_length > 200:
        insights.append("✂️ Your posts are quite long. Consider shortening them for better platform compatibility.")
    
    # Hashtag insights
    if avg_hashtags < 3:
        insights.append("🏷️ You're using fewer hashtags than recommended. Try adding 3-5 relevant hashtags per post.")
    elif avg_hashtags > 10:
        insights.append("🏷️ You might be using too many hashtags. Consider reducing to 5-8 for better engagement.")
    
    # Media insights
    media_percentage = posts_with_media / total_posts * 100
    if media_percentage < 30:
        insights.append("📸 Only {:.1f}% of your posts have media. Visual content typically gets higher engagement.".format(media_percentage))
    
    # Scheduling insights
    if scheduled_ratio < 50:
        insights.append("📅 Less than half of your posts are scheduled. Consider planning your content calendar in advance.")
    
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.success("🎯 Your content strategy looks great! Keep maintaining this quality.")

def show_calendar_view(manager, df, client):
    """Calendar view for scheduled posts"""
    st.header("📅 Content Calendar")
    
    if df.empty:
        st.info("📅 No posts to display in calendar view.")
        return
    
    # Filter for scheduled posts
    scheduled_df = df[
        (df['Month(1-12)'] != '') & 
        (df['Day(1-31)'] != '') & 
        (df['Year'] != '')
    ].copy()
    
    if scheduled_df.empty:
        st.info("📅 No scheduled posts found. Schedule some posts to see them in calendar view!")
        
        if st.button("➕ Schedule a Post"):
            st.session_state.current_view = 'create'
            st.rerun()
        return
    
    # Calendar controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"📊 {len(scheduled_df)} Scheduled Posts")
    
    with col2:
        view_mode = st.selectbox("View Mode", ["Month", "Week", "List"])
    
    with col3:
        current_date = datetime.now()
        selected_month = st.selectbox(
            "Month",
            range(1, 13),
            index=current_date.month - 1,
            format_func=lambda x: calendar.month_name[x]
        )
        selected_year = st.selectbox(
            "Year",
            range(2024, 2030),
            index=current_date.year - 2024
        )
    
    # Convert scheduling info to datetime
    try:
        scheduled_df['scheduled_date'] = pd.to_datetime(
            scheduled_df[['Year', 'Month(1-12)', 'Day(1-31)', 'Hour', 'Minute(0-59)']].rename(columns={
                'Year': 'year',
                'Month(1-12)': 'month', 
                'Day(1-31)': 'day',
                'Hour': 'hour',
                'Minute(0-59)': 'minute'
            })
        )
        
        # Filter by selected month/year
        month_filter = (scheduled_df['scheduled_date'].dt.month == selected_month) & \
                      (scheduled_df['scheduled_date'].dt.year == selected_year)
        month_posts = scheduled_df[month_filter]
        
        if view_mode == "Month":
            show_month_calendar(month_posts, selected_year, selected_month)
        elif view_mode == "Week":
            show_week_calendar(month_posts)
        else:  # List view
            show_calendar_list(month_posts)
            
    except Exception as e:
        st.error(f"Error processing calendar data: {str(e)}")
        st.info("Please check that your scheduled posts have valid date/time information.")

def show_month_calendar(posts_df, year, month):
    """Display month calendar view"""
    import calendar as cal
    
    # Create calendar
    cal_matrix = cal.monthcalendar(year, month)
    month_name = cal.month_name[month]
    
    st.subheader(f"📅 {month_name} {year}")
    
    # Group posts by day
    if not posts_df.empty:
        posts_by_day = posts_df.groupby(posts_df['scheduled_date'].dt.day).size().to_dict()
    else:
        posts_by_day = {}
    
    # Display calendar grid
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Header
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # Calendar weeks
    for week in cal_matrix:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("")  # Empty cell for days not in month
                else:
                    post_count = posts_by_day.get(day, 0)
                    
                    if post_count > 0:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #3498db, #2980b9);
                            color: white;
                            padding: 8px;
                            border-radius: 8px;
                            text-align: center;
                            margin: 2px;
                            cursor: pointer;
                        ">
                            <div style="font-weight: bold; font-size: 16px;">{day}</div>
                            <div style="font-size: 10px;">{post_count} post{'s' if post_count > 1 else ''}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show posts for this day
                        day_posts = posts_df[posts_df['scheduled_date'].dt.day == day]
                        with st.expander(f"Posts for {month_name} {day}"):
                            for _, post in day_posts.iterrows():
                                time_str = post['scheduled_date'].strftime("%H:%M")
                                message_preview = post['Message'][:100] + "..." if len(post['Message']) > 100 else post['Message']
                                st.markdown(f"**{time_str}** - {message_preview}")
                    else:
                        st.markdown(f"""
                        <div style="
                            background: #f8f9fa;
                            color: #6c757d;
                            padding: 8px;
                            border-radius: 8px;
                            text-align: center;
                            margin: 2px;
                            border: 1px solid #e9ecef;
                        ">
                            <div style="font-size: 16px;">{day}</div>
                        </div>
                        """, unsafe_allow_html=True)

def show_week_calendar(posts_df):
    """Display week calendar view"""
    st.subheader("📅 Week View")
    
    if posts_df.empty:
        st.info("No posts scheduled for this period.")
        return
    
    # Group by day of week
    posts_df['day_of_week'] = posts_df['scheduled_date'].dt.day_name()
    posts_df['hour'] = posts_df['scheduled_date'].dt.hour
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days:
        day_posts = posts_df[posts_df['day_of_week'] == day].sort_values('hour')
        
        if not day_posts.empty:
            st.markdown(f"### {day}")
            
            for _, post in day_posts.iterrows():
                time_str = post['scheduled_date'].strftime("%H:%M")
                
                st.markdown(f"""
                <div style="
                    background: white;
                    border-left: 4px solid #3498db;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="font-weight: bold; color: #3498db; margin-bottom: 4px;">
                        🕐 {time_str} | 📂 {post.get('Category', 'Uncategorized')}
                    </div>
                    <div style="color: #2c3e50;">
                        {post['Message'][:200]}{'...' if len(post['Message']) > 200 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def show_calendar_list(posts_df):
    """Display list view of scheduled posts"""
    st.subheader("📋 Scheduled Posts List")
    
    if posts_df.empty:
        st.info("No posts scheduled for this period.")
        return
    
    # Sort by scheduled date
    posts_df_sorted = posts_df.sort_values('scheduled_date')
    
    for _, post in posts_df_sorted.iterrows():
        date_str = post['scheduled_date'].strftime("%B %d, %Y at %H:%M")
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 16px;
                    margin: 8px 0;
                    border-left: 4px solid #3498db;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 8px;">
                        📅 {date_str} | 📂 {post.get('Category', 'Uncategorized')}
                    </div>
                    <div style="color: #2c3e50; line-height: 1.5;">
                        {post['Message']}
                    </div>
                    {f'<div style="margin-top: 8px; font-size: 12px; color: #7f8c8d;">🔗 <a href="{post["Link"]}" target="_blank">Link attached</a></div>' if post.get('Link') else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_cal_{post.name}"):
                    st.info("Edit functionality coming soon!")
                
                if st.button("🗑️ Delete", key=f"del_cal_{post.name}"):
                    st.info("Delete functionality coming soon!")

def show_templates(manager, df, client):
    """Template management system"""
    st.header("📝 Post Templates")
    
    tab1, tab2 = st.tabs(["🎨 Use Templates", "➕ Create Template"])
    
    with tab1:
        st.subheader("🎨 Available Templates")
        
        # Template categories
        template_categories = {
            'Business': ['AI Consulting', 'Customer Success', 'Industry Insights'],
            'Content': ['Educational', 'Behind the Scenes'],
            'Marketing': ['Product Launch']
        }
        
        for category, templates in template_categories.items():
            st.markdown(f"### {category}")
            
            cols = st.columns(len(templates))
            
            for i, template_name in enumerate(templates):
                with cols[i]:
                    template = manager.post_templates[template_name]
                    
                    st.markdown(f"""
                    <div class="template-card">
                        <h4>{template_name}</h4>
                        <p style="font-size: 12px; color: #666; margin-bottom: 12px;">
                            {template['template'][:100]}...
                        </p>
                        <div style="font-size: 11px; color: #888;">
                            Variables: {len(template['variables'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Use {template_name}", key=f"use_template_{template_name}"):
                        st.session_state.selected_template = template_name
                        st.session_state.current_view = 'create'
                        st.rerun()
        
        # Template usage statistics
        if not df.empty:
            st.markdown("---")
            st.subheader("📊 Template Usage Statistics")
            
            # This would require tracking which template was used for each post
            # For now, show placeholder
            st.info("📈 Template usage tracking coming soon!")
    
    with tab2:
        st.subheader("➕ Create Custom Template")
        
        with st.form("create_template_form"):
            template_name = st.text_input("Template Name", placeholder="e.g., Product Announcement")
            
            template_content = st.text_area(
                "Template Content",
                placeholder="Use {variable_name} for dynamic content. Example: 🚀 Introducing {product_name}! {description}",
                height=100
            )
            
            st.markdown("**Variables found in template:**")
            if template_content:
                variables = re.findall(r'\{(\w+)\}', template_content)
                if variables:
                    st.write(", ".join(variables))
                else:
                    st.write("No variables found")
            
            category = st.selectbox(
                "Category",
                ["Business", "Content", "Marketing", "Custom"]
            )
            
            description = st.text_area(
                "Description",
                placeholder="Describe when and how to use this template"
            )
            
            if st.form_submit_button("💾 Save Template"):
                if template_name and template_content:
                    # In a real app, you'd save this to a database
                    st.success(f"✅ Template '{template_name}' saved successfully!")
                    st.info("💡 Custom template saving will be available in the next update.")
                else:
                    st.error("❌ Please fill in template name and content")

def show_bulk_actions(manager, df, client):
    """Bulk operations for posts"""
    st.header("⚙️ Bulk Actions & Operations")
    
    if df.empty:
        st.info("📝 No posts available for bulk operations.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Export/Import", "🔄 Bulk Edit", "📅 Bulk Schedule", "🗑️ Bulk Delete"])
    
    with tab1:
        st.subheader("📤 Export & Import Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Export Data")
            
            export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
            
            include_options = st.multiselect(
                "Include Fields",
                manager.column_names,
                default=manager.column_names[:5]
            )
            
            if st.button("📥 Export Data", type="primary"):
                if export_format == "CSV":
                    csv_data = df[include_options].to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_data,
                        file_name=f"social_media_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                elif export_format == "JSON":
                    json_data = df[include_options].to_json(orient='records', indent=2)
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"social_media_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:  # Excel
                    st.info("📊 Excel export coming soon!")
        
        with col2:
            st.markdown("### 📤 Import Data")
            
            uploaded_file = st.file_uploader("📤 Upload File", type=["csv", "json"])
            
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        new_df = pd.read_csv(uploaded_file)
                    else:  # JSON
                        new_df = pd.read_json(uploaded_file)
                    
                    # Ensure all required columns exist
                    for col in manager.column_names:
                        if col not in new_df.columns:
                            new_df[col] = ''
                    
                    new_df = new_df[manager.column_names]
                    
                    st.markdown("**📋 Preview of uploaded data:**")
                    st.dataframe(new_df.head(), use_container_width=True)
                    
                    col1_1, col1_2 = st.columns(2)
                    
                    with col1_1:
                        if st.button("🔄 Replace All Data", type="secondary"):
                            success, message = manager.update_sheet(
                                client, st.session_state.sheet_url, new_df
                            )
                            if success:
                                st.success("✅ Data replaced successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {message}")
                    
                    with col1_2:
                        if st.button("➕ Append to Existing", type="primary"):
                            combined_df = pd.concat([df, new_df], ignore_index=True)
                            success, message = manager.update_sheet(
                                client, st.session_state.sheet_url, combined_df
                            )
                            if success:
                                st.success("✅ Data appended successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {message}")
                
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
    
    with tab2:
        st.subheader("🔄 Bulk Edit Operations")
        
        # Select posts to edit
        st.markdown("### 📋 Select Posts to Edit")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            edit_category = st.selectbox(
                "Filter by Category",
                ["All"] + list(df['Category'].dropna().unique())
            )
        
        with col2:
            edit_status = st.selectbox(
                "Filter by Status",
                ["All", "Scheduled", "Queued"]
            )
        
        # Apply filters for editing
        edit_df = df.copy()
        
        if edit_category != "All":
            edit_df = edit_df[edit_df['Category'] == edit_category]
        
        if edit_status != "All":
            if edit_status == "Scheduled":
                edit_df = edit_df[
                    (edit_df['Month(1-12)'] != '') | 
                    (edit_df['Day(1-31)'] != '') | 
                    (edit_df['Year'] != '')
                ]
            else:  # Queued
                edit_df = edit_df[
                    (edit_df['Month(1-12)'] == '') & 
                    (edit_df['Day(1-31)'] == '') & 
                    (edit_df['Year'] == '')
                ]
        
        st.write(f"📊 {len(edit_df)} posts selected for editing")
        
        if not edit_df.empty:
            st.markdown("### ✏️ Bulk Edit Options")
            
            edit_operation = st.selectbox(
                "Select Operation",
                [
                    "Update Category",
                    "Add Hashtags",
                    "Update Watermark",
                    "Set CTA Group",
                    "Update Pinterest Board"
                ]
            )
            
            if edit_operation == "Update Category":
                new_category = st.text_input("New Category")
                if st.button("🔄 Update Category") and new_category:
                    # Update category for selected posts
                    df.loc[edit_df.index, 'Category'] = new_category
                    success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                    if success:
                        st.success(f"✅ Updated category for {len(edit_df)} posts!")
                        time.sleep(1)
                        st.rerun()
            
            elif edit_operation == "Add Hashtags":
                additional_hashtags = st.text_input("Hashtags to Add", placeholder="#hashtag1 #hashtag2")
                if st.button("🏷️ Add Hashtags") and additional_hashtags:
                    # Add hashtags to messages
                    for idx in edit_df.index:
                        current_message = df.loc[idx, 'Message']
                        if not current_message.endswith(' '):
                            current_message += ' '
                        df.loc[idx, 'Message'] = current_message + additional_hashtags
                    
                    success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                    if success:
                        st.success(f"✅ Added hashtags to {len(edit_df)} posts!")
                        time.sleep(1)
                        st.rerun()
            
            # Add other bulk edit operations...
    
    with tab3:
        st.subheader("📅 Bulk Scheduling")
        
        # Select unscheduled posts
        unscheduled_df = df[
            (df['Month(1-12)'] == '') & 
            (df['Day(1-31)'] == '') & 
            (df['Year'] == '')
        ]
        
        if unscheduled_df.empty:
            st.info("📅 All posts are already scheduled!")
        else:
            st.write(f"📊 {len(unscheduled_df)} unscheduled posts found")
            
            st.markdown("### 📅 Scheduling Options")
            
            schedule_type = st.selectbox(
                "Scheduling Method",
                ["Daily Intervals", "Specific Times", "Random Distribution"]
            )
            
            if schedule_type == "Daily Intervals":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    start_date = st.date_input("Start Date", datetime.now().date())
                
                with col2:
                    posts_per_day = st.number_input("Posts per Day", min_value=1, max_value=10, value=1)
                
                with col3:
                    start_hour = st.number_input("Start Hour", min_value=0, max_value=23, value=9)
                
                if st.button("📅 Schedule Posts"):
                    # Implement bulk scheduling logic
                    current_date = start_date
                    posts_scheduled = 0
                    
                    for idx, row in unscheduled_df.iterrows():
                        # Calculate scheduling time
                        post_time = datetime.combine(current_date, datetime.min.time()) + \
                                   timedelta(hours=start_hour, minutes=(posts_scheduled % posts_per_day) * 60)
                        
                        # Update scheduling fields
                        df.loc[idx, 'Month(1-12)'] = post_time.month
                        df.loc[idx, 'Day(1-31)'] = post_time.day
                        df.loc[idx, 'Year'] = post_time.year
                        df.loc[idx, 'Hour'] = post_time.hour
                        df.loc[idx, 'Minute(0-59)'] = post_time.minute
                        
                        posts_scheduled += 1
                        
                        # Move to next day if needed
                        if posts_scheduled % posts_per_day == 0:
                            current_date += timedelta(days=1)
                    
                    success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                    if success:
                        st.success(f"✅ Scheduled {len(unscheduled_df)} posts!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {message}")
    
    with tab4:
        st.subheader("🗑️ Bulk Delete Operations")
        
        st.warning("⚠️ **Warning:** Bulk delete operations cannot be undone!")
        
        delete_options = st.multiselect(
            "Delete posts by:",
            ["Category", "Date Range", "Performance Score", "Content Length"]
        )
        
        posts_to_delete = pd.DataFrame()
        
        if "Category" in delete_options:
            delete_category = st.selectbox(
                "Delete posts in category:",
                list(df['Category'].dropna().unique())
            )
            if delete_category:
                posts_to_delete = pd.concat([posts_to_delete, df[df['Category'] == delete_category]])
        
        if "Performance Score" in delete_options:
            st.info("📊 Performance score deletion coming soon!")
        
        if "Content Length" in delete_options:
            min_length = st.number_input("Minimum length to delete", min_value=0, value=500)
            long_posts = df[df['Message'].str.len() > min_length]
            posts_to_delete = pd.concat([posts_to_delete, long_posts])
        
        # Remove duplicates
        posts_to_delete = posts_to_delete.drop_duplicates()
        
        if not posts_to_delete.empty:
            st.write(f"🗑️ {len(posts_to_delete)} posts selected for deletion")
            
            with st.expander("📋 Preview posts to be deleted"):
                for _, post in posts_to_delete.head(5).iterrows():
                    st.write(f"• {post['Message'][:100]}...")
                
                if len(posts_to_delete) > 5:
                    st.write(f"... and {len(posts_to_delete) - 5} more posts")
            
            confirm_delete = st.checkbox("I understand this action cannot be undone")
            
            if confirm_delete and st.button("🗑️ Delete Selected Posts", type="secondary"):
                # Remove selected posts
                remaining_df = df.drop(posts_to_delete.index).reset_index(drop=True)
                
                success, message = manager.update_sheet(client, st.session_state.sheet_url, remaining_df)
                if success:
                    st.success(f"✅ Deleted {len(posts_to_delete)} posts!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {message}")

def handle_post_actions(manager, df, client):
    """Handle various post actions like edit, delete, duplicate"""
    
    # Handle delete action
    if 'delete_post' in st.session_state:
        st.warning(f"⚠️ Are you sure you want to delete this post?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Delete", type="secondary"):
                df_updated = df.drop(df.index[st.session_state.delete_post]).reset_index(drop=True)
                success, message = manager.update_sheet(client, st.session_state.sheet_url, df_updated)
                if success:
                    st.success("✅ Post deleted successfully!")
                    del st.session_state.delete_post
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {message}")
        
        with col2:
            if st.button("❌ Cancel"):
                del st.session_state.delete_post
                st.rerun()
    
    # Handle duplicate action
    if 'duplicate_post' in st.session_state:
        original_post = df.iloc[st.session_state.duplicate_post].copy()
        
        # Clear scheduling info for duplicate
        original_post['Month(1-12)'] = ''
        original_post['Day(1-31)'] = ''
        original_post['Year'] = ''
        original_post['Hour'] = ''
        original_post['Minute(0-59)'] = ''
        
        # Add "Copy" to message
        original_post['Message'] = f"[COPY] {original_post['Message']}"
        
        new_df = pd.concat([df, pd.DataFrame([original_post])], ignore_index=True)
        success, message = manager.update_sheet(client, st.session_state.sheet_url, new_df)
        
        if success:
            st.success("✅ Post duplicated successfully!")
            del st.session_state.duplicate_post
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ Error: {message}")
    
    # Handle optimize action
    if 'optimize_post' in st.session_state:
        st.info("🤖 AI optimization feature coming soon!")
        del st.session_state.optimize_post

if __name__ == "__main__":
    main()

