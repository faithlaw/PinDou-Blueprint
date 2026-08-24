import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.color import rgb2lab, deltaE_cie76

def extract_all_mard_colors(chart_path="MARD.png"):
    """
    Scans the MARD chart image across its 13 columns and 17 rows 
    and extracts the exact RGB values for all 221 bead swatches.
    """
    chart_img = cv2.imread(chart_path)
    if chart_img is None:
        raise FileNotFoundError(f"Could not load {chart_path}. Please place MARD.png in the directory.")
        
    chart_img = cv2.cvtColor(chart_img, cv2.COLOR_BGR2RGB)
    
    col_labels = [
        ["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10","A11","A12","A13","A14","A15","A16","A17"],
        ["A18","A19","A20","A21","A22","A23","A24","A25","A26","B01","B02","B03","B04","B05","B06","B07","B08"],
        ["B09","B10","B11","B12","B13","B14","B15","B16","B17","B18","B19","B20","B21","B22","B23","B24","B25"],
        ["B26","B27","B28","B29","B30","B31","B32","C01","C02","C03","C04","C05","C06","C07","C08","C09","C10"],
        ["C11","C12","C13","C14","C15","C16","C17","C18","C19","C20","C21","C22","C23","C24","C25","C26","C27"],
        ["C28","C29","D01","D02","D03","D04","D05","D06","D07","D08","D09","D10","D11","D12","D13","D14","D15"],
        ["D16","D17","D18","D19","D20","D21","D22","D23","D24","D25","D26","E01","E02","E03","E04","E05","E06"],
        ["E07","E08","E09","E10","E11","E12","E13","E14","E15","E16","E17","E18","E19","E20","E21","E22","E23"],
        ["E24","F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16"],
        ["F17","F18","F19","F20","F21","F22","F23","F24","F25","G01","G02","G03","G04","G05","G06","G07","G08"],
        ["G09","G10","G11","G12","G13","G14","G15","G16","G17","G18","G19","G20","G21","H01","H02","H03","H04"],
        ["H05","H06","H07","H08","H09","H10","H11","H12","H13","H14","H15","H16","H17","H18","H19","H20","H21"],
        ["H22","H23","M01","M02","M03","M04","M05","M06","M07","M08","M09","M10","M11","M12","M13","M14","M15"]
    ]

    h, w, _ = chart_img.shape
    cols_x = np.linspace(0.045 * w, 0.955 * w, 13)
    rows_y = np.linspace(0.125 * h, 0.955 * h, 17)

    extracted_palette = {}

    for c_idx, col_x in enumerate(cols_x):
        for r_idx, row_y in enumerate(rows_y):
            code = col_labels[c_idx][r_idx]
            
            sample_x = int(col_x + 20)
            sample_y = int(row_y)
            
            patch = chart_img[sample_y-2:sample_y+3, sample_x-2:sample_x+3]
            avg_rgb = patch.mean(axis=(0, 1)).astype(int)
            
            extracted_palette[code] = tuple(avg_rgb)

    return extracted_palette

def find_nearest_mard_color(rgb_pixel, mard_palette):
    pixel_lab = rgb2lab(np.uint8([[rgb_pixel]])) / 100.0
    min_dist = float('inf')
    best_code, best_rgb = None, (0, 0, 0)

    for code, mard_rgb in mard_palette.items():
        mard_lab = rgb2lab(np.uint8([[mard_rgb]])) / 100.0
        dist = deltaE_cie76(pixel_lab, mard_lab)[0][0]
        if dist < min_dist:
            min_dist = dist
            best_code = code
            best_rgb = mard_rgb

    return best_code, best_rgb

def generate_blueprint_from_image(input_path="input.png", output_path="图纸.png", grid_w=64, grid_h=64):
    print("1. Reading MARD.png chart and extracting 221 colors...")
    mard_palette = extract_all_mard_colors("MARD.png")

    print(f"2. Processing {input_path} and downsampling to {grid_w}x{grid_h} grid...")
    img = Image.open(input_path).convert('RGB')
    img_resized = img.resize((grid_w, grid_h), Image.Resampling.BILINEAR)
    img_np = np.array(img_resized)

    grid_codes = np.empty((grid_h, grid_w), dtype=object)
    grid_rgbs = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)
    color_counts = {}

    for y in range(grid_h):
        for x in range(grid_w):
            pixel = img_np[y, x]
            code, rgb = find_nearest_mard_color(pixel, mard_palette)
            grid_codes[y, x] = code
            grid_rgbs[y, x] = rgb
            color_counts[code] = color_counts.get(code, 0) + 1

    cell_size = 45  
    ruler_w = 60
    margin = 60
    
    grid_px_w = grid_w * cell_size
    grid_px_h = grid_h * cell_size
    
    canvas_w = grid_px_w + (ruler_w * 2) + (margin * 2)
    canvas_h = grid_px_h + (ruler_w * 2) + margin + 320

    blueprint = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(blueprint)

    def load_font(size):
        font_paths = ["simhei.ttf", "msyh.ttc", "arial.ttf", "/System/Library/Fonts/PingFang.ttc"]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_cell = load_font(12)
    font_axis = load_font(13)
    font_watermark = load_font(80)
    font_summary = load_font(34)
    font_card = load_font(26)

    start_x = margin + ruler_w
    start_y = margin + ruler_w

    for y in range(grid_h):
        for x in range(grid_w):
            cx1 = start_x + x * cell_size
            cy1 = start_y + y * cell_size
            cx2 = cx1 + cell_size
            cy2 = cy1 + cell_size

            code = grid_codes[y, x]
            fill_color = tuple(grid_rgbs[y, x])

            draw.rectangle([cx1, cy1, cx2, cy2], fill=fill_color)
            draw.rectangle([cx1, cy1, cx2, cy2], outline=(230, 230, 230), width=1)

            luminance = 0.299 * fill_color[0] + 0.587 * fill_color[1] + 0.114 * fill_color[2]
            text_color = (15, 15, 15) if luminance > 125 else (240, 240, 240)

            bbox = font_cell.getbbox(code)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx = cx1 + (cell_size - tw) / 2
            ty = cy1 + (cell_size - th) / 2 - 2
            draw.text((tx, ty), code, fill=text_color, font=font_cell)

    for x in range(grid_w):
        val = str(x + 1)
        nx = start_x + x * cell_size + cell_size / 2
        bbox = font_axis.getbbox(val)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        draw.text((nx - tw / 2, start_y - 20 - th / 2), val, fill=(120, 120, 120), font=font_axis)
        draw.text((nx - tw / 2, start_y + grid_px_h + 20 - th / 2), val, fill=(120, 120, 120), font=font_axis)

    for y in range(grid_h):
        val = str(y + 1)
        ny = start_y + y * cell_size + cell_size / 2
        bbox = font_axis.getbbox(val)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        draw.text((start_x - 30 - tw / 2, ny - th / 2), val, fill=(120, 120, 120), font=font_axis)
        draw.text((start_x + grid_px_w + 30 - tw / 2, ny - th / 2), val, fill=(120, 120, 120), font=font_axis)

    for x in range(0, grid_w + 1, 10):
        lx = start_x + x * cell_size
        draw.line([(lx, start_y), (lx, start_y + grid_px_h)], fill=(240, 80, 80), width=2)
    for y in range(0, grid_h + 1, 10):
        ly = start_y + y * cell_size
        draw.line([(start_x, ly), (start_x + grid_px_w, ly)], fill=(240, 80, 80), width=2)

    draw.rectangle([start_x, start_y, start_x + grid_px_w, start_y + grid_px_h], outline=(240, 80, 80), width=3)

    legend_y = start_y + grid_px_h + ruler_w + 30
    total_beads = sum(color_counts.values())
    summary_text = f"{grid_w}x{grid_h}/{len(color_counts)}色/共{total_beads}颗"
    draw.text((start_x, legend_y), summary_text, fill=(0, 0, 0), font=font_summary)

    card_x = start_x
    card_y = legend_y + 70
    card_w, card_h = 240, 80

    for code, count in color_counts.items():
        rgb = mard_palette[code]
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=rgb, outline=(210, 210, 210), width=2)
        
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        txt_col = (0, 0, 0) if luminance > 125 else (255, 255, 255)
        
        card_text = f"{code} ({count})"
        bbox = font_card.getbbox(card_text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((card_x + (card_w - tw) / 2, card_y + (card_h - th) / 2 - 2), card_text, fill=txt_col, font=font_card)

        card_x += card_w + 25
        if card_x + card_w > start_x + grid_px_w:
            card_x = start_x
            card_y += card_h + 20

    print("3. Saving final blueprint to 图纸.png...")
    blueprint.save(output_path, quality=100, dpi=(300, 300))
    print("Done!")

generate_blueprint_from_image(
    input_path="input.png",
    output_path="图纸.png",
    grid_w=64,
    grid_h=64
)
