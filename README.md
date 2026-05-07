# CS303 Image Manipulation Tool

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Pillow](https://img.shields.io/badge/Pillow-PIL-success.svg)

A dark-themed **Python GUI** application for basic image manipulation, built with **Tkinter**, **NumPy**, and **Pillow (PIL)**. Load an image, preview results side-by-side, and export the processed image.

> Supported formats: **JPG, PNG, BMP, TIFF, WEBP**


## Features

- **Tabbed workflow** with 5 tools:
  - **RGB → Grayscale** — converts a colour image to grayscale using the perceptual weighted formula:

    ```text
    gray = 0.299·R + 0.587·G + 0.114·B
    ```

  - **RGB Channel Split** — splits a colour image into its individual **Red**, **Green**, and **Blue** channel images displayed side by side
  - **Histogram Stretching** — improves image contrast by stretching pixel intensities to the full range using:

    ```text
    new_pixel = (pixel − I_min) × 255 / (I_max − I_min)
    ```

    Displays live stats (**I_min**, **I_max**, range before and after)

  - **Point Operations** — three interactive sliders to apply in real time:
    - **Brightness** — adds a constant to all pixels: `y = x + C`
    - **Darkness** — subtracts a constant from all pixels: `y = x - C`
    - **Multiply Contrast** — scales all pixels by a factor: `y = x × C` (range **0.0** to **3.0**)

    Each result has its own **Save** button

  - **Morphological Operations** — converts the image to binary then applies:
    - **Dilation** — expands bright regions
    - **Erosion** — shrinks bright regions
    - **Opening** — erosion followed by dilation (removes noise)
    - **Closing** — dilation followed by erosion (fills gaps)

- **Side-by-side preview** (original vs. processed)
- **Save output** to common formats
- **Dark-themed UI**

## Requirements

- **Python 3.x**
- Dependencies:
  - `pillow`
  - `numpy`

> Tkinter is included with most Python installations on Windows/macOS. On some Linux distributions you may need to install it separately (e.g., `python3-tk`).

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Meedooh13/Image-Processing-Project.git
cd Image-Processing-Project
```

2. (Optional but recommended) Create a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```text
pip install pillow numpy scipy
```

## How to run

From the project root:

```bash
python main.py
```

## Tabs / Tools (How each feature works)

### 1) RGB → Grayscale

Converts a color image to grayscale using the perceptual weighted luminance formula:

```text
gray = 0.299·R + 0.587·G + 0.114·B
```

**Use case:** Producing a visually accurate grayscale image that reflects human sensitivity to green more than red and blue.

---

### 2) RGB Channel Split

Splits a color image into three separate single-channel images:

- **Red channel**
- **Green channel**
- **Blue channel**

**Use case:** Visualizing and analyzing how each channel contributes to the final image, or preparing data for channel-wise processing.

---

### 3) Histogram Stretching

Improves contrast by linearly stretching pixel intensities to the full range.

```text
new_pixel = (pixel − I_min) × 255 / (I_max − I_min)
```

Where:
- `I_min` is the minimum intensity in the image
- `I_max` is the maximum intensity in the image

**Use case:** Enhancing images with poor lighting or low contrast.

## Usage tips

- Load any supported image format, then switch between tabs to apply different operations.
- Use the preview panels to compare the **original** and **processed** results.
- Save the processed output from the active tab.
