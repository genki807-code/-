# おしゃれ版 3案（A：文字だけ・B：木もれ日の写真・C：やわらかい色の切りかえ）
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]   # 木もれ日の写真（音疲れ カット2）
OUTDIR = sys.argv[2]
W, H = 1280, 670
MIN = '/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf'
PINK = (236, 122, 152)
BEIGE = (244, 236, 226)
BROWN = (92, 70, 60)

T1, T2 = '職場にいるだけで', 'ぐったりする繊細さんへ'
SUB = '音・電話・人の機嫌に疲れたときの小さな工夫'

def f(size): return ImageFont.truetype(MIN, size)

def ctext(d, t, y, size, fill, x0=0, x1=W, spacing=0):
    fo = f(size)
    w = d.textlength(t, font=fo) + spacing * (len(t) - 1)
    x = x0 + (x1 - x0 - w) / 2
    for ch in t:
        d.text((x, y), ch, font=fo, fill=fill)
        x += d.textlength(ch, font=fo) + spacing

def title_block(d, cy, color, sub_color, accent, x0=0, x1=W):
    ctext(d, T1, cy - 120, 66, color, x0, x1, 4)
    ctext(d, T2, cy - 30, 66, color, x0, x1, 4)
    mx = (x0 + x1) / 2
    d.line([(mx - 40, cy + 70), (mx + 40, cy + 70)], fill=accent, width=3)
    ctext(d, SUB, cy + 100, 30, sub_color, x0, x1, 2)

# A：文字だけ（ベージュ・細い枠・明朝）
a = Image.new('RGB', (W, H), BEIGE)
d = ImageDraw.Draw(a)
d.rectangle([40, 40, W - 40, H - 40], outline=PINK, width=2)
d.rectangle([52, 52, W - 52, H - 52], outline=PINK + (0,), width=1)
ctext(d, 'for sensitive people at work', 120, 24, PINK, spacing=3)
title_block(d, 360, BROWN, BROWN, PINK)
a.save(f'{OUTDIR}/A_文字だけ.jpg', quality=92)

# B：木もれ日の写真に白いベール＋まんなかに白い枠
ph = Image.open(SRC).convert('RGB')
s = max(W / ph.width, H / ph.height)
ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
l, t = (ph.width - W) // 2, (ph.height - H) // 2
b = ph.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(2))
b = Image.blend(b, Image.new('RGB', (W, H), (255, 255, 255)), 0.35)
d = ImageDraw.Draw(b, 'RGBA')
d.rectangle([170, 110, W - 170, H - 110], fill=(255, 252, 248, 225))
d.rectangle([182, 122, W - 182, H - 122], outline=PINK + (255,), width=2)
title_block(d, 360, BROWN, BROWN, PINK)
b.save(f'{OUTDIR}/B_木もれ日.jpg', quality=92)

# C：左がピンク・右がベージュ（左に小さな言葉、右にタイトル）
c = Image.new('RGB', (W, H), BEIGE)
d = ImageDraw.Draw(c)
d.rectangle([0, 0, 380, H], fill=PINK)
for i, ch in enumerate('ちいさな工夫'):
    fo = f(40)
    d.text((190 - d.textlength(ch, font=fo) / 2, 190 + i * 50), ch, font=fo, fill='white')
title_block(d, 360, BROWN, BROWN, PINK, x0=380, x1=W)
c.save(f'{OUTDIR}/C_2色.jpg', quality=92)
