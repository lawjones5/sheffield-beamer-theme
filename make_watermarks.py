# Extract the four coat-of-arms motifs from the template background art as
# transparent watermarks, for use on white paper in sheffielddoc.sty.
import os
from PIL import Image

SRC = os.path.dirname(__file__) + '/assets'
OUT = SRC

for name in ['rose', 'arrows', 'crown', 'book']:
    src = os.path.join(SRC, f'bg-{name}.png')
    im = Image.open(src).convert('L')  # 243 bg, ~232 motif
    w, h = im.size
    px = im.load()

    # alpha: 0 for background (243), smooth ramp to 255 for motif (232)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if v >= 241:      # background
                continue
            a = (241 - v) / (241 - 232) * 255
            a = max(0, min(255, int(a)))
            # tone the motif slightly darker so it reads on white paper
            g = 243 - int((243 - v) * 1.7)
            g = max(0, min(255, g))
            op[x, y] = (g, g, g, a)

    # crop to the motif's bounding box
    bbox = out.getbbox()
    out = out.crop(bbox)
    dst = os.path.join(OUT, f'wm-{name}.png')
    out.save(dst, optimize=True)
    print(f'wm-{name}.png', out.size, f'bbox={bbox}')
