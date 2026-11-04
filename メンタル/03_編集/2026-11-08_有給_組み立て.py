import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 46.5
DARK_START, DARK_LEN = 45.5, 1.0  # 最後は映像だけゆっくり暗く（CTA が読めるうちは明るいまま）
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# 11/8「有給」（共感型・画面1は大きい文字・最後に CTA）。写真3枚はアカウント主が 11/5 に添付
# カット1＝白いシャツの人がノートにペンで書く手元と観葉植物（上に黒い帯があるので切る）
# カット2＝木の机の書類・ペン・めがね・コーヒー・スマホ（書類の文字はぼかす）
# カット3＝公園の木のベンチ（人なし）
# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了[, 切り抜きの上端[0-1]])
CUTS = [
    ('カット1.jpg', 0, 3, (0.42, 0.42), (1.0, 1.0)),            # ペンを持つ手。画面1は動かさない
    ('カット1.jpg', 3, 8.5, (0.42, 0.44), (1.0, 1.05)),         # 同じ写真のまま、ゆっくり寄る
    ('カット2.jpg', 8.5, 14, (0.59, 0.59), (1.0, 1.05)),        # 付せん・書類と万年筆
    ('カット2.jpg', 14, 18.5, (0.99, 0.99), (1.0, 1.05)),       # コーヒーとめがね
    ('カット2.jpg', 18.5, 23.5, (0.0, 0.0), (1.0, 1.05)),       # 重ねた書類とスマホ
    ('カット1.jpg', 23.5, 28, (0.62, 0.66), (1.35, 1.4), 0.35),  # ペン先とノートに寄る（引き継ぎメモ）
    ('カット3.jpg', 28, 46.5, (0.6, 0.66), (1.0, 1.06)),        # 公園のベンチ（画面7〜10）
]

CROP = {'カット1.jpg': (0, 14, 812, 545)}  # 上の黒い帯を切る

FIT = {}

BRIGHT = {'カット3.jpg': 1.15}  # ベンチの写真は少し暗いので明るく

# ぼかす場所：ファイル → [(左, 上, 右, 下), ...]（もとの写真の座標）
BLUR = {'カット2.jpg': [(0, 0, 300, 230),        # 封筒の赤い文字
                        (300, 290, 880, 692),    # 書類の文字（全部）
                        (0, 230, 300, 692)]}     # 左の書類の文字
BLUR_R = {'カット2.jpg': 6}
FEATHER = {'カット2.jpg': 6}
BLUR_STRONG = {'カット2.jpg': [(20, 100, 130, 200),   # 封筒の赤い文字
                               (430, 310, 520, 360)]}  # 書類のいちばん上の大きい文字

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
# 句読点なし・行の途中に空白を入れない
SCREENS = [
    (0, 3, ['有給なのに', '謝ってる'], 0, 0, 'hook'),
    (3, 8.5, ['「忙しいのにすみません」と', '何度も頭を下げていませんか？'], 0, 0.3, 'normal'),
    (8.5, 14, ['申し訳なく思うのは', '周りを大切にしているから'], 0.3, 0.3, 'emph'),
    (14, 18.5, ['有給を使うのは', 'わがままではありません'], 0.3, 0.3, 'normal'),
    (18.5, 23.5, ['①「すみません」を', '「お願いします」に変えてみる'], 0.3, 0.3, 'normal'),
    (23.5, 28, ['②引き継ぎメモを先に作って', 'お互いの安心に'], 0.3, 0.3, 'normal'),
    (28, 33, ['③有給の日の楽しみを', '1つ思いうかべておく'], 0.3, 0.3, 'normal'),
    (33, 37.5, ['お休みの日は', '心ごと休めますように'], 0.4, 0.4, 'emph'),
    (37.5, 42.5, ['有給を出す前に見返せるよう', '保存してくださいね'], 0.4, 0.3, 'small'),
    (42.5, 46.5, ['毎日20時に更新しています', 'フォローしてまた会いに来てね'], 0.3, 0, 'small'),
]


def prep(name):
    im = Image.open(f'{SRC}/{name}').convert('RGB')
    if name in BLUR:
        mask = Image.new('L', im.size, 0)
        for box in BLUR[name]:
            ImageDraw.Draw(mask).rectangle(box, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(FEATHER.get(name, 25)))  # 境目をなじませる
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(BLUR_R.get(name, 12))), im, mask)
    if name in BLUR_STRONG:
        mask = Image.new('L', im.size, 0)
        for box in BLUR_STRONG[name]:
            ImageDraw.Draw(mask).rectangle(box, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(8))
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(20)), im, mask)
    if name in CROP:
        im = im.crop(CROP[name])
    im = ImageEnhance.Color(im).enhance(0.88)  # 色を少し落ち着かせる
    if name in BRIGHT:
        im = ImageEnhance.Brightness(im).enhance(BRIGHT[name])
    if name in FIT:
        s = max(W / im.width, H / im.height)
        back = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        l, t = (back.width - W) // 2, (back.height - H) // 2
        back = back.crop((l, t, l + W, t + H))
        back = ImageEnhance.Brightness(back.filter(ImageFilter.GaussianBlur(30))).enhance(0.85)
        front = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        back.paste(front, (0, round(H * FIT[name] - front.height / 2)))
        return back
    s = H / im.height
    return im.resize((round(im.width * s), H), Image.LANCZOS)


def bg_frame(big, t, cut):
    _, a, b, (x0, x1), (z0, z1) = cut[:5]
    yr = cut[5] if len(cut) > 5 else 0.5
    p = (t - a) / (b - a)
    z = z0 + (z1 - z0) * p
    cw, ch = W / z, H / z
    xr = x0 + (x1 - x0) * p
    left = (big.width - cw) * xr
    top = (H - ch) * yr
    return big.resize((W, H), Image.BICUBIC, box=(left, top, left + cw, top + ch))


def text_layer(lines, kind):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == 'hook':
        sizes, gap, band, stroke = [100, 108], 34, 235, 6
    elif kind == 'small':
        sizes, gap, band, stroke = [50, 50], 28, 225, 4
    else:
        sizes, gap, band, stroke = [52, 52], 30, 225, 4
    if kind == 'emph':
        sizes = [52, 58]
    if kind == 'hook':  # 画面1は大きく（10/30 アカウント主OK）。横はみ出さない大きさまで
        sizes, gap, stroke = [140, 140], 40, 8
        for i, l in enumerate(lines):
            while d.textlength(l, font=ImageFont.truetype(FONT, sizes[i])) > W - 160:
                sizes[i] -= 2
        sizes = [min(sizes)] * 2
    fonts = [ImageFont.truetype(FONT, s) for s in sizes]
    widths = [d.textlength(l, font=f) for l, f in zip(lines, fonts)]
    total_h = sum(sizes) + gap
    cy = 860 if kind == 'hook' else 880
    y = cy - total_h / 2
    pad_x, pad_y = 30, 45
    bw = max(widths) + pad_x * 2
    d.rounded_rectangle([(W - bw) / 2, y - pad_y, (W + bw) / 2, y + total_h + pad_y],
                        radius=24, fill=(236, 122, 152, band))  # ブランドのピンク
    colors = ['white', 'white']
    if kind == 'emph':
        colors[1] = (255, 240, 170)
    if kind == 'soft':
        colors[1] = (255, 228, 196)
    for i, (l, f, w) in enumerate(zip(lines, fonts, widths)):
        d.text(((W - w) / 2, y), l, font=f, fill=colors[i],
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += sizes[i] + gap
    return im


bigs = [prep(c[0]) for c in CUTS]
layers = [text_layer(s[2], s[5]) for s in SCREENS]

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                       '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
n = int(DUR * FPS)
shots = {0: '00_最初のコマ'}
for i, s in enumerate(SCREENS):
    shots[int(((s[0] + s[1]) / 2) * FPS)] = f'画面{i + 1}'
for f in range(n):
    t = f / FPS
    ci = max(i for i, c in enumerate(CUTS) if c[1] <= t)
    frame = bg_frame(bigs[ci], t, CUTS[ci])
    if t >= DARK_START:  # 最後は映像だけゆっくり暗く
        frame = ImageEnhance.Brightness(frame).enhance(1 - 0.8 * min((t - DARK_START) / DARK_LEN, 1))
    frame = frame.convert('RGBA')
    for (a, b, _, fi, fo, _), lay in zip(SCREENS, layers):
        if a <= t < b:
            al = 1.0
            if fi and t < a + fi:
                al = (t - a) / fi
            if fo and t > b - fo:
                al = min(al, (b - t) / fo)
            if al >= 1:
                frame.alpha_composite(lay)
            else:
                l2 = lay.copy()
                l2.putalpha(l2.getchannel('A').point(lambda v: int(v * al)))
                frame.alpha_composite(l2)
    frame = frame.convert('RGB')
    if f in shots:
        frame.save(f'{SHOT}/{shots[f]}.jpg', quality=90)
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print('done', ff.returncode)
