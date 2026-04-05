import cv2
import numpy as np
import os
import shutil
import subprocess
import sys

INPUT_DIR = "input"
OUTPUT_DIR = "output/images"


def process_and_count(image, filename):
    base_name = os.path.splitext(filename)[0]
    debug_dir = "output/debug"
    os.makedirs(debug_dir, exist_ok=True)

    original = image.copy()

    # 1. Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Gray", gray)
    cv2.imwrite(f"{debug_dir}/{base_name}_gray.jpg", gray)

    # 2. Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Threshold
    _, thresh = cv2.threshold(
        blurred, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    cv2.imshow("Threshold", thresh)
    cv2.imwrite(f"{debug_dir}/{base_name}_thresh.jpg", thresh)

    # 4. Morphology (adaptive kernel)
    h, w = gray.shape
    k = max(3, int(min(h, w) / 100))
    kernel = np.ones((k, k), np.uint8)

    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # 5. Contours
    contours, _ = cv2.findContours(
        clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Adaptive area filtering
    areas = [cv2.contourArea(c) for c in contours]
    if len(areas) == 0:
        return original, 0

    avg_area = np.mean(areas)
    min_area = avg_area * 0.3

    count = 0

    for c in contours:
        if cv2.contourArea(c) > min_area:
            count += 1
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(original, (x, y), (x+w, y+h), (0,255,0), 2)

    return original, count


def run_image():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("1 → Input folder | 2 → File picker")
    choice = input("Enter choice: ")

    if choice == "1":
        files = os.listdir(INPUT_DIR)

        if not files:
            print("No images in input/")
            return

        for i, f in enumerate(files):
            print(i+1, f)

        idx = int(input("Select: ")) - 1
        file_name = files[idx]
        path = os.path.join(INPUT_DIR, file_name)

    elif choice == "2":
        # Use Windows native file picker via PowerShell
        ps_script = """
[System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null
$OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$OpenFileDialog.initialDirectory = [System.IO.Directory]::GetCurrentDirectory()
$OpenFileDialog.filter = "Image files (*.jpg;*.jpeg;*.png;*.bmp)|*.jpg;*.jpeg;*.png;*.bmp|All files (*.*)|*.*"
$OpenFileDialog.ShowDialog() | Out-Null
$OpenFileDialog.filename
"""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            file_path = result.stdout.strip()
            
            if not file_path or not os.path.exists(file_path):
                print("No file selected")
                return
                
        except Exception as e:
            print(f"Error opening file picker: {e}")
            return

        file_name = os.path.basename(file_path)
        path = os.path.join(INPUT_DIR, file_name)
        shutil.copy(file_path, path)

    img = cv2.imread(path)

    if img is None:
        print("Image load failed")
        return

    output, count = process_and_count(img, file_name)

    print("Count:", count)

    name, ext = os.path.splitext(file_name)
    out_path = os.path.join(OUTPUT_DIR, f"{name}_output{ext}")

    cv2.imwrite(out_path, output)
    print("Saved:", out_path)

    # ✅ SHOW RESULT + CLEAN EXIT
    cv2.imshow("Result", output)
    print("Press ESC to exit")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_image()