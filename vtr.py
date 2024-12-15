import os
import cv2
import pytesseract
from collections import Counter
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# possible state codes
VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "DN", "DD", "DL", "GA", "GJ", "HR", "HP", "JK", "KA", "KL", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OR", "PY", "PN", "RJ", "SK", "TN", "TR", "UP", "WB"
}

def is_valid_number_plate(text):
    # we are only cosidering the format: 'AA00AA0000'
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4,5}$', text):
        return False
    state_code = text[:2]
    return state_code in VALID_STATE_CODES

def correct_text(text):
    corrected_text = []
    for i, char in enumerate(text):
        if i < 2 or (4 <= i < 6):
            if not char.isalpha():
                char = 'A'
        elif (2 <= i < 4) or (6 <= i):
            if not char.isdigit():
                char = '0'
        corrected_text.append(char)
    return ''.join(corrected_text)

def extract_number_plate(video_path, output_file=None):

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return

    frame_count = 0
    detected_texts = []

    while True:
        ret, frame = cap.read()
        if not ret:
            # print("No more frames to process.")
            break

        frame_count += 1
        # print(f"Processing Frame {frame_count}...")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        text = pytesseract.image_to_string(thresh, config=config).strip()

        if 9 <= len(text) <= 11 and text.isalnum():
            corrected = correct_text(text)
            if is_valid_number_plate(corrected):
                print(f"Valid number plate detected in Frame {frame_count}: {corrected}")
                detected_texts.append(corrected)

    cap.release()

    if detected_texts:
        text_counts = Counter(detected_texts)
        most_common_text, _ = text_counts.most_common(1)[0]

        print(f"Most common number plate detected: {most_common_text}")

        if output_file:
            with open(output_file, 'w') as f:
                f.write(most_common_text)
            print(f"Result saved to {output_file}")
    else:
        print("No valid number plates detected.")

video_path = r'C:\Users\Nikhil\Desktop\VIDEO_OCR\venv\Video_OCR\vid1.mp4'
extract_number_plate(video_path, output_file='detected_number_plate.txt')