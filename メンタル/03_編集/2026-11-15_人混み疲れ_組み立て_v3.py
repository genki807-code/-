import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 47.5
DARK_START, DARK_LEN = 46.5, 1.0  # 最後は映像だけゆっくり暗く（CTA が読めるうちは明るいまま）
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# v3：ぼかしを全部外した（アカウント主「モザイクいらない」）・画面7〜10をアカウント主が 11/14 に送り直したお茶のカップ（人なし）に差しかえ（カット4_v3.jpg）
# v2：checker の直し（ポスターの顔・TOHO の右はし・袋の下のロゴのぼかし位置）
# 11/15「人混み疲れ」（11/14 からの型：画面1は心の声＋問いかけの3行・マイナスから入る・最後に CTA）
# 写真4枚はアカウント主が 11/14 に添付（写真リスト v2 とちがうところは、届いた写真に合わせた）
# カット1＝交差点を歩く人たちの足元（画面1・3）。画面1の言葉「人が多いだけで」がすぐ伝わるので画面1に使う
#          （静かな写真は届かなかった）。看板・ポスター（顔）はぼかす
# カット2＝買いもの袋を持つ人（画面2・4）。顔なし。袋の大きな文字とロゴはぼかす
# カット3＝人の少ない交差点（画面5・6＝すいている時間）。看板の文字はぼかす
# カット4_v3＝お茶のカップとソーサー（画面7〜10・人なし）
# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了[, 切り抜きの上端[0-1]])
CUTS = [
    ('カット1.jpg', 0, 4, (0.5, 0.5), (1.0, 1.0)),            # 人混みの足元。画面1は動かさない
    ('カット2.jpg', 4, 9.5, (0.5, 0.5), (1.0, 1.04)),         # 買いもの袋（画面1と絵を変える）
    ('カット1.jpg', 9.5, 15, (0.3, 0.38), (1.08, 1.14), 0.9), # 足元に寄る
    ('カット2.jpg', 15, 19.5, (0.6, 0.66), (1.04, 1.08), 0.8),# 袋とねぎに寄る
    ('カット3.jpg', 19.5, 29, (0.62, 0.7), (1.0, 1.06), 0.7), # すいた交差点（画面5・6）
    ('カット4_v3.jpg', 29, 47.5, (0.16, 0.3), (1.0, 1.05)),    # お茶のカップ（画面7〜10）
]

CROP = {'カット3.jpg': (0, 0, 880, 698),        # 下のはしの黒い線を切る
        'カット4.jpg': (130, 118, 420, 391)}    # 口・あご（y115 より上）と髪の多いところを切る

FIT = {}

BRIGHT = {}

BLUR = {}
BLUR_R = {}
FEATHER = {}
BLUR_STRONG = {}  # v3：アカウント主「モザイクいらない」（11/14）→ ぼかしは全部外した

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
# 句読点なし・行の途中に空白を入れない
SCREENS = [
    (0, 4, ['「人が多いだけで', 'もう帰りたい…」', 'この気もちわかる？'], 0, 0, 'hook3'),
    (4, 9.5, ['人の多い場所では', '知らないうちに気を張っている'], 0, 0.3, 'normal'),
    (9.5, 15, ['人の動きや声に', 'ずっとアンテナを立てているのかも'], 0.3, 0.3, 'emph'),
    (15, 19.5, ['ぐったりするのは', 'あなたが弱いからじゃないんです'], 0.3, 0.3, 'normal'),
    (19.5, 24.5, ['①出かけるなら', 'すいている時間を選ぶ'], 0.3, 0.3, 'normal'),
    (24.5, 29, ['②行く前に', '帰る時間を決めておく'], 0.3, 0.3, 'normal'),
    (29, 34, ['③帰ったらまず', '好きな飲みものを1杯'], 0.3, 0.3, 'normal'),
    (34, 38.5, ['人混みのあとは', 'ゆっくり休んで大丈夫です'], 0.4, 0.4, 'emph'),
    (38.5, 43.5, ['出かける前に見返せるよう', '保存してくださいね'], 0.4, 0.3, 'small'),
    (43.5, 47.5, ['毎日20時に更新しています', 'フォローしてまた会いに来てね'], 0.3, 0, 'small'),
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
    if kind == 'hook3':  # 11/14 からの型：心の声2行＋問いかけ1行。帯から出ない大きさ
        sizes, gap, band, stroke = [80, 80, 80], 30, 235, 6
        for i, l in enumerate(lines):
            while d.textlength(l, font=ImageFont.truetype(FONT, sizes[i])) > W - 120:
                sizes[i] -= 2
        sizes = [min(sizes)] * 3
    if kind == 'hook':  # 画面1は大きく（10/30 アカウント主OK）。横はみ出さない大きさまで
        sizes, gap, stroke = [140, 140], 40, 8
        for i, l in enumerate(lines):
            while d.textlength(l, font=ImageFont.truetype(FONT, sizes[i])) > W - 160:
                sizes[i] -= 2
        sizes = [min(sizes)] * 2
    fonts = [ImageFont.truetype(FONT, s) for s in sizes]
    widths = [d.textlength(l, font=f) for l, f in zip(lines, fonts)]
    total_h = sum(sizes) + gap * (len(lines) - 1)
    cy = 860 if kind in ('hook', 'hook3') else 880
    y = cy - total_h / 2
    pad_x, pad_y = 30, 45
    bw = max(widths) + pad_x * 2
    d.rounded_rectangle([(W - bw) / 2, y - pad_y, (W + bw) / 2, y + total_h + pad_y],
                        radius=24, fill=(236, 122, 152, band))  # ブランドのピンク
    colors = ['white'] * len(lines)
    if kind == 'emph':
        colors[1] = (255, 240, 170)
    if kind == 'soft':
        colors[1] = (255, 228, 196)
    if kind == 'hook3':
        colors[2] = (255, 240, 170)  # 問いかけの行
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
