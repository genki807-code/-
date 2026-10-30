import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]  # 出力フォルダ
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)


def plain(color=(240, 228, 214)):
    return Image.new('RGB', (W, H), color)


def block(im, lines, cy, size=60, gap=24, para=36):
    """lines の '' は段落の区切り（少しあける）。cy はかたまりの真ん中の高さ"""
    d = ImageDraw.Draw(im, 'RGBA')
    f = ImageFont.truetype(FONT, size)
    hs = [para if l == '' else size for l in lines]
    total = sum(hs) + gap * (len(lines) - 1)
    bw = max(d.textlength(l, font=f) for l in lines if l) + 80
    y = cy - total / 2
    d.rounded_rectangle([(W - bw) / 2, y - 50, (W + bw) / 2, y + total + 50],
                        radius=28, fill=PINK + (235,))
    for l, h in zip(lines, hs):
        if l:
            w = d.textlength(l, font=f)
            d.text(((W - w) / 2, y), l, font=f, fill='white', stroke_width=4, stroke_fill=(0, 0, 0))
        y += h + gap
    return im


# 文字は上下240pxの外に出さない（画面の真ん中に置く）
PAGES = [
    ['セロトニンって', '聞いたことありますか？', '',
     '脳の中で', '気持ちを安定させる働きが', 'あるといわれている物質です'],
    ['セロトニンの材料は', '「トリプトファン」', '食べものからとる栄養です', '',
     '夜になると', 'セロトニンをもとに', '眠りにかかわる「メラトニン」が', '作られるといわれています'],
    ['眠りのリズムを整えるために', '毎日の中でできること', '',
     '①朝起きたらカーテンを開けて', '光を浴びる', '',
     '②朝ごはんを食べる', '（乳製品や大豆製品など）', '',
     '③日中に少し体を動かす', '',
     '④寝る前はスマホの光を', 'ひかえめに'],
    ['全部じゃなくて大丈夫', 'できそうなことを', '1つだけ試してみてね', '',
     '気分の落ちこみが続くときは', '一人で抱えこまず', '医師や専門の相談窓口に', '相談してくださいね'],
]
for i, lines in enumerate(PAGES, 1):
    im = block(plain(), lines, H / 2, size=58)
    im.save(f'{OUT}/{i}枚目.jpg', quality=92)
