# pindou-blueprint
此代码可做出拼豆图纸（有些瑕疵）

# Bead Pattern (拼豆图纸) Generator
Converts an input image into a bead/perler-style pixel blueprint using the **MARD** colour chart, and renders it as an annotated PNG with a colour grid, axis rulers, and a colour-usage legend.

## What it does
1. **Extract palette from chart** (`extract_all_mard_colors`)
   Reads `MARD.png` (a reference sheet of 221 bead colour swatches arranged in a 13×17 layout) and samples the RGB value at each swatch position using a hardcoded label map (`A01`–`H23`, `M01`–`M15`).

2. **Match pixels to nearest bead color** (`find_nearest_mard_color`)
   For each pixel, it converts RGB → CIE Lab and finds the closest MARD colour by CIE76 ΔE distance.

3. **Build the blueprint** (`generate_blueprint_from_image`)
   - Resizes the input image to a `grid_w × grid_h` grid (default 64×64).
   - Maps every grid cell to its nearest bead colour and code.
   - Draws each cell as a colored square with its bead code printed inside.
   - Adds row/column ruler numbers and red guide lines every 10 cells.
   - Appends a summary line (grid size, colour count, total bead count) and a legend of colour-code cards showing how many beads of each colour are needed.
   - Saves the result to `图纸.png`.

## Requirements

```bash
pip install opencv-python numpy pillow scikit-image
```

## Usage
Place `MARD.png` (the colour chart) and `input.png` (the source image) in the working directory, then run:

```bash
python script.py
```

Output: `图纸.png` — a printable bead-crafting blueprint.

### Parameters (in `generate_blueprint_from_image`)
| Parameter     | Default       | Meaning                          |
|---------------|---------------|-----------------------------------|
| `input_path`  | `"input.png"` | Source image to convert          |
| `output_path` | `"图纸.png"`   | Output blueprint file            |
| `grid_w`      | `64`          | Grid width in beads              |
| `grid_h`      | `64`          | Grid height in beads              |

## Fonts
The script looks for `simhei.ttf`, `msyh.ttc`, `arial.ttf`, or macOS's `PingFang.ttc` (in that order) to render Chinese labels, falling back to PIL's default bitmap font if none are found.
