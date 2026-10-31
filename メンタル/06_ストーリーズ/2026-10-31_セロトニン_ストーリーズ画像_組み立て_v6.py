import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]  # 素材フォルダ（アカウント主の写真）
OUT = sys.argv[2]  # 出力フォルダ
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
PINK = (236, 122, 152)


def photo(name, blur=None):
    """写真を縦長いっぱいに広げて真ん中を切り抜く。blur は読める文字をぼかす範囲（もとの写真の座標）"""
    im = Image.open(f'{SRC}/{name}').convert('RGB')
    if blur:
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).rectangle(blur, fill=255)
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(14)), im, mask.filter(ImageFilter.GaussianBlur(10)))
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))


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


# アカウント主の写真3枚（10/31）。顔にかからないよう、文字は下のほうに置く（上下240pxの外には出さない）
# 写真3のパーカーの文字はぼかす
BG = [('写真1.png', None), ('写真1.png', None), ('写真2.png', None),
      ('写真3.png', (0, 1020, 1024, 1536)), ('写真3.png', (0, 1020, 1024, 1536))]
PAGES = [
    ['セロトニンってなに？？', '',
     '脳の中で', '気持ちを安定させる働きが', 'あるって言われてる物質だよ'],
    ['材料は「トリプトファン」', '食べものからとる栄養なんだ', '',
     '夜になると', 'セロトニンをもとに', '眠りにかかわる「メラトニン」が', '作られるって言われてるよ'],
    ['私も適応障害が', 'ひどかったときは', 'セロトニンが', '足りてなかったのかも…', '', 'これは私の場合の感じ方で', '原因は人それぞれだよ'],
    ['眠りのリズムを整えるために', '毎日の中でできること', '',
     '①朝起きたらカーテンを開けて', '光を浴びる', '',
     '②朝ごはんを食べる', '（乳製品や大豆製品とか）', '',
     '③昼間にちょっと体を動かす', '',
     '④寝る前はスマホの光を', 'ひかえめに'],
    ['全部やらなくて大丈夫', 'できそうなことを', '1つだけ試してみてね'],
]
for i, lines in enumerate(PAGES, 1):
    total = sum(36 if l == '' else 58 for l in lines) + 24 * (len(lines) - 1)
    cy = min(1640 - 50 - total / 2, 1350)  # 帯の下が 1640px より上になるように
    im = block(photo(*BG[i - 1]), lines, cy, size=58)
    im.save(f'{OUT}/{i}枚目.jpg', quality=92)
