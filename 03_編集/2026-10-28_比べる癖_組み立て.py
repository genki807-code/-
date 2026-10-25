import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 42.5
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了)
CUTS = [
    ('カット1.jpg', 0, 3, (0.5, 0.5), (1.0, 1.0)),       # 画面1は動かさない
    ('カット1.jpg', 3, 9, (0.5, 0.5), (1.0, 1.05)),      # 同じ写真のまま、ゆっくり寄る
    ('カット2.jpg', 9, 14, (0.6, 0.6), (1.0, 1.05)),
    ('カット3.jpg', 14, 19.5, (0.85, 0.85), (1.0, 1.04)), # マグカップ（袋の文字はぼかす）
    ('カット4.jpg', 19.5, 24, (0.75, 0.75), (1.0, 1.05)),
    ('カット5.jpg', 24, 28.5, (0.0, 0.0), (1.0, 1.05)),   # マグの写真の左側（暗いスマホ）
    ('カット4.jpg', 28.5, 33, (0.8, 0.8), (1.1, 1.15)),   # ノートをもう一度、少し寄りで
    ('カット6.jpg', 33, 42.5, (0.5, 0.5), (1.0, 1.05)),
]

# 読める文字をぼかす場所：ファイル → (左, 上, 右, 下)（もとの写真の座標）
BLUR = {'カット3.jpg': (495, 65, 787, 240)}

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
SCREENS = [
    (0, 3, ['同期と比べて', '落ちこむ'], 0, 0, 'hook'),
    (3, 9, ['周りがまぶしく見える日', '小さなコツを3つ置きますね'], 0, 0.3, 'normal'),
    (9, 14, ['見えているのは　たぶん', '相手のいちばんいいところ'], 0.3, 0.3, 'normal'),
    (14, 19.5, ['比べてしまうのは', 'ちゃんとしたい心があるから'], 0.5, 0.3, 'emph'),
    (19.5, 24, ['①比べる相手は', '「昨日の自分」にしてみる'], 0.3, 0.3, 'normal'),
    (24, 28.5, ['②疲れた日は　SNSを', '開く前にひと呼吸'], 0.3, 0.3, 'normal'),
    (28.5, 33, ['③寝る前に', '「今日できたこと」を1つ書く'], 0.3, 0.3, 'soft'),
    (33, 37.5, ['あなたのペースで', '進んでいって大丈夫です'], 0.3, 0.3, 'normal'),
    (37.5, 42.5, ['比べて落ちこんだ夜に', '見返せるよう　保存してね'], 0.5, 0, 'small'),
]


def prep(name):
    im = Image.open(f'{SRC}/{name}').convert('RGB')
    if name in BLUR:
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).rectangle(BLUR[name], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(25))  # 境目をなじませる
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(12)), im, mask)
    im = ImageEnhance.Color(im).enhance(0.88)  # 色を少し落ち着かせる
    s = H / im.height
    return im.resize((round(im.width * s), H), Image.LANCZOS)


def bg_frame(big, t, cut):
    _, a, b, (x0, x1), (z0, z1) = cut
    p = (t - a) / (b - a)
    z = z0 + (z1 - z0) * p
    cw, ch = W / z, H / z
    xr = x0 + (x1 - x0) * p
    left = (big.width - cw) * xr
    top = (H - ch) / 2
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
    if t >= 41:  # 最後は映像だけゆっくり暗く
        frame = ImageEnhance.Brightness(frame).enhance(1 - 0.8 * min((t - 41) / 1.5, 1))
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
