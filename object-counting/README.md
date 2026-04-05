# Object Counting System

A simple Python application that counts objects in images using computer vision techniques.

## Features

- **Two input methods:**
  - Option 1: Select from images in the `input/` folder
  - Option 2: Open Windows file picker to select any image
  
- **Object detection & counting:**
  - Converts image to grayscale
  - Applies Gaussian blur for noise reduction
  - Uses Otsu thresholding for binary conversion
  - Applies morphological operations to clean up the image
  - Detects contours and counts objects
  - Draws bounding boxes around detected objects

- **Output files:**
  - Processed image with bounding boxes saved to `output/images/`
  - Debug images saved to `output/debug/` showing:
    - Grayscale conversion
    - Threshold result
  - Object count displayed in terminal
  - **Note:** No live image display (uses PIL instead of OpenCV)

## Installation

### Requirements
- Python 3.6+
- Pillow (PIL) - for image processing
- NumPy - for numerical operations
- PowerShell (for Windows file picker)

### Setup

```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python countobj.py
```

When prompted, choose:
- **Option 1:** List images in `input/` folder and select one by number
- **Option 2:** Open Windows file picker to select any image file

The script will:
1. Process the selected image
2. Count detected objects
3. Display the result with bounding boxes
4. Save output image and debug files
5. Press ESC to exit the viewer

## Directory Structure

```
object-counting/
├── countobj.py          # Main script
├── README.md           # This file
├── input/              # Place images here for option 1
├── output/
│   ├── images/         # Processed output images
│   └── debug/          # Debug processing stages
```

## How It Works

### Image Processing Pipeline

1. **Grayscale Conversion** - Convert color image to grayscale using PIL
2. **Simple Thresholding** - Binary conversion at midpoint (128)
3. **Connected Component Analysis** - Find connected dark regions
4. **Grid-based Detection** - Divide image into regions and count dark areas
5. **Draw & Save** - Add bounding boxes and save result

### Detection Method

The system uses a simple grid-based approach:
- Divides the image into 50x50 pixel regions
- Counts regions that are predominantly dark (below threshold)
- Draws red rectangles around detected regions

This is much simpler than advanced computer vision but works for basic object counting.

## Troubleshooting

**No live image preview:**
- This version uses PIL instead of OpenCV
- Results are saved to files only
- Open the output image manually to see results

**Image not found:**
- Check that the input image is in a supported format (JPG, PNG, BMP)
- Verify the file path is correct

**No objects detected:**
- The image may not have sufficient contrast
- Adjust lighting or try a different image
- Debug images may help identify the issue
* At the end we display the contour bounding box;


## Results

It is a fast object counting algorithm suitable for real time applications. For its prototype nature it doesn’t handle light problems;

For preprocessing we tried 4 kinds of filters:

1. Normalized Box Filter: doesn’t preserve edges;
1. **Median filter: the winner**;
1. Bilateral filter [[4]](#4): better than median but too slow;
1. Adaptive bilateral filter [[5]](#5): as above;


### Demo video

[![Alt text](https://img.youtube.com/vi/eXYA7o1Lbik/0.jpg)](https://www.youtube.com/watch?v=eXYA7o1Lbik)


## Usage on Images

It is also provided an implementation of the algorithm for images. In this case there are two choices:

1. _Fidelity range:_ if objects have a similar size/area it is helpful to prevent false detection;
1. _Normal:_ no area thresholding is applied;


## References

<a name="1">[1]</a> Median Filter: [https://en.wikipedia.org/wiki/Median_filter](https://en.wikipedia.org/wiki/Median_filter);

<a name="2">[2]</a> Mixture of Gaussians: http://www.ai.mit.edu/projects/vsam/Publications/stauffer_cvpr98_track.pdf;

<a name="3">[3]</a> Suzuki, S. and Abe, K., Topological Structural Analysis of Digitized Binary Images by Border Following. CVGIP 30 1, pp 32-46 (1985);

<a name="4">[4]</a> C. Tomasi and R. Manduchi, "Bilateral Filtering for Gray and Color Images", Proceedings of the 1998 IEEE International Conference on Computer Vision, Bombay, India;

<a name="5">[5]</a> Buyue Zhang; Allebach, J.P., "Adaptive Bilateral Filter for Sharpness Enhancement and Noise Removal," Image Processing, IEEE Transactions on , vol.17, no.5, pp.664,678, May 2008;
