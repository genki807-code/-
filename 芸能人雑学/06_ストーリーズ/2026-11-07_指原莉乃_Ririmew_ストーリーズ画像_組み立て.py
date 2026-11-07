# 芸能人雑学：指原莉乃さん × Ririmew のストーリーズ画像（2枚）。背景・PR は草川さんの v4 と同じ（夜空のおしゃれ背景・商品の絵なし・リンクの案内なし）
# 実行：python3 このファイル <出力フォルダ>
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_編集"))
import importlib.util
spec = importlib.util.spec_from_file_location("kumitate", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_編集", "2026-11-01_草川拓弥_立ち位置_組み立て.py"))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
from PIL import Image, ImageDraw, ImageFilter
import math, random

def fancy_bg(seed):
    rnd = random.Random(seed)
    W, H = k.W, k.H
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    top, mid, bot = (8, 10, 28), (22, 16, 48), (10, 12, 30)
    for y in range(H):
        t = y / (H - 1)
        a, b, u = (top, mid, t * 2) if t < 0.5 else (mid, bot, (t - 0.5) * 2)
        d.line([(0, y), (W, y)], fill=tuple(int(p + (q - p) * u) for p, q in zip(a, b)))
    im = im.convert("RGBA")
    # ぼけた大きな光（ゴールド・くすみローズ・ラベンダー）
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    for (x, y, r, c, al) in ((900, 300, 420, (242, 193, 78), 60), (120, 900, 460, (190, 120, 160), 55),
                             (980, 1500, 380, (140, 120, 210), 55), (200, 1800, 300, (242, 193, 78), 35)):
        g.ellipse([x - r, y - r, x + r, y + r], fill=c + (al,))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(140)))
    # 小さなぼけ（丸）
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(bok)
    for _ in range(26):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(10, 46)
        c = rnd.choice([(242, 193, 78), (255, 241, 201), (220, 190, 230)])
        b.ellipse([x - r, y - r, x + r, y + r], fill=c + (rnd.randint(18, 45),))
    im = Image.alpha_composite(im, bok.filter(ImageFilter.GaussianBlur(6)))
    # きらめき（4つの光の星と、こまかい点）
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s2 = ImageDraw.Draw(sp)
    for _ in range(120):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        s2.point((x, y), fill=(255, 255, 255, rnd.randint(60, 160)))
    for _ in range(9):
        x = rnd.choice([rnd.randint(40, 85), rnd.randint(995, 1040)])  # 文字にかからないよう左右のはしだけ
        y, L = rnd.randint(120, H - 120), rnd.randint(14, 30)
        c = (242, 193, 78, 200)
        s2.polygon([(x, y - L), (x + 3, y - 3), (x + L, y), (x + 3, y + 3), (x, y + L), (x - 3, y + 3), (x - L, y), (x - 3, y - 3)], fill=c)
    im = Image.alpha_composite(im, sp)
    # 金の細い二重の枠（上下の表示に重ならない内側）
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = ImageDraw.Draw(fr)
    f.rounded_rectangle([36, 230, W - 36, H - 230], radius=28, outline=(242, 193, 78, 150), width=3)
    f.rounded_rectangle([50, 244, W - 50, H - 244], radius=22, outline=(242, 193, 78, 70), width=1)
    im = Image.alpha_composite(im, fr)
    # うすい粒子（フィルムっぽさ）
    noise = Image.effect_noise((W, H), 24).convert("L").point(lambda v: 12 if v > 150 else 0)
    gr = Image.new("RGBA", (W, H), (255, 255, 255, 0)); gr.putalpha(noise)
    return Image.alpha_composite(im, gr)

def pr(im):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 270, 240, 370], radius=12, fill=k.WHITE)
    f = k.font(64); tw = d.textlength("PR", font=f)
    d.text((60 + (180 - tw) / 2, 270 + 16), "PR", font=f, fill=k.BLACK)

def text(im, lines, y):
    im.alpha_composite(k.with_shadow(k.draw_lines(lines, y)))

def dashed_box(im, box, label):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    for x in range(x0, x1, 40):
        d.line([(x, y0), (min(x + 20, x1), y0)], fill=(255, 255, 255, 140), width=3)
        d.line([(x, y1), (min(x + 20, x1), y1)], fill=(255, 255, 255, 140), width=3)
    for y in range(y0, y1, 40):
        d.line([(x0, y), (x0, min(y + 20, y1))], fill=(255, 255, 255, 140), width=3)
        d.line([(x1, y), (x1, min(y + 20, y1))], fill=(255, 255, 255, 140), width=3)
    f = k.font(40); tw = d.textlength(label, font=f)
    d.text(((x0 + x1 - tw) / 2, (y0 + y1) / 2 - 20), label, font=f, fill=(255, 255, 255, 150))

def band(im, lines, y0=1555, y1=1665):
    d = ImageDraw.Draw(im)
    d.rectangle([0, y0, k.W, y1], fill=(0, 0, 0, 140))
    for i, s3 in enumerate(lines):
        tw = d.textlength(s3, font=k.font(42)); d.text(((k.W - tw) / 2, y0 + 8 + i * 50), s3, font=k.font(42), fill=k.WHITE)

def main(out):
    os.makedirs(out, exist_ok=True)
    # 1枚目：リールの案内（まん中にリールを共有して置く）
    im = fancy_bg(3)
    pr(im)
    text(im, [("新しいリール出したよ", 52), ("芸能人がプロデュースしたコスメって", 50), ("{どんな思い}で作られてるか", 60), ("知ってる？", 60)], (390, 760))
    text(im, [("指原莉乃さんの Ririmew の", 50), ("名前とコンセプトの話はリールで", 48), ("後半で商品を紹介してるよ", 42)], (1345, 1545))
    band(im, ["※このアカウントは、指原さん・Ririmew の", "公式アカウントではありません"])
    im.convert("RGB").save(os.path.join(out, "1枚目_リールの案内.png"))
    # 2枚目：商品の案内
    im = fancy_bg(4)
    pr(im)
    text(im, [("リールで紹介した", 52), ("Ririmew", 84), ("トーンアップカラープライマー", 64), ("", 26),
              ("色は5つ", 52), ("赤みをカバー → {サテングリーン}", 50), ("メイクで透明感 → {グローラベンダー}", 50),
              ("血色感をプラス → {パールピンク}", 50), ("", 20), ("SPF29・PA+++", 56)], (480, 1330))
    band(im, ["※肌の赤みが続くときは、", "皮膚科とかのお医者さんに相談してね"])
    im.convert("RGB").save(os.path.join(out, "2枚目_商品の案内.png"))

if __name__ == "__main__":
    main(sys.argv[1])
