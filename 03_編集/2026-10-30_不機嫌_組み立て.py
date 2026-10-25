import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 41.0
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了)
CUTS = [
    ('カット1.jpg', 0, 3, (0.5, 0.5), (1.0, 1.0)),     # 画面1は動かさない
    ('カット2.jpg', 3, 9, (0.62, 0.62), (1.0, 1.05)),  # 電卓のロゴを外す
    ('カット3.jpg', 9, 19, (0.5, 1.0), (1.0, 1.04)),   # 夕焼けのほうへゆっくり
    ('カット4.jpg', 19, 23, (0.5, 0.5), (1.0, 1.05)),
    ('カット5.jpg', 23, 27.5, (0.45, 0.45), (1.0, 1.05)),
    ('カット6.jpg', 27.5, 31.5, (0.5, 0.5), (1.0, 1.05)),
    ('カット7.jpg', 31.5, 41, (0.5, 0.5), (1.0, 1.05)),
]

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
SCREENS = [
    (0, 3, ['そのため息、', '私のせい？'], 0, 0, 'hook'),
    (3, 9, ['隣の不機嫌に、つい顔色を', 'うかがって疲れていませんか？'], 0, 0.3, 'normal'),
    (9, 13.5, ['でも、その不機嫌を', 'あなたが直さなくていい。'], 0.5, 0.5, 'emph'),
    (13.5, 19, ['仕事のやりとりはふだん通り、', '気分までは背負わない。'], 0.5, 0.3, 'normal'),
    (19, 23, ['①ひと息つきに、', '少しだけ席を離れる'], 0.3, 0.3, 'normal'),
    (23, 27.5, ['②温かい飲み物で、', '自分の機嫌を先にとる'], 0.3, 0.3, 'normal'),
    (27.5, 31.5, ['③心の中で', '「これは私の係じゃない」'], 0.3, 0.3, 'soft'),
    (31.5, 35.5, ['その優しさ、', 'まず自分に使ってね。'], 0.3, 0.5, 'normal'),
    (35.5, 41, ['空気が重い日に見返せるよう、', '保存してくださいね。'], 0.5, 0, 'small'),
]


def prep(name):
    im = Image.open(f'{SRC}/{name}').convert('RGB')
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
        sizes, gap, band, stroke = [130, 142], 40, 150, 6
    elif kind == 'small':
        sizes, gap, band, stroke = [60, 60], 34, 140, 4
    else:
        sizes, gap, band, stroke = [64, 64], 36, 140, 4
    if kind == 'emph':
        sizes = [64, 72]
    fonts = [ImageFont.truetype(FONT, s) for s in sizes]
    widths = [d.textlength(l, font=f) for l, f in zip(lines, fonts)]
    total_h = sum(sizes) + gap
    cy = 860 if kind == 'hook' else 880
    y = cy - total_h / 2
    pad_x, pad_y = 50, 45
    bw = max(widths) + pad_x * 2
    d.rounded_rectangle([(W - bw) / 2, y - pad_y, (W + bw) / 2, y + total_h + pad_y],
                        radius=24, fill=(15, 15, 15, band))
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
    if ci == 2:  # 曇り→晴れ：画面4でだんだん明るく
        k = min(max((t - 13.5) / 5.5, 0), 1)
        frame = ImageEnhance.Brightness(frame).enhance(1 + 0.6 * k)
    if t >= 39.5:  # 最後は映像だけゆっくり暗く
        frame = ImageEnhance.Brightness(frame).enhance(1 - 0.8 * min((t - 39.5) / 1.5, 1))
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
