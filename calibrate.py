import cv2
import numpy as np
import json

# This will hold the (lower, upper) HSV ranges for our 6 colors
color_ranges = {}

# Define the (x, y) coordinates for the top-left corner
# and the (width, height) of our sampling box.
box_x = 295  # (640 / 2) - 25
box_y = 215  # (480 / 2) - 25
box_w = 50
box_h = 50

# A helper function to make sure values are in the 0-255 range
def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

# Start the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

print("--- Color Calibration Tool (v3 - Forgiving) ---")
print("Point a color at the green box.")
print("Press the key for the color you are sampling:")
print("'w' = White")
print("'g' = Green")
print("'r' = Red")
print("'b' = Blue")
print("'o' = Orange")
print("'y' = Yellow")
print("------------------------------")
print("Press 's' to SAVE and EXIT.")
print("Press 'q' to EXIT without saving.")

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame. Exiting ...")
        break
    
    # Flip the frame so it's a mirror image (more intuitive)
    frame = cv2.flip(frame, 1)

    # Draw the sampling box on the frame
    cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 255, 0), 2)
    
    # Show the webcam feed
    cv2.imshow("Calibration - Press 's' to save", frame)
    
    # Wait for a key press
    key = cv2.waitKey(1) & 0xFF

    # Check if the key is one of our color keys
    if key in [ord('w'), ord('g'), ord('r'), ord('b'), ord('o'), ord('y')]:
        color_name = chr(key)
        
        # Grab the small region of interest (ROI) inside the box
        roi = frame[box_y:box_y + box_h, box_x:box_x + box_w]
        
        # Convert this small piece to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Find the MEDIAN (average) HUE
        median_h = np.median(hsv_roi[:, :, 0])
        
        # --- NEW LOGIC (v3) ---
        
        # HUE: +/- 10 buffer around the median
        min_h = clamp(median_h - 10, 0, 179)
        max_h = clamp(median_h + 10, 0, 179)

        # SATURATION & VALUE: Set wide, forgiving ranges
        # We assume any *color* is at least somewhat colorful and bright
        min_s = 60
        max_s = 255
        min_v = 60
        max_v = 255

        # *** Special rule for 'w' (White) ***
        if color_name == 'w':
            min_h = 0   # White's hue doesn't matter
            max_h = 179
            min_s = 0   # White has low saturation
            max_s = 80  # Max saturation for white
            min_v = 150 # White must be bright
        
        # *** Special rule for 'r' (Red) ***
        # Handle the hue "wrap-around" (0/179)
        if median_h < 10: # It's on the low end (e.g., 5)
            min_h = 0
            max_h = 10
        elif median_h > 170: # It's on the high end (e.g., 175)
            min_h = 170
            max_h = 179
        
        # Store these new, better ranges
        color_ranges[color_name] = {
            'lower': [int(min_h), int(min_s), int(min_v)],
            'upper': [int(max_h), int(max_s), int(max_v)]
        }
        
        print(f"-> Captured '{color_name}'. Range: {color_ranges[color_name]}")

    # 's' key to save
    elif key == ord('s'):
        with open('colors.json', 'w') as f:
            json.dump(color_ranges, f, indent=4)
        print(f"\nSaved {len(color_ranges)} colors to 'colors.json'!")
        break # Exit the loop

    # 'q' key to quit
    elif key == ord('q'):
        print("\nQuit without saving.")
        break # Exit the loop

# Clean up
cap.release()
cv2.destroyAllWindows()