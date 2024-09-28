import cv2 #libary อ่านภาพจากล้อง
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

prev_frame_time = 0
new_frame_time = 0

d_pressed = False
a_pressed = False
p_pressed = False
space_pressed = False

def in_idx_finger_up(landmarks):
    if landmarks[8].y < landmarks[6].y:
        return True
    return False

def is_hand_fist(landmarks):
    if landmarks[8].y >= landmarks[6].y and landmarks[12].y >= landmarks[10].y and landmarks[16].y >= landmarks[14].y:
        return True
    return False

def is_hand_open(landmarks):
    if landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y and landmarks[16].y < landmarks[14].y:
        return True
    return False

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read from the camera")
        break

    frame = cv2.flip(frame, 1) # 1 = Right --> Left   Left --> Right
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Change format BGR --> RGB
    results = hands.process(frame_rgb)

    right_idx_finger_up = False
    right_hand_fist = False
    left_idx_finger_up = False
    left_hand_fist = False
    right_hand_open = False

# landmark
    if results.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            hand_label = hand_info.classification[0].label
            # print(f"Detected {hand_label} hand") 
            if hand_label == "Right":
                if is_hand_open(hand_landmarks.landmark):
                    right_hand_open = True
                elif in_idx_finger_up(hand_landmarks.landmark):
                    right_idx_finger_up = True
                elif is_hand_fist(hand_landmarks.landmark):
                    right_hand_fist = True
            elif hand_label == "Left":
                if in_idx_finger_up(hand_landmarks.landmark):
                    left_idx_finger_up = True
                elif is_hand_fist(hand_landmarks.landmark):
                    left_hand_fist = True
    
    # Condition 0: Right hand open, Left hand fist -> press "p"
    if right_hand_open and left_hand_fist:
        if not p_pressed:
            pyautogui.keyDown("p")
            p_pressed = True
            print("press 'p'")
        if a_pressed:
            pyautogui.keyUp("a")
            a_pressed = False
        if space_pressed:
            pyautogui.keyUp("space")
            space_pressed = False
        if d_pressed:
            pyautogui.keyUp("d")
            d_pressed = False

    # Condition 1: Right index finger up, Left hand fist -> press "d"
    if right_idx_finger_up and left_hand_fist:
        if p_pressed:
            pyautogui.keyDown("p")
            pyautogui.keyUp("p")
            p_pressed = False
        if not d_pressed:
            pyautogui.keyDown("d")
            d_pressed = True
            print("press 'd'")
        if a_pressed:
            pyautogui.keyUp("a")
            a_pressed = False
        if space_pressed:
            pyautogui.keyUp("space")
            space_pressed = False

    # Condition 2: Right hand fist, Left index finger up -> press "a"
    elif right_hand_fist and left_idx_finger_up:
        if p_pressed:
            pyautogui.keyDown("p")
            pyautogui.keyUp("p")
            p_pressed = False
        if not a_pressed:
            pyautogui.keyDown("a")
            a_pressed = True
            print("press 'a'")
        if d_pressed:
            pyautogui.keyUp("d")
            d_pressed = False
        if space_pressed:
            pyautogui.keyUp("space")
            space_pressed = False

    # Condition 3: Right index finger up, Left index finger up -> press "space"
    elif right_idx_finger_up and left_idx_finger_up:
        if p_pressed:
            pyautogui.keyDown("p")
            pyautogui.keyUp("p")
            p_pressed = False
        if not space_pressed:
            pyautogui.keyDown("space")
            space_pressed = True
            print("press 'space'")
        if d_pressed:
            pyautogui.keyUp("d")
            d_pressed = False
        if a_pressed:
            pyautogui.keyUp("a")
            a_pressed = False

    # Condition 4: Both hands fist -> release all keys
    elif right_hand_fist and left_hand_fist:
        if p_pressed:
            pyautogui.keyDown("p")
            pyautogui.keyUp("p")
            p_pressed = False
        if d_pressed:
            pyautogui.keyUp("d")
            d_pressed = False
        if a_pressed:
            pyautogui.keyUp("a")
            a_pressed = False
        if space_pressed:
            pyautogui.keyUp("space")
            space_pressed = False

    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time

    cv2.putText(frame, f'FPS: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('Mario controller', frame)
    
    if cv2.waitKey(5) & 0xFF == 27:
        print("exiting...")
        break

    if cv2.getWindowProperty('Mario controller', cv2.WND_PROP_VISIBLE) < 1:
        print("exiting...")
        break

cap.release()
cv2.destroyAllWindows()
