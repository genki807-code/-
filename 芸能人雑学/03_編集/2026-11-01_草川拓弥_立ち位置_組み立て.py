# 芸能人雑学：草川拓弥さん「立ち位置」リールの組み立て（写真なし・文字と図形だけ）
# 設計図：03_編集/2026-11-01_草川拓弥_立ち位置_編集設計図.md（秒数は案B・約46秒）
# 実行：python3 このファイル <出力.mp4> <確認画像フォルダ>
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
WHITE, GOLD, BLACK = (255, 255, 255), (242, 193, 78), (0, 0, 0)
LIGHT = (255, 241, 201)
DUR = [4.5, 5, 5.5, 6, 5.5, 4, 3.5, 6.5, 5.5]  # 案B
XFADE, FADEIN = 0.3, 0.25
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


# ---------- 背景 ----------
def gradient():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    top, bot = (6, 8, 15), (14, 21, 48)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    return im.convert("RGBA")


def glow(base, draw_fn, alpha, blur):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), alpha)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, layer)


def spotlight(im):
    im = glow(im, lambda d, a: d.polygon([(470, 0), (610, 0), (920, 1560), (160, 1560)], fill=LIGHT + (a,)), 56, 60)
    im = glow(im, lambda d, a: d.ellipse([200, 1500, 880, 1620], fill=LIGHT + (a,)), 90, 30)
    return glow(im, lambda d, a: d.line([(0, 1560), (W, 1560)], fill=WHITE + (a,), width=2), 38, 0)


def bamiri(d, cx, cy, color):
    for ang in (12, 102):
        r = math.radians(ang)
        dx, dy = 60 * math.cos(r), 60 * math.sin(r)
        nx, ny = 11 * -math.sin(r), 11 * math.cos(r)
        d.polygon([(cx - dx + nx, cy - dy + ny), (cx + dx + nx, cy + dy + ny),
                   (cx + dx - nx, cy + dy - ny), (cx - dx - nx, cy - dy - ny)], fill=color)


def bg(n):
    im = gradient()
    if n in (1, 9):
        return spotlight(im)
    if n == 2:
        im = glow(im, lambda d, a: d.rectangle([0, 1100, W, H], fill=(20, 28, 56, a)), 255, 0)
        def lines(d, a):
            for x0 in (-200, 200, 880, 1280):
                d.line([(540, 1100), (x0, H)], fill=WHITE + (a,), width=2)
        im = glow(im, lines, 20, 0)
        im = glow(im, lambda d, a: d.polygon([(420, 0), (660, 0), (900, 1100), (180, 1100)], fill=LIGHT + (a,)), 38, 60)
        def marks(d, a):
            bamiri(d, 260, 1330, WHITE + (90,))
            bamiri(d, 540, 1330, GOLD + (180,))
            bamiri(d, 820, 1330, WHITE + (90,))
        return glow(im, marks, 0, 0)
    if n == 3:
        def frame(d, a):
            x0, y0, x1, y1, L = 90, 330, 990, 1590, 110
            for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
                d.line([(x, y), (x + sx * L, y)], fill=WHITE + (153,), width=6)
                d.line([(x, y), (x, y + sy * L)], fill=WHITE + (153,), width=6)
            d.line([(510, 1400), (570, 1400)], fill=WHITE + (100,), width=3)
            d.line([(540, 1370), (540, 1430)], fill=WHITE + (100,), width=3)
            bamiri(d, 540, 1500, GOLD + (180,))
        return glow(im, frame, 0, 0)
    if n == 4:
        def bokeh(d, a):
            for (x, y, r, c, al) in ((150, 260, 120, GOLD, 50), (820, 180, 90, WHITE, 40), (560, 330, 60, GOLD, 35),
                                     (950, 420, 140, WHITE, 25), (120, 1560, 100, WHITE, 35), (430, 1700, 140, GOLD, 45),
                                     (860, 1600, 80, GOLD, 50), (980, 1780, 50, WHITE, 40), (300, 1420, 40, GOLD, 40)):
                d.ellipse([x - r, y - r, x + r, y + r], fill=c + (al,))
        return glow(im, bokeh, 0, 25)
    if n == 5:
        im = glow(im, lambda d, a: d.polygon([(700, 0), (W, 0), (W, 500), (300, 1300)], fill=LIGHT + (a,)), 38, 60)
        def papers(d, a):
            for ang, dx in ((-6, -30), (3, 10), (9, 40)):
                p = Image.new("RGBA", (420, 220), WHITE + (32,))
                p = p.rotate(ang, expand=True)
                im.alpha_composite(p, (330 + dx, 1300))
        papers(None, 0)
        return im
    if n == 6:
        im = glow(im, lambda d, a: d.polygon([(0, 0), (380, 0), (W, 1300), (500, 1500)], fill=LIGHT + (a,)), 51, 60)
        def rules(d, a):
            for y in range(1000, H, 70):
                d.line([(0, y), (W, y)], fill=WHITE + (a,), width=2)
        return glow(im, rules, 15, 0)
    if n == 7:
        def morning(d, a):
            for y in range(1100, H):
                t = (y - 1100) / (H - 1100)
                d.line([(0, y), (W, y)], fill=(58, 42, 20, int(200 * t)))
        im = glow(im, morning, 0, 0)
        im = glow(im, lambda d, a: d.rectangle([240, 1150, 840, 1650], fill=LIGHT + (a,)), 30, 0)
        def window(d, a):
            d.rectangle([240, 1150, 840, 1650], outline=WHITE + (a,), width=6)
            d.line([(540, 1150), (540, 1650)], fill=WHITE + (a,), width=6)
            d.line([(240, 1400), (840, 1400)], fill=WHITE + (a,), width=6)
        return glow(im, window, 51, 0)
    if n == 8:
        im = glow(im, lambda d, a: d.polygon([(420, 0), (660, 0), (940, 1300), (140, 1300)], fill=LIGHT + (a,)), 38, 60)
        def shelf(d, a):
            d.line([(140, 1300), (940, 1300)], fill=GOLD + (230,), width=4)
            c = WHITE + (153,)
            d.rounded_rectangle([200, 996, 380, 1296], radius=14, outline=c, width=6)   # アクスタ用
            d.rounded_rectangle([450, 1046, 630, 1296], radius=12, outline=c, width=6)  # トレカ用
            d.ellipse([705, 1126, 875, 1296], outline=c, width=6)                       # 缶バッジ用
            cols = [(196, 120, 120), (214, 160, 110), (214, 196, 120), (150, 186, 120), (110, 170, 150), (110, 170, 190),
                    (120, 140, 200), (150, 130, 200), (190, 130, 190), (210, 140, 170), (170, 170, 170), (230, 230, 230)]
            for i, col in enumerate(cols):
                x = 540 + (i - 5.5) * 56
                d.ellipse([x - 13, 1335, x + 13, 1361], fill=col + (220,))
        return glow(im, shelf, 0, 0)
    return im


# ---------- 文字 ----------
# 1行 = (文字, 大きさ)。{ } の中はゴールド。
SCREENS = {
    1: dict(y=(560, 1300), lines=[("実は草川拓弥さん（超特急）、", 56), ("撮影で", 60), ("{「わりとビタ止まり}", 84),
                                  ("{できる」}んだって", 84), ("その理由、{ライブ}にあった", 60)]),
    2: dict(y=(420, 1000), lines=[("ステージでは", 56), ("「この曲のこのタイミングで", 60), ("ここに立つ」", 60),
                                  ("って感覚が、", 60), ("{身体に染み付いてる}んだって", 64)]),
    3: dict(y=(480, 1240), lines=[("だから撮影で", 56), ("「ここで止まってほしい」", 60), ("「ここから動いてほしい」", 60),
                                  ("って言われても、", 56), ("わりと{ビタ止まり}できる", 72)]),
    4: dict(y=(560, 1300), left=150, lines=[("本人いわく", 52), ("「グループ活動で培った", 62), ("{立ち位置の意識}は、", 62),
                                            ("芝居の撮影でも", 62), ("確実に生きていると", 62), ("思います」", 62)]),
    5: dict(y=(460, 1220), boxes=True, lines=[("ちなみにセリフの覚え方は", 56), ("{黙読} → {声に出す} →", 64),
                                              ("{動きながら言う}", 64), ("振りとは", 56), ("「全然違います（笑）」だって", 56)]),
    6: dict(y=(640, 1160), lines=[("身体で覚えるというより", 60), ("「{反復して}", 72), ("{染み込ませていく}感じ」", 72)]),
    7: dict(y=(760, 960), lines=[("今コツコツやってることも、", 64), ("いつか{別の場所で生きる}かも", 64)]),
    8: dict(y=(400, 930), lines=[("ここからPR", 52), ("{推し色}でえらべる", 76), ("推し活フレーム", 76),
                                 ("アクスタ・トレカ・", 56), ("缶バッジ用があるよ", 56), ("Cherish Palette", 64)]),
    9: dict(y=(480, 1400), lines=[("がんばる意味が", 60), ("見えない日に", 60), ("見返せるように、", 60), ("{保存してね}", 72),
                                  ("", 40), ("フレームが気になる人は、", 56), ("{プロフのリンク}から", 56), ("見てみてね", 56)]),
}


def segments(s):
    out, gold, buf = [], False, ""
    for ch in s:
        if ch in "{}":
            if buf:
                out.append((buf, gold))
            buf, gold = "", ch == "{"
        else:
            buf += ch
    if buf:
        out.append((buf, gold))
    return out


def draw_lines(lines, y_range, left=None, boxes=False, layer=None):
    layer = layer or Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    heights = [int(sz * 1.45) for _, sz in lines]
    y = (y_range[0] + y_range[1] - sum(heights)) // 2
    gold_boxes, quote_top, quote_bot = [], None, None
    for (s, sz), h in zip(lines, heights):
        segs = segments(s)
        f = font(sz)
        width = sum(d.textlength(t, font=f) for t, _ in segs)
        x = left if left is not None else (W - width) / 2
        ty = y + (h - sz) // 2
        for t, g in segs:
            d.text((x, ty), t, font=f, fill=GOLD if g else WHITE)
            tw = d.textlength(t, font=f)
            if g and boxes:
                gold_boxes.append((x - 16, ty - 8, x + tw + 16, ty + sz + 8))
            x += tw
        if left is not None and s.startswith(("「", "{", "芝", "確", "思")) and s:
            quote_top = ty if quote_top is None else quote_top
            quote_bot = ty + sz
        y += h
    for b in gold_boxes:
        d.rounded_rectangle(b, radius=14, outline=WHITE + (128,), width=3)
    if left is not None and quote_top is not None:
        d.line([(110, quote_top), (110, quote_bot)], fill=GOLD, width=6)
    return layer


def with_shadow(layer):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.6))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(a)
    return Image.alpha_composite(sh, layer)


def pr_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([64, 260, 224, 352], radius=10, fill=WHITE)
    f = font(56)
    tw = d.textlength("PR", font=f)
    d.text((64 + (160 - tw) / 2, 260 + (92 - 56) / 2 - 2), "PR", font=f, fill=BLACK)
    return lay


def disclaimer_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 1405, W, 1565], fill=(0, 0, 0, 128))
    for i, s in enumerate(["※草川さん・超特急とは関係のない商品です", "（草川さんが使っている物ではありません）"]):
        tw = d.textlength(s, font=font(42))
        d.text(((W - tw) / 2, 1430 + i * 62), s, font=font(42), fill=WHITE)
    s = "※絵はイメージです"
    tw = d.textlength(s, font=font(42))
    d.text((940 - tw, 940), s, font=font(42), fill=WHITE)
    return lay


# ---------- 組み立て ----------
def zoom(im, t, dur):
    s = 1 + 0.04 * min(t / dur, 1)
    w, h = int(W * s), int(H * s)
    big = im.resize((w, h), Image.BICUBIC)
    x, y = (w - W) // 2, (h - H) // 2
    return big.crop((x, y, x + W, y + H))


def main(out, check_dir):
    os.makedirs(check_dir, exist_ok=True)
    bgs = {n: bg(n) for n in SCREENS}
    texts = {n: with_shadow(draw_lines(c["lines"], c["y"], c.get("left"), c.get("boxes", False))) for n, c in SCREENS.items()}
    PR, DISC = pr_layer(), disclaimer_layer()
    starts = [sum(DUR[:i]) for i in range(len(DUR))]
    total = sum(DUR)

    def screen_frame(n, t):
        dur = DUR[n - 1]
        im = zoom(bgs[n], t, dur)
        if n == 1 or t >= FADEIN:
            im = Image.alpha_composite(im, texts[n])
        else:
            tl = texts[n].copy()
            tl.putalpha(tl.getchannel("A").point(lambda v: int(v * t / FADEIN)))
            im = Image.alpha_composite(im, tl)
        return im

    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                             "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nframes = int(round(total * FPS))
    checks = {0: "00_最初のコマ"}
    for i, s in enumerate(starts):
        checks[int((s + DUR[i] / 2) * FPS)] = f"{i + 1:02d}_画面{i + 1}"
    for k in range(nframes):
        t = k / FPS
        i = max(j for j, s in enumerate(starts) if s <= t + 1e-9)
        n, lt = i + 1, t - starts[i]
        frame = screen_frame(n, lt)
        if n < 9 and lt > DUR[i] - XFADE:
            a = (lt - (DUR[i] - XFADE)) / XFADE
            frame = Image.blend(frame, screen_frame(n + 1, FADEIN), a)
        if n in (1, 8, 9):
            frame = Image.alpha_composite(frame, PR)
        if n == 8:
            frame = Image.alpha_composite(frame, DISC)
        rgb = frame.convert("RGB")
        proc.stdin.write(rgb.tobytes())
        if k in checks:
            rgb.save(os.path.join(check_dir, checks[k] + ".jpg"), quality=88)
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
