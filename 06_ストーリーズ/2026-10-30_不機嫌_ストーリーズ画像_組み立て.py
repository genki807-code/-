import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

SRC = sys.argv[1]  # 素材フォルダ
OUT = sys.argv[2]  # 出力フォルダ
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)


def bg_photo(name, bright=1.0, xr=0.5):
    im = Image.open(f'{SRC}/{name}').convert('RGB')
    im = ImageEnhance.Color(im).enhance(0.88)
    s = H / im.height
    im = im.resize((round(im.width * s), H), Image.LANCZOS)
    left = round((im.width - W) * xr)
    im = im.crop((left, 0, left + W, H))
    return ImageEnhance.Brightness(im).enhance(bright)


def plain(color=(232, 216, 200)):
    return Image.new('RGB', (W, H), color)


def block(im, lines, cy, size=60, gap=24, para=36):
    """lines の '' は段落の区切り（少しあける）。cy はかたまりの真ん中の高さ"""
    d = ImageDraw.Draw(im, 'RGBA')
    f = ImageFont.truetype(FONT, size)
    rows = [l for l in lines]
    hs = [para if l == '' else size for l in rows]
    total = sum(hs) + gap * (len(rows) - 1)
    widths = [d.textlength(l, font=f) for l in rows if l]
    bw = max(widths) + 60
    y = cy - total / 2
    d.rounded_rectangle([(W - bw) / 2, y - 40, (W + bw) / 2, y + total + 40],
                        radius=28, fill=PINK + (225,))
    for l, h in zip(rows, hs):
        if l:
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2, y), l, font=f, fill='white', stroke_width=4, stroke_fill=(0, 0, 0))
        y += h + gap
    return im


# 1枚目（朝・アンケートは真ん中に貼る）
im = bg_photo('カット3.jpg', 1.0, 0.5)
block(im, ['近くの人のため息に', '「私のせいかな」と', '思うことはありますか？'], 560)
im.save(f'{OUT}/1枚目.jpg', quality=92)

# 2枚目（投稿のあと）
im = bg_photo('カット3.jpg', 1.35, 0.9)
block(im, ['朝のアンケート', '答えてくれて', 'ありがとうございます', '',
           '人の不機嫌が', '気になってしまう人に向けて', 'リールを作りました'], 880)
im.save(f'{OUT}/2枚目.jpg', quality=92)

# 3枚目（リールのシェアの上に重ねる・背景は透明）
im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
block(im, ['新しいリール', '「その不機嫌', 'あなたが直さなくていい」を', '投稿しました'], 470)
block(im, ['空気が重い日に', '見返してね'], 1380)
im.save(f'{OUT}/3枚目_重ねる文字.png')

# 4枚目（質問ボックスは真ん中に貼る）
im = plain()
block(im, ['空気が重い日に', '自分の機嫌をとるために', 'していることはありますか？', '', 'ひと言で大丈夫です'], 560)
im.save(f'{OUT}/4枚目.jpg', quality=92)

# 表紙（サムネA・句読点なし）。プロフィールの一覧では真ん中の 3:4 だけ見えるので、文字はその中に入れる
im = bg_photo('カット3.jpg', 1.3, 0.9)
d = ImageDraw.Draw(im, 'RGBA')
fb = ImageFont.truetype(FONT, 104)
fs = ImageFont.truetype(FONT, 46)
big = ['その不機嫌', 'あなたが', '直さなくていい']
small = ['やりとりはふだん通り', '気分までは背負わない3つのコツ']
y = 640
d.rounded_rectangle([70, y - 50, W - 70, y + 3 * 104 + 2 * 30 + 50 + 40 + 2 * 46 + 18 + 40],
                    radius=32, fill=PINK + (235,))
for l in big:
    w = d.textlength(l, font=fb)
    d.text(((W - w) / 2, y), l, font=fb, fill='white', stroke_width=6, stroke_fill=(0, 0, 0))
    y += 104 + 30
y += 40
for l in small:
    w = d.textlength(l, font=fs)
    d.text(((W - w) / 2, y), l, font=fs, fill='white', stroke_width=4, stroke_fill=(0, 0, 0))
    y += 46 + 18
im.save(f'{OUT}/表紙_サムネA.jpg', quality=92)
print('done')
