# note の知らせ（2枚）。上下240pxの外に文字を置かない
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]      # 出力フォルダ
HEADER = sys.argv[2]   # note の見出し画像 v3
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)
BEIGE = (240, 228, 214)

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
im = Image.new('RGB', (W, H), BEIGE)
block(im, ['noteを書きました'], 470, size=72)
hd = Image.open(HEADER).convert('RGB').resize((960, int(960 * 670 / 1280)))
im.paste(hd, ((W - 960) // 2, 640))
block(im, ['職場で疲れやすい繊細さんへ', '音・電話・人の機嫌に', '疲れたときの小さな工夫を', 'まとめました'], 1400, size=52)
im.save(f'{OUT}/1枚目.jpg', quality=92)

# 2枚目：中身と、リンクスタンプを置く場所
im = Image.new('RGB', (W, H), BEIGE)
block(im, ['こんな中身です', '',
           '①職場の音で疲れたとき', '②電話がこわいとき', '③近くの人が不機嫌なとき', '',
           'そのまま使える電話メモ', '1日の流れ', '書きこんで使えるメモ', '',
           '有料（300円）です'], 800, size=52)
block(im, ['よかったら読んでみてね'], 1390, size=52)
d = ImageDraw.Draw(im)
d.rounded_rectangle([290, 1500, 790, 1640], radius=24, outline=PINK, width=4)  # リンクスタンプの目安の場所
im.save(f'{OUT}/2枚目.jpg', quality=92)
