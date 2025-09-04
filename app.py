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

# Clean CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .calendar-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
    
    .post-card-clean {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .post-meta-info {
        color: #666;
        font-size: 12px;
        margin-bottom: 10px;
    }
    
    .post-content {
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    
    .status-badge-clean {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .status-scheduled {
        background: #4caf50;
        color: white;
    }
    
    .status-queued {
        background: #ff9800;
        color: white;
    }
    
    .edit-form-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

class SocialMediaManager:
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

def show_calendar_view(manager, df, client):
    """Clean calendar view with clickable date buttons"""
    st.markdown('<div class="main-header"><h2>📅 Calendar View</h2></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = datetime.now().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = datetime.now().year
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'editing_post_date' not in st.session_state:
        st.session_state.editing_post_date = None
    
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
                    
                    # Determine button style
                    button_class = "calendar-day-button"
                    if posts_today:
                        button_class += " calendar-day-with-posts"
                    if is_today:
                        button_class += " calendar-day-today"
                    
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
    """Show posts for selected date"""
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
    
    for i, post in enumerate(posts_sorted):
        # Find the original index in the dataframe
        original_index = df[df['Message'] == post['Message']].index[0] if not df[df['Message'] == post['Message']].empty else i
        
        # Post card
        st.markdown('<div class="post-card-clean">', unsafe_allow_html=True)
        
        # Status badge
        month_val = manager.safe_str_conversion(post.get('Month(1-12)', ''))
        day_val = manager.safe_str_conversion(post.get('Day(1-31)', ''))
        year_val = manager.safe_str_conversion(post.get('Year', ''))
        
        if month_val and day_val and year_val:
            status = "Scheduled"
            status_class = "status-scheduled"
        else:
            status = "Queued"
            status_class = "status-queued"
        
        st.markdown(f'<div class="status-badge-clean {status_class}">📅 {status}</div>', unsafe_allow_html=True)
        
        # Time info
        hour = manager.safe_str_conversion(post.get('Hour', ''))
        minute = manager.safe_int_conversion(post.get('Minute(0-59)', ''), 0)
        time_str = f"{hour}:{minute:02d}" if hour else "No time set"
        
        st.markdown(f'<div class="post-meta-info">⏰ {time_str}</div>', unsafe_allow_html=True)
        
        # Category
        category = manager.safe_str_conversion(post.get('Category', ''))
        if category:
            st.markdown(f'<div class="post-meta-info">🏷️ {category}</div>', unsafe_allow_html=True)
        
        # Full message content
        message = manager.safe_str_conversion(post.get('Message', ''), 'No message')
        st.markdown(f'<div class="post-content">{message}</div>', unsafe_allow_html=True)
        
        # Links and media
        link = manager.safe_str_conversion(post.get('Link', ''))
        if link:
            st.markdown(f"🔗 [Link]({link})")
        
        image_url = manager.safe_str_conversion(post.get('ImageURL', ''))
        if image_url:
            st.markdown(f"🖼️ [Image]({image_url})")
        
        video_url = manager.safe_str_conversion(post.get('VideoURL', ''))
        if video_url:
            st.markdown(f"🎥 [Video]({video_url})")
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
    """Show all posts in a clean list format"""
    st.markdown('<div class="main-header"><h2>📋 All Posts</h2></div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("No posts available. Create some posts first!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + list(df['Category'].dropna().unique())
        category_filter = st.selectbox("Filter by Category", categories)
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Unscheduled"])
    
    with col3:
        search_term = st.text_input("Search", placeholder="Search in messages...")
    
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
    
    st.write(f"Showing {len(filtered_df)} of {len(df)} posts")
    
    # Display posts
    for index, post in filtered_df.iterrows():
        st.markdown('<div class="post-card-clean">', unsafe_allow_html=True)
        
        # Status and scheduling info
        month = manager.safe_str_conversion(post.get('Month(1-12)', ''))
        day = manager.safe_str_conversion(post.get('Day(1-31)', ''))
        year = manager.safe_str_conversion(post.get('Year', ''))
        hour = manager.safe_str_conversion(post.get('Hour', ''))
        minute = manager.safe_int_conversion(post.get('Minute(0-59)', ''), 0)
        
        if month and day and year:
            status = "Scheduled"
            status_class = "status-scheduled"
            time_str = f"{hour}:{minute:02d}" if hour else "No time"
            schedule_info = f"{month}/{day}/{year} at {time_str}"
        else:
            status = "Unscheduled"
            status_class = "status-queued"
            schedule_info = "Not scheduled"
        
        st.markdown(f'<div class="status-badge-clean {status_class}">{status}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="post-meta-info">📅 {schedule_info}</div>', unsafe_allow_html=True)
        
        # Category
        category = manager.safe_str_conversion(post.get('Category', ''))
        if category:
            st.markdown(f'<div class="post-meta-info">🏷️ {category}</div>', unsafe_allow_html=True)
        
        # Message
        message = manager.safe_str_conversion(post.get('Message', ''), 'No message')
        st.markdown(f'<div class="post-content">{message}</div>', unsafe_allow_html=True)
        
        # Links and media
        link = manager.safe_str_conversion(post.get('Link', ''))
        if link:
            st.markdown(f"🔗 [Link]({link})")
        
        image_url = manager.safe_str_conversion(post.get('ImageURL', ''))
        if image_url:
            st.markdown(f"🖼️ [Image]({image_url})")
        
        video_url = manager.safe_str_conversion(post.get('VideoURL', ''))
        if video_url:
            st.markdown(f"🎥 [Video]({video_url})")
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_create_post(manager, df, client):
    """Simple post creation form"""
    st.markdown('<div class="main-header"><h2>➕ Create New Post</h2></div>', unsafe_allow_html=True)
    
    with st.form("create_post_form", clear_on_submit=True):
        # Message
        message = st.text_area("Post Message *", height=120, placeholder="Write your social media post here...")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            category = st.text_input("Category", placeholder="e.g., Marketing, Business")
            link = st.text_input("Link", placeholder="https://example.com")
        
        with col2:
            image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
            video_url = st.text_input("Video URL", placeholder="https://example.com/video.mp4")
        
        # Scheduling
        st.markdown("#### Scheduling (Optional)")
        schedule_now = st.checkbox("Schedule this post")
        
        if schedule_now:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                month = st.selectbox("Month", [0] + list(range(1, 13)), format_func=lambda x: "Select" if x == 0 else calendar.month_name[x])
            
            with col2:
                day = st.selectbox("Day", [0] + list(range(1, 32)), format_func=lambda x: "Select" if x == 0 else str(x))
            
            with col3:
                year = st.selectbox("Year", [0] + list(range(2024, 2030)), format_func=lambda x: "Select" if x == 0 else str(x))
            
            with col4:
                hour = st.selectbox("Hour", list(range(0, 24)), format_func=lambda x: f"{x:02d}:00")
            
            with col5:
                minute = st.selectbox("Minute", list(range(0, 60, 15)), format_func=lambda x: f":{x:02d}")
        else:
            month = day = year = hour = minute = 0
        
        # Additional fields
        with st.expander("Additional Fields"):
            col1, col2 = st.columns(2)
            with col1:
                pin_title = st.text_input("Pinterest Title")
                watermark = st.text_input("Watermark")
                cta_group = st.text_input("CTA Group")
            
            with col2:
                first_comment = st.text_area("First Comment")
                story = st.selectbox("Story Post?", ["N", "Y"])
                pinterest_board = st.text_input("Pinterest Board")
            
            alt_text = st.text_area("Alt Text (for accessibility)")
        
        # Submit
        if st.form_submit_button("🚀 Create Post", type="primary"):
            if message:
                # Create new post
                new_row = {
                    'Message': message,
                    'Link': link,
                    'ImageURL': image_url,
                    'VideoURL': video_url,
                    'Month(1-12)': month if month > 0 else '',
                    'Day(1-31)': day if day > 0 else '',
                    'Year': year if year > 0 else '',
                    'Hour': hour if schedule_now and month > 0 else '',
                    'Minute(0-59)': minute if schedule_now and month > 0 else '',
                    'PinTitle': pin_title,
                    'Category': category,
                    'Watermark': watermark,
                    'HashtagGroup': '',
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
                success, result_message = manager.update_sheet(client, st.session_state.sheet_url, new_df)
                
                if success:
                    st.success("✅ Post created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result_message}")
            else:
                st.error("❌ Please enter a message for your post")

def main():
    """Main application function"""
    st.title("🚀 Social Media Manager Pro")
    
    # Initialize manager
    manager = SocialMediaManager()
    
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
    
    # Main content
    if 'google_credentials' in st.session_state and 'sheet_url' in st.session_state:
        # Setup Google Sheets connection
        client, error = manager.setup_google_sheets()
        
        if error:
            st.error(f"❌ {error}")
            return
        
        # Load data
        with st.spinner("📊 Loading data..."):
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
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to Social Media Manager Pro!
        
        **Get started in 3 easy steps:**
        
        1. **📁 Upload Credentials** - Upload your Google service account JSON file
        2. **🔗 Add Sheet URL** - Paste your Google Sheets URL
        3. **🚀 Start Managing** - Begin organizing your social media content!
        
        ### ✨ Features:
        - 📅 **Interactive Calendar** - Click dates to view and edit posts
        - 📋 **Clean Post Management** - View full posts without HTML clutter
        - 📅 **Easy Date Editing** - Dedicated page for scheduling posts
        - 🎯 **Simple Interface** - Clean, intuitive design
        - 📱 **Mobile Friendly** - Works on all devices
        
        **Ready to get organized?** Upload your credentials to begin! 🎯
        """)

if __name__ == "__main__":
    main()

