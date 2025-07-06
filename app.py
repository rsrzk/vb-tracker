import streamlit as st
import pandas as pd
import os


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

st.title("🏐 Volleyball Match Logger")

# --- Load CSV selection ---
st.sidebar.header("📄 Load Match Log")

# List all CSVs in logs directory
log_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".csv")]
selected_log = st.sidebar.selectbox("Select a CSV to load or start new:", ["-- New Match --"] + log_files)

# Determine file path and load mode
if selected_log != "-- New Match --":
	csv_file_path = os.path.join(LOG_DIR, selected_log)
	load_csv = True
	new_log_name = None
else:
	new_log_name = st.sidebar.text_input("Enter new match log name (no spaces):", value="match1")
	if new_log_name:
		safe_name = new_log_name.strip().replace(" ", "_")
		csv_file_path = os.path.join(LOG_DIR, f"{safe_name}.csv")
		load_csv = os.path.exists(csv_file_path)
	else:
		csv_file_path = None
		load_csv = False

# Keep track of which log is currently loaded
if "current_log" not in st.session_state:
    st.session_state.current_log = None

# If the user picked a DIFFERENT file (or first time)
if csv_file_path != st.session_state.current_log:
    if csv_file_path and os.path.exists(csv_file_path):
        st.session_state.entries = (
            pd.read_csv(csv_file_path).to_dict("records")
        )
    else:
        st.session_state.entries = []         # fresh/new file
    st.session_state.current_log = csv_file_path   # remember it

if csv_file_path:
	st.sidebar.success(f"Loaded {len(st.session_state.entries)} entries from `{os.path.basename(csv_file_path)}`")

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
		if not csv_file_path:
			st.error("❗ Please enter a file name before logging data.")
		else:
			new_entry = {
				"Timestamp": timestamp,
				"Player": player,
				"Team": team,
				"Action": action
			}
			st.session_state.entries.append(new_entry)
			df = pd.DataFrame(st.session_state.entries)
			df.to_csv(csv_file_path, index=False)
			st.success("Action logged and saved to " + os.path.basename(csv_file_path))

# Table view
st.header("📊 Logged Data")

if csv_file_path:
    st.sidebar.caption(f"📁 Current file: `{os.path.basename(csv_file_path)}`")

if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "volleyball_log.csv", "text/csv")
else:
    st.info("No entries yet.")

