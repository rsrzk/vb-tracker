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
# Load CSV and restore state
if csv_file_path != st.session_state.current_log:
    if csv_file_path and os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
		st.session_state.entries = df.to_dict("records")

		# Restore score from last row
		if not df.empty:
			last_row = df.iloc[-1]
			st.session_state.score = {
				"Team A": int(last_row.get("Score A", 0)),
				"Team B": int(last_row.get("Score B", 0))
			}
			st.session_state.serve_team = last_row.get("Team") if last_row.get("Action") == "Serve" else None
			st.session_state.prev_serve_team = None
			st.session_state.rally = int(last_row.get("Rally", 1))
    else:
        st.session_state.entries = []         # fresh/new file
    st.session_state.current_log = csv_file_path   # remember it

if csv_file_path:
	st.sidebar.success(f"Loaded {len(st.session_state.entries)} entries from `{os.path.basename(csv_file_path)}`")

# --- Initialize session state ---
if "entries" not in st.session_state:
    st.session_state.entries = []

if "rally" not in st.session_state:
    st.session_state.rally = 1

if "serve_team" not in st.session_state:
    st.session_state.serve_team = None

if "prev_serve_team" not in st.session_state:
    st.session_state.prev_serve_team = None

if "rotations" not in st.session_state:
    st.session_state.rotations = {"Team A": [], "Team B": []}

if "score" not in st.session_state:
    st.session_state.score = {"Team A": 0, "Team B": 0}

# --- Setup rotations ---

with st.expander("🔁 Set Initial Rotations"):
    with st.form("rotation_form"):
        col1, col2 = st.columns(2)
        with col1:
            team_a_players = st.text_input("Team A Players (P1 to P6)", "#1,#2,#3,#4,#5,#6")
        with col2:
            team_b_players = st.text_input("Team B Players (P1 to P6)", "#7,#8,#9,#10,#11,#12")
        set_rotations = st.form_submit_button("Set Rotations")

    if set_rotations:
        try:
            st.session_state.rotations = {
                "Team A": [p.strip() for p in team_a_players.split(",")],
                "Team B": [p.strip() for p in team_b_players.split(",")]
            }
            st.session_state.rotation_index = {"Team A": 0, "Team B": 0}

            # Add to CSV log
            for team, rotation in st.session_state.rotations.items():
                st.session_state.entries.append({
                    "Timestamp": "00:00",
                    "Player": "",
                    "Team": team,
                    "Action": "Rotation Init",
                    "Rally": "",
                    "Rotation": ",".join(rotation)
                })
            st.success("Rotations initialized!")
        except Exception as e:
            st.error(f"Failed to set rotations: {e}")

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

# --- New rally ---
st.markdown("### 🎯 Rally Control")
if st.button("Start New Rally"):
    st.session_state.rally += 1
    st.session_state.serve_team = None  # new rally
    st.session_state.entries.append({
        "Timestamp": "",
        "Player": "",
        "Team": "",
        "Action": "Start Rally",
        "Rally": st.session_state.rally,
        "Rotation": ""
    })
    st.success(f"Started Rally #{st.session_state.rally}")

# --- Form input ---
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
				"Action": action,
				"Rally": st.session_state.rally,
				"Rotation": ",".join(st.session_state.rotations[team]) if action == "Serve" else "",
				"Score A": st.session_state.score["Team A"],
				"Score B": st.session_state.score["Team B"]
			}
			st.session_state.entries.append(new_entry)

			# Set serve team if this was a serve
			if action == "Serve":
				#Detect sideout
				if st.session_state.serve_team and team != st.session_state.serve_team:
					# Sideout → award point to receiving team
					st.session_state.score[team] += 1

				# Update rally + serve team
				st.session_state.rally += 1
				st.session_state.prev_serve_team = st.session_state.serve_team
				st.session_state.serve_team = team

				# Input new rotation (e.g. libero switch or sub)
				with st.expander("🔁 Update Rotation Before Serve"):
					rotation_input = st.text_input(f"New rotation for {team} (comma-separated)", value=",".join(st.session_state.rotations[team]))
					if rotation_input:
						st.session_state.rotations[team] = [p.strip() for p in rotation_input.split(",")]
				# Award point to serving team (if not a sideout)
				if team == st.session_state.prev_serve_team:
					st.session_state.score[team] += 1

			df = pd.DataFrame(st.session_state.entries)
			df.to_csv(csv_file_path, index=False)
			st.success("Action logged and saved to " + os.path.basename(csv_file_path))

# --- Table view ---
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

