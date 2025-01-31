import streamlit as st
import cv2
import tempfile
import os
import numpy as np
import pandas as pd
from PIL import Image

# Cache video file to avoid repeated processing
@st.cache_data
def save_uploaded_file(uploaded_file):
    """Save the uploaded video file to a temporary directory and return its path."""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Save uploaded video
    return file_path

# Function to extract frames
@st.cache_data
def extract_frames(video_path):
    """Extracts and caches frames from the video for smoother playback."""
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert BGR to RGB (OpenCV loads as BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
        frame_count += 1

    cap.release()
    return frames, frame_count

# Function to save annotations to CSV
def save_annotations(annotations, csv_path="annotations.csv"):
    """Save clicked points (frame, X, Y, action) to a CSV file."""
    df = pd.DataFrame(annotations, columns=["Frame", "X", "Y", "Action"])
    df.to_csv(csv_path, index=False)
    st.success(f"✅ Annotations saved to {csv_path}")

# Streamlit UI
st.title("📹 Fast Video Processing with Streamlit")

# Upload video
video_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if video_file is not None:
    video_path = save_uploaded_file(video_file)
    
    # Show video using Streamlit's built-in player (much faster)
    st.video(video_path)

    # Extract frames and store them in cache
    frames, total_frames = extract_frames(video_path)

    # Frame navigation
    frame_idx = st.slider("Select Frame", 0, total_frames - 1, 0)

    # Display selected frame
    if frames:
        annotated_frame = frames[frame_idx].copy()  # Copy frame for drawing
        st.image(annotated_frame, caption=f"Frame {frame_idx}", use_column_width=True)

        # Click event simulation (annotation)
        if st.button("Add Annotation"):
            x = st.number_input("X Coordinate", min_value=0, max_value=annotated_frame.shape[1])
            y = st.number_input("Y Coordinate", min_value=0, max_value=annotated_frame.shape[0])
            action = st.selectbox("Select Action", [
                "Center of Mass", "Right Hand Pull", "Right Hand Push", 
                "Left Hand Pull", "Left Hand Push", 
                "Right Foot Pull", "Right Foot Push", 
                "Left Foot Pull", "Left Foot Push"
            ])
            if st.button("Confirm Annotation"):
                st.session_state.annotations.append([frame_idx, x, y, action])
                st.success(f"✅ Annotation added: Frame {frame_idx}, X: {x}, Y: {y}, Action: {action}")

    # Save Annotations
    if st.button("Save Annotations to CSV"):
        save_annotations(st.session_state.annotations)

# Initialize annotation storage
if "annotations" not in st.session_state:
    st.session_state.annotations = []

st.write("🚀 Optimized for speed by caching video frames and using Streamlit's native player.")

