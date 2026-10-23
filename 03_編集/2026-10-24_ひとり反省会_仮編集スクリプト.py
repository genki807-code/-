"""10/24 ひとり反省会 リールの仮編集（編集設計図 v3 どおり）"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = "/home/user/-"
SRC = f"{ROOT}/03_編集/素材/2026-10-24_ひとり反省会"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/03_編集/2026-10-24_ひとり反省会_仮編集_v2.mp4"
WORK = tempfile.mkdtemp(prefix="build_1024_")
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H = 1080, 1920

WHITE = (255, 255, 255)
CREAM = (250, 238, 214)      # 心の声（淡い色）
ACCENT = (255, 226, 140)     # 「閉会」だけ淡い黄色
BROWN = (90, 70, 54)         # 仮置き（ベージュ地）用
BEIGE_BG = (222, 208, 188)
PINK = (244, 167, 196, 225)   # 文字のうしろの帯

# (開始, 終了, 行のリスト[[(文字, 色)...]...], 文字サイズ, 中心y比率, 帯あり, 影色)
TEXTS = [
    (0.0, 4.0, [[("休みなのに、", WHITE)], [("ひとり反省会がはじまる", WHITE)]], 74, 0.74, False),
    (4.0, 9.5, [[("「あの返事、まずかったかな」", WHITE)], [("「変に思われたかも」", WHITE)]], 62, 0.24, True),
    (9.5, 14.0, [[("それだけ、相手を", WHITE)], [("大切に思っていたから。", WHITE)]], 70, 0.40, True),
    (14.0, 18.5, [[("今週の反省会は、", WHITE)], [("ここで", WHITE), ("閉会", ACCENT), ("にしませんか。", WHITE)]], 76, 0.40, True),
    (18.5, 23.0, [[("①気になる場面を書き出し、", WHITE)], [("ノートを閉じる", WHITE)]], 66, 0.30, True),
    (23.0, 27.5, [[("②友だちが同じ返事をしたら", WHITE)], [("気になる？", WHITE)]], 66, 0.30, False),
    (27.5, 32.0, [[("③シャツのしわをのばすなど、", WHITE)], [("手を動かしてみる", WHITE)]], 60, 0.47, True),
    (32.0, 35.5, [[("今週も、", WHITE)], [("よく乗りきりましたね。", WHITE)]], 72, 0.36, False),
    (35.5, 41.5, [[("考えが止まらない夜のために、", WHITE)], [("保存しておいてくださいね。", WHITE)]], 60, 0.36, False),
]


def text_png(i, lines, size, cy, band):
    """白い文字＋黒いふち、うしろにピンクの帯（アカウント主の指定・2026-10-23）"""
    font = ImageFont.truetype(FONT, size)
    stroke = max(4, size // 13)
    gap = int(size * 0.45)
    widths = [sum(font.getlength(s) for s, _ in ln) for ln in lines]
    lh = size
    block_h = len(lines) * lh + (len(lines) - 1) * gap
    top = int(H * cy - block_h / 2)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bw = max(widths) + 100
    ImageDraw.Draw(img).rounded_rectangle(
        [(W - bw) / 2, top - 40, (W + bw) / 2, top + block_h + 48], radius=30, fill=PINK)
    d = ImageDraw.Draw(img)
    for li, ln in enumerate(lines):
        x = (W - widths[li]) / 2
        y = top + li * (lh + gap)
        for s, c in ln:
            d.text((x, y), s, font=font, fill=c + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += font.getlength(s)
    p = f"{WORK}/t{i}.png"
    img.save(p)
    return p


def run(cmd):
    subprocess.run(cmd, check=True)


VF = "scale=1080:1920,setsar=1,fps=30,format=yuv420p"


def clip(name, src, start, dur, speed=1.0, eq=None):
    """src の start 秒から、画面上で dur 秒ぶんの映像を作る"""
    filt = [f"setpts=PTS/{speed}" if speed != 1.0 else "setpts=PTS-STARTPTS"]
    if eq:
        filt.append(eq)
    filt.append(VF)
    out = f"{WORK}/{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur * speed + 0.1), "-i", src,
         "-an", "-vf", ",".join(filt), "-t", str(dur), "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
    return out


def plain(name, dur):
    out = f"{WORK}/{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         f"color=c=0x{''.join('%02x' % v for v in BEIGE_BG)}:s={W}x{H}:r=30:d={dur}",
         "-vf", "setsar=1,format=yuv420p", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
    return out


warm = "colortemperature=temperature=5800:mix=0.6"
# 0.5秒のふわっと切り替えは境目をまたぐので、前後のカットを0.25秒ずつ長めに作る
a = clip("a", f"{SRC}/01.mp4", 10.0, 4.25, speed=0.7, eq=f"eq=gamma=0.97:saturation=0.92,{warm}")
b = clip("b", f"{SRC}/02.mp4", 3.0, 6.0, eq=f"eq=brightness=0.04:contrast=0.93,{warm}")
c = clip("c", f"{SRC}/03.mp4", 4.0, 9.25, eq=f"eq=brightness=-0.03,colortemperature=temperature=6000:mix=0.4")
# ほかの机が入らないよう、手元と紙のある下のほうに寄せて拡大する
d = clip("d", f"{SRC}/04.mp4", 17.5, 4.5, eq=f"crop=iw/1.4:ih/1.4:(iw-iw/1.4)/2:ih-ih/1.4,eq=brightness=0.03,{warm}")
e = clip("e", f"{SRC}/05.mp4", 5.0, 4.5, eq=f"eq=brightness=0.04:saturation=1.08,{warm}")
f = clip("f", f"{SRC}/06.mp4", 5.0, 4.5, eq="eq=gamma=0.95,colortemperature=temperature=6000:mix=0.4")
g = clip("g", f"{SRC}/07.mp4", 0.1, 9.5, eq="eq=saturation=0.9:gamma=1.0")

base = f"{WORK}/base.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", a, "-i", b, "-i", c, "-i", d, "-i", e, "-i", f, "-i", g,
     "-filter_complex",
     "[0][1]xfade=transition=fade:duration=0.5:offset=3.75[ab];"
     "[ab][2]xfade=transition=fade:duration=0.5:offset=9.25[abc];"
     "[abc][3][4][5][6]concat=n=5:v=1:a=0,fade=t=out:st=40.5:d=1[v]",
     "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", base])

pngs = [text_png(i, t[2], t[3], t[4], t[5]) for i, t in enumerate(TEXTS)]
inputs = ["-i", base]
for p in pngs:
    inputs += ["-loop", "1", "-t", "41.5", "-i", p]
chain, last = [], "0:v"
for i, (st, en, *_rest) in enumerate(TEXTS):
    fi = 0.3
    # 最後の画面は、映像が暗くなり終わるまで文字を残す
    fade_out = "" if i == len(TEXTS) - 1 else f",fade=t=out:st={en - fi}:d={fi}:alpha=1"
    chain.append(f"[{i + 1}:v]format=rgba,fade=t=in:st={st}:d={fi}:alpha=1{fade_out}[t{i}]")
    chain.append(f"[{last}][t{i}]overlay=0:0:enable='between(t,{st},{en})'[o{i}]")
    last = f"o{i}"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
     "-map", f"[{last}]", "-t", "41.5", "-r", "30", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT])
print(OUT)
