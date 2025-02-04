import cv2
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

def save_click_to_csv(frame_number, x, y, comment):
    """Append a single click event to the CSV file without overwriting previous data."""
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header only if file does not exist
            writer.writerow(["Frame Number", "X", "Y", "Comment"])
        writer.writerow([frame_number, x, y, comment])

    print(f"✅ Saved: Frame {frame_number}, X: {x}, Y: {y}, Action: {comment}")

def click_event(event, x, y, flags, param):
    global frame
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

def move_to_next_frame():
    """Advance to the next frame only when the user requests."""
    global frame_number, frame
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

def move_to_previous_frame():
    """Go back one frame when the user requests."""
    global frame_number, frame
    if frame_number > 0:
        frame_number -= 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if not ret or frame is None or frame.size == 0:
            print("Failed to read frame.")
            return

        draw_frame_number()
        for point in data:
            if point[0] == frame_number:
                cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)

        cv2.imshow("Video", frame)

def draw_frame_number():
    """Draw the frame number in the top-left corner of the video."""
    if frame is not None and frame.size > 0:
        cv2.putText(frame, f"Frame: {frame_number}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Open video
video_path = "NM 2022 Tromso Visningsrute 1.mp4"  # Change this to your video path
print(f"🎥 Opening video file: {video_path}")
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Error: Could not open video.")
    exit()

print("✅ Video opened successfully.")

cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Video", click_event)

# Read the first frame
ret, frame = cap.read()
if ret:
    draw_frame_number()
    cv2.imshow("Video", frame)
else:
    print("❌ Error reading the first frame.")

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):  # Quit
        break
    elif key == ord(' '):  # Toggle pause/play
        paused = not paused
    elif key == ord('a'):  # Move to next frame (manual)
        move_to_next_frame()
    elif key == ord('d'):  # Move to previous frame
        move_to_previous_frame()
    
    if not paused:  # If not paused, keep playing video
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("Reached end of video.")
            break
        frame_number += 1
        draw_frame_number()
        for point in data:
            if point[0] == frame_number:
                cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
        cv2.imshow("Video", frame)

cap.release()
cv2.destroyAllWindows()
print("✅ Video processing completed.")
