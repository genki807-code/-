#!/usr/bin/env python3
"""10/30 リール「その不機嫌、あなたが直さなくていい」を書き出すスクリプト（担当：editor）

もとにしたもの：03_編集/2026-10-30_不機嫌_編集設計図.md（41秒・7カット・9画面）

使い方：
    python3 03_編集/2026-10-30_不機嫌_書き出し.py

- 03_編集/素材/2026-10-30_不機嫌/ に 01.mp4〜07.mp4 があれば、その動画を使う。
- まだ置いていないカットは、設計図の色の流れに合わせた「仮の背景」で作る。
- 音は入れない（BGM は投稿するときに Instagram で付ける）。
- 書き出し先：03_編集/2026-10-30_不機嫌_仮編集.mp4（素材が全部そろったら _v2 で書き出す）

必要なもの：ffmpeg、Pillow、日本語フォント（Noto Sans CJK JP）
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SOZAI = os.path.join(HERE, "素材", "2026-10-30_不機嫌")
W, H = 1080, 1920
FPS = 30

FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

WHITE = (255, 255, 255, 255)
PALE_YELLOW = (255, 241, 196, 255)  # 強調（画面3の2行目）
PALE_BEIGE = (245, 228, 208, 255)  # 心の中のひと言（画面7の「」）

# 映像のカット：(秒数, 素材ファイル名, 仮の背景の色 上→下, 次のカットへのつなぎ)
# つなぎ "fade" は 0.5秒のふわっとした切り替え、"cut" はそのまま切り替え
CUTS = [
    (4.0, "01.mp4", ((120, 124, 130), (88, 92, 98)), "fade"),     # 0〜4   キーボードの手元
    (5.0, "02.mp4", ((112, 114, 118), (80, 82, 88)), "fade"),     # 4〜9   手が止まる手元・書類
    (10.0, "03.mp4", ((150, 160, 172), (196, 214, 232)), "cut"),  # 9〜19  曇り空 → 晴れる
    (4.0, "04.mp4", ((196, 176, 152), (150, 128, 106)), "cut"),   # 19〜23 廊下を歩く足元
    (4.5, "05.mp4", ((210, 184, 150), (160, 128, 96)), "cut"),    # 23〜27.5 温かい飲み物
    (4.0, "06.mp4", ((214, 192, 168), (168, 140, 116)), "cut"),   # 27.5〜31.5 ハンドクリーム
    (9.5, "07.mp4", ((214, 140, 84), (60, 44, 52)), None),        # 31.5〜41 帰り道の灯り
]
FADE = 0.5

# テロップ：(はじまり, おわり, [(行の文字, 色, 大きさ, 太字)], 帯を敷くか, フェード秒)
# 帯：明るい空・ベージュの画面でも読めるよう、全画面に敷く（読み切れることを優先）
# 文言は台本・設計図のとおり（変えない）。改行は台本の「／」の位置。
TELOPS = [
    (0.0, 4.0, [("隣のため息に", WHITE, 84, True), ("『私のせい？』と思う人へ", WHITE, 84, True)], True, 0.3),
    (4.0, 9.0, [("つい顔色をうかがって、", WHITE, 72, True), ("ぐったりしていませんか？", WHITE, 72, True)], True, 0.5),
    (9.0, 13.5, [("でも、その不機嫌を", WHITE, 72, True), ("あなたが直さなくていい。", PALE_YELLOW, 82, True)], True, 0.4),
    (13.5, 19.0, [("仕事のやりとりはふだん通り、", WHITE, 68, True), ("気分までは背負わない。", WHITE, 68, True)], True, 0.4),
    (19.0, 23.0, [("①ひと息つきに、", WHITE, 72, True), ("少しだけ席を離れる", WHITE, 72, True)], True, 0.3),
    (23.0, 27.5, [("②温かい飲み物で、", WHITE, 72, True), ("自分の機嫌を先にとる", WHITE, 72, True)], True, 0.4),
    (27.5, 31.5, [("③心の中で", WHITE, 72, True), ("『これは私の係じゃない』", PALE_BEIGE, 72, False)], True, 0.3),
    (31.5, 35.5, [("その優しさ、", WHITE, 72, True), ("まず自分に使ってね。", WHITE, 72, True)], True, 0.3),
    (35.5, 41.0, [("空気が重い日に見返せるよう、", WHITE, 62, True), ("保存してくださいね。", WHITE, 62, True)], True, 0.4),
]
TOTAL = 41.0
END_DARK = (40.0, 1.0)  # 40〜41秒：映像だけゆっくり暗くする（文字は残す）

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

    if band:  # 半透明のベージュの帯
        pad_x, pad_y = 56, 44
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle(
            (cx - max_w // 2 - pad_x, top - pad_y, cx + max_w // 2 + pad_x, top + total_h + pad_y),
            radius=36, fill=(120, 100, 84, 110))
        img = Image.alpha_composite(img, layer)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(text_layer)
    y = top
    for (text, color, _, _), (f, tw, th, box) in zip(lines, sizes):
        x = cx - tw // 2 - box[0]
        ds.text((x + 3, y - box[1] + 4), text, font=f, fill=(40, 30, 30, 170))
        dt.text((x, y - box[1]), text, font=f, fill=color)
        y += th + gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))  # 薄い影
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, text_layer)
    img.save(path)


def make_gradient_png(top, bottom, path):
    grad = Image.new("RGB", (1, 256))
    for i in range(256):
        t = i / 255
        grad.putpixel((0, i), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    grad.resize((W, H), Image.BICUBIC).save(path)


def main():
    out = os.path.join(HERE, "2026-10-30_不機嫌_仮編集.mp4")
    tmp = tempfile.mkdtemp()
    args = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    filters = []
    used, missing = [], []

    # 背景（カット）。ふわっとつなぐカットは、重なるぶん 0.5秒長く用意する
    for i, (dur, name, colors, trans) in enumerate(CUTS):
        length = dur + (FADE if trans == "fade" else 0)
        src = os.path.join(SOZAI, name)
        if os.path.exists(src):
            used.append(name)
            args += ["-stream_loop", "-1", "-t", f"{length}", "-i", src]
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
        fade_out = "" if k == len(TELOPS) - 1 else f",fade=out:st={dur - fd}:d={fd}:alpha=1"  # 最後の画面は残す
        filters.append(
            f"[{n + k}:v]format=rgba,fade=in:st=0:d={fd}:alpha=1{fade_out},"
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
