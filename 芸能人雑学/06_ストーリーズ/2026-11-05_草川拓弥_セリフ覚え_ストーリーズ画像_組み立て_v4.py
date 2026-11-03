# 芸能人雑学：草川拓弥さん「セリフ覚え」PR版のストーリーズ画像（2枚）v4：v3 から、2枚目のリンクの案内（「気になる人は、ここから見てみてね」とスタンプの置き場所）をなくした
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

def main(out, guide):
    os.makedirs(out, exist_ok=True)
    # 1枚目：リールへの案内（まん中にリールを共有して置く）
    im = fancy_bg(1)
    pr(im)
    text(im, [("新しいリール出したよ", 56), ("ダンスも芝居もこなす人って", 60), ("{最初から器用}だと思わない？", 64)], (400, 680))
    if guide: dashed_box(im, (240, 710, 840, 1330), "ここにリールを共有して置く")
    text(im, [("草川拓弥さん（超特急）の", 52), ("セリフの覚え方の話はリールで見てね", 52), ("後半で商品を紹介してるよ", 44)], (1345, 1545))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1555, k.W, 1665], fill=(0, 0, 0, 140))
    for i, s2 in enumerate(["※紹介する商品は、", "草川さん・超特急とは関係ありません"]):
        tw = d.textlength(s2, font=k.font(42)); d.text(((k.W - tw) / 2, 1563 + i * 50), s2, font=k.font(42), fill=k.WHITE)
    im.convert("RGB").save(os.path.join(out, "1枚目_リールの案内" + ("_置き場所つき" if guide else "") + ".png"))
    # 2枚目：商品の案内＋リンクスタンプ
    im = fancy_bg(2)
    pr(im)
    text(im, [("リールで紹介した", 56), ("{推し色}でえらべる", 84), ("推し活フレーム", 84), ("", 30),
              ("アクスタ・カード・缶バッジ用があるよ", 46), ("", 30), ("Cherish Palette", 72)], (620, 1300))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1548, k.W, 1668], fill=(0, 0, 0, 140))
    for i, s3 in enumerate(["※草川さん・超特急とは関係のない商品です", "（草川さんが使っている物ではありません）"]):
        tw = d.textlength(s3, font=k.font(42)); d.text(((k.W - tw) / 2, 1560 + i * 54), s3, font=k.font(42), fill=k.WHITE)
    im.convert("RGB").save(os.path.join(out, "2枚目_商品とリンク" + ("_置き場所つき" if guide else "") + ".png"))

if __name__ == "__main__":
    main(sys.argv[1], False)
