import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import time
from ultralytics import YOLO
from sort import *
from twilio.rest import Client

# Twilio configuration
ACCOUNT_SID = "Create a Twilio account"
AUTH_TOKEN = "get SID,Token,twilio-no"
TWILIO_PHONE = "********"
TARGET_PHONE = "+9112345678"
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_alert(camera_index):
    message = client.messages.create(
        body=f"Alert: Vehicle count exceeded 50 at camera {camera_index + 1}",
        from_=TWILIO_PHONE,
        to=TARGET_PHONE
    )


def start_main_program():
    welcome_window.destroy()  # Close the welcome page

    # Load video sources
    video_paths = [
        "traffic4.mp4",
        "traffic8.mp4",
        "traffic3.mp4",
        "traffic4.mp4"
    ]
    caps = [cv2.VideoCapture(path) for path in video_paths]

    # Load YOLO model
    global model
    model = YOLO('object detection project/yolov8s.pt')
    
    vehicle_classes = {"car", "truck", "motorbike", "bus", "bicycle"}

    vehicle_counts = [0 for _ in range(4)]
    tracking_ids = [set() for _ in range(4)]
    trackers = [Sort(max_age=2, min_hits=1, iou_threshold=0.3) for _ in range(4)]
    alert_sent_flags = [False for _ in range(4)]  # Flag to prevent repeated alerts
    
    screen_width, screen_height = 1600, 900
    FRAME_WIDTH, FRAME_HEIGHT = screen_width // 2, screen_height // 2
    LINE_THICKNESS = 4

    current_video = -1
    time_left = 0

    cv2.namedWindow("ML-Powered Traffic Control System", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ML-Powered Traffic Control System", screen_width, screen_height)

    while True:
        frames, detections_list = [], []
        emergency_detected = False

        for i, cap in enumerate(caps):
            if i == current_video:
                success, img = cap.read()
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) - 1)
                success, img = cap.read()

            if not success:
                frames.append(None)
                continue

            img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
            frames.append(img)

            detections = np.empty((0, 5))
            if i != current_video:
                results = model(img, stream=True)

                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = round(box.conf[0].item(), 2)
                        cls = int(box.cls[0])
                        currentClass = model.names[cls] if cls < len(model.names) else "unknown"

                        if currentClass in vehicle_classes and conf > 0.3:
                            detections = np.vstack((detections, np.array([x1, y1, x2, y2, conf])))
                            # cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box without label
            detections_list.append(detections)

        white_background = np.ones((screen_height, screen_width, 3), dtype=np.uint8) * 240

        for i, (img, detections) in enumerate(zip(frames, detections_list)):
            if img is None:
                continue

            if i != current_video:
                resultsTracker = trackers[i].update(detections)
                tracking_ids[i] = set(int(result[-1]) for result in resultsTracker)
                vehicle_counts[i] = len(tracking_ids[i])

                # Alert logic with flag
                if vehicle_counts[i] > 50:
                    if not alert_sent_flags[i]:
                        send_alert(i)
                        alert_sent_flags[i] = True
                else:
                    alert_sent_flags[i] = False

                count_text = f"COUNT: {vehicle_counts[i]}"
                overlay = img.copy()
                cv2.rectangle(overlay, (15, 10), (220, 60), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
                cv2.putText(img, count_text, (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            else:
                tracking_ids[i].clear()
                vehicle_counts[i] = 0

            if i == current_video:
                time_text = f"TIME: {time_left}"
                overlay = img.copy()
                cv2.rectangle(overlay, (15, 10), (180, 60), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
                cv2.putText(img, time_text, (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

            circle_color = (0, 255, 0) if i == current_video else (0, 255, 255) if i == (current_video + 1) % 4 and time_left <= 7 else (0, 0, 255)
            cv2.circle(img, (FRAME_WIDTH - 30, 30), 15, circle_color, -1)

            row, col = divmod(i, 2)
            y1, y2 = row * FRAME_HEIGHT, (row + 1) * FRAME_HEIGHT
            x1, x2 = col * FRAME_WIDTH, (col + 1) * FRAME_WIDTH
            white_background[y1:y2, x1:x2] = img

        cv2.line(white_background, (FRAME_WIDTH, 0), (FRAME_WIDTH, screen_height), (50, 50, 50), LINE_THICKNESS)
        cv2.line(white_background, (0, FRAME_HEIGHT), (screen_width, FRAME_HEIGHT), (50, 50, 50), LINE_THICKNESS)

        cv2.imshow("ML-Powered Traffic Control System", white_background)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('n') or time_left == 0:
            current_video = (current_video + 1) % 4
            time_left = max(vehicle_counts[current_video] * 2, 5)

        if current_video != -1 and time_left > 0:
            time_left -= 1

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

# GUI setup
welcome_window = tk.Tk()
welcome_window.title("ML-Powered Traffic Control System")
welcome_window.state('zoomed')
welcome_window.configure(bg="#282C35")

title_label = tk.Label(
    welcome_window,
    text="🚦 ML-Powered Traffic Control System 🚦",
    font=("Arial", 28, "bold"),
    fg="#FFD700",
    bg="#282C35"
)
title_label.pack(pady=50)

button_frame = tk.Frame(welcome_window, bg="#282C35")
button_frame.pack(expand=True)

start_button = tk.Button(
    button_frame,
    text="▶ Start",
    font=("Arial", 18, "bold"),
    bg="#61AFEF",
    fg="white",
    padx=40,
    pady=15,
    relief="raised",
    bd=5,
    command=start_main_program
)
start_button.pack()

footer_label = tk.Label(
    welcome_window,
    text="Press 'Q' to quit or 'N' to switch to the next clip",
    font=("Arial", 12),
    fg="white",
    bg="#282C35"
)
footer_label.pack(side="bottom", pady=20)

welcome_window.mainloop()
