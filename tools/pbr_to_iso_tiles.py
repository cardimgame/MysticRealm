# tools/pbr_to_iso_tiles.py
# Usage: python tools/pbr_to_iso_tiles.py <src_png> <tile_w> <tile_h> <variants>
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import sys, random, math

def diamond_mask(w, h):
    mask = Image.new('L', (w, h), 0)
    mpx = mask.load()
    for y in range(h):
        if y <= h//2:
            k = y / (h/2)
        else:
            k = (h - 1 - y) / (h/2)
        half_width = int((w/2) * k + 0.5)
        x0 = w//2 - half_width
        x1 = w//2 + half_width
        for x in range(max(0, x0), min(w, x1+1)):
            mpx[x, y] = 255
    return mask

def square_to_iso(img: Image.Image, tile_w=128, tile_h=64):
    base = max(tile_w, tile_h*2)
    img_sq = img.resize((base, base), Image.LANCZOS)
    rot = img_sq.rotate(45, resample=Image.BICUBIC, expand=True)
    w, h = rot.size
    iso = rot.resize((w, max(1, int(h*0.5))), Image.LANCZOS)
    w2, h2 = iso.size
    cx, cy = w2//2, h2//2
    left = cx - tile_w//2
    upper = cy - tile_h//2
    iso_crop = iso.crop((left, upper, left+tile_w, upper+tile_h))
    m = diamond_mask(tile_w, tile_h)
    iso_crop.putalpha(m)
    return iso_crop

def jitter(img: Image.Image):
    b = ImageEnhance.Brightness(img).enhance(1.0 + random.uniform(-0.04, 0.04))
    c = ImageEnhance.Contrast(b).enhance(1.0 + random.uniform(-0.03, 0.03))
    s = ImageEnhance.Color(c).enhance(1.0 + random.uniform(-0.05, 0.05))
    return s.filter(ImageFilter.GaussianBlur(random.uniform(0.0, 0.3)))

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: python tools/pbr_to_iso_tiles.py <src_png> <tile_w> <tile_h> <variants>')
        sys.exit(1)
    src_path = Path(sys.argv[1])
    tile_w = int(sys.argv[2]); tile_h = int(sys.argv[3]); variants = int(sys.argv[4])
    img = Image.open(src_path).convert('RGB')
    out_dir = Path('assets/tiles/grass'); out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(variants):
        iso = square_to_iso(jitter(img), tile_w, tile_h)
        iso.save(out_dir / f'grass_{tile_w}x{tile_h}_v{i+1:02d}.png')
    print(f'Saved {variants} tiles to {out_dir}')
