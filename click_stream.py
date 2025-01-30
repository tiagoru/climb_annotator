import streamlit as st
import numpy as np
import cv2
from streamlit_drawable_canvas import st_canvas
import csv
import os
import tkinter as tk
from tkinter import messagebox

# Initialize global variables
data = []
frame_number = 0
paused = True  # Start in paused mode
csv_file_path = "clicked_points.csv"
frame = None  # Store the current frame
video_path = "NM 2022 Tromso Visningsrute 1.mp4"  # Replace with your video path

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
def click_event(event, x, y, flags, param):
    global frame, frame_number
    if event == cv2.EVENT_LBUTTONDOWN:
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Create a dialog with action buttons
        def on_action(action):
            if messagebox.askyesno("Confirm Action", f"Do you confirm '{action}' for frame {frame_number}?"):
                root.comment = action
                root.destroy()

        dialog = tk.Toplevel(root)
        dialog.title("Select Action")
        tk.Label(dialog, text=f"Click at ({x}, {y}) on frame {frame_number}").pack()
        actions = ["Center of Mass", "Right Hand Pull", "Right Hand Push", "Left Hand Pull", "Left Hand Push",
                   "Right Foot Pull", "Right Foot Push", "Left Foot Pull", "Left Foot Push"]
        for action in actions:
            tk.Button(dialog, text=action, command=lambda a=action: on_action(a)).pack()
        dialog.mainloop()

        comment = getattr(root, 'comment', None)
        if comment:
            print(f"🖱 Clicked at: ({x}, {y}) on frame {frame_number} with action: {comment}")
            data.append([frame_number, x, y, comment])
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)  # Draw on the frame
            cv2.imshow("Video", frame)  # Update frame display
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
    
    cv2.imshow("Video", frame)

# Function to draw the frame number on the frame
def draw_frame_number():
    if frame is not None and frame.size > 0:
        cv2.putText(frame, f"Frame: {frame_number}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    st.error("Error: Unable to open video file.")
    exit()

# Read the first frame
ret, frame = cap.read()
if ret:
    background_image = video_to_image(frame)  # Convert to RGB for canvas background
else:
    background_image = None

# Streamlit UI
st.title("🧗 Climbing Video Annotator")

# Show canvas only if the background image is available
if background_image is not None and isinstance(background_image, np.ndarray):
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
            comment = "User Defined Action"  # You can add logic here to define actions
            save_click_to_csv(frame_number, x, y, comment)

else:
    st.error("Error: Unable to load video frame as background image.")

# Streamlit controls for video
st.sidebar.title("Controls")
if st.sidebar.button("Next Frame"):
    move_to_next_frame()
if st.sidebar.button("Previous Frame"):
    move_to_previous_frame()

# Display the video and handle key presses for navigation
if not paused:
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        print("Reached end of video.")
        st.stop()  # Stop Streamlit app if video ends
    frame_number += 1
    draw_frame_number()
    for point in data:
        if point[0] == frame_number:
            cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
    cv2.imshow("Video", frame)

cap.release()
cv2.destroyAllWindows()
