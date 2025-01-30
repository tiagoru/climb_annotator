import streamlit as st
import cv2
import numpy as np
import tempfile
import time
import csv
import os

# 🎥 Streamlit UI
st.title("🧗 Climbing Video Annotator")

# Initialize session state
if "frame_number" not in st.session_state:
    st.session_state.frame_number = 0
if "paused" not in st.session_state:
    st.session_state.paused = True
if "clicked_points" not in st.session_state:
    st.session_state.clicked_points = []
if "cap" not in st.session_state:
    st.session_state.cap = None

# 📂 Upload Video File
uploaded_file = st.file_uploader("📤 Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    # Save uploaded file to a temporary location
    temp_video = tempfile.NamedTemporaryFile(delete=False)
    temp_video.write(uploaded_file.read())

    # Open video using OpenCV
    cap = cv2.VideoCapture(temp_video.name)
    st.session_state.cap = cap  # Store in session state
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 📌 Helper function to get a frame
    def get_frame(frame_num):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            return frame
        return None

    # 🖼 Display Frame
    st_frame = st.empty()  # Placeholder for video frame
    frame = get_frame(st.session_state.frame_number)
    if frame is not None:
        st_frame.image(frame, caption=f"Frame {st.session_state.frame_number}/{total_frames}")

    # 🎯 Click Handler
    def save_click(x, y, action):
        st.session_state.clicked_points.append([st.session_state.frame_number, x, y, action])
        save_to_csv(st.session_state.frame_number, x, y, action)
        st.success(f"✅ Clicked at ({x}, {y}) on Frame {st.session_state.frame_number} - Action: {action}")

    # 📌 Save Clicks to CSV
    csv_file_path = "clicked_points.csv"

    def save_to_csv(frame, x, y, action):
        file_exists = os.path.exists(csv_file_path)
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Frame Number", "X", "Y", "Action"])
            writer.writerow([frame, x, y, action])

    # 🖱 Mouse Click Event
    st.sidebar.header("🖱 Click Annotation")
    click_x = st.sidebar.number_input("X Coordinate", min_value=0, value=100)
    click_y = st.sidebar.number_input("Y Coordinate", min_value=0, value=100)
    action = st.sidebar.selectbox("Select Action", [
        "Center of Mass", "Right Hand Pull", "Right Hand Push",
        "Left Hand Pull", "Left Hand Push", "Right Foot Pull",
        "Right Foot Push", "Left Foot Pull", "Left Foot Push"
    ])
    if st.sidebar.button("🔘 Save Click"):
        save_click(click_x, click_y, action)

    # 🎥 Video Playback Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏪ Previous Frame") and st.session_state.frame_number > 0:
            st.session_state.frame_number -= 1
    with col2:
        if st.button("⏯ Pause/Play"):
            st.session_state.paused = not st.session_state.paused
    with col3:
        if st.button("⏩ Next Frame") and st.session_state.frame_number < total_frames - 1:
            st.session_state.frame_number += 1

    # 🎬 Auto-Play Video if Not Paused
    while not st.session_state.paused:
        frame = get_frame(st.session_state.frame_number)
        if frame is not None:
            st_frame.image(frame, caption=f"Frame {st.session_state.frame_number}/{total_frames}")
            time.sleep(1 / fps)  # Simulate real-time playback
            st.session_state.frame_number += 1
            if st.session_state.frame_number >= total_frames:
                st.session_state.frame_number = 0  # Restart video

    cap.release()
