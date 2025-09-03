import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import requests
from io import BytesIO
import os

# ------------------------
# App Setup
# ------------------------
st.set_page_config(page_title="IG Post Scheduler", layout="wide")
st.title("📸 Instagram Post Scheduler")

# ------------------------
# Demo Data
# ------------------------
demo_images = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
    "https://images.unsplash.com/photo-1501594907352-04cda38ebc29",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
    "https://images.unsplash.com/photo-1519125323398-675f0ddb6308",
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
    "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e",
    "https://images.unsplash.com/photo-1487412912498-0447578fcca8",
    "https://images.unsplash.com/photo-1520975918318-7da438c3c91a",
    "https://images.unsplash.com/photo-1522205408450-add114ad53fe"
]

# Initialize session
if "posts" not in st.session_state:
    st.session_state.posts = pd.DataFrame([
        {"ImagePath": url, "Caption": f"Demo caption {i+1}", "PostDate": str((datetime.today() + timedelta(days=i)).date())}
        for i, url in enumerate(demo_images)
    ])

# ------------------------
# Tabs
# ------------------------
tab1, tab2, tab3 = st.tabs(["➕ Upload", "📅 Calendar View", "⚙️ Manage Posts"])

# ------------------------
# Upload Section
# ------------------------
with tab1:
    st.header("➕ Upload New Instagram Post")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    caption = st.text_area("Caption (text on bottom)", "")
    post_date = st.date_input("Schedule Post Date", min_value=datetime.today().date())

    if st.button("Save Post"):
        if uploaded_file:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            new_row = pd.DataFrame([{
                "ImagePath": file_path,
                "Caption": caption if caption else "No caption",
                "PostDate": str(post_date)
            }])
            st.session_state.posts = pd.concat([st.session_state.posts, new_row], ignore_index=True)
            st.success("✅ Post saved successfully!")

# ------------------------
# Calendar/Grid View
# ------------------------
with tab2:
    st.header("📅 Scheduled Posts (Grid)")

    if not st.session_state.posts.empty:
        # Filters
        st.sidebar.subheader("🔎 Filters")
        search_text = st.sidebar.text_input("Search by caption")
        sort_order = st.sidebar.radio("Sort by date", ["Ascending", "Descending"])

        posts = st.session_state.posts.copy()

        # Search filter
        if search_text:
            posts = posts[posts["Caption"].str.contains(search_text, case=False)]

        # Sort
        posts = posts.sort_values("PostDate", ascending=True if sort_order == "Ascending" else False)

        # Display grid
        cols = st.columns(3)
        for i, row in posts.iterrows():
            col = cols[i % 3]
            with col:
                try:
                    if str(row["ImagePath"]).startswith("http"):
                        response = requests.get(row["ImagePath"])
                        img = Image.open(BytesIO(response.content))
                    else:
                        img = Image.open(row["ImagePath"])
                    st.image(img, use_column_width=True)
                except:
                    st.warning("⚠️ Could not load image")

                st.caption(row["Caption"])
                st.write(f"📅 {row['PostDate']}")

                # Inline date edit
                new_date = st.date_input(
                    f"Edit Date for {i}",
                    value=datetime.strptime(row["PostDate"], "%Y-%m-%d").date(),
                    key=f"date_{i}"
                )
                if new_date != datetime.strptime(row["PostDate"], "%Y-%m-%d").date():
                    st.session_state.posts.at[i, "PostDate"] = str(new_date)
                    st.info(f"Updated date for post {i+1} ✅")
    else:
        st.info("No posts scheduled yet.")

# ------------------------
# Manage Section
# ------------------------
with tab3:
    st.header("⚙️ Manage Posts")

    if not st.session_state.posts.empty:
        st.dataframe(st.session_state.posts)

        # Export to CSV
        csv = st.session_state.posts.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Posts as CSV",
            data=csv,
            file_name="scheduled_posts.csv",
            mime="text/csv"
        )

        # Import from CSV
        uploaded_csv = st.file_uploader("Upload CSV to import posts", type=["csv"], key="csv")
        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
            st.session_state.posts = pd.concat([st.session_state.posts, df], ignore_index=True)
            st.success("✅ Imported posts from CSV")
    else:
        st.info("No posts available to manage yet.")
