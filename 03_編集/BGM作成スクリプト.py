"""リール用の静かなピアノ風BGMを、その場で作曲して書き出す（オリジナル曲なので著作権・クレジットの心配がない）

使い方：python3 BGM作成スクリプト.py 出力.wav 秒数
"""
import sys, wave
import numpy as np

OUT = sys.argv[1]
SEC = float(sys.argv[2]) if len(sys.argv) > 2 else 41.5
SR = 44100
BPM = 64
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def piano(freq, dur, vel):
    """やわらかいピアノのような音（倍音を少し重ねて、ゆっくり消える）"""
    t = np.arange(int(SR * dur)) / SR
    tone = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in [(1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)])
    env = np.exp(-t * 2.2) * np.minimum(1, t / 0.008)
    return tone * env * vel


def pad(freqs, dur):
    """うしろでうすく鳴る和音"""
    t = np.arange(int(SR * dur)) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    return s * env * 0.035


# 和音の流れ（Fmaj7 → Em7 → Dm7 → Cmaj7 をくり返す）。1小節4拍
CHORDS = [
    [53, 57, 60, 64],  # F A C E
    [52, 55, 59, 62],  # E G B D
    [50, 53, 57, 60],  # D F A C
    [48, 52, 55, 59],  # C E G B
]
bar = BEAT * 4
n = int(SR * (SEC + 4))
mix = np.zeros(n)
bar_i, pos = 0, 0.0
while pos < SEC:
    ch = CHORDS[bar_i % 4]
    s = int(pos * SR)
    p = pad([hz(m) for m in ch[:3]], bar + 0.6)
    mix[s:s + len(p)] += p[: n - s]
    # 8分音符の分散和音（上がって下がる）。ときどき音を抜いて、すき間をつくる
    pattern = [ch[0], ch[2] + 12, ch[1] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[3], ch[2] + 12]
    for k, m in enumerate(pattern):
        if k in (5, 7) and rng.random() < 0.4:
            continue
        st = int((pos + k * BEAT / 2 + rng.uniform(0, 0.012)) * SR)
        note = piano(hz(m), 2.5, 0.16 if k else 0.22)
        e = min(n, st + len(note))
        mix[st:e] += note[: e - st]
    pos += bar
    bar_i += 1

# 部屋の響き（遅れて小さく重なる音）
wet = np.zeros_like(mix)
for d, g in [(0.083, 0.35), (0.131, 0.28), (0.197, 0.22), (0.271, 0.16), (0.389, 0.11)]:
    k = int(d * SR)
    wet[k:] += mix[:-k] * g
mix = mix + wet
mix = mix[: int(SR * SEC)]

# はじめ2秒でふわっと出て、最後3秒でゆっくり消える
t = np.arange(len(mix)) / SR
mix *= np.minimum(1, t / 2.0) * np.clip((SEC - t) / 3.0, 0, 1)
mix = mix / np.max(np.abs(mix)) * 0.5  # 音量はひかえめに（約 -6dB）
left = mix
right = np.concatenate([np.zeros(int(0.012 * SR)), mix])[: len(mix)]  # 少しだけ左右に広げる
data = (np.stack([left, right], axis=1) * 32767).astype(np.int16)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print(OUT)
