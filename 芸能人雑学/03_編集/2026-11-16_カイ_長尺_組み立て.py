# 芸能人雑学：カイさん 長尺（横長 1920x1080）の組み立て
# 写真3枚（アカウント主がくれたもの・11/16「写真つかってね」）＋ずんだもんの音声
# テロップはまだ入れていない（読み上げの文が届いたら足す）
# 実行：python3 このファイル <素材フォルダ> <出力.mp4> <確認画像フォルダ>
#   素材フォルダの中：photo1.jpg photo2.jpg photo3.jpg voice1.wav voice2.wav
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H, FPS = 1920, 1080, 30
GOLD = (242, 193, 78)
GAP, TAIL, XF = 0.4, 0.8, 0.5  # 音声のあいだ・最後の余白・写真の切りかえ（秒）

src, out, chk = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(chk, exist_ok=True)
tmp = out + "_frames"
os.makedirs(tmp, exist_ok=True)


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout)


# ---------- 音声をつなぐ ----------
voices = [os.path.join(src, f"voice{i}.wav") for i in (1, 2)]
total = sum(dur(v) for v in voices) + GAP * (len(voices) - 1) + TAIL
audio = os.path.join(tmp, "audio.wav")
inputs, filt = [], []
for i, v in enumerate(voices):
    inputs += ["-i", v]
    filt.append(f"[{i}:a]apad=pad_dur={GAP if i < len(voices) - 1 else TAIL}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(voices))) + f"concat=n={len(voices)}:v=0:a=1[out]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", audio], check=True)


# ---------- 1画面ぶんの土台（写真ごと） ----------
def scene_base(path):
    ph = Image.open(path).convert("RGB")
    # 背景：同じ写真を大きくぼかして暗く
    s = max(W / ph.width, H / ph.height)
    b = ph.resize((int(ph.width * s) + 1, int(ph.height * s) + 1), Image.LANCZOS)
    b = b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H))
    b = ImageEnhance.Brightness(b.filter(ImageFilter.GaussianBlur(40))).enhance(0.35)
    # 下のテロップ用に、下をさらに暗く
    shade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(shade)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=int(max(0, (y - 600) / (H - 600)) * 150))
    b = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), b, shade)
    return b, ph


def frame(base, ph, t, d_scene):
    im = base.copy()
    # 写真：真ん中に、高さ 860px を目安。ゆっくり少しずつ大きく（1.00→1.04）
    z = 1.0 + 0.04 * (t / d_scene)
    ph_h = int(860 * z)
    ph_w = int(ph.width * ph_h / ph.height)
    p = ph.resize((ph_w, ph_h), Image.LANCZOS)
    x, y = (W - ph_w) // 2, 60 - (ph_h - 860) // 2
    # 影
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([x + 10, y + 16, x + ph_w + 10, y + ph_h + 16], fill=(0, 0, 0, 170))
    im = Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(18))).convert("RGB")
    im.paste(p, (x, y))
    ImageDraw.Draw(im).rectangle([x - 4, y - 4, x + ph_w + 3, y + ph_h + 3], outline=GOLD, width=4)
    return im


photos = [os.path.join(src, f"photo{i}.jpg") for i in (1, 2, 3)]
bases = [scene_base(p) for p in photos]
n = len(photos)
d_scene = (total + XF * (n - 1)) / n  # 写真1枚の長さ（切りかえの重なりこみ）
N = int(round(total * FPS))
for f in range(N):
    t = f / FPS
    k = min(int(t // (d_scene - XF)), n - 1)
    t0 = k * (d_scene - XF)
    img = frame(*bases[k], t - t0, d_scene)
    if k + 1 < n and t > t0 + d_scene - XF:  # 次の写真へ ふわっと切りかえ
        a = (t - (t0 + d_scene - XF)) / XF
        img = Image.blend(img, frame(*bases[k + 1], t - (t0 + d_scene - XF), d_scene), a)
    if t < 0.3:  # 最初は黒からふわっと
        img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.3)
    img.save(os.path.join(tmp, f"{f:05d}.png"))
    if f in (int(0.5 * FPS), int((d_scene - XF + 0.6) * FPS), int((2 * (d_scene - XF) + 0.6) * FPS)):
        img.save(os.path.join(chk, f"確認_{f / FPS:04.1f}秒.png"))

subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "%05d.png"),
                "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
subprocess.run(["rm", "-rf", tmp])
print(f"できた：{out}（{total:.1f}秒）")
