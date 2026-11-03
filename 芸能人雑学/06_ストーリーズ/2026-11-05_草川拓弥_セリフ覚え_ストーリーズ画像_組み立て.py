# 芸能人雑学：草川拓弥さん「セリフ覚え」PR版のストーリーズ画像（2枚）
# 実行：python3 このファイル <出力フォルダ>
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_編集"))
import importlib.util
spec = importlib.util.spec_from_file_location("kumitate", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_編集", "2026-11-01_草川拓弥_立ち位置_組み立て.py"))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
from PIL import Image, ImageDraw

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
    im = k.bg(1)
    pr(im)
    text(im, [("新しいリール出したよ", 56), ("ダンスも芝居もこなす人って", 60), ("{最初から器用}だと思わない？", 64)], (400, 680))
    if guide: dashed_box(im, (240, 720, 840, 1380), "ここにリールを共有して置く")
    text(im, [("草川拓弥さん（超特急）の", 52), ("セリフの覚え方の話は、リールで", 52), ("リールの後半で商品を紹介してるよ", 44)], (1420, 1650))
    im.convert("RGB").save(os.path.join(out, "1枚目_リールの案内" + ("_置き場所つき" if guide else "") + ".png"))
    # 2枚目：商品の案内＋リンクスタンプ
    im = k.bg(8)
    pr(im)
    text(im, [("リールで紹介した", 52), ("{推し色}でえらべる", 72), ("推し活フレーム", 72), ("アクスタ・カード・缶バッジ用があるよ", 50), ("Cherish Palette", 64)], (400, 940))
    d = ImageDraw.Draw(im)
    s = "※絵はイメージです"; tw = d.textlength(s, font=k.font(40)); d.text((940 - tw, 960), s, font=k.font(40), fill=k.WHITE)
    if guide: dashed_box(im, (290, 1390, 790, 1470), "ここにリンクスタンプ")
    text(im, [("気になる人は、ここから見てみてね", 48)], (1475, 1540))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1548, k.W, 1668], fill=(0, 0, 0, 140))
    for i, s in enumerate(["※草川さん・超特急とは関係のない商品です", "（草川さんが使っている物ではありません）"]):
        tw = d.textlength(s, font=k.font(42)); d.text(((k.W - tw) / 2, 1560 + i * 54), s, font=k.font(42), fill=k.WHITE)
    im.convert("RGB").save(os.path.join(out, "2枚目_商品とリンク" + ("_置き場所つき" if guide else "") + ".png"))

if __name__ == "__main__":
    main(sys.argv[1], False); main(sys.argv[1], True)
