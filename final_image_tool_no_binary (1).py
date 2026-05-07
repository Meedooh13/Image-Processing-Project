import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import os
from scipy.ndimage import binary_dilation, binary_erosion

# ─── App State ───────────────────────────────────────────────────────────────
class AppState:
    original_pil = None
    original_np  = None

state = AppState()

# ─── Core Processing Functions ────────────────────────────────────────────────
def rgb_to_grayscale(img_np):
    """Weighted average (perceptual) grayscale conversion."""
    r, g, b = img_np[..., 0], img_np[..., 1], img_np[..., 2]
    gray = (0.299 * r.astype(np.float32) +
            0.587 * g.astype(np.float32) +
            0.114 * b.astype(np.float32)).astype(np.uint8)
    return gray

def split_channels(img_np):
    """Return R, G, B channel images (as RGB images for display)."""
    h, w = img_np.shape[:2]
    r_img = np.zeros((h, w, 3), dtype=np.uint8); r_img[..., 0] = img_np[..., 0]
    g_img = np.zeros((h, w, 3), dtype=np.uint8); g_img[..., 1] = img_np[..., 1]
    b_img = np.zeros((h, w, 3), dtype=np.uint8); b_img[..., 2] = img_np[..., 2]
    return r_img, g_img, b_img

def histogram_stretching(img_np):
    """Stretch contrast of a grayscale image to full [0, 255] range."""
    i_min = int(img_np.min())
    i_max = int(img_np.max())
    if i_max == i_min:
        return img_np.copy()
    stretched = ((img_np.astype(np.float32) - i_min) * 255.0 / (i_max - i_min)).clip(0, 255).astype(np.uint8)
    return stretched

# ─── Point Operations ─────────────────────────────────────────────────────────
def adjust_brightness(img_np, value):
    """Add constant to all pixels (brightness +)."""
    return np.clip(img_np.astype(np.float32) + value, 0, 255).astype(np.uint8)

def adjust_darkness(img_np, value):
    """Subtract constant from all pixels (darkness -)."""
    return np.clip(img_np.astype(np.float32) - value, 0, 255).astype(np.uint8)

def multiply_contrast(img_np, factor):
    """Multiply all pixels by factor (contrast scaling)."""
    return np.clip(img_np.astype(np.float32) * factor, 0, 255).astype(np.uint8)



# ─── Morphological Operations ─────────────────────────────────────────────────
def to_binary(img_np, threshold=128):
    """Convert image to binary."""
    if img_np.ndim == 3:
        img_np = rgb_to_grayscale(img_np)
    binary = (img_np > threshold).astype(np.uint8)
    return binary

def dilation_operation(img_np):
    binary = to_binary(img_np)
    dilated = binary_dilation(binary).astype(np.uint8) * 255
    return dilated

def erosion_operation(img_np):
    binary = to_binary(img_np)
    eroded = binary_erosion(binary).astype(np.uint8) * 255
    return eroded

def opening_operation(img_np):
    binary = to_binary(img_np)
    opened = binary_dilation(binary_erosion(binary)).astype(np.uint8) * 255
    return opened

def closing_operation(img_np):
    binary = to_binary(img_np)
    closed = binary_erosion(binary_dilation(binary)).astype(np.uint8) * 255
    return closed

# ─── Image Display Helpers ────────────────────────────────────────────────────
def np_to_photoimage(arr, max_size=(320, 320)):
    if arr.ndim == 2:
        pil = Image.fromarray(arr, mode='L')
    else:
        pil = Image.fromarray(arr, mode='RGB')
    pil.thumbnail(max_size, Image.LANCZOS)
    return ImageTk.PhotoImage(pil)

def set_panel(label_widget, title_label, arr, title):
    photo = np_to_photoimage(arr)
    label_widget.configure(image=photo)
    label_widget.image = photo  # keep reference
    title_label.configure(text=title)

# ─── GUI ─────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("CS303 Image Manipulation Tool")
root.configure(bg="#1c1b19")
root.resizable(True, True)

DARK_BG   = "#1c1b19"
PANEL_BG  = "#201f1d"
CARD_BG   = "#262523"
ACCENT    = "#4f98a3"
ACCENT_H  = "#227f8b"
TEXT      = "#cdccca"
TEXT_MUTED= "#797876"
BORDER    = "#393836"
FONT_BODY = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 11, "bold")
FONT_TITLE= ("Segoe UI", 14, "bold")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=DARK_BG, borderwidth=0)
style.configure("TNotebook.Tab", background=CARD_BG, foreground=TEXT_MUTED,
                padding=[14, 8], font=FONT_BODY)
style.map("TNotebook.Tab",
          background=[("selected", PANEL_BG)],
          foreground=[("selected", ACCENT)])
style.configure("TFrame", background=PANEL_BG)
style.configure("TSeparator", background=BORDER)

# ── Header ───────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=DARK_BG, pady=12)
header.pack(fill="x", padx=20)
tk.Label(header, text="🖼  Image Manipulation Tool", font=FONT_TITLE,
         bg=DARK_BG, fg=TEXT).pack(side="left")
tk.Label(header, text="CS303 Lab Toolkit", font=FONT_BODY,
         bg=DARK_BG, fg=TEXT_MUTED).pack(side="left", padx=10)

sep = tk.Frame(root, height=1, bg=BORDER)
sep.pack(fill="x", padx=20)

# ── Load Image Button ─────────────────────────────────────────────────────────
ctrl_bar = tk.Frame(root, bg=DARK_BG, pady=10)
ctrl_bar.pack(fill="x", padx=20)

orig_thumb_label = tk.Label(ctrl_bar, text="No image loaded", bg=DARK_BG,
                             fg=TEXT_MUTED, font=FONT_BODY)
orig_thumb_label.pack(side="left", padx=(0, 12))

def btn(parent, text, cmd, accent=True):
    color = ACCENT if accent else CARD_BG
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg="#ffffff" if accent else TEXT,
                  activebackground=ACCENT_H, activeforeground="#fff",
                  relief="flat", padx=14, pady=6, font=FONT_BODY,
                  cursor="hand2", bd=0)
    b.pack(side="left", padx=4)
    return b

def load_image():
    path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"), ("All", "*.*")])
    if not path:
        return
    pil = Image.open(path).convert("RGB")
    state.original_pil = pil
    state.original_np  = np.array(pil)
    # show thumbnail in header
    thumb = pil.copy(); thumb.thumbnail((60, 60), Image.LANCZOS)
    photo = ImageTk.PhotoImage(thumb)
    orig_thumb_label.configure(image=photo, text=f"  {os.path.basename(path)}",
                                compound="left", fg=TEXT)
    orig_thumb_label.image = photo
    # reset all tabs
    for tab_refresh in tab_refreshers:
        tab_refresh()

btn(ctrl_bar, "📂  Load Image", load_image)

# ── Notebook Tabs ─────────────────────────────────────────────────────────────
nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True, padx=20, pady=(8, 16))

tab_refreshers = []

def make_panel_frame(parent, col=0, colspan=1):
    f = tk.Frame(parent, bg=CARD_BG, bd=0, pady=12, padx=12,
                 highlightthickness=1, highlightbackground=BORDER)
    f.grid(row=1, column=col, columnspan=colspan, padx=8, pady=6, sticky="nsew")
    return f

def image_panel(parent):
    """Returns (title_label, image_label) inside a card frame."""
    t = tk.Label(parent, text="—", bg=CARD_BG, fg=TEXT_MUTED, font=FONT_BODY)
    t.pack(pady=(0, 6))
    img_lbl = tk.Label(parent, bg=CARD_BG, cursor="crosshair")
    img_lbl.pack()
    return t, img_lbl

def check_loaded():
    if state.original_np is None:
        messagebox.showwarning("No Image", "Please load an image first.")
        return False
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RGB to Grayscale
# ═══════════════════════════════════════════════════════════════════════════════
tab1 = ttk.Frame(nb); nb.add(tab1, text="  RGB → Grayscale  ")
tab1.columnconfigure(0, weight=1); tab1.columnconfigure(1, weight=1)
tab1.rowconfigure(1, weight=1)

info1 = tk.Label(tab1, text="Converts a colour image to grayscale using the perceptual weighted average:  gray = 0.299·R + 0.587·G + 0.114·B",
                 bg=PANEL_BG, fg=TEXT_MUTED, font=FONT_BODY, wraplength=700, justify="left", pady=6, padx=10)
info1.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 0))

p1_orig = make_panel_frame(tab1, col=0)
t1_orig, l1_orig = image_panel(p1_orig)

p1_gray = make_panel_frame(tab1, col=1)
t1_gray, l1_gray = image_panel(p1_gray)

btn1_bar = tk.Frame(tab1, bg=PANEL_BG, pady=6)
btn1_bar.grid(row=2, column=0, columnspan=2)

def run_grayscale():
    if not check_loaded(): return
    img = state.original_np
    set_panel(l1_orig, t1_orig, img, "Original (RGB)")
    gray = rgb_to_grayscale(img)
    set_panel(l1_gray, t1_gray, gray, "Grayscale Output")

def save_grayscale():
    if l1_gray.image is None: return
    path = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
    if path:
        gray = rgb_to_grayscale(state.original_np)
        Image.fromarray(gray, 'L').save(path)
        messagebox.showinfo("Saved", f"Grayscale image saved to:\n{path}")

btn(btn1_bar, "▶  Convert to Grayscale", run_grayscale)
btn(btn1_bar, "💾  Save Result", save_grayscale, accent=False)

def refresh_tab1():
    if state.original_np is not None: run_grayscale()

tab_refreshers.append(refresh_tab1)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RGB Channel Splitting
# ═══════════════════════════════════════════════════════════════════════════════
tab2 = ttk.Frame(nb); nb.add(tab2, text="  RGB Channel Split  ")
for c in range(4): tab2.columnconfigure(c, weight=1)
tab2.rowconfigure(1, weight=1)

info2 = tk.Label(tab2, text="Splits the colour image into its Red, Green, and Blue channels independently.",
                 bg=PANEL_BG, fg=TEXT_MUTED, font=FONT_BODY, wraplength=700, justify="left", pady=6, padx=10)
info2.grid(row=0, column=0, columnspan=4, sticky="ew", padx=8, pady=(8, 0))

p2_orig = make_panel_frame(tab2, col=0); t2_orig, l2_orig = image_panel(p2_orig)
p2_r    = make_panel_frame(tab2, col=1); t2_r,    l2_r    = image_panel(p2_r)
p2_g    = make_panel_frame(tab2, col=2); t2_g,    l2_g    = image_panel(p2_g)
p2_b    = make_panel_frame(tab2, col=3); t2_b,    l2_b    = image_panel(p2_b)

btn2_bar = tk.Frame(tab2, bg=PANEL_BG, pady=6)
btn2_bar.grid(row=2, column=0, columnspan=4)

def run_split():
    if not check_loaded(): return
    img = state.original_np
    set_panel(l2_orig, t2_orig, img, "Original")
    r, g, b = split_channels(img)
    set_panel(l2_r, t2_r, r, "🔴 Red Channel")
    set_panel(l2_g, t2_g, g, "🟢 Green Channel")
    set_panel(l2_b, t2_b, b, "🔵 Blue Channel")

def save_channels():
    if not check_loaded(): return
    path = filedialog.askdirectory(title="Select folder to save channels")
    if path:
        r, g, b = split_channels(state.original_np)
        Image.fromarray(r).save(os.path.join(path, "channel_red.png"))
        Image.fromarray(g).save(os.path.join(path, "channel_green.png"))
        Image.fromarray(b).save(os.path.join(path, "channel_blue.png"))
        messagebox.showinfo("Saved", f"3 channel images saved to:\n{path}")

btn(btn2_bar, "▶  Split Channels", run_split)
btn(btn2_bar, "💾  Save All Channels", save_channels, accent=False)

def refresh_tab2():
    if state.original_np is not None: run_split()

tab_refreshers.append(refresh_tab2)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Histogram Stretching
# ═══════════════════════════════════════════════════════════════════════════════
tab3 = ttk.Frame(nb); nb.add(tab3, text="  Histogram Stretching  ")
tab3.columnconfigure(0, weight=1); tab3.columnconfigure(1, weight=1)
tab3.rowconfigure(1, weight=1)

info3 = tk.Label(tab3,
    text="Stretches the pixel intensity range to the full [0, 255] span to improve contrast.\n"
         "Formula:  new_pixel = (pixel − I_min) × 255 / (I_max − I_min)",
    bg=PANEL_BG, fg=TEXT_MUTED, font=FONT_BODY, wraplength=700, justify="left", pady=6, padx=10)
info3.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 0))

p3_orig = make_panel_frame(tab3, col=0); t3_orig, l3_orig = image_panel(p3_orig)
p3_str  = make_panel_frame(tab3, col=1); t3_str,  l3_str  = image_panel(p3_str)

# Stats labels
stats3 = tk.Label(tab3, text="", bg=PANEL_BG, fg=ACCENT, font=("Courier", 9), pady=4)
stats3.grid(row=2, column=0, columnspan=2)

btn3_bar = tk.Frame(tab3, bg=PANEL_BG, pady=6)
btn3_bar.grid(row=3, column=0, columnspan=2)

def run_stretch():
    if not check_loaded(): return
    img = state.original_np
    gray = rgb_to_grayscale(img)
    set_panel(l3_orig, t3_orig, gray, "Grayscale (before stretch)")
    stretched = histogram_stretching(gray)
    set_panel(l3_str,  t3_str,  stretched, "After Histogram Stretching")
    i_min, i_max = int(gray.min()), int(gray.max())
    stats3.configure(
        text=f"Before → I_min: {i_min}   I_max: {i_max}   Range: {i_max - i_min}   "
             f"  |   After → I_min: 0   I_max: 255   Range: 255")

def save_stretched():
    if not check_loaded(): return
    path = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
    if path:
        gray = rgb_to_grayscale(state.original_np)
        stretched = histogram_stretching(gray)
        Image.fromarray(stretched, 'L').save(path)
        messagebox.showinfo("Saved", f"Stretched image saved to:\n{path}")

btn(btn3_bar, "▶  Apply Histogram Stretching", run_stretch)
btn(btn3_bar, "💾  Save Result", save_stretched, accent=False)

def refresh_tab3():
    if state.original_np is not None: run_stretch()

tab_refreshers.append(refresh_tab3)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Point Operations (Brightness / Darkness / Contrast)
# ═══════════════════════════════════════════════════════════════════════════════
tab4 = ttk.Frame(nb); nb.add(tab4, text="  Point Operations  ")
for c in range(4): tab4.columnconfigure(c, weight=1)
tab4.rowconfigure(1, weight=1)

info4 = tk.Label(tab4,
    text="Point operations applied directly on pixel values.\n"
         "Brightness (+) adds a constant, Darkness (-) subtracts a constant, "
         "and Multiply Contrast scales pixel values by a factor.",
    bg=PANEL_BG, fg=TEXT_MUTED, font=FONT_BODY, wraplength=800, justify="left", pady=6, padx=10)
info4.grid(row=0, column=0, columnspan=4, sticky="ew", padx=8, pady=(8, 0))

p4_orig = make_panel_frame(tab4, col=0); t4_orig, l4_orig = image_panel(p4_orig)
p4_bright = make_panel_frame(tab4, col=1); t4_bright, l4_bright = image_panel(p4_bright)
p4_dark = make_panel_frame(tab4, col=2); t4_dark, l4_dark = image_panel(p4_dark)
p4_contrast = make_panel_frame(tab4, col=3); t4_contrast, l4_contrast = image_panel(p4_contrast)

# Sliders variables
bright_val = tk.IntVar(value=50)
dark_val = tk.IntVar(value=50)
contrast_val = tk.DoubleVar(value=1.5)

# ======= تعريف run_point_ops قبل make_slider =======

def run_point_ops():
    if not check_loaded(): return
    img = state.original_np
    set_panel(l4_orig, t4_orig, img, "Original")
    
    b = adjust_brightness(img, bright_val.get())
    set_panel(l4_bright, t4_bright, b, f"Brightness +{bright_val.get()}")
    
    d = adjust_darkness(img, dark_val.get())
    set_panel(l4_dark, t4_dark, d, f"Darkness -{dark_val.get()}")
    
    c = multiply_contrast(img, contrast_val.get())
    set_panel(l4_contrast, t4_contrast, c, f"Contrast ×{contrast_val.get():.1f}")

# ======= Slider helper =======

def make_slider(parent, var, from_, to_, label, resolution, cmd):
    f = tk.Frame(parent, bg=CARD_BG)
    f.pack(pady=(8, 0))
    tk.Label(f, text=label, bg=CARD_BG, fg=TEXT_MUTED, font=("Segoe UI", 8)).pack()
    s = tk.Scale(f, from_=from_, to=to_, orient=tk.HORIZONTAL, variable=var,
                 resolution=resolution, length=140,
                 bg=CARD_BG, fg=TEXT, troughcolor=BORDER, highlightthickness=0,
                 activebackground=ACCENT, command=lambda x: cmd())
    s.pack()
    return s

make_slider(p4_bright, bright_val, 0, 255, "Brightness +", 1, run_point_ops)
make_slider(p4_dark, dark_val, 0, 255, "Darkness -", 1, run_point_ops)
make_slider(p4_contrast, contrast_val, 0.0, 3.0, "Contrast Factor", 0.1, run_point_ops)

btn4_bar = tk.Frame(tab4, bg=PANEL_BG, pady=6)
btn4_bar.grid(row=2, column=0, columnspan=4)

def save_brightness():
    if not check_loaded(): return
    path = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
    if path:
        b = adjust_brightness(state.original_np, bright_val.get())
        Image.fromarray(b).save(path)
        messagebox.showinfo("Saved", f"Brightness image saved to:\n{path}")

def save_darkness():
    if not check_loaded(): return
    path = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
    if path:
        d = adjust_darkness(state.original_np, dark_val.get())
        Image.fromarray(d).save(path)
        messagebox.showinfo("Saved", f"Darkness image saved to:\n{path}")

def save_contrast():
    if not check_loaded(): return
    path = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
    if path:
        c = multiply_contrast(state.original_np, contrast_val.get())
        Image.fromarray(c).save(path)
        messagebox.showinfo("Saved", f"Contrast image saved to:\n{path}")

btn(btn4_bar, "▶  Apply Point Ops", run_point_ops)
btn(btn4_bar, "💾  Save Brightness", save_brightness, accent=False)
btn(btn4_bar, "💾  Save Darkness", save_darkness, accent=False)
btn(btn4_bar, "💾  Save Contrast", save_contrast, accent=False)

def refresh_tab4():
    if state.original_np is not None: run_point_ops()

tab_refreshers.append(refresh_tab4)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Morphological Operations
# ═══════════════════════════════════════════════════════════════════════════════
tab5 = ttk.Frame(nb)
nb.add(tab5, text="  Morphological Operations  ")

for c in range(5):
    tab5.columnconfigure(c, weight=1)

tab5.rowconfigure(1, weight=1)

info5 = tk.Label(
    tab5,
    text="Morphological Operations on binary images:\n"
         "Dilation expands objects, Erosion shrinks objects,\n"
         "Opening removes noise, Closing fills gaps.",
    bg=PANEL_BG,
    fg=TEXT_MUTED,
    font=FONT_BODY,
    wraplength=800,
    justify="left",
    pady=6,
    padx=10
)

info5.grid(row=0, column=0, columnspan=5, sticky="ew", padx=8, pady=(8, 0))

p5_orig = make_panel_frame(tab5, col=0)
t5_orig, l5_orig = image_panel(p5_orig)

p5_dil = make_panel_frame(tab5, col=1)
t5_dil, l5_dil = image_panel(p5_dil)

p5_ero = make_panel_frame(tab5, col=2)
t5_ero, l5_ero = image_panel(p5_ero)

p5_open = make_panel_frame(tab5, col=3)
t5_open, l5_open = image_panel(p5_open)

p5_close = make_panel_frame(tab5, col=4)
t5_close, l5_close = image_panel(p5_close)

btn5_bar = tk.Frame(tab5, bg=PANEL_BG, pady=6)
btn5_bar.grid(row=2, column=0, columnspan=5)

def run_morphology():
    if not check_loaded():
        return

    img = state.original_np

    dilation = dilation_operation(img)
    erosion = erosion_operation(img)
    opening = opening_operation(img)
    closing = closing_operation(img)

    set_panel(l5_orig, t5_orig, img, "Original Image")
    set_panel(l5_dil, t5_dil, dilation, "Dilation")
    set_panel(l5_ero, t5_ero, erosion, "Erosion")
    set_panel(l5_open, t5_open, opening, "Opening")
    set_panel(l5_close, t5_close, closing, "Closing")

btn(btn5_bar, "▶ Apply Morphological Operations", run_morphology)

def save_morphology():
    if not check_loaded():
        return

    folder = filedialog.askdirectory(title="Select folder to save images")

    if folder:
        Image.fromarray(dilation_operation(state.original_np)).save(
            os.path.join(folder, "dilation.png"))

        Image.fromarray(erosion_operation(state.original_np)).save(
            os.path.join(folder, "erosion.png"))

        Image.fromarray(opening_operation(state.original_np)).save(
            os.path.join(folder, "opening.png"))

        Image.fromarray(closing_operation(state.original_np)).save(
            os.path.join(folder, "closing.png"))

        messagebox.showinfo("Saved", f"Morphological images saved to:\n{folder}")

btn(btn5_bar, "💾 Save Results", save_morphology, accent=False)

def refresh_tab5():
    if state.original_np is not None:
        run_morphology()

tab_refreshers.append(refresh_tab5)


# ── Status Bar ────────────────────────────────────────────────────────────────
status_bar = tk.Frame(root, bg=DARK_BG, pady=4)
status_bar.pack(fill="x", padx=20, side="bottom")
tk.Label(status_bar, text="CS303 Lab Toolkit  •  Supported: JPG, PNG, BMP, TIFF, WEBP",
         font=("Segoe UI", 9), bg=DARK_BG, fg=TEXT_MUTED).pack(side="left")

root.mainloop()