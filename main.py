import cv2
import numpy as np
import json
import kociemba

# --- 1. LOAD CALIBRATION DATA ---
try:
    with open('colors.json', 'r') as f:
        color_ranges = json.load(f)
    print("Calibration file 'colors.json' loaded.")
except FileNotFoundError:
    print("ERROR: 'colors.json' not found.")
    print("Please run 'calibrate.py' first to create it.")
    exit()

# --- 2. COLOR DETECTION ---

# This map translates our scanned color char (from calibrate.py)
# to the official Kociemba face letter.
COLOR_TO_KOCIEMBA_MAP = {
    'W': 'U', # White is Up
    'G': 'F', # Green is Front
    'R': 'R', # Red is Right
    'B': 'B', # Blue is Back
    'O': 'L', # Orange is Left
    'Y': 'D'  # Yellow is Down
}

# --- NEW: Kociemba letter to BGR color for drawing the map ---
# These are approximate BGR values for display, tune if needed
KOCIEMBA_TO_BGR_MAP = {
    'U': (255, 255, 255),  # White
    'F': (0, 255, 0),      # Green
    'R': (0, 0, 255),      # Red
    'B': (255, 0, 0),      # Blue
    'L': (0, 165, 255),    # Orange (approximate)
    'D': (0, 255, 255),    # Yellow
    '?': (100, 100, 100)   # Unknown/Placeholder
}

def get_color_name(h, s, v):
    """
    Compares a single HSV pixel to our calibrated color ranges.
    Smarter check: saturated colors first, then white, then red's wrap-around.
    """
    
    colors = []
    white_range = None
    red_range = None
    orange_range = None

    for name, ranges in color_ranges.items():
        if name == 'w':
            white_range = ranges
        elif name == 'r':
            red_range = ranges
            colors.append((name, ranges)) # Add red to general colors first
        elif name == 'o':
            orange_range = ranges
            colors.append((name, ranges)) # Add orange to general colors first
        else:
            colors.append((name, ranges))

    # 1. Check all saturated colors (except red's wrap-around for now)
    for color_name, ranges in colors:
        if (ranges['lower'][0] <= h <= ranges['upper'][0] and
            ranges['lower'][1] <= s <= ranges['upper'][1] and
            ranges['lower'][2] <= v <= ranges['upper'][2]):
            return color_name
            
    # 2. Special check for Red's "wrap-around" Hue (0-10)
    # The calibrate.py sets red to 170-179. If hue is low (e.g. 0-10)
    # but saturation and value match red's, it's red.
    if red_range and (0 <= h <= 10):
        if (red_range['lower'][1] <= s <= red_range['upper'][1] and
            red_range['lower'][2] <= v <= red_range['upper'][2]):
            return 'r'

    # 3. If no other color matched, check for White LAST
    if white_range:
        if (white_range['lower'][0] <= h <= white_range['upper'][0] and
            white_range['lower'][1] <= s <= white_range['upper'][1] and
            white_range['lower'][2] <= v <= white_range['upper'][2]):
            return 'w'

    return 'unknown' # If no color matches

# --- 3. UI & DRAWING FUNCTIONS ---

# Define the (x, y) coordinates for our 9 sticker centers for live scanning
STICKER_CENTERS = [
    (250, 190), (320, 190), (390, 190), # Top row
    (250, 260), (320, 260), (390, 260), # Middle row
    (250, 330), (320, 330), (390, 330)  # Bottom row
]

# --- NEW: Parameters for the unfolded 2D cube map ---
MAP_START_X = 10  # Top-left X position of the whole map
MAP_START_Y = 10  # Top-left Y position of the whole map
STICKER_SIZE = 25 # Size of each individual sticker square in the map
GAP = 2           # Gap between stickers

# Map layout for Kociemba faces (U, L, F, R, B, D) to grid positions
# Each value is (row, col) in a 3x3 grid for that face
UNFOLDED_LAYOUT = {
    'U': [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)], # U face (top middle)
    'L': [(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)], # L face (left of front)
    'F': [(3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)], # F face (middle)
    'R': [(3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)], # R face (right of front)
    'B': [(3, 9), (3,10), (3,11), (4, 9), (4,10), (4,11), (5, 9), (5,10), (5,11)], # B face (rightmost, looks weird but correct)
    'D': [(6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)]  # D face (bottom middle)
}

# This will store the scanned colors for the unfolded map
# Initialized with '?' for unknown/unscanned stickers
unfolded_map_colors = {face: ['?' for _ in range(9)] for face in UNFOLDED_LAYOUT.keys()}


def draw_unfolded_cube_map(frame, current_face_char):
    """
    Draws the 2D unfolded cube map with scanned colors.
    """
    for face_char, layout_positions in UNFOLDED_LAYOUT.items():
        for i, (row, col) in enumerate(layout_positions):
            # Calculate pixel coordinates for this sticker
            x1 = MAP_START_X + col * (STICKER_SIZE + GAP)
            y1 = MAP_START_Y + row * (STICKER_SIZE + GAP)
            x2 = x1 + STICKER_SIZE
            y2 = y1 + STICKER_SIZE
            
            # Get the color to draw
            sticker_kociemba_char = unfolded_map_colors[face_char][i]
            color = KOCIEMBA_TO_BGR_MAP.get(sticker_kociemba_char, (0, 0, 0)) # Default to black if unknown

            # Draw the sticker
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1) # -1 to fill

            # Draw a border, highlight if it's the current face being scanned
            border_color = (200, 200, 200) # Light gray default
            border_thickness = 1
            if face_char == current_face_char:
                border_color = (0, 255, 255) # Yellow highlight
                border_thickness = 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, border_thickness)


def draw_grid_on_camera_feed(frame, sticker_centers):
    """
    Draws the 9 sticker boxes on the live camera feed.
    """
    for (x, y) in sticker_centers:
        cv2.rectangle(frame, (x - 10, y - 10), (x + 10, y + 10), (0, 255, 0), 2)


def scan_colors_from_camera(frame, sticker_centers):
    """
    Gets the color for each of the 9 sticker positions from the live camera feed.
    """
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    face_colors = [] # List of 'W', 'R', 'G', etc.
    
    for (x, y) in sticker_centers:
        h, s, v = hsv_frame[y, x]
        color_name = get_color_name(h, s, v) # Get calibrated color name
        face_colors.append(color_name.upper()) 
        
        # Display the detected color letter on the camera feed
        cv2.putText(frame, color_name.title(), (x + 15, y + 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return face_colors

# --- 4. MAIN APPLICATION ---

# Define the order of faces to scan
# Kociemba's algorithm requires this specific order: U, R, F, D, L, B
FACES_TO_SCAN = [
    ("Up (White)", "U"),
    ("Right (Red)", "R"),
    ("Front (Green)", "F"),
    ("Down (Yellow)", "D"),
    ("Left (Orange)", "L"),
    ("Back (Blue)", "B")
]

# --- Application State Variables ---
cap = cv2.VideoCapture(0)
current_face_index = 0
cube_state_string = ""
solution = ""

print("\n--- Rubik's Cube Solver (v3 - Unfolded UI) ---")
print("Follow the highlighted face on the 2D map.")
print("Use the 'Roll and Rotate' method for accurate scanning:")
print("1. Start: White-UP, Green-FRONT.")
print("2. Scan U: Tilt cube forward.")
print("3. Scan R: Return to start, Rotate cube 90 deg CW, Tilt forward.")
print("4. Scan F: Return to start, Tilt forward.")
print("5. Scan D: Return to start, Tilt cube backward.")
print("6. Scan L: Return to start, Rotate cube 90 deg CCW, Tilt forward.")
print("7. Scan B: Return to start, Rotate cube 180 deg, Tilt forward.")
print("\nPress 'Space' to scan. | 'r' to reset. | 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # frame = cv2.flip(frame, 1)

    # --- State 1: Scanning Faces ---
    if current_face_index < len(FACES_TO_SCAN):
        face_name, face_char = FACES_TO_SCAN[current_face_index]
        
        # Draw the 2D unfolded map with current colors and highlight
        draw_unfolded_cube_map(frame, face_char)
        
        # Draw the 3x3 scanning grid on the live camera feed
        draw_grid_on_camera_feed(frame, STICKER_CENTERS)

        # Display instructions on the camera feed
        cv2.putText(frame, f"Show: {face_name}", (10, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Align with grid", (10, 270), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Run the color detection preview continuously
        scan_colors_from_camera(frame, STICKER_CENTERS)
    
    # --- State 2: Displaying Solution ---
    else:
        # Draw the 2D unfolded map one last time (no faces highlighted)
        draw_unfolded_cube_map(frame, None) 
        
        cv2.putText(frame, "Scan complete! Solution:", (10, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the solution string, breaking it into lines
        y_offset = 270
        for i, move in enumerate(solution.split()):
            # Display 8 moves per line
            cv2.putText(frame, move, (10 + (i % 8) * 60, y_offset + (i // 8) * 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, "Press 'r' to scan again", (10, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Show the final image
    cv2.imshow("Rubik's Cube Solver", frame)

    # --- 5. KEYBOARD CONTROLS ---
    key = cv2.waitKey(1) & 0xFF

    # 'q' to quit
    if key == ord('q'):
      break

    # 'r' to reset
    if key == ord('r'):
        current_face_index = 0
        cube_state_string = ""
        solution = ""
        # Reset the unfolded map colors too
        unfolded_map_colors = {face: ['?' for _ in range(9)] for face in UNFOLDED_LAYOUT.keys()}
        print("Resetting... Show 'Up (White)' face.")

    # 'Space' to scan
    if key == 32: # 32 is the Spacebar
        if current_face_index < len(FACES_TO_SCAN):
            face_name, face_char = FACES_TO_SCAN[current_face_index]
            
            # Scan the 9 colors from the camera feed
            scanned_raw_colors = scan_colors_from_camera(frame, STICKER_CENTERS)
            
            # Check for 'unknown' colors
            if 'UNKNOWN' in scanned_raw_colors:
                print(f"Error: Unknown color detected. Please check lighting/calibration and try scanning '{face_name}' again.")
            else:
                kociemba_face_string = ""
                
                # Loop through all 9 stickers (0-8)
                for i, raw_color_char in enumerate(scanned_raw_colors):
                    # i == 4 is the CENTER sticker
                    if i == 4:
                        # FORCE the center sticker to be the one we expect (e.g., 'U' for White face)
                        kociemba_face_string += face_char
                        unfolded_map_colors[face_char][i] = face_char # Update map
                    else:
                        # For all 8 other stickers, translate them using our map
                        if raw_color_char in COLOR_TO_KOCIEMBA_MAP:
                            translated_char = COLOR_TO_KOCIEMBA_MAP[raw_color_char]
                            kociemba_face_string += translated_char
                            unfolded_map_colors[face_char][i] = translated_char # Update map
                        else:
                            kociemba_face_string += "?" # Should not happen now
                            unfolded_map_colors[face_char][i] = '?' # Update map with unknown

                print(f"Scanned {face_name}: {kociemba_face_string}")
                cube_state_string += kociemba_face_string
                current_face_index += 1
                
                # --- This is the FINAL SCAN ---
                if current_face_index == len(FACES_TO_SCAN):
                    print("\nAll 6 faces scanned.")
                    print(f"Final State String: {cube_state_string}")
                    
                    # --- CALL THE SOLVER ---
                    try:
                        print("Solving...")
                        solution = kociemba.solve(cube_state_string)
                        print(f"Solution: {solution}")
                    except ValueError as e:
                        print(f"--- SOLVE ERROR ---")
                        print(f"The cube state string was invalid: {e}")
                        print("This usually means a color was scanned wrong or cube is impossible.")
                        print("Please press 'r' and try scanning again, following the 'Roll and Rotate' method carefully.")
                        solution = "ERROR: Invalid Scan"

# Clean up
cap.release()
cv2.destroyAllWindows()