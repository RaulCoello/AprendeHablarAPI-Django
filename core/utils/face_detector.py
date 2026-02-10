import cv2
import os
import uuid

def detectar_rostros(image_path, output_dir, padding=0.25):
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    h_img, w_img = img.shape[:2]
    saved_faces = []

    for (x, y, w, h) in faces:
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w_img, x + w + pad_w)
        y2 = min(h_img, y + h + pad_h)

        rostro = img[y1:y2, x1:x2]

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(output_dir, filename)

        cv2.imwrite(filepath, rostro)
        saved_faces.append(filename)

    return saved_faces
