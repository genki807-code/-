# YouTube 長尺1本目「職場で疲れやすい繊細さんへ」5分版（横長 1920x1080・音なし）
# 11/12 アカウント主「撮らずに今あるリールの写真で先に作る」「一旦5分の長尺作ってみて」
# 台本：02_台本/2026-11-12_YouTube職場疲れ_台本_v3_5分.md（v2 の67画面から短くした）
# 写真は 03_編集/素材/ の、これまでのリールで使ったもの（11/13 の分は出どころ確認中なので使わない）
# v2：画面9・33は縦長のパソコンの写真をやめてオフィスの別の場所に。checker の指摘で、横長で映るようになったロゴ・文字をぼかした。最後の4画面の写真を変えた（切り替えを増やす）
# 実行：python3 <この.py> <素材フォルダ（03_編集/素材）> <出力.mp4> <確認画像フォルダ>
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC, OUT, SHOT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1920, 1080, 30
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

# 写真の名前 → ファイル
P = {
    'オフィス': '2026-10-30_音疲れ/カット1.jpg', 'キーボード': '2026-10-30_不機嫌/カット1.jpg',
    '机と時計': '2026-10-30_不機嫌/カット2.jpg', '曇り空': '2026-10-30_不機嫌/カット3.jpg',
    '廊下の足': '2026-10-30_不機嫌/カット4.jpg', 'コーヒー': '2026-10-30_不機嫌/カット5.jpg',
    'ハンドクリーム': '2026-10-30_不機嫌/カット6.jpg', '夜景': '2026-10-30_不機嫌/カット7.jpg',
    '木もれ日': '2026-10-30_音疲れ/カット2.jpg', '階段': '2026-10-30_音疲れ/カット3.jpg',
    '耳栓': '2026-10-30_音疲れ/カット4.jpg', '暗い部屋のライト': '2026-10-30_音疲れ/カット5.jpg',
    '夕方の空': '2026-10-29_疲れのサイン/カット7.jpg', 'ノートとペン': '2026-10-29_疲れのサイン/カット1.jpg',
    '駅': '2026-11-10_通院と仕事/カット3.jpg', 'パソコンの机': '2026-11-04_自分責め/カット1.jpg',
    '葉っぱ': '2026-10-31_予定の入れすぎ/カット4.jpg', 'ソファ': '2026-10-31_予定の入れすぎ/カット3.jpg',
    '歩く足': '2026-10-31_予定の入れすぎ/カット2.jpg', '花びん': '2026-11-01_褒め言葉/カット2.jpg',
    '付せん': '2026-11-01_褒め言葉/カット1.jpg', '付せん2': '2026-11-06_調子の波/カット3.jpg',
    '電灯': '2026-11-01_褒め言葉/カット4.jpg', '電話機': '2026-11-02_電話/カット1.jpg',
    '書く手': '2026-11-02_電話/カット3.jpg', '置いたスマホ': '2026-10-28_比べる癖/カット2.jpg',
    'スマホを持つ手': '2026-11-07_返信疲れ/カット1.jpg', 'バラ': '2026-11-07_返信疲れ/カット3.jpg',
    '窓辺の花': '2026-10-28_比べる癖/カット6.jpg', 'ベンチ': '2026-11-08_有給/カット3.jpg',
    '枝と空': '2026-11-04_自分責め/カット4.jpg', '青空': '2026-11-03_季節の変わり目/カット2.jpg',
    '落ち葉': '2026-11-03_季節の変わり目/カット1.jpg', '夕焼け': '2026-11-03_季節の変わり目/カット4.jpg',
    'ベッド': '2026-11-12_寝る前の考えごと/カット4.jpg',
}

# ぼかす場所（これまでのリールと同じ。もとの写真の座標）
BLUR = {
    '2026-10-30_音疲れ/カット1.jpg': ([(285, 245, 445, 345), (475, 235, 560, 345), (120, 185, 205, 290),
                                     (630, 225, 705, 305), (35, 125, 115, 205), (675, 175, 758, 265)], 12, 25),
    '2026-10-30_不機嫌/カット1.jpg': ([(10, 530, 140, 625)], 20, 8),                       # Windows キーのマーク
    '2026-10-30_不機嫌/カット2.jpg': ([(5, 160, 80, 215), (430, 155, 505, 195)], 20, 8),  # 電卓のロゴ・時計の文字
    '2026-11-04_自分責め/カット1.jpg': ([(0, 30, 140, 520)], 8, 10),                      # 左のモニターの文字
    '2026-11-01_褒め言葉/カット4.jpg': ([(345, 225, 400, 270)], 12, 8),                   # 電球の横のラベル
    '2026-10-31_予定の入れすぎ/カット2.jpg': ([(50, 330, 185, 430), (340, 330, 470, 440)], 20, 8),  # くつのロゴ
}
BRIGHT = {'ベッド': 0.8, '暗い部屋のライト': 1.15}

# 画面：(秒, 1行目, 2行目, 写真, 種類, 切り抜きの左[0-1] 開始→終了, 上[0-1])
# 種類：hook＝画面1（大きい文字・写真は動かさない）／title＝章の始まり／emph＝2行目を黄色／normal／small
S = [
    # はじめに
    (5, '職場にいるだけで', 'ぐったりする人へ', 'オフィス', 'hook', (0.5, 0.5), 0.5),
    (5, '音と電話と人の機嫌に', '疲れたときの小さな工夫', 'キーボード', 'normal', (0.4, 0.6), 0.5),
    (5, '帰るころには', 'もうへとへと', '駅', 'normal', (0.3, 0.5), 0.5),
    (6, '疲れやすいのは', 'あなたが弱いからじゃないんです', '夕方の空', 'emph', (0.5, 0.5), 0.6),
    (6, 'この動画では職場の', '3つの場面を順に見ていきます', 'ノートとペン', 'normal', (0.4, 0.6), 0.5),
    (6, '①職場の音②電話③人の機嫌', '気になるところから見てくださいね', 'ノートとペン', 'normal', (0.6, 0.4), 0.5),
    # その1
    (6, 'その1', '職場の音でぐったりする日', '机と時計', 'title', (0.5, 0.5), 0.4),
    (6, 'キーボードの音や話し声', 'ずっと耳に残っていませんか？', 'キーボード', 'normal', (0.7, 0.5), 0.6),
    (5, '集中したいのに', '音に気をとられてしまう', 'オフィス', 'normal', (0.8, 1.0), 0.6),
    (6, '周りは平気そうなのに', '自分だけ疲れている気がする', '曇り空', 'normal', (0.3, 0.6), 0.4),
    (6, '細かい音に気づけるのは', '感じとる力があるからかも', '木もれ日', 'emph', (0.5, 0.5), 0.5),
    (5, '疲れるのは', '自然なことです', '葉っぱ', 'emph', (0.5, 0.5), 0.45),
    (5, 'ここから小さな工夫を', '3つ置きますね', '階段', 'normal', (0.4, 0.5), 0.5),
    (6, '①休憩中の1分だけ', '静かな場所で目と耳を休める', '階段', 'normal', (0.6, 0.5), 0.6),
    (6, '②耳栓を「お守り」に持つ', '（職場の決まりに合わせて）', '耳栓', 'normal', (0.5, 0.5), 0.65),
    (6, '③帰ったら少しだけ', '音のない時間をつくる', '暗い部屋のライト', 'normal', (0.4, 0.5), 0.5),
    (6, '①静かな場所で1分②耳栓をお守りに', '③帰ったら音のない時間', 'ソファ', 'normal', (0.5, 0.5), 0.6),
    (5, 'がんばった自分を', '今日はいたわってね', '花びん', 'emph', (0.5, 0.5), 0.45),
    # その2
    (6, 'その2', '電話が鳴るとドキッとする', '電話機', 'title', (0.5, 0.5), 0.4),
    (4, '電話が鳴ると', 'ドキッ', '電話機', 'emph', (0.3, 0.2), 0.3),
    (5, '鳴った瞬間に', '胸がぎゅっとする', '置いたスマホ', 'normal', (0.5, 0.5), 0.5),
    (6, '顔が見えない電話は', '気をくばるところが多いもの', 'スマホを持つ手', 'normal', (0.3, 0.4), 0.55),
    (6, '苦手なのはあなたが', 'ていねいな人だからかも', 'バラ', 'emph', (0.5, 0.5), 0.5),
    (5, '電話の前の準備を', '3つ置きますね', '書く手', 'normal', (0.5, 0.5), 0.4),
    (6, '①最初のひと言を付せんに', '書いて貼っておく', '付せん', 'normal', (0.5, 0.5), 0.5),
    (6, '②かける前に話すことを', '3つだけ書き出す', 'ノートとペン', 'normal', (0.5, 0.3), 0.6),
    (6, '③「確認して折り返します」と', '言っていいと決めておく', '電話機', 'normal', (0.6, 0.4), 0.55),
    (5, '使い方は', '職場の決まりに合わせてね', '机と時計', 'normal', (0.3, 0.5), 0.6),
    (6, '①ひと言を付せんに②話すことを3つ', '③「確認して折り返します」', '付せん2', 'normal', (0.5, 0.5), 0.5),
    (5, '電話のあとは自分に', '「おつかれさま」を', '電灯', 'emph', (0.5, 0.5), 0.5),
    # その3
    (6, 'その3', '近くの人が不機嫌なとき', '曇り空', 'title', (0.6, 0.5), 0.5),
    (5, 'そのため息', '私のせい？', '枝と空', 'emph', (0.5, 0.5), 0.5),
    (6, '隣の不機嫌につい顔色を', 'うかがって疲れていませんか？', 'オフィス', 'normal', (0.0, 0.2), 0.6),
    (6, '気持ちを感じとりやすい人ほど', '空気の重さを受けとりやすいのかも', '夜景', 'normal', (0.5, 0.5), 0.5),
    (6, 'でもその不機嫌を', 'あなたが直さなくていい', '青空', 'emph', (0.4, 0.5), 0.5),
    (5, '相手の機嫌は', '相手のもの', '青空', 'emph', (0.6, 0.5), 0.6),
    (6, '仕事のやりとりはふだん通り', '気分までは背負わない', '窓辺の花', 'normal', (0.5, 0.5), 0.35),
    (5, 'ここからは自分を守る', '小さな工夫を3つ', '窓辺の花', 'normal', (0.5, 0.5), 0.55),
    (5, '①ひと息つきに', '少しだけ席を離れる', '廊下の足', 'normal', (0.5, 0.5), 0.6),
    (6, '②温かい飲み物で', '自分の機嫌を先にとる', 'コーヒー', 'normal', (0.5, 0.5), 0.45),
    (6, '③心の中で', '「これは私の係じゃない」', 'ベンチ', 'normal', (0.5, 0.5), 0.5),
    (6, '①少しだけ席を離れる②温かい飲み物', '③「これは私の係じゃない」', 'バラ', 'normal', (0.4, 0.6), 0.4),
    (5, 'その優しさ', 'まず自分に使ってね', 'ハンドクリーム', 'emph', (0.5, 0.5), 0.45),
    # おわりに
    (6, 'おわりに', '今日のまとめ', '夕方の空', 'title', (0.5, 0.5), 0.45),
    (6, '音も電話も人の機嫌も', '気づける人ほど疲れやすいのかも', '歩く足', 'normal', (0.5, 0.5), 0.6),
    (6, '疲れやすいのは', 'あなたが弱いからじゃないんです', '落ち葉', 'emph', (0.5, 0.5), 0.5),
    (6, '今日の工夫はぜんぶ', 'できなくて大丈夫です', 'ソファ', 'normal', (0.3, 0.5), 0.5),
    (6, 'ひとつだけ', '試せそうなものからでいい', '木もれ日', 'normal', (0.5, 0.5), 0.3),
    (6, '今日も職場で', 'がんばったあなたへおつかれさま', '夕焼け', 'emph', (0.4, 0.5), 0.5),
    (6, '職場で疲れた日に見返せるよう', 'よかったら保存してくださいね', 'ベッド', 'small', (0.4, 0.5), 0.5),
    (6, '役に立ったら高評価で', '教えてもらえるとうれしいです', '窓辺の花', 'small', (0.5, 0.5), 0.6),
    (6, '繊細さんが少しラクになるヒントを', '動画で届けていきます', '木もれ日', 'small', (0.3, 0.4), 0.7),
    (6, 'よかったらチャンネル登録して', 'また会いに来てね', '葉っぱ', 'small', (0.5, 0.5), 0.6),
]
DUR = sum(s[0] for s in S)
DARK_LEN = 1.0  # 最後の1秒は映像だけ暗く


def prep(key):
    f = P[key]
    im = Image.open(f'{SRC}/{f}').convert('RGB')
    if f in BLUR:
        boxes, r, fe = BLUR[f]
        mask = Image.new('L', im.size, 0)
        for b in boxes:
            ImageDraw.Draw(mask).rectangle(b, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(fe))
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(r)), im, mask)
    im = ImageEnhance.Color(im).enhance(0.88)
    if key in BRIGHT:
        im = ImageEnhance.Brightness(im).enhance(BRIGHT[key])
    s = max(W / im.width, H / im.height)  # 画面いっぱい（横長に合わせて上下を切る）
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def bg_frame(big, p, xr0, xr1, yr, z0, z1):
    z = z0 + (z1 - z0) * p
    cw, ch = W / z, H / z
    xr = xr0 + (xr1 - xr0) * p
    left, top = (big.width - cw) * xr, (big.height - ch) * yr
    return big.resize((W, H), Image.BICUBIC, box=(left, top, left + cw, top + ch))


def text_layer(lines, kind):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size, gap, stroke, cy = 62, 26, 5, 800
    if kind == 'small':
        size = 56
    if kind == 'title':
        cy = 540
    if kind == 'hook':  # 画面1は大きく・横いっぱい近く
        size, gap, stroke, cy = 150, 40, 9, 540
        while max(d.textlength(l, font=ImageFont.truetype(FONT, size)) for l in lines) > W - 260:
            size -= 2
    sizes = [size, size]
    if kind == 'title':
        sizes = [size + 24, size + 8]
    fonts = [ImageFont.truetype(FONT, s) for s in sizes]
    widths = [d.textlength(l, font=f) for l, f in zip(lines, fonts)]
    total = sum(sizes) + gap
    y = cy - total / 2
    px, py = 44, 34
    bw = max(widths) + px * 2
    d.rounded_rectangle([(W - bw) / 2, y - py, (W + bw) / 2, y + total + py],
                        radius=26, fill=(236, 122, 152, 225))  # ブランドのピンク
    colors = ['white', (255, 240, 170) if kind == 'emph' else 'white']
    for l, f, w, c, s in zip(lines, fonts, widths, colors, sizes):
        d.text(((W - w) / 2, y), l, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += s + gap
    return im


bigs = {k: prep(k) for k in {s[3] for s in S}}
ff = subprocess.Popen(['cat'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) if os.environ.get('PREVIEW') else subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                       '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
t0 = 0
chapters = []
for i, (sec, l1, l2, key, kind, (x0, x1), yr) in enumerate(S):
    if kind in ('title', 'hook'):
        chapters.append((t0, l2 if kind == 'title' else 'はじめに'))
    lay = text_layer([l1, l2], kind)
    n = round(sec * FPS)
    z0, z1 = (1.0, 1.0) if kind == 'hook' else (1.0, 1.06)
    if kind == 'hook':
        x1 = x0
    fi = 0 if i == 0 else 0.3
    for f in (range(n) if not os.environ.get('PREVIEW') else [n // 2]):
        t = f / FPS
        frame = bg_frame(bigs[key], f / n, x0, x1, yr, z0, z1)
        if i == len(S) - 1 and t > sec - DARK_LEN:
            frame = ImageEnhance.Brightness(frame).enhance(1 - 0.8 * (t - (sec - DARK_LEN)) / DARK_LEN)
        frame = frame.convert('RGBA')
        al = min(1, t / fi) if fi else 1
        if al >= 1:
            frame.alpha_composite(lay)
        else:
            l2_ = lay.copy()
            l2_.putalpha(l2_.getchannel('A').point(lambda v: int(v * al)))
            frame.alpha_composite(l2_)
        frame = frame.convert('RGB')
        if f == n // 2:
            frame.save(f'{SHOT}/画面{i + 1:02d}.jpg', quality=85)
        if i == 0 and f == 0:
            frame.save(f'{SHOT}/00_最初のコマ.jpg', quality=85)
        ff.stdin.write(frame.tobytes())
    t0 += sec
ff.stdin.close()
ff.wait()
print('done', ff.returncode, 'DUR', DUR, 'screens', len(S))
for t, name in chapters:
    print(f'{int(t // 60)}:{int(t % 60):02d} {name}')
