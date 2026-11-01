import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = sys.argv[1]   # 素材フォルダ
OUT = sys.argv[2]   # 出力 mp4
SHOT = sys.argv[3]  # 確認用画像の出力先フォルダ
W, H, FPS, DUR = 1080, 1920, 30, 47.5
DARK_START, DARK_LEN = 46.5, 1.0  # 最後は映像だけゆっくり暗く（CTA が読めるうちは明るいまま）
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# 11/3「季節の変わり目」（共感型・画面1は大きい文字・最後に CTA）。写真4枚はアカウント主が 11/1 に添付
# カット1＝落ち葉・カット2＝青空と太陽・カット3＝ニットの人（顔が大きいので首から下だけ切り抜く）・カット4＝夕焼け（右の人と鉄塔は入れない）
# カット：(ファイル, 開始, 終了, 切り抜きの左端[0-1] 開始→終了, ズーム 開始→終了[, 切り抜きの上端[0-1]])
CUTS = [
    ('カット1.jpg', 0, 3, (0.35, 0.35), (1.0, 1.0)),         # 落ち葉。画面1は動かさない
    ('カット1.jpg', 3, 8.5, (0.35, 0.35), (1.0, 1.05)),      # 同じ写真のまま、ゆっくり寄る
    ('カット1.jpg', 8.5, 14.5, (0.9, 0.9), (1.3, 1.35)),     # 同じ写真の別の場所
    ('カット2.jpg', 14.5, 18.5, (0.05, 0.05), (1.0, 1.05)),  # 太陽のほう
    ('カット2.jpg', 18.5, 23.5, (0.7, 0.7), (1.0, 1.05)),    # 雲のほう
    ('カット3.jpg', 23.5, 27.5, (0.25, 0.25), (1.0, 1.05)),  # ニット（首から下）
    ('カット3.jpg', 27.5, 32, (0.55, 0.55), (1.0, 1.05)),    # 同じ写真の袖のほう
    ('カット4.jpg', 32, 47.5, (0.0, 0.05), (1.0, 1.06)),     # 夕焼けの空（画面8〜10）
]

# 先に切り抜く範囲：ファイル → (左, 上, 右, 下)
CROP = {'カット3.jpg': (0, 440, 731, 1023)}  # 顔が入らないよう首から下だけ

# ぼかす場所：ファイル → [(左, 上, 右, 下), ...]（もとの写真の座標）
BLUR = {}
BLUR_R = {}  # ぼかしの強さ
FEATHER = {}  # 境目のなじませ（小さい範囲は弱めに）

# 画面：(開始, 終了, 行, フェードイン, フェードアウト, 種類)
# 句読点なし（読点は改行か詰める）・行の途中に空白を入れない
SCREENS = [
    (0, 3, ['最近理由なく', 'しんどい？'], 0, 0, 'hook'),
    (3, 8.5, ['何かあったわけじゃないのに', 'なんだか元気が出ない'], 0, 0.3, 'normal'),
    (8.5, 14.5, ['季節の変わり目は心も体も', '慣れるまで時間がかかることも'], 0.3, 0.3, 'normal'),
    (14.5, 18.5, ['なまけているわけじゃ', 'ないんです'], 0.3, 0.3, 'emph'),
    (18.5, 23.5, ['①朝カーテンを開けて', '外の明るさを感じてみる'], 0.3, 0.3, 'normal'),
    (23.5, 27.5, ['②首・手首・足首を', 'あたためてみる'], 0.3, 0.3, 'normal'),
    (27.5, 32, ['③今月は「季節に慣れる月」', 'ゆっくりめでいい'], 0.3, 0.3, 'normal'),
    (32, 38.5, ['つらさが続くときは医師や', '専門の相談窓口に相談してください'], 0.4, 0.4, 'normal'),
    (38.5, 43.5, ['ひとりで抱えこまないでね', '見返せるよう保存してくださいね'], 0.4, 0.3, 'small'),
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
