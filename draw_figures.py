import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"

os.makedirs("figures", exist_ok=True)

source_candidates = [
    ("clean.wav", "Clean Speech", "spectrogram_clean.png"),
    ("clean.wav.m4a", "Clean Speech", "spectrogram_clean.png"),
    ("clean.mp3", "Clean Speech", "spectrogram_clean.png")
]

signals = []
for wav, title, save_name in source_candidates:
    if os.path.exists(wav):
        signals.append((wav, title, save_name))
        break

for wav, title, save_name in [("noisy.wav", "Noisy Speech", "spectrogram_noisy.png"),
                              ("denoised.wav", "Enhanced Speech", "spectrogram_enhanced.png")]:
    if os.path.exists(wav):
        signals.append((wav, title, save_name))

if not signals:
    raise FileNotFoundError(
        "未找到 clean.wav / clean.wav.m4a / clean.mp3，或 noisy.wav / denoised.wav。请将音频文件放在当前目录。"
    )


def convert_to_wav(src_path):
    import tempfile
    import subprocess
    from imageio_ffmpeg import get_ffmpeg_exe

    fd, dst_path = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    ffmpeg_exe = get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_exe,
        '-y',
        '-i', src_path,
        '-ar', '16000',
        '-ac', '1',
        dst_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return dst_path

created_temp = []
for wav, title, save_name in signals:
    if not wav.lower().endswith('.wav'):
        print('Converting', wav, 'to WAV...')
        wav = convert_to_wav(wav)
        created_temp.append(wav)

    y, sr = librosa.load(wav, sr=16000)

    D = librosa.stft(
        y,
        n_fft=512,
        hop_length=256,
        window="hann"
    )

    D_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    plt.figure(figsize=(8,4))

    librosa.display.specshow(
        D_db,
        sr=sr,
        hop_length=256,
        x_axis="time",
        y_axis="hz",
        cmap="magma"
    )

    plt.colorbar(format="%+2.0f dB")

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        os.path.join("figures", save_name),
        dpi=600
    )

    plt.close()

for tmp in created_temp:
    try:
        os.remove(tmp)
    except OSError:
        pass

plt.figure(figsize=(5,4))

snr = [0, 10.13]

bars = plt.bar(
    ["Noisy", "Enhanced"],
    snr
)

plt.ylabel("SNR (dB)")
plt.title("SNR Comparison")

for bar in bars:
    h = bar.get_height()
    plt.text(
        bar.get_x()+bar.get_width()/2,
        h+0.2,
        f"{h:.2f}",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    "figures/snr_compare.png",
    dpi=600
)

plt.close()

print("Finished.")