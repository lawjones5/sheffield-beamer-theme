# Generate LaTeX theme assets from the extracted pptx media.
import os
from PIL import Image

SRC = os.path.join(os.path.dirname(__file__), '..', '_extract', 'ppt', 'media')
OUT = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(OUT, exist_ok=True)

# Full-slide watermarked backgrounds (16:9, F3F3F3 canvas + tone-on-tone motif)
for src, dst in [('image1.png', 'bg-rose.png'), ('image4.png', 'bg-arrows.png'),
                 ('image7.png', 'bg-crown.png'), ('image10.png', 'bg-book.png')]:
    im = Image.open(os.path.join(SRC, src)).convert('RGB')
    im.save(os.path.join(OUT, dst), optimize=True)
    print(dst, im.size, os.path.getsize(os.path.join(OUT, dst)))

# TOP 100 lockup (already transparent)
im = Image.open(os.path.join(SRC, 'image2.png'))
im.save(os.path.join(OUT, 'top100.png'), optimize=True)
print('top100.png', im.size)

# Crest from image8 (white crest on purple block): crop to the crest, then make
# the surrounding purple transparent while KEEPING interior purple detail
# (Disce Doce lettering, rose centre) so it works on light backgrounds too.
crest = Image.open(os.path.join(SRC, 'image8.png')).convert('RGB')
w, h = crest.size
px = crest.load()

def is_bg(p):
    r, g, b = p
    return abs(r-0x44) < 30 and abs(g-0x00) < 30 and abs(b-0x99) < 30

# columns containing non-bg pixels -> crest bounding box
cols = [x for x in range(w) if any(not is_bg(px[x, y]) for y in range(h))]
rows = [y for y in range(h) if any(not is_bg(px[x, y]) for x in range(w))]
x0, x1, y0, y1 = min(cols), max(cols), min(rows), max(rows)
print('crest bbox', x0, y0, x1, y1)

crop = crest.crop((max(0, x0-6), max(0, y0-6), x1+7, y1+7))
cw, ch = crop.size
cp = crop.load()

from collections import deque
seen = [[False]*ch for _ in range(cw)]
q = deque()
for x in range(cw):
    for y in (0, ch-1):
        if is_bg(cp[x, y]) and not seen[x][y]:
            seen[x][y] = True; q.append((x, y))
for y in range(ch):
    for x in (0, cw-1):
        if is_bg(cp[x, y]) and not seen[x][y]:
            seen[x][y] = True; q.append((x, y))
while q:
    x, y = q.popleft()
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < cw and 0 <= ny < ch and not seen[nx][ny] and is_bg(cp[nx, ny]):
            seen[nx][ny] = True; q.append((nx, ny))

out = Image.new('RGBA', (cw, ch))
op = out.load()
for x in range(cw):
    for y in range(ch):
        r, g, b = cp[x, y][:3]
        op[x, y] = (r, g, b, 0) if seen[x][y] else (r, g, b, 255)
out.save(os.path.join(OUT, 'crest.png'), optimize=True)
print('crest.png', out.size, 'bbox-cropped')

# White crest (for use on purple backgrounds): same mask, recoloured white,
# interior detail holes (Disce Doce, rose centre) kept as purple -> transparent
# is wrong there, so interior non-white detail becomes purple-on-white? Instead:
# white version keeps everything opaque, recolouring purple->transparent only for
# exterior, and interior purple detail is kept PURPLE (visible on white).
out2 = Image.new('RGBA', (cw, ch))
op2 = out2.load()
for x in range(cw):
    for y in range(ch):
        r, g, b = cp[x, y][:3]
        if seen[x][y]:
            op2[x, y] = (255, 255, 255, 255)   # exterior bg -> white?? no: transparent
# Rebuild properly: exterior -> transparent; crest body -> white; interior purple detail -> purple.
for x in range(cw):
    for y in range(ch):
        r, g, b = cp[x, y][:3]
        if seen[x][y]:
            op2[x, y] = (r, g, b, 0)           # exterior purple -> transparent
        elif is_bg((r, g, b)):
            op2[x, y] = (0x44, 0x00, 0x99, 255)  # interior detail (Disce Doce, rose) stays purple
        else:
            op2[x, y] = (255, 255, 255, 255)   # crest body -> white
out2.save(os.path.join(OUT, 'crest-white.png'), optimize=True)
print('crest-white.png', out2.size)
