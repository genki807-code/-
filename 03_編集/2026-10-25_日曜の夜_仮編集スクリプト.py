"""10/25 日曜の夜 リールの仮編集（台本 v2・編集設計図 v2 の文言と秒数どおり）

動画素材がないため、背景は色のグラデーションと光の玉を描いて作る（素材の出どころ・クレジット表記の心配がない）。
テロップは 10/24 と同じ見た目：白い文字・黒いふち・ピンクの帯・画面中央・「、」「。」なし。
"""
import os, subprocess, sys, tempfile, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = "/home/user/-"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/03_編集/2026-10-25_日曜の夜_仮編集_v3.mp4"
WORK = tempfile.mkdtemp(prefix="build_1025_")
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H = 1080, 1920
TOTAL = 41.5

WHITE = (255, 255, 255)
ACCENT = (255, 226, 140)     # 「感じていい」だけ淡い黄色（サムネAと同じ強調）
PINK = (244, 167, 196, 225)  # 文字のうしろの帯

# (開始, 終了, 行のリスト[[(文字, 色)...]...], 文字サイズ)
TEXTS = [
    (0.0, 4.0, [[("日曜の夜、", WHITE)], [("なんだか心が重くない？", WHITE)]], 70),
    (4.0, 10.0, [[("「明日、行きたくないな」", WHITE)], [("「なんでこうなるんだろう」", WHITE)]], 64),
    (10.0, 14.5, [[("理由を探して、", WHITE)], [("そんな自分にがっかりする。", WHITE)]], 66),
    (14.5, 19.0, [[("理由がなくても、", WHITE)], [("重く", WHITE), ("感じていい", ACCENT), ("んです。", WHITE)]], 72),
    (19.0, 23.0, [[("①朝やることを", WHITE)], [("1つにしぼっておく", WHITE)]], 70),
    (23.0, 28.0, [[("②明日着る服と持ち物を、", WHITE)], [("今のうちにそろえる", WHITE)]], 66),
    (28.0, 32.5, [[("③明日の夜の楽しみを、", WHITE)], [("1つ用意しておく", WHITE)]], 68),
    (32.5, 36.5, [[("月曜は、", WHITE)], [("ゆっくり始めればいいからね。", WHITE)]], 64),
    (36.5, 41.5, [[("来週の日曜の夜のために、", WHITE)], [("保存してくださいね。", WHITE)]], 64),
]

# 背景：(開始, 終了, 上の色, 下の色, 光の玉の色, 玉の数, 玉の大きさ, 玉の上がる速さpx/秒, 特別な飾り)
SCENES = [
    (0.0, 4.0, (22, 32, 70), (118, 122, 168), (255, 255, 255), 40, (2, 5), 6, "dusk"),       # 日が沈んだあとの青〜紺の空
    (4.0, 10.0, (52, 58, 86), (98, 100, 122), (200, 205, 230), 14, (30, 70), 12, None),      # 少し沈んだ部屋の色
    (10.0, 14.5, (20, 26, 50), (44, 48, 78), (245, 190, 120), 18, (40, 110), 14, None),      # 夜の窓に映る部屋の明かり
    (14.5, 19.0, (12, 20, 45), (40, 70, 110), (230, 236, 255), 10, (3, 7), 4, "moon"),       # 夜の静かな湖と月
    (19.0, 23.0, (240, 226, 206), (214, 188, 158), (255, 255, 255), 16, (40, 100), 12, None),  # 温かいベージュ
    (23.0, 28.0, (234, 216, 198), (200, 174, 148), (255, 246, 230), 16, (40, 100), 12, None),
    (28.0, 32.5, (246, 224, 192), (220, 178, 128), (255, 225, 160), 18, (40, 100), 12, None),
    (32.5, TOTAL, (30, 22, 20), (48, 34, 28), (245, 180, 110), 20, (40, 120), 10, "lamp"),   # 夜の部屋の間接照明
]
XF = 0.5  # 背景どうしの、ふわっとした切り替え（秒）

# アカウント主がくれた素材（縦に切り出し済み）。置いてある場面は、描いた背景の代わりにこちらを使う
# 場面の番号（0から）: (ファイル名, 使い始める秒, 色の調整)
SRC = f"{ROOT}/03_編集/素材/2026-10-25_日曜の夜"
FOOTAGE = {
    0: ("01.mp4", 2.0, "eq=saturation=0.85:gamma=0.97"),           # 夕焼けの空と木のシルエット
    1: ("02.mp4", 2.0, "eq=gamma=1.4:brightness=0.02:saturation=0.8"),  # 雨の夜の手すりと明かり（暗いので少し明るく）
    2: ("03.mp4", 2.0, "eq=saturation=0.95"),  # 夜の寝室、あたたかいランプの明かり
    3: ("04.mp4", 0.2, "eq=contrast=1.25:brightness=-0.04:saturation=1.2,colorbalance=bs=0.25:bm=0.12:rs=-0.05"),  # 星空（少し青く）
    4: ("05.jpg", 0, "eq=saturation=0.9"),  # 付箋（静止画。ゆっくりズーム）
    5: ("06.jpg", 0, "eq=brightness=0.02,colortemperature=temperature=5800:mix=0.4"),  # 椅子にかけた服（静止画。ゆっくりズーム）
    6: ("07.mp4", 3.0, "eq=brightness=0.02,colortemperature=temperature=5800:mix=0.4"),  # お皿のカヌレ（明日の夜の楽しみ）
    7: ("08.mp4", 0.5, "eq=saturation=0.9"),  # ピンクの砂時計（ゆっくり始めればいい）
}


def gradient(top, bottom):
    t = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top, float) * (1 - t) + np.array(bottom, float) * t
    return np.repeat(arr, W, axis=1)


def glow(arr, cx, cy, radius, color, strength):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    a = np.clip(np.exp(-d ** 2) * strength, 0, 1)[:, :, None]
    return arr * (1 - a) + np.array(color, float) * a


def background(i, top, bottom, deco):
    arr = gradient(top, bottom)
    if deco == "dusk":
        arr = glow(arr, W * 0.5, H * 1.05, W * 0.9, (214, 160, 150), 0.55)   # 地平線に少しだけ残る夕方の色
    elif deco == "moon":
        arr = glow(arr, W * 0.68, H * 0.2, 260, (210, 222, 245), 0.45)
        arr = glow(arr, W * 0.68, H * 0.2, 70, (250, 250, 255), 1.0)
        yy, xx = np.mgrid[0:H, 0:W]
        band = np.exp(-((xx - W * 0.68) / 90) ** 2) * np.clip((yy - H * 0.6) / (H * 0.4), 0, 1) * 0.35
        arr = arr * (1 - band[:, :, None]) + np.array((200, 214, 240), float) * band[:, :, None]  # 水面に映る月の光
        yy2 = np.linspace(0, 1, H)[:, None, None]
        arr *= 1 - 0.15 * np.clip((yy2 - 0.55) / 0.1, 0, 1)  # 水面のほうを少し暗く（境目はなめらかに）
    elif deco == "lamp":
        arr = glow(arr, W * 0.5, H * 0.72, W * 0.85, (240, 170, 100), 0.6)
        arr = glow(arr, W * 0.5, H * 0.72, W * 0.3, (255, 210, 150), 0.5)
    arr += np.random.default_rng(i).uniform(-1.5, 1.5, arr.shape)  # 色の段々（しま模様）が出ないよう、ごく少しざらつきを足す
    p = f"{WORK}/bg{i}.png"
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(p)
    return p


def bokeh(i, color, n, size, rise, dur):
    """光の玉のレイヤー（上にゆっくり流れるよう、縦に長く作る）"""
    rnd = random.Random(i)
    hh = H + int(rise * (dur + 1)) + 200
    img = Image.new("RGBA", (W, hh), color + (0,))  # すき間も同じ色にして、ぼかしで玉のふちが黒くならないようにする
    d = ImageDraw.Draw(img)
    for _ in range(n):
        r = rnd.uniform(*size)
        x, y = rnd.uniform(0, W), rnd.uniform(0, hh)
        a = int(rnd.uniform(40, 110) if r > 10 else rnd.uniform(120, 220))
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    blur = max(1, int(size[1] / 6)) if size[1] > 10 else 1
    img = img.filter(ImageFilter.GaussianBlur(blur))
    p = f"{WORK}/bk{i}.png"
    img.save(p)
    return p


def text_png(i, lines, size):
    """白い文字＋黒いふち、うしろにピンクの帯。画面の中央に置く"""
    lines = [[(s.replace("、", "").replace("。", ""), c) for s, c in ln] for ln in lines]
    font = ImageFont.truetype(FONT, size)
    stroke = max(4, size // 13)
    gap = int(size * 0.45)
    widths = [sum(font.getlength(s) for s, _ in ln) for ln in lines]
    block_h = len(lines) * size + (len(lines) - 1) * gap
    top = int(H * 0.5 - block_h / 2)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bw = max(widths) + 100
    ImageDraw.Draw(img).rounded_rectangle(
        [(W - bw) / 2, top - 40, (W + bw) / 2, top + block_h + 48], radius=30, fill=PINK)
    d = ImageDraw.Draw(img)
    for li, ln in enumerate(lines):
        x = (W - widths[li]) / 2
        y = top + li * (size + gap)
        for s, c in ln:
            d.text((x, y), s, font=font, fill=c + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += font.getlength(s)
    p = f"{WORK}/t{i}.png"
    img.save(p)
    return p


def run(cmd):
    subprocess.run(cmd, check=True)


# 1. 場面ごとの背景動画（切り替えの0.5秒ぶん、前後に少し長く作る）
clips = []
for i, (st, en, top, bottom, bc, n, size, rise, deco) in enumerate(SCENES):
    s = st - (XF / 2 if i > 0 else 0)
    e = en + (XF / 2 if i < len(SCENES) - 1 else 0)
    dur = e - s
    out = f"{WORK}/c{i}.mp4"
    if i in FOOTAGE and os.path.exists(f"{SRC}/{FOOTAGE[i][0]}"):
        name, ss, eq = FOOTAGE[i]
        if name.endswith(".jpg"):
            # 静止画は、2倍の大きさにしてから少しずつ寄る（1.0→1.06倍）。動きがカクカクしないようにするため
            frames = int(round(dur * 30)) + 1
            run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"{SRC}/{name}",
                 "-vf", f"scale=2160:3840,zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30,{eq},setsar=1,format=yuv420p",
                 "-frames:v", f"{frames}", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
            clips.append(out)
            continue
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur + 0.1}", "-i", f"{SRC}/{name}", "-an",
             "-vf", f"{eq},scale=1080:1920,setsar=1,fps=30,format=yuv420p",
             "-t", f"{dur}", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
        clips.append(out)
        continue
    bg, bk = background(i, top, bottom, deco), bokeh(i, bc, n, size, rise, dur)
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{dur}", "-i", bg, "-loop", "1", "-t", f"{dur}", "-i", bk,
         "-filter_complex", f"[0][1]overlay=0:'-{rise}*t',fps=30,format=yuv420p,setsar=1",
         "-t", f"{dur}", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
    clips.append(out)

# 2. 背景をふわっとつないで、最後の1秒でゆっくり暗くする
inputs, chain, last = [], [], "0"
for c in clips:
    inputs += ["-i", c]
for i in range(1, len(clips)):
    off = SCENES[i][0] - XF / 2
    chain.append(f"[{last}][{i}]xfade=transition=fade:duration={XF}:offset={off}[x{i}]")
    last = f"x{i}"
chain.append(f"[{last}]fade=t=out:st={TOTAL - 1}:d=1[v]")
base = f"{WORK}/base.mp4"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[v]",
     "-c:v", "libx264", "-crf", "16", "-preset", "fast", base])

# 3. テロップをのせる（0.3秒でふわっと出し入れ。最後の画面は暗くなり終わるまで残す）
pngs = [text_png(i, t[2], t[3]) for i, t in enumerate(TEXTS)]
inputs = ["-i", base]
for p in pngs:
    inputs += ["-loop", "1", "-t", f"{TOTAL}", "-i", p]
chain, last = [], "0:v"
for i, (st, en, *_rest) in enumerate(TEXTS):
    fi = 0.3
    fade_out = "" if i == len(TEXTS) - 1 else f",fade=t=out:st={en - fi}:d={fi}:alpha=1"
    chain.append(f"[{i + 1}:v]format=rgba,fade=t=in:st={st}:d={fi}:alpha=1{fade_out}[t{i}]")
    chain.append(f"[{last}][t{i}]overlay=0:0:enable='between(t,{st},{en})'[o{i}]")
    last = f"o{i}"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
     "-map", f"[{last}]", "-t", f"{TOTAL}", "-r", "30", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT])
print(OUT)
