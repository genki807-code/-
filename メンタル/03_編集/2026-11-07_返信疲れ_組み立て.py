import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 46.5
DARK_START, DARK_LEN = 45.5, 1.0  # 最後は映像だけゆっくり暗く（CTA が読めるうちは明るいまま）
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# 11/7「返信疲れ」（共感型・画面1は大きい文字・最後に CTA）。写真3枚はアカウント主が 11/4 に添付
# カット1＝ニットの人がスマホ（裏側）とバッテリーを持つ手元・カット2＝木の机に伏せたスマホ2台・ヘッドホン・ペン
# カット3＝花びんのピンクの花とプレゼントの箱
# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了[, 切り抜きの上端[0-1]])
CUTS = [
    ('カット1.jpg', 0, 3, (0.79, 0.79), (1.0, 1.0)),            # スマホを持つ右手。画面1は動かさない
    ('カット1.jpg', 3, 8.5, (0.79, 0.77), (1.0, 1.05)),         # 同じ写真のまま、ゆっくり寄る
    ('カット2.jpg', 8.5, 14, (0.64, 0.64), (1.0, 1.05)),        # 黒いスマホ
    ('カット2.jpg', 14, 18.5, (0.99, 0.99), (1.0, 1.05)),       # 白いスマホとペンケース
    ('カット2.jpg', 18.5, 23.5, (0.0, 0.0), (1.0, 1.05)),       # ヘッドホンと手帳
    ('カット1.jpg', 23.5, 28, (0.45, 0.5), (1.15, 1.2), 0.6),   # 両手の手元に寄る
    ('カット2.jpg', 28, 33, (0.3, 0.34), (1.0, 1.05)),          # ヘッドホンと黒いスマホのあいだ
    ('カット3.jpg', 33, 46.5, (0.6, 0.66), (1.0, 1.06)),        # 花びんの花（画面8〜10）
]

CROP = {}

FIT = {}  # アカウント主が選んだ写真は画面いっぱいに使う

# ぼかす場所：ファイル → [(左, 上, 右, 下), ...]（もとの写真の座標）
BLUR = {'カット2.jpg': [(400, 318, 455, 372), (385, 462, 440, 498),   # 黒いスマホのロゴと文字
                        (540, 228, 595, 278), (570, 365, 640, 415),   # 白いスマホのロゴと文字
                        (10, 325, 120, 400),                           # 手帳の文字
                        (700, 420, 778, 559)]}                         # カメラ（文字が入るおそれ）
BLUR_R = {'カット2.jpg': 20}
FEATHER = {'カット2.jpg': 8}

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
# 句読点なし・行の途中に空白を入れない
SCREENS = [
    (0, 3, ['その返信', '何回直した？'], 0, 0, 'hook'),
    (3, 8.5, ['「冷たく見えないかな」と', '送信ボタンが押せない'], 0, 0.3, 'normal'),
    (8.5, 14, ['相手を思って迷えるのは', 'あなたのいいところです'], 0.3, 0.3, 'emph'),
    (14, 18.5, ['相手はそこまで細かく', '読んでいないかも'], 0.3, 0.3, 'normal'),
    (18.5, 23.5, ['①冷たく見えるか迷ったら', '「ありがとうございます」を足す'], 0.3, 0.3, 'normal'),
    (23.5, 28, ['②書き直しは', '「2回まで」と決める'], 0.3, 0.3, 'normal'),
    (28, 33, ['③通知を見ない時間を', '1日の中に少し作る'], 0.3, 0.3, 'normal'),
    (33, 37.5, ['返信に疲れたら', 'スマホから少しはなれていい'], 0.4, 0.4, 'emph'),
    (37.5, 42.5, ['返信に迷う日に見返せるよう', '保存してくださいね'], 0.4, 0.3, 'small'),
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
    if name in CROP:
        im = im.crop(CROP[name])
    im = ImageEnhance.Color(im).enhance(0.88)  # 色を少し落ち着かせる
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
