import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]  # 出力ファイル
W, H = 1280, 670   # note の見出し画像の大きさ
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)
BEIGE = (240, 228, 214)

im = Image.new('RGB', (W, H), BEIGE)
d = ImageDraw.Draw(im, 'RGBA')

def center(text, y, size, stroke=5):
    f = ImageFont.truetype(FONT, size)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill='white', stroke_width=stroke, stroke_fill=(0, 0, 0))
    return w

# 大きい文字（2行）をピンクの帯にのせる
big = ['職場にいるだけで', 'ぐったりする繊細さんへ']
fb = ImageFont.truetype(FONT, 92)
bw = max(d.textlength(t, font=fb) for t in big) + 100
top, gap = 150, 30
d.rounded_rectangle([(W - bw) / 2, top - 45, (W + bw) / 2, top + 92 * 2 + gap + 45], radius=32, fill=PINK + (240,))
for i, t in enumerate(big):
    center(t, top + i * (92 + gap), 92)

# 小さい文字（帯の下）
fs = ImageFont.truetype(FONT, 46)
sub = '音・電話・人の機嫌に疲れたときの小さな工夫'
sw = d.textlength(sub, font=fs) + 60
sy = 470
d.rounded_rectangle([(W - sw) / 2, sy - 22, (W + sw) / 2, sy + 46 + 22], radius=22, fill=PINK + (240,))
center(sub, sy, 46, stroke=3)

im.save(OUT, quality=92)
