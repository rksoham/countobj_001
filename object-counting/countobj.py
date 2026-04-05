from PIL import Image, ImageFilter, ImageDraw
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

    # Convert to grayscale
    gray = image.convert('L')
    gray.save(f"{debug_dir}/{base_name}_gray.jpg")

    # Convert to numpy array for processing
    img_array = np.array(gray)

    # Simple thresholding (invert for dark objects on light background)
    thresh_value = 128  # Simple midpoint threshold
    thresh = np.where(img_array > thresh_value, 255, 0).astype(np.uint8)

    # Save threshold image
    thresh_img = Image.fromarray(thresh, mode='L')
    thresh_img.save(f"{debug_dir}/{base_name}_thresh.jpg")

    # Simple blob detection using connected components
    # This is a basic implementation - count distinct regions
    height, width = thresh.shape
    visited = np.zeros_like(thresh, dtype=bool)
    count = 0

    def flood_fill(x, y):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx < 0 or cx >= width or cy < 0 or cy >= height or
                visited[cy, cx] or thresh[cy, cx] == 255):
                continue
            visited[cy, cx] = True
            # Add neighbors
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                stack.append((cx + dx, cy + dy))

    # Find connected components (dark regions)
    for y in range(height):
        for x in range(width):
            if thresh[y, x] == 0 and not visited[y, x]:  # Dark pixel, not visited
                flood_fill(x, y)
                count += 1

    # Draw bounding boxes on original image
    draw = ImageDraw.Draw(image)

    # Simple approach: divide image into grid and count regions
    # This is much simpler than contour detection
    grid_size = 50  # pixels
    regions_found = []

    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            region = thresh[y:min(y+grid_size, height), x:min(x+grid_size, width)]
            if np.mean(region) < 200:  # Dark region found
                regions_found.append((x, y, min(x+grid_size, width), min(y+grid_size, height)))

    # Draw rectangles around detected regions
    for x1, y1, x2, y2 in regions_found:
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    return image, len(regions_found)


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

    img = Image.open(path)

    try:
        # Verify image loaded
        img.verify()
        img = Image.open(path)  # Reopen after verify
    except Exception as e:
        print(f"Image load failed: {e}")
        return

    output, count = process_and_count(img, file_name)

    print("Count:", count)

    name, ext = os.path.splitext(file_name)
    out_path = os.path.join(OUTPUT_DIR, f"{name}_output{ext}")

    output.save(out_path)
    print("Saved:", out_path)

    # Show result (PIL can't display windows, so just print info)
    print(f"Image processed: {output.size} pixels")
    print("Open the output file to see results")
    print("Press Enter to continue...")
    input()


if __name__ == "__main__":
    run_image()