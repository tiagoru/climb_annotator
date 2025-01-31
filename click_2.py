import cv2
import csv
import tkinter as tk
from tkinter import simpledialog, messagebox

# Initialize global variables
data = []
frame_number = 0
paused = False

def click_event(event, x, y, flags, param):
    global frame_number
    if event == cv2.EVENT_LBUTTONDOWN:
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Create a dialog with "Pull" and "Push" buttons
        def on_pull():
            root.comment = "Pull"
            root.destroy()

        def on_push():
            root.comment = "Push"
            root.destroy()

        dialog = tk.Toplevel(root)
        dialog.title("Select Action")
        tk.Label(dialog, text=f"Click at ({x}, {y}) on frame {frame_number}").pack()
        tk.Button(dialog, text="Pull", command=on_pull).pack(side=tk.LEFT)
        tk.Button(dialog, text="Push", command=on_push).pack(side=tk.RIGHT)
        dialog.mainloop()

        comment = getattr(root, 'comment', None)
        if comment:
            print(f"Clicked at: ({x}, {y}) on frame {frame_number} with comment: {comment}")
            data.append([frame_number, x, y, comment])
            cv2.circle(param, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Video", param)

# Open video
video_path = "NM 2022 Tromso Visningsrute 1.mp4"  # Change this to your video path
print(f"Opening video file: {video_path}")
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

print("Video opened successfully.")

cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Video", click_event)

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            print("Reached end of video.")
            break
        frame_number += 1
        for point in data:
            if point[0] == frame_number:
                cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
        cv2.imshow("Video", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):  # Spacebar to pause/resume
        paused = not paused
    elif key == ord('a'):  # 'A' key to move frame by frame
        if paused:
            ret, frame = cap.read()
            if not ret:
                print("Reached end of video.")
                break
            frame_number += 1
            for point in data:
                if point[0] == frame_number:
                    cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
            cv2.imshow("Video", frame)
    elif key == ord('d'):  # 'D' key to rewind frame by frame
        if paused and frame_number > 0:
            frame_number -= 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            for point in data:
                if point[0] == frame_number:
                    cv2.circle(frame, (point[1], point[2]), 5, (0, 0, 255), -1)
            cv2.imshow("Video", frame)
    elif key == ord('s'):  # 'S' key to save clicked points
        csv_file_path = "clicked_points.csv"
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Frame Number", "X", "Y", "Comment"])
            writer.writerows(data)
        print(f"Clicked points saved to {csv_file_path}.")

cap.release()
cv2.destroyAllWindows()
print("Video processing completed.")