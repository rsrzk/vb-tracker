import streamlit as st
import pandas as pd
import os

# Session state to store entries
if "entries" not in st.session_state:
    st.session_state.entries = []

st.title("🏐 Volleyball Match Logger")

# --- Video selection section ---

st.sidebar.header("🎞️ Select or enter a video")
video_dir = "videos"
available_videos = []

# List video files from folder if it exists
if os.path.exists(video_dir):
	available_videos = [
		f for f in os.listdir(video_dir)
		if f.lower().endswith(('.mp4', '.mov', '.avi'))
	]

# Dropdown selection
selected_video = st.sidebar.selectbox("Choose from /videos folder:", ["-- Select --"] + available_videos)

# Manual path input
custom_video_path = st.sidebar.text_input("Or enter a full video path manually:")

# Determine final video path
video_path = None
if custom_video_path.strip() != "":
    video_path = custom_video_path
elif selected_video != "-- Select --":
    video_path = os.path.join(video_dir, selected_video)

# --- File validation ---
if video_path:
    if not os.path.exists(video_path):
        st.error(f"⚠️ File not found: `{video_path}`")
    else:
        try:
            st.video(video_path)
        except Exception as e:
            st.error(f"❌ Could not load video: {e}")
else:
    st.info("No video selected yet.")

# Form input
with st.form("log_form"):
    timestamp = st.text_input("Timestamp (e.g. 00:12)")
    player = st.text_input("Player (e.g. #5)")
    team = st.selectbox("Team", ["Team A", "Team B"])
    action = st.selectbox("Action", ["Serve", "First Touch", "Second Touch", "Third Touch", "Block"])
    submitted = st.form_submit_button("Log Action")

    if submitted:
        st.session_state.entries.append({
            "Timestamp": timestamp,
            "Player": player,
            "Team": team,
            "Action": action
        })
        st.success("Action logged!")

# Table view
st.header("📊 Logged Data")
if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "volleyball_log.csv", "text/csv")
else:
    st.info("No entries yet.")

