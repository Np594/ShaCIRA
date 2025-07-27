import cv2
import math
import time
from ultralytics import YOLO


colour = (0, 0, 0)
model = YOLO("shape_detector.pt")
ncnn = YOLO("best_ncnn_model")

classNames = ['Blue-Cube', 'Blue-Cylinder', 'Blue-Hexagonal-Prism', 'Blue-Triangular-Prism', 'Green-Cube', 'Green-Cylinder', 'Green-Hexagonal-Prism', 'Green-Triangular-Prism',
              'Red-Cube', 'Red-Cylinder', 'Red-Hexagonal-Prism', 'Red-Triangular-Prism', 'White-Cube', 'White-Cylinder', 'White-Hexagonal-Prism', 'White-Triangular-Prism']
classColours = [(255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 255, 0), (0, 255, 0),
                (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

cap = cv2.VideoCapture(0)
# Set image resolution to 640x640
cap.set(3, 640)
cap.set(4, 640)
prev_frame = 0
while True:
    success, img = cap.read()
    results = ncnn(img)
    current_frame = time.time()
    fps = 1 / (current_frame - prev_frame)
    prev_frame = current_frame
    cv2.putText(img, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # coordinates
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values
            # confidence
            confidence = math.ceil((box.conf[0] * 100)) / 100

            if confidence > 0.8:
                # class name
                cls = int(box.cls[0])
                print("Class =", classNames[cls], "Confidence", confidence)
                colour = classColours[cls]
                # object details
                org = [x1, y2]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                thickness = 2
                cv2.putText(img, classNames[cls], org, font, fontScale, colour, thickness)
                cv2.rectangle(img, (x1, y1), (x2, y2), colour, 3)

    cv2.imshow('Shape and Colour Detection', img)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
