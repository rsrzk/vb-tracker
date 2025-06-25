import streamlit as st
import pandas as pd

# Session state to store entries
if "entries" not in st.session_state:
    st.session_state.entries = []

st.title("🏐 Volleyball Match Logger")

# Video upload
video = st.sidebar.file_uploader("Upload Match Video", type=["mp4", "mov"])
if video:
    st.video(video)

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

