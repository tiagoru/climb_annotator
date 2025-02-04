# **Climb Annotator**  
### *by Tiago G. Russomanno | 31.01.2025*

---

## **🎥 Overview**

**Climb Annotator** is a **Video Frame Annotator** tool that allows users to annotate specific points on video frames. It is particularly useful for analyzing movements, marking key locations, and tracking interactions within videos.

### **Key Features:**
- Open a video file from your computer (file selection prompt integrated).
- Click on the video to annotate points with defined actions.
- Choose actions from a predefined list for each annotation.
- Navigate through the video frame-by-frame using keyboard shortcuts.
- Save all annotations to a CSV file for easy data analysis.

---

## **🛠 Features**
- ✅ Select and open video files from your local storage.  
- ✅ Click anywhere on the video to add annotations.  
- ✅ Choose from predefined actions (e.g., "Right Hand Pull", "Left Foot Push").  
- ✅ Navigate frame-by-frame using **A** (next) and **D** (previous) keys.  
- ✅ Pause and resume playback using the **Spacebar**.  
- ✅ All annotations are automatically saved in a **CSV file** (`clicked_points.csv`).  

---

## **📥 Installation**

### **1️⃣ Prerequisites**
Ensure you have **Python 3.8+** installed on your system.

### **2️⃣ Install Dependencies**
Run the following command in your terminal to install the necessary libraries:

```bash
pip install opencv-python tkinter
```

---

## **3️⃣ How to Use**

1. **Run the Script**  
   Execute the script to launch the application.

2. **Select a Video**  
   When prompted, choose a video file from your local storage.

3. **Annotate Points**  
   Click on any point in the video to add an annotation. A pop-up menu will appear asking you to select an action.

4. **Choose an Action**  
   Pick an action from the list (e.g., "Right Hand Pull", "Left Foot Push") for the selected point.

5. **Navigate Frames**  
   - **Next Frame**: Press the **A** key to move to the next frame.
   - **Previous Frame**: Press the **D** key to move back to the previous frame.

6. **Pause/Resume Playback**  
   Press the **Spacebar** to toggle between pausing and resuming video playback.

7. **Annotations Saved Automatically**  
   All clicked points, their associated actions, and frame information will be saved in the `clicked_points.csv` file located in the same directory as the script.

---

## **📄 License**
This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for more details.

---

## still on development
