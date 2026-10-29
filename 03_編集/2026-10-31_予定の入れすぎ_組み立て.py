import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 43
DARK_START, DARK_LEN = 42, 1.0  # 最後は映像だけゆっくり暗く
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# 10/31「予定の入れすぎ」（予告型）。写真4枚はアカウント主が 10/29 に添付
# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了[, 切り抜きの上端[0-1]])
CUTS = [
    ('カット1.jpg', 0, 3, (0.2, 0.2), (1.0, 1.0)),          # 卓上カレンダー。画面1は動かさない
    ('カット1.jpg', 3, 9, (0.2, 0.2), (1.0, 1.05)),         # 同じ写真のまま、ゆっくり寄る
    ('カット2.jpg', 9, 14.5, (0.36, 0.36), (1.0, 1.05)),    # 夕方の足元
    ('カット3.jpg', 14.5, 19.5, (0.5, 0.5), (1.0, 1.05)),   # ソファとクッション
    ('カット1.jpg', 19.5, 24, (0.0, 0.0), (1.1, 1.15)),     # カレンダーの左側（リング）
    ('カット1.jpg', 24, 28, (0.75, 0.75), (1.3, 1.35), 1.0),  # カレンダーの丸のついた日（文字の上に見えるよう下寄り）
    ('カット1.jpg', 28, 32.5, (1.0, 1.0), (1.0, 1.05)),     # カレンダーの右側
    ('カット4.jpg', 32.5, 43, (0.5, 0.5), (1.0, 1.08)),     # 緑の葉（画面8・9）
]

# 先に切り抜く範囲：ファイル → (左, 上, 右, 下)（顔が入らないように）
CROP = {}

# ぼかす場所：ファイル → [(左, 上, 右, 下), ...]（もとの写真の座標）
# カット1：カレンダーの数字と文字（形はわかるように弱めにぼかす）
# カット2：くつのロゴ
BLUR = {'カット1.jpg': [(90, 0, 692, 632)],
        'カット2.jpg': [(70, 340, 165, 410), (360, 335, 450, 405)]}
BLUR_R = {'カット1.jpg': 3, 'カット2.jpg': 12}  # ぼかしの強さ

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
# 句読点なし（読点は改行か詰める）・行の途中に空白を入れない
SCREENS = [
    (0, 3, ['休日の予定は', '1日1つでいい'], 0, 0, 'hook'),
    (3, 9, ['楽しかったのにへとへと', '予定の組み方のコツを3つ'], 0, 0.3, 'normal'),
    (9, 14.5, ['楽しいことも繊細さんには', 'エネルギーを使う時間かもしれません'], 0.3, 0.3, 'normal'),
    (14.5, 19.5, ['楽しめたのも疲れたのも', 'どちらも本当です'], 0.3, 0.3, 'normal'),
    (19.5, 24, ['①予定のあいだに', '「何もしない時間」を入れる'], 0.3, 0.3, 'normal'),
    (24, 28, ['②休日の予定は', '1日1つを目安に'], 0.3, 0.3, 'normal'),
    (28, 32.5, ['③大きな予定の次の日は', '先に空けておく'], 0.3, 0.3, 'normal'),
    (32.5, 37.5, ['何もしない休日も', 'ちゃんと意味のある1日です'], 0.4, 0.4, 'emph'),
    (37.5, 43, ['週末の予定を立てる前に', '見返せるよう保存してくださいね'], 0.4, 0, 'small'),
]


def prep(name):
    im = Image.open(f'{SRC}/{name}').convert('RGB')
    if name in BLUR:
        mask = Image.new('L', im.size, 0)
        for box in BLUR[name]:
            ImageDraw.Draw(mask).rectangle(box, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(25))  # 境目をなじませる
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(BLUR_R.get(name, 12))), im, mask)
    if name in CROP:
        im = im.crop(CROP[name])
    im = ImageEnhance.Color(im).enhance(0.88)  # 色を少し落ち着かせる
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
