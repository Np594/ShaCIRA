import cv2
import numpy as np
import math
import time


def colour_detection(mask_colour):
    global img, overlay_colour, mask
    # Define kernel size
    kernel = np.ones((5, 5), np.uint8)

    if mask_colour == "Blue":
        overlay_colour = 255, 0, 0
        # Define blue colour range and create mask in HSV
        blue_lower = np.array([100, 150, 50])
        blue_upper = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, blue_lower, blue_upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    if mask_colour == "Green":
        overlay_colour = 0, 255, 0
        # Define green colour range and create mask in HSV
        green_lower = np.array([40, 50, 50])  # lower bound for the colour green
        green_upper = np.array([90, 255, 255])  # upper bound for the colour detection of green
        mask = cv2.inRange(hsv, green_lower, green_upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    if mask_colour == "Red":
        overlay_colour = 0, 0, 255
        # Define Red colour range and create mask in HSV
        lower_red = np.array([0, 150, 200])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        mask2 = cv2.inRange(hsv, (170, 150, 100), (180, 255, 255))
        mask = cv2.bitwise_or(mask1, mask2)

    # shape detection
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for shapes in contours:
        area = cv2.contourArea(shapes)
        if 500 < area <= 20000:
            x, y, w, h = cv2.boundingRect(shapes)
            # Approximate the contour
            approx = cv2.approxPolyDP(shapes, 0.02 * cv2.arcLength(shapes, True), True)
            cv2.drawContours(img, [approx], 0, overlay_colour, 5)
            if len(approx) == 3:
                shape = "Triangle"
            elif len(approx) == 4:
                shape = "Rectangle"
            elif len(approx) == 6:
                shape = "Hexagon"
            else:
                shape = "Circle"
            cv2.putText(img, f"{mask_colour, shape}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, overlay_colour, 2)
            M = cv2.moments(shapes)
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            cv2.circle(img, (cx, cy), 5, overlay_colour, -1)
            cp = (cx + cy) / 2
            print("centre =", cp)
            print(mask_colour, shape, area)



cap = cv2.VideoCapture(0)
prev_frame = 0

while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.flip(img, 1)
    current_frame = time.time()
    fps = 1/(current_frame - prev_frame)
    prev_frame = current_frame
    cv2.putText(img, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert BGR to HSV for masks

    colour_detection("Blue")
    colour_detection("Green")
    colour_detection("Red")

    # Showing the output
    cv2.imshow("Shape and Colour Detection", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
