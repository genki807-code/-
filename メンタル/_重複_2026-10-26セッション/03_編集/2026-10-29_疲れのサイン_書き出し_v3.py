#!/usr/bin/env python3
"""10/29 リール「疲れのサイン」を書き出すスクリプト（担当：editor）

もとにしたもの：03_編集/2026-10-29_疲れのサイン_編集設計図.md（39.5秒・7カット・9画面）

使い方：
    python3 03_編集/2026-10-29_疲れのサイン_書き出し.py

v3 の見た目（アカウント主の指定）：
- テロップは白い文字に黒い縁取り、文字の後ろにピンクの帯
- 0秒の1コマ目からテロップを出す（最初の画面はフェードなしでいきなり出す）
- 最初の効果音はアカウント主が付ける。このスクリプトでは音を入れない（BGM も投稿時に Instagram で付ける）

- 03_編集/素材/2026-10-29_疲れのサイン/ に 01〜07 の動画（.mp4）か写真（.jpg / .png）があれば、それを使う。
- まだ置いていないカットは、設計図の色の流れに合わせた「仮の背景」で作る。
- 書き出し先：03_編集/2026-10-29_疲れのサイン_編集_v3.mp4

必要なもの：ffmpeg、Pillow、日本語フォント（Noto Sans CJK JP）
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SOZAI = os.path.join(HERE, "素材", "2026-10-29_疲れのサイン")
W, H = 1080, 1920
FPS = 30

FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

WHITE = (255, 255, 255, 255)
PALE_YELLOW = WHITE  # 文字は全部白（強調は大きさだけ）
BAND_PINK = (244, 143, 177, 235)  # テロップの帯のピンク
OUTLINE = (0, 0, 0, 255)  # 黒い縁取り

# 映像のカット：(秒数, 素材ファイル名, 仮の背景の色 上→下, 次のカットへのつなぎ)
# つなぎ "fade" は 0.5秒のふわっとした切り替え、"cut" はそのまま切り替え
CUTS = [
    (7.5, "01.mp4", ((232, 228, 220), (196, 188, 176)), "fade"),  # 0〜7.5   白いノート
    (4.0, "02.mp4", ((176, 172, 168), (132, 128, 124)), "cut"),   # 7.5〜11.5 机とスマホ
    (4.0, "03.mp4", ((220, 222, 214), (176, 184, 178)), "cut"),   # 11.5〜15.5 窓辺の光
    (4.0, "04.mp4", ((214, 196, 168), (168, 146, 118)), "fade"),  # 15.5〜19.5 ランチのテーブル
    (4.5, "05.mp4", ((210, 190, 170), (160, 136, 116)), "cut"),   # 19.5〜24 毛布・クッション
    (5.0, "06.mp4", ((226, 220, 206), (178, 166, 148)), "fade"),  # 24〜29   ノートに書く手元
    (10.5, "07.mp4", ((214, 140, 84), (60, 44, 52)), None),       # 29〜39.5 夕方の窓辺の灯り
]
FADE = 0.5

# テロップ：(はじまり, おわり, [(行の文字, 色, 大きさ, 太字)], 帯を敷くか, フェード秒)
# 文言は台本・設計図のとおり（変えない）。改行は台本の「／」の位置。
# 帯：全画面にピンクの帯を敷く
TELOPS = [
    (0.0, 3.0, [("疲れサイン", WHITE, 84, True), ("3つ書ける？", WHITE, 84, True)], True, 0.3),
    (3.0, 7.5, [("疲れがたまったときの", WHITE, 72, True), ("小さなサインを3つ", WHITE, 72, True)], True, 0.4),
    (7.5, 11.5, [("①返信を、つい", WHITE, 72, True), ("後回しにしてしまう", WHITE, 72, True)], True, 0.3),
    (11.5, 15.5, [("②いつもの音や光が、", WHITE, 72, True), ("なんだかつらい", WHITE, 72, True)], True, 0.3),
    (15.5, 19.5, [("③お昼に食べたいものが", WHITE, 72, True), ("決められない", WHITE, 72, True)], True, 0.3),
    (19.5, 24.0, [("気づけたら、今日は", WHITE, 72, True), ("少しゆっくりで大丈夫。", PALE_YELLOW, 82, True)], True, 0.4),
    (24.0, 29.0, [("あなたの疲れサインも、", WHITE, 70, True), ("3つ書き出してみてね", WHITE, 70, True)], True, 0.4),
    (29.0, 34.0, [("つらさが続くときは、", WHITE, 68, True), ("医師や相談窓口を頼ってね", WHITE, 68, True)], True, 0.4),
    (34.0, 39.5, [("疲れたかなと思う日に", WHITE, 62, True), ("見返せるよう、保存してね。", WHITE, 62, True)], True, 0.4),
]
TOTAL = 39.5
END_DARK = (38.5, 1.0)  # 38.5〜39.5秒：映像だけゆっくり暗くする（文字は残す）

# 文字を置く範囲：下から2割と右端にはかけない。真ん中より少し上に置く。
TEXT_CENTER_Y = int(H * 0.44)
SAFE_LEFT, SAFE_RIGHT = 80, W - 140
MAX_TEXT_W = SAFE_RIGHT - SAFE_LEFT - 40


def font(size, bold):
    # .ttc の 0 番が日本語（JP）
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size, index=0)


def make_telop_png(lines, band, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # いちばん長い行が横幅に入るよう、その画面の文字をまとめて小さくする（大きさの差は残す）
    widest = max(font(size, bold).getlength(text) for text, _, size, bold in lines)
    scale = min(1.0, MAX_TEXT_W / widest)
    gap = int(28 * scale)
    sizes = []
    for text, _, size, bold in lines:
        f = font(int(size * scale), bold)
        box = f.getbbox(text)
        sizes.append((f, box[2] - box[0], box[3] - box[1], box))
    total_h = sum(s[2] for s in sizes) + gap * (len(lines) - 1)
    max_w = max(s[1] for s in sizes)
    top = TEXT_CENTER_Y - total_h // 2
    cx = (SAFE_LEFT + SAFE_RIGHT) // 2  # 右端のボタンをよけた範囲の真ん中

    if band:  # ピンクの帯
        pad_x, pad_y = 56, 44
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle(
            (cx - max_w // 2 - pad_x, top - pad_y, cx + max_w // 2 + pad_x, top + total_h + pad_y),
            radius=36, fill=BAND_PINK)
        img = Image.alpha_composite(img, layer)

    dt = ImageDraw.Draw(img)
    y = top
    for (text, color, _, _), (f, tw, th, box) in zip(lines, sizes):
        x = cx - tw // 2 - box[0]
        # 白い文字に黒い縁取り
        dt.text((x, y - box[1]), text, font=f, fill=color, stroke_width=max(4, f.size // 12), stroke_fill=OUTLINE)
        y += th + gap
    img.save(path)


def make_gradient_png(top, bottom, path):
    grad = Image.new("RGB", (1, 256))
    for i in range(256):
        t = i / 255
        grad.putpixel((0, i), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    grad.resize((W, H), Image.BICUBIC).save(path)


def main():
    out = os.path.join(HERE, "2026-10-29_疲れのサイン_編集_v3.mp4")
    tmp = tempfile.mkdtemp()
    args = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    filters = []
    used, missing = [], []

    # 背景（カット）。ふわっとつなぐカットは、重なるぶん 0.5秒長く用意する
    for i, (dur, name, colors, trans) in enumerate(CUTS):
        length = dur + (FADE if trans == "fade" else 0)
        # 動画（.mp4）がなければ、同じ番号の写真（.jpg / .jpeg / .png）を探す
        stem = os.path.splitext(name)[0]
        src = next((os.path.join(SOZAI, stem + ext) for ext in (".mp4", ".jpg", ".jpeg", ".png")
                    if os.path.exists(os.path.join(SOZAI, stem + ext))), None)
        if src:
            used.append(os.path.basename(src))
            loop = ["-stream_loop", "-1"] if src.endswith(".mp4") else ["-loop", "1", "-framerate", f"{FPS}"]
            args += loop + ["-t", f"{length}", "-i", src]
            # 縦長に切り出し、明るさ・彩度を少し下げて色をそろえる
            filters.append(
                f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"fps={FPS},eq=brightness=-0.02:saturation=0.85,setsar=1,format=yuv420p,"
                f"trim=duration={length},setpts=PTS-STARTPTS,settb=1/{FPS}[c{i}]")
        else:
            missing.append(name)
            png = os.path.join(tmp, f"bg{i}.png")
            make_gradient_png(*colors, png)
            args += ["-loop", "1", "-framerate", f"{FPS}", "-t", f"{length}", "-i", png]
            filters.append(f"[{i}:v]format=yuv420p,setsar=1,trim=duration={length},setpts=PTS-STARTPTS,settb=1/{FPS}[c{i}]")

    # カットをつなぐ
    prev, t = "c0", CUTS[0][0]
    for i in range(1, len(CUTS)):
        trans = CUTS[i - 1][3]
        lab = f"j{i}"
        if trans == "fade":
            filters.append(f"[{prev}][c{i}]xfade=transition=fade:duration={FADE}:offset={t}[{lab}]")
        else:
            # 時間の単位をそろえる（concat のあとに xfade が来てもつながるように）
            filters.append(f"[{prev}][c{i}]concat=n=2:v=1:a=0,settb=1/{FPS}[{lab}]")
        prev, t = lab, t + CUTS[i][0]
    s, d = END_DARK
    filters.append(f"[{prev}]trim=duration={TOTAL},fade=out:st={s}:d={d}[bg]")

    # テロップを重ねる
    n = len(CUTS)
    prev = "bg"
    for k, (t0, t1, lines, band, fd) in enumerate(TELOPS):
        png = os.path.join(tmp, f"telop{k + 1}.png")
        make_telop_png(lines, band, png)
        dur = t1 - t0
        args += ["-loop", "1", "-framerate", f"{FPS}", "-t", f"{dur}", "-i", png]
        fade_in = "" if k == 0 else f",fade=in:st=0:d={fd}:alpha=1"  # 1枚目は0秒からそのまま出す
        fade_out = "" if k == len(TELOPS) - 1 else f",fade=out:st={dur - fd}:d={fd}:alpha=1"  # 最後の画面は残す
        filters.append(
            f"[{n + k}:v]format=rgba{fade_in}{fade_out},"
            f"setpts=PTS-STARTPTS+{t0}/TB[t{k}]")
        filters.append(f"[{prev}][t{k}]overlay=0:0:eof_action=pass[o{k}]")
        prev = f"o{k}"

    args += ["-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-an",
             "-t", f"{TOTAL}", "-r", f"{FPS}", "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(args, check=True)

    print(f"書き出し：{out}")
    print(f"使った素材：{', '.join(used) or 'なし'}")
    if missing:
        print(f"仮の背景にしたカット：{', '.join(missing)}（{SOZAI} に置くと差し替わります）")


if __name__ == "__main__":
    main()
