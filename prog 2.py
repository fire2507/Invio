import cv2
import numpy as np
import pyttsx3
import os
import mediapipe as mp
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from PIL import Image
import pytesseract

# Initialize text-to-speech engine
engine = pyttsx3.init()

# YOLO Setup
required_files = ['yolov4-tiny.weights', 'yolov4-tiny.cfg', 'coco.names']
if not all(os.path.exists(file) for file in required_files):
    print("Required YOLO files are missing!")
    exit(1)

net = cv2.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# KNN Setup
K = 1000
dataset_path = "facial_expression_data_new.csv"
data = pd.read_csv(dataset_path)
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, y)

# MediaPipe Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=False, max_num_faces=1)

# OCR Setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def calculate_distance(focal_length, real_object_width, object_width_in_image):
    return (real_object_width * focal_length) / object_width_in_image if object_width_in_image > 0 else float('inf')

def calculate_pose_distance(area, K):
    return K / np.sqrt(area) if area > 0 else float('inf')

def infer_action(landmarks):
    if landmarks:
        left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

        if left_hand.y < nose.y and right_hand.y < nose.y:
            return "Hands raised"
        elif left_hand.y > nose.y and right_hand.y > nose.y:
            return "Hands lowered"
        else:
            return "Neutral position"
    return "No action detected"

def detect_movement(landmarks):
    if landmarks:
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        left_leg_angle = abs(np.degrees(np.arctan2(left_hip.y - left_knee.y, left_hip.x - left_knee.x) -
                             np.arctan2(left_ankle.y - left_knee.y, left_ankle.x - left_knee.x))) % 180
        right_leg_angle = abs(np.degrees(np.arctan2(right_hip.y - right_knee.y, right_hip.x - right_knee.x) -
                              np.arctan2(right_ankle.y - right_knee.y, right_ankle.x - right_knee.x))) % 180

        if left_leg_angle > 160 and right_leg_angle > 160:
            return "Standing"
        elif left_leg_angle < 120 and right_leg_angle < 120:
            return "Sitting"
        else:
            return "Walking"
    return "Movement not detected"

def read_text_from_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pil_image = Image.fromarray(gray_frame)
    return pytesseract.image_to_string(pil_image)

def integrate_system():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        engine.say("Error: Could not open the camera.")
        engine.runAndWait()
        return

    instructions = "Press 'S' to recognize text, and 'Q' to quit."
    print(instructions)
    engine.say(instructions)
    engine.runAndWait()

    focal_length = 650
    real_object_width = 20

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            engine.say("Error: Could not read frame.")
            engine.runAndWait()
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(rgb_frame)
        face_results = face_mesh.process(rgb_frame)

        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            nose = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            if nose.visibility > 0.5:
                area = 10000
                distance = calculate_pose_distance(area, K)
                cv2.putText(frame, f"Distance: {distance:.2f} cm", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            action = infer_action(pose_results.pose_landmarks.landmark)
            cv2.putText(frame, f"Action: {action}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            movement = detect_movement(pose_results.pose_landmarks.landmark)
            cv2.putText(frame, f"Movement: {movement}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                landmarks = [lm.x for lm in face_landmarks.landmark] + [lm.y for lm in face_landmarks.landmark]
                expression = knn.predict([landmarks])[0]
                cv2.putText(frame, f"Expression: {expression}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Integrated System", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            engine.say("Processing frame for text recognition. Please wait.")
            engine.runAndWait()
            recognized_text = read_text_from_frame(frame)
            if recognized_text.strip():
                print("Recognized Text:", recognized_text)
                engine.say("Recognized text is: " + recognized_text)
                engine.runAndWait()
            else:
                print("No text recognized.")
                engine.say("No text recognized.")
                engine.runAndWait()
        elif key == ord('q'):
            print("Exiting program.")
            engine.say("Exiting the program. Goodbye!")
            engine.runAndWait()
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    integrate_system()

if __name__ == "__main__":
    main()