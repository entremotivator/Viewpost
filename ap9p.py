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

# Page configuration
st.set_page_config(
    page_title="Social Media Post Manager",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .post-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 20px;
        margin: 10px;
        border-left: 4px solid #1f77b4;
        transition: transform 0.2s ease;
    }
    .post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .post-message {
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 15px;
        color: #333;
    }
    .post-meta {
        font-size: 12px;
        color: #666;
        margin-bottom: 8px;
    }
    .post-actions {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    .media-container {
        max-height: 200px;
        overflow: hidden;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .status-scheduled {
        background: #e3f2fd;
        color: #1976d2;
    }
    .status-queued {
        background: #f3e5f5;
        color: #7b1fa2;
    }
    .character-count {
        font-size: 11px;
        color: #888;
        text-align: right;
        margin-top: 5px;
    }
    .platform-limits {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
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
            'Facebook': 63206,
            'Instagram': 2200,
            'Bluesky': 300,
            'LinkedIn': 3000,
            'Twitter/X': 280,
            'Google My Business': 1500,
            'Pinterest': 500,
            'TikTok': 150
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
                # If sheet is empty, create headers
                sheet.append_row(self.column_names)
                return pd.DataFrame(columns=self.column_names)
            
            df = pd.DataFrame(data)
            
            # Ensure all required columns exist
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
            
            # Update with headers and data
            data_to_upload = [self.column_names] + df.fillna('').values.tolist()
            sheet.update(f'A1:S{len(data_to_upload)}', data_to_upload)
            return True, "Sheet updated successfully!"
        except Exception as e:
            return False, f"Error updating sheet: {str(e)}"
    
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
    
    def truncate_text(self, text, max_length):
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def get_post_status(self, row):
        """Determine post status based on scheduling info"""
        if any([row.get(f, '') for f in ['Month(1-12)', 'Day(1-31)', 'Year', 'Hour']]):
            return "Scheduled", "status-scheduled"
        return "Queued", "status-queued"
    
    def display_post_card(self, row, index):
        """Display a single post as a card"""
        status, status_class = self.get_post_status(row)
        
        # Create card HTML
        card_html = f"""
        <div class="post-card">
            <div class="status-badge {status_class}">{status}</div>
            <div class="post-message">{self.truncate_text(row.get('Message', ''), 200)}</div>
        """
        
        # Add scheduling info if available
        if status == "Scheduled":
            schedule_info = f"{row.get('Month(1-12)', '')}/{row.get('Day(1-31)', '')}/{row.get('Year', '')} at {row.get('Hour', '')}:{row.get('Minute(0-59)', '0')}"
            card_html += f'<div class="post-meta">📅 Scheduled: {schedule_info}</div>'
        
        # Add category and other meta info
        if row.get('Category'):
            card_html += f'<div class="post-meta">🏷️ Category: {row.get("Category")}</div>'
        
        if row.get('Link'):
            card_html += f'<div class="post-meta">🔗 <a href="{row.get("Link")}" target="_blank">Link attached</a></div>'
        
        # Character count for different platforms
        message_length = len(row.get('Message', ''))
        card_html += f'<div class="character-count">Character count: {message_length}</div>'
        
        card_html += "</div>"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Display media if available
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
            if st.button("✏️ Edit", key=f"edit_{index}"):
                st.session_state.editing_post = index
                st.rerun()
            
            if st.button("🗑️ Delete", key=f"delete_{index}"):
                st.session_state.delete_post = index
                st.rerun()
            
            if st.button("📋 Duplicate", key=f"duplicate_{index}"):
                st.session_state.duplicate_post = index
                st.rerun()

def main():
    st.title("📱 Social Media Post Manager")
    st.markdown("Manage your social media posts with Google Sheets integration")
    
    manager = SocialMediaManager()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google Sheets credentials upload
        st.subheader("Google Sheets Setup")
        credentials_file = st.file_uploader(
            "Upload Google Service Account JSON",
            type="json",
            help="Upload your Google service account credentials file"
        )
        
        if credentials_file:
            credentials_dict = json.load(credentials_file)
            st.session_state.google_credentials = credentials_dict
            st.success("✅ Credentials loaded!")
        
        # Google Sheets URL
        sheet_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste your Google Sheets URL here"
        )
        
        if sheet_url:
            st.session_state.sheet_url = sheet_url
        
        # Platform character limits display
        st.subheader("📊 Platform Limits")
        with st.expander("Character Limits"):
            for platform, limit in manager.platform_limits.items():
                st.write(f"**{platform}:** {limit:,}")
    
    # Main content area
    if 'google_credentials' not in st.session_state:
        st.warning("⚠️ Please upload your Google service account credentials in the sidebar")
        
        # Show setup instructions
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            ### Google Sheets API Setup:
            
            1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
            2. **Create a new project** or select existing one
            3. **Enable Google Sheets API**:
               - Go to "APIs & Services" > "Library"
               - Search for "Google Sheets API"
               - Click "Enable"
            4. **Create Service Account**:
               - Go to "APIs & Services" > "Credentials"
               - Click "Create Credentials" > "Service Account"
               - Fill in the details and create
            5. **Download JSON Key**:
               - Click on your service account
               - Go to "Keys" tab
               - Click "Add Key" > "Create new key" > "JSON"
               - Download the JSON file
            6. **Share your Google Sheet**:
               - Open your Google Sheet
               - Click "Share" button
               - Add your service account email (found in the JSON file)
               - Give "Editor" permissions
            
            ### Your Sheet URL is already pre-filled!
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
    with st.spinner("Loading data from Google Sheets..."):
        df = manager.get_sheet_data(client, st.session_state.sheet_url)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Posts", "➕ Add New Post", "📊 Analytics", "⚙️ Bulk Actions"])
    
    with tab1:
        st.header("📋 Your Social Media Posts")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + list(df['Category'].dropna().unique()) if not df.empty else ["All"]
            )
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Queued"])
        
        with col3:
            search_term = st.text_input("Search in messages", placeholder="Search posts...")
        
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
        
        st.write(f"Showing {len(filtered_df)} of {len(df)} posts")
        
        # Display posts in grid
        if not filtered_df.empty:
            # Grid layout - 2 columns for posts
            for i in range(0, len(filtered_df), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    if i + j < len(filtered_df):
                        with col:
                            manager.display_post_card(filtered_df.iloc[i + j], i + j)
        else:
            st.info("No posts found matching your filters.")
        
        # Handle post actions
        if 'delete_post' in st.session_state:
            if st.button("Confirm Delete", type="secondary"):
                df = df.drop(df.index[st.session_state.delete_post]).reset_index(drop=True)
                success, message = manager.update_sheet(client, st.session_state.sheet_url, df)
                if success:
                    st.success(message)
                else:
                    st.error(message)
                del st.session_state.delete_post
                st.rerun()
            
            if st.button("Cancel"):
                del st.session_state.delete_post
                st.rerun()
    
    with tab2:
        st.header("➕ Add New Social Media Post")
        
        # Form for adding new post
        with st.form("new_post_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                message = st.text_area(
                    "Message *",
                    height=100,
                    help="Your social media post content"
                )
                
                # Character count display
                if message:
                    st.write("**Character counts:**")
                    for platform, limit in manager.platform_limits.items():
                        count = len(message)
                        color = "green" if count <= limit else "red"
                        st.markdown(
                            f"<span style='color: {color}'>{platform}: {count}/{limit}</span>",
                            unsafe_allow_html=True
                        )
                
                link = st.text_input("Link", placeholder="https://example.com")
                image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
                video_url = st.text_input("Video URL (.mp4)", placeholder="https://example.com/video.mp4")
                category = st.text_input("Category", placeholder="e.g., Marketing, Food, Tech")
            
            with col2:
                st.subheader("Scheduling (Optional)")
                st.caption("Leave blank to add to queue")
                
                schedule_col1, schedule_col2 = st.columns(2)
                with schedule_col1:
                    month = st.selectbox("Month", [""] + list(range(1, 13)))
                    day = st.selectbox("Day", [""] + list(range(1, 32)))
                    year = st.selectbox("Year", [""] + list(range(2024, 2030)))
                
                with schedule_col2:
                    hour = st.selectbox("Hour (24h)", [""] + list(range(0, 24)))
                    minute = st.selectbox("Minute", ["", "Random"] + list(range(0, 60)))
                
                st.subheader("Additional Options")
                pin_title = st.text_input("Pinterest Title")
                watermark = st.text_input("Watermark", placeholder="Default or watermark name")
                hashtag_group = st.text_input("Hashtag Group")
                cta_group = st.text_input("CTA Group")
                first_comment = st.text_area("First Comment", height=60)
                
                col_story, col_board = st.columns(2)
                with col_story:
                    story = st.selectbox("Post as Story?", ["", "Y", "N"])
                with col_board:
                    pinterest_board = st.text_input("Pinterest Board")
                
                alt_text = st.text_area("Alt Text", height=60, placeholder="Describe images for accessibility")
            
            submitted = st.form_submit_button("Add Post", type="primary")
            
            if submitted:
                if not message:
                    st.error("Message is required!")
                else:
                    # Create new row
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
                        st.success("✅ Post added successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {message_result}")
    
    with tab3:
        st.header("📊 Analytics Overview")
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Posts", len(df))
            
            with col2:
                scheduled_count = len(df[
                    (df['Month(1-12)'] != '') | 
                    (df['Day(1-31)'] != '') | 
                    (df['Year'] != '')
                ])
                st.metric("Scheduled Posts", scheduled_count)
            
            with col3:
                queued_count = len(df) - scheduled_count
                st.metric("Queued Posts", queued_count)
            
            with col4:
                posts_with_media = len(df[
                    (df['ImageURL'] != '') | (df['VideoURL'] != '')
                ])
                st.metric("Posts with Media", posts_with_media)
            
            # Category breakdown
            if 'Category' in df.columns and not df['Category'].isna().all():
                st.subheader("Posts by Category")
                category_counts = df['Category'].value_counts()
                st.bar_chart(category_counts)
            
            # Character length analysis
            st.subheader("Message Length Analysis")
            df['message_length'] = df['Message'].str.len()
            st.histogram(df['message_length'], bins=20)
        
        else:
            st.info("No data available for analytics.")
    
    with tab4:
        st.header("⚙️ Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Data")
            if st.button("📥 Download as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"social_media_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.subheader("Import Data")
            uploaded_file = st.file_uploader("📤 Upload CSV", type="csv")
            
            if uploaded_file:
                try:
                    new_df = pd.read_csv(uploaded_file)
                    
                    # Ensure all required columns exist
                    for col in manager.column_names:
                        if col not in new_df.columns:
                            new_df[col] = ''
                    
                    new_df = new_df[manager.column_names]
                    
                    if st.button("Import Data", type="primary"):
                        success, message = manager.update_sheet(
                            client, st.session_state.sheet_url, new_df
                        )
                        if success:
                            st.success("✅ Data imported successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {message}")
                    
                    st.write("Preview of uploaded data:")
                    st.dataframe(new_df.head())
                    
                except Exception as e:
                    st.error(f"Error reading CSV: {str(e)}")
        
        st.subheader("Bulk Operations")
        
        if not df.empty:
            bulk_col1, bulk_col2 = st.columns(2)
            
            with bulk_col1:
                if st.button("🗑️ Clear All Data", type="secondary"):
                    if st.button("Confirm Clear All", type="secondary"):
                        empty_df = pd.DataFrame(columns=manager.column_names)
                        success, message = manager.update_sheet(
                            client, st.session_state.sheet_url, empty_df
                        )
                        if success:
                            st.success("✅ All data cleared!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {message}")
            
            with bulk_col2:
                category_to_delete = st.selectbox(
                    "Delete by Category",
                    ["Select category..."] + list(df['Category'].dropna().unique())
                )
                
                if category_to_delete != "Select category...":
                    if st.button(f"Delete all '{category_to_delete}' posts"):
                        filtered_df = df[df['Category'] != category_to_delete]
                        success, message = manager.update_sheet(
                            client, st.session_state.sheet_url, filtered_df
                        )
                        if success:
                            st.success(f"✅ Deleted all posts in '{category_to_delete}' category!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {message}")

if __name__ == "__main__":
    main()
