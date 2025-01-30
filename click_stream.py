import streamlit as st
import cv2
import numpy as np
import tempfile
import csv
import os

# Initialize global variables
frame_number = 0
paused = True
clicked_points = []
csv_file_path = "clicked_points.csv"

# 🎥 Streamlit Title
st.title("🧗 Climbing Video Annotator")

# 📂 Upload Video File
uploaded_file = st.file_uploader("📤 Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    # Save uploaded file to a temporary location
    temp_video = tempfile.NamedTemporaryFile(delete=False)
    temp_video.write(uploaded_file.read())

    # Open video using OpenCV
    cap = cv2.VideoCapture(temp_video.name)
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
    frame = get_frame(frame_number)
    if frame is not None:
        st_frame.image(frame, caption=f"Frame {frame_number}/{total_frames}")

    # 🎯 Click Handler
    def save_click(x, y, action):
        global frame_number
        clicked_points.append([frame_number, x, y, action])
        save_to_csv(frame_number, x, y, action)
        st.success(f"✅ Clicked at ({x}, {y}) on Frame {frame_number} - Action: {action}")

    # 📌 Save Clicks to CSV
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
        if st.button("⏪ Previous Frame") and frame_number > 0:
            frame_number -= 1
    with col2:
        if st.button("⏯ Pause/Play"):
            paused = not paused
    with col3:
        if st.button("⏩ Next Frame") and frame_number < total_frames - 1:
            frame_number += 1

    # 🏃 Auto-Play Video if Not Paused
    if not paused:
        frame_number += 1
        if frame_number >= total_frames:
            frame_number = 0  # Loop back to the start

    # 🖼 Update Frame Display
    frame = get_frame(frame_number)
    if frame is not None:
        st_frame.image(frame, caption=f"Frame {frame_number}/{total_frames}")

    cap.release()
