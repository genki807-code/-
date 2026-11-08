# v3：背景を無地のベージュ →「光のぼけ」（ピンク・ベージュ系）に。小さい文字は白い半透明のカードにのせて読みやすく（アカウント主「背景なんか寂しい」11/8）
# v2：6枚目・4枚目の小さい文字を直し、2〜6枚目の帯の幅をそろえた（checker）
# 11/11 カルーセル「疲れた日の自分にかけたい言葉5選」7枚（1080×1350・写真なし）
import sys
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H = 1080, 1350
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)
BG = (240, 228, 214)   # うすいベージュ（セロトニンのストーリーズ v1 と同じ）
SUB = (110, 84, 70)    # 小さい文字の色（こげ茶）


def bokeh(seed):
    random.seed(seed)
    bg = Image.new('RGB', (W, H))
    dd = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        dd.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((250, 238, 228), (243, 220, 214))))
    im = bg.convert('RGBA')
    cols = [(255, 255, 248), (255, 214, 222), (250, 196, 206), (255, 232, 205), (246, 222, 196)]
    for _ in range(70):
        r = random.randint(30, 130)
        x, y = random.randint(-60, W + 60), random.randint(-60, H + 60)
        col = random.choice(cols)
        layer = Image.new('RGBA', (W, H), col + (0,))
        ImageDraw.Draw(layer).ellipse([x - r, y - r, x + r, y + r], fill=col + (random.randint(70, 150),))
        im = Image.alpha_composite(im, layer.filter(ImageFilter.GaussianBlur(14)))
    glow = Image.new('RGBA', (W, H), (255, 255, 248, 0))
    ImageDraw.Draw(glow).ellipse([-350, -350, 650, 450], fill=(255, 255, 248, 170))
    return Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(90))).convert('RGB')


def card(im, top, n, size=50, gap=24):
    # 小さい文字の下に白い半透明のカード
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    h = n * size + (n - 1) * gap
    ImageDraw.Draw(lay).rounded_rectangle([60, top - 36, W - 60, top + h + 36], radius=30, fill=(255, 255, 255, 175))
    return Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB')


def f(s):
    return ImageFont.truetype(FONT, s)


def band(d, lines, cy, size, stroke=5, gap=26, fixed_w=None):
    fn = f(size)
    for i, l in enumerate(lines):  # 横にはみ出さない大きさまで小さくする
        while d.textlength(l, font=fn) > W - 200:
            size -= 2
            fn = f(size)
    total = size * len(lines) + gap * (len(lines) - 1)
    bw = fixed_w or max(d.textlength(l, font=fn) for l in lines) + 90
    y = cy - total / 2
    d.rounded_rectangle([(W - bw) / 2, y - 48, (W + bw) / 2, y + total + 48], radius=28, fill=PINK)
    for l in lines:
        w = d.textlength(l, font=fn)
        d.text(((W - w) / 2, y), l, font=fn, fill='white', stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += size + gap


def sub(d, lines, top, size=50, gap=24):
    fn = f(size)
    for l in lines:
        while d.textlength(l, font=fn) > W - 200:
            size -= 2
            fn = f(size)
    y = top
    for l in lines:
        w = d.textlength(l, font=fn)
        d.text(((W - w) / 2, y), l, font=fn, fill=SUB)
        y += size + gap


def num(d, n):
    r = 62
    cx, cy = W / 2, 440
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='white', outline=PINK, width=6)
    fn = f(64)
    w = d.textlength(n, font=fn)
    d.text((cx - w / 2, cy - 34), n, font=fn, fill=PINK)


PAGES = [
    ('cover', ['疲れた日の自分に', 'かけたい言葉5選'], ['しんどい日にめくってみてね']),
    ('1', ['「今日はここまでで十分」'], ['全部できなくても', '今日のあなたはちゃんとがんばりました']),
    ('2', ['「疲れたって思っていい」'], ['疲れを感じるのは', 'あなたが弱いからではありません']),
    ('3', ['「返事はあしたでもいい」'], ['急ぎじゃない連絡なら', 'あしたの自分にまかせて大丈夫']),
    ('4', ['「できたことを1つだけ」'], ['できなかったことより', 'できたことを1つ思い出してみてね']),
    ('5', ['「今日はもう休んでいい」'], ['休むのは', 'がんばった日だけのものではありません']),
    ('end', ['しんどい日に見返せるよう', '保存してくださいね'], ['毎日20時に更新しています', 'フォローしてまた会いに来てね']),
]

for i, (kind, big, small) in enumerate(PAGES, 1):
    im = bokeh(3 if kind == 'cover' else 21 if kind == 'end' else 12)  # 2〜6枚目は同じ背景
    top = 830 if kind == 'cover' else 820 if kind == 'end' else 840
    im = card(im, top, len(small), size=54 if kind == 'cover' else 50)
    d = ImageDraw.Draw(im)
    if kind == 'cover':
        band(d, big, 600, 104, stroke=7)
        sub(d, small, 830, size=54)
    elif kind == 'end':
        band(d, big, 620, 66)
        sub(d, small, 820)
    else:
        num(d, kind)
        band(d, big, 680, 72, fixed_w=960)  # 2〜6枚目は帯の幅をそろえる
        sub(d, small, 840)
    d.text((W - 110, H - 80), f'{i}/7', font=f(34), fill=SUB)
    im.save(f'{OUT}/{i:02d}.jpg', quality=95)
print('done')
