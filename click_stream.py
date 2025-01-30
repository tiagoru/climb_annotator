import streamlit as st
import numpy as np
import cv2
import os
import tempfile
from streamlit_drawable_canvas import st_canvas
import csv

# Initialize global variables
data = []
frame_number = 0
paused = True  # Start in paused mode
csv_file_path = "clicked_points.csv"
frame = None  # Store the current frame
cap = None  # Initialize the video capture object

# Function to save the click events to CSV file
def save_click_to_csv(frame_number, x, y, comment):
    """Append a single click event to the CSV file without overwriting previous data."""
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header only if file does not exist
            writer.writerow(["Frame Number", "X", "Y", "Comment"])
        writer.writerow([frame_number, x, y, comment])

    print(f"✅ Saved: Frame {frame_number}, X: {x}, Y: {y}, Action: {comment}")

# Function to handle mouse click events
def handle_click(x, y):
    global frame_number
    actions = [
        "Center of Mass", "Right Hand Pull", "Right Hand Push", "Left Hand Pull", 
        "Left Hand Push", "Right Foot Pull", "Right Foot Push", "Left Foot Pull", "Left Foot Push"
    ]

    # Let user select the action from a dropdown
    comment = st.selectbox(f"Select Action for Click at ({x}, {y}) on Frame {frame_number}", actions)
    
    # Save the click to CSV file
    if comment:
        print(f"🖱 Clicked at: ({x}, {y}) on frame {frame_number} with action: {comment}")
        data.append([frame_number, x, y, comment])
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)  # Draw on the frame
        save_click_to_csv(frame_number, x, y, comment)  # Save to CSV

# Function to convert video frame to image for canvas background
def video_to_image(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Function to move to the next frame
def move_to_next_frame():
    global frame_number, frame, cap
    frame_number += 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if not ret or frame is None or frame.size == 0:
        print("Reached end of video or failed to read frame.")
        return

    draw_frame_number()  # Ensure frame number is displayed
    for point in data:
        if point[0] == frame_number:
            cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
    
    st.image(video_to_image(frame), caption=f"Frame {frame_number}", channels="RGB", use_column_width=True)

# Function to draw the frame number on the frame
def draw_frame_number():
    if frame is not None and frame.size > 0:
        cv2.putText(frame, f"Frame: {frame_number}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Streamlit UI
st.title("🧗 Climbing Video Annotator")

# Allow the user to upload a video file
video_file = st.file_uploader("Upload Video", type=["mp4"])

if video_file is not None:
    # Save the uploaded video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(video_file.read())  # Write the uploaded file content to the temporary file
        tmp_file_path = tmp_file.name  # Store the temporary file path
    
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(tmp_file_path)

    # Ensure cap is successfully opened before proceeding
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            background_image = video_to_image(frame)  # Convert to RGB for canvas background
        else:
            background_image = None

        # Show canvas only if the background image is available
        if background_image is not None and isinstance(background_image, np.ndarray) and background_image.any():
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Set canvas background
                background_image=background_image,
                width=frame.shape[1],
                height=frame.shape[0],
                drawing_mode="freedraw",
                key="canvas",
            )

            # If the user clicks on the canvas, record the coordinates
            if canvas_result.json_data is not None:
                clicks = canvas_result.json_data['objects']
                for click in clicks:
                    x, y = click['left'], click['top']
                    handle_click(x, y)  # Handle the click using Streamlit components

        else:
            st.error("Error: Unable to load video frame as background image.")

        # Streamlit controls for video
        st.sidebar.title("Controls")
        if st.sidebar.button("Next Frame"):
            move_to_next_frame()
        if st.sidebar.button("Previous Frame"):
            move_to_previous_frame()

else:
    st.error("Please upload a video file to start.")

# Release video capture at the end
if cap is not None:
    cap.release()

# cv2.destroyAllWindows()  # Removed because it's not necessary in a headless environment
