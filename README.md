# 🤖 Rubik's Cube Solver using OpenCV & AI

This Python project uses your **webcam** to scan a scrambled 3×3 Rubik’s Cube, detect all 54 stickers, and compute the optimal moves to solve it using the **Kociemba algorithm**.

It also features an **interactive 2D cube map** that fills with colors as you scan—helping you verify every face in real time.

---

## 📸 Features

### 🎨 Live Color Detection

* Uses **OpenCV** to identify the 6 sticker colors in real time.

### 🧪 Robust Calibration Tool

* A dedicated `calibrate.py` script trains the program to understand **your cube’s colors under your lighting**.
* Automatically generates a `colors.json` file.

### 🧱 Interactive 2D “Unfolded” Cube Map

* Highlights the face that needs scanning.
* Shows detected colors instantly.
* Prevents common scanning mistakes.

### 🏷️ Logo Handling

* Smart scanning logic ignores brand logos on center stickers.

### ⚡ Fast Solving

* Uses the **Kociemba algorithm** to compute a near-optimal solution.
* Typically under 21 moves.
* Solves almost instantly.

---

## ⚙️ Requirements

* Python 3.x
* OpenCV
* NumPy
* Kociemba

Install dependencies:

```bash
pip install opencv-python numpy kociemba
```

Or install using `requirements.txt`:

```
opencv-python
numpy
kociemba
```

---

# 🚀 Installation & Setup

1. Clone or download this project.
2. Install the required dependencies.
3. Run the calibration tool first.
4. Then run the solver.

---

# 💡 How to Use (Step-by-Step Guide)

This project works in **two stages**:

1. **Calibration (mandatory)**
2. **Cube scanning & solving**

---

# 🥇 Step 1: Calibrate Your Colors (CRITICAL)

This step creates the `colors.json` file that defines how your cube’s colors look under your lighting.
Without calibration, the solver will **not** work.

Run:

```bash
python calibrate.py
```

A webcam window will appear with a **green sampling box**.

---

## 🎯 How to sample a color

Point a **center sticker** so it fully fills the box.

Press the key associated with that color:

| Color  | Key |
| ------ | --- |
| White  | w   |
| Green  | g   |
| Red    | r   |
| Blue   | b   |
| Orange | o   |
| Yellow | y   |

You can re-sample colors as many times as needed.

---

## 💾 Save calibration

When all six colors are sampled, press:

```
s
```

This creates `colors.json` and exits.

---

# 🥈 Step 2: Run the Solver

Now scan your scrambled cube:

```bash
python main.py
```

A webcam window + a 2D cube map will appear.
The **highlighted face** indicates which side you must scan.

---

# 🔄 The Roll–Rotate Scanning Method

This is the **most important** part.
Incorrect scanning orientation = invalid cube string.

---

## 🎮 Start Grip (ALWAYS return to this)

* **White face UP**
* **Green face FRONT (facing you)**

Follow this exact sequence:

---

## 1️⃣ Scan U (Up – White)

* UI highlights **U**
* Tilt the cube forward (“roll”)
* White face looks at the camera
* Press **Spacebar**

---

## 2️⃣ Scan R (Right – Red)

* Return to Start Grip
* Rotate cube **90° clockwise**
* Tilt Red face forward
* Press **Spacebar**

---

## 3️⃣ Scan F (Front – Green)

* Return to Start Grip
* Green face is already in front
* Tilt forward
* Press **Spacebar**

---

## 4️⃣ Scan D (Down – Yellow)

* Return to Start Grip
* Tilt cube backward (“roll”)
* Yellow face looks at camera
* Press **Spacebar**

---

## 5️⃣ Scan L (Left – Orange)

* Return to Start Grip
* Rotate cube **90° counter-clockwise**
* Tilt Orange face forward
* Press **Spacebar**

---

## 6️⃣ Scan B (Back – Blue)

* Return to Start Grip
* Rotate cube **180°**
* Tilt Blue face forward
* Press **Spacebar**

---

# 🧠 Getting the Solution

After the final scan:

* The full **54-character cube string** appears in the terminal.
* The Kociemba solver computes the complete solution.
* Moves such as:

```
R U' F2 L B' ...
```

appear on the screen.

Your cube is now ready to solve manually!

---

# 🚨 Troubleshooting

### ❌ Error: Unknown color detected

Your lighting changed, or calibration was inaccurate.

**Fix:** Delete `colors.json` → run `calibrate.py` again.

---

### ❌ Error: Invalid cubestring / SOLVE ERROR

Your scanning orientation was wrong.

**Fix:** Press `r` in the program to reset. Carefully follow the **Roll–Rotate** method exactly.

---

### 🔶 Red/Orange confusion

A common computer vision challenge.

**Fix:**

* Use bright, even lighting.
* Avoid glare or harsh shadows.

---

# 📁 Project Files

| File           | Description                                     |
| -------------- | ----------------------------------------------- |
| `main.py`      | Main solver with webcam, UI, and solving logic  |
| `calibrate.py` | Generates the HSV color profile (`colors.json`) |
| `colors.json`  | Stores HSV ranges for all six cube colors       |
| `README.md`    | Project documentation                           |

---

# 🎉 You're Ready to Solve!

Your webcam-powered **Rubik’s Cube Solver** is fully set up.
Have fun scanning and solving your cube with AI! 🎉
