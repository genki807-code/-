# note 2本目「休むのが苦手な繊細さんへ」の見出し画像。1本目の v3 と同じ形（光のぼけを絵で描く・白いカード・明朝体）。色だけ朝の光（ピンク〜クリーム）に
import sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H = 1280, 670
MIN = '/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf'
PINK = (236, 122, 152)
BROWN = (92, 70, 60)
random.seed(7)

# うすい緑〜クリームのグラデーション
bg = Image.new('RGB', (W, H))
d = ImageDraw.Draw(bg)
for y in range(H):
    t = y / H
    c = tuple(int(a + (b - a) * t) for a, b in zip((246, 222, 222), (250, 242, 228)))
    d.line([(0, y), (W, y)], fill=c)

# 光の玉（ぼけ）
im = bg.convert('RGBA')
cols = [(255, 255, 240), (250, 210, 215), (245, 190, 200), (255, 236, 200), (230, 215, 240)]
for _ in range(70):
    r = random.randint(25, 110)
    x, y = random.randint(-50, W + 50), random.randint(-50, H + 50)
    col = random.choice(cols)
    layer = Image.new('RGBA', (W, H), col + (0,))
    ImageDraw.Draw(layer).ellipse([x - r, y - r, x + r, y + r], fill=col + (random.randint(60, 140),))
    im = Image.alpha_composite(im, layer.filter(ImageFilter.GaussianBlur(14)))
# 左上から光
glow = Image.new('RGBA', (W, H), (255, 255, 245, 0))
ImageDraw.Draw(glow).ellipse([-300, -350, 600, 350], fill=(255, 255, 245, 170))
im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(80))).convert('RGB')

d = ImageDraw.Draw(im, 'RGBA')
d.rectangle([170, 110, W - 170, H - 110], fill=(255, 252, 248, 225))
d.rectangle([182, 122, W - 182, H - 122], outline=PINK + (255,), width=2)

def ctext(t, y, size, spacing):
    fo = ImageFont.truetype(MIN, size)
    w = sum(d.textlength(ch, font=fo) for ch in t) + spacing * (len(t) - 1)
    x = (W - w) / 2
    for ch in t:
        d.text((x, y), ch, font=fo, fill=BROWN)
        x += d.textlength(ch, font=fo) + spacing

ctext('休むのが苦手な', 240, 66, 4)
ctext('繊細さんへ', 330, 66, 4)
d.line([(W / 2 - 40, 430), (W / 2 + 40, 430)], fill=PINK, width=3)
ctext('罪悪感をほどく休み方と「休みの連絡」のひな形', 458, 33, 2)
im.save(OUT, quality=92)
