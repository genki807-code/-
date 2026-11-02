# note の知らせ（2枚）v2：背景を見出し画像と同じ「光のぼけ」に（写真は使わない）。上下240pxの外に文字を置かない
import sys
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]      # 出力フォルダ
HEADER = sys.argv[2]   # note の見出し画像 v3
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)
BEIGE = (240, 228, 214)

def bokeh(seed):
    random.seed(seed)
    bg = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((222, 234, 204), (246, 238, 226))))
    im = bg.convert('RGBA')
    cols = [(255, 255, 240), (200, 225, 170), (175, 208, 145), (255, 236, 200), (245, 200, 210)]
    for _ in range(80):
        r = random.randint(30, 140)
        x, y = random.randint(-60, W + 60), random.randint(-60, H + 60)
        col = random.choice(cols)
        layer = Image.new('RGBA', (W, H), col + (0,))
        ImageDraw.Draw(layer).ellipse([x - r, y - r, x + r, y + r], fill=col + (random.randint(60, 140),))
        im = Image.alpha_composite(im, layer.filter(ImageFilter.GaussianBlur(16)))
    glow = Image.new('RGBA', (W, H), (255, 255, 245, 0))
    ImageDraw.Draw(glow).ellipse([-400, -400, 700, 500], fill=(255, 255, 245, 170))
    return Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(90))).convert('RGB')


def block(im, lines, cy, size=58, gap=24, para=36):
    d = ImageDraw.Draw(im, 'RGBA')
    f = ImageFont.truetype(FONT, size)
    hs = [para if l == '' else size for l in lines]
    total = sum(hs) + gap * (len(lines) - 1)
    bw = max(d.textlength(l, font=f) for l in lines if l) + 80
    y = cy - total / 2
    d.rounded_rectangle([(W - bw) / 2, y - 50, (W + bw) / 2, y + total + 50], radius=28, fill=PINK + (235,))
    for l, h in zip(lines, hs):
        if l:
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2, y), l, font=f, fill='white', stroke_width=4, stroke_fill=(0, 0, 0))
        y += h + gap

# 1枚目：見出し画像を見せる
im = bokeh(7)
block(im, ['noteを書きました'], 470, size=72)
hd = Image.open(HEADER).convert('RGB').resize((960, int(960 * 670 / 1280)))
im.paste(hd, ((W - 960) // 2, 640))
block(im, ['職場で疲れやすい繊細さんへ', '音・電話・人の機嫌に', '疲れたときの小さな工夫を', 'まとめました'], 1400, size=52)
im.save(f'{OUT}/1枚目.jpg', quality=92)

# 2枚目：中身と、リンクスタンプを置く場所
im = bokeh(11)
block(im, ['こんな中身です', '',
           '①職場の音で疲れたとき', '②電話がこわいとき', '③近くの人が不機嫌なとき', '',
           'そのまま使える電話メモ', '1日の流れ', '書きこんで使えるメモ', '',
           '有料（300円）です'], 800, size=52)
block(im, ['よかったら読んでみてね'], 1390, size=52)
im.save(f'{OUT}/2枚目.jpg', quality=92)
