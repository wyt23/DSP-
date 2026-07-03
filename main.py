import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
import os
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_files = ["clean.wav", "clean.wav.m4a", "clean.mp3"]
audio_path = None
for filename in possible_files:
    candidate = os.path.join(BASE_DIR, filename)
    if os.path.exists(candidate):
        audio_path = candidate
        break

if audio_path is None:
    raise FileNotFoundError(
        f"未找到输入音频文件，请将 clean.wav、clean.wav.m4a 或 clean.mp3 放在 {BASE_DIR}"
    )

print("当前读取路径：", audio_path)

def convert_to_wav(src_path):
    from imageio_ffmpeg import get_ffmpeg_exe

    ffmpeg_exe = get_ffmpeg_exe()
    dst_fd, dst_path = tempfile.mkstemp(suffix=".wav")
    os.close(dst_fd)

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        src_path,
        "-ar",
        "16000",
        "-ac",
        "1",
        dst_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return dst_path

converted_wav_path = None
if not audio_path.lower().endswith('.wav'):
    print('正在转码为 WAV 文件以便读取...')
    converted_wav_path = convert_to_wav(audio_path)
    audio_path = converted_wav_path
    print('转码完成，临时文件：', audio_path)


try:
    clean, sr = librosa.load(audio_path, sr=16000)
finally:
    if converted_wav_path and os.path.exists(converted_wav_path):
        os.remove(converted_wav_path)


def add_noise(signal, snr_db=0):
    noise = np.random.normal(0, 1, len(signal))

    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)

    scale = np.sqrt(signal_power / (10 ** (snr_db / 10) * noise_power))
    noisy = signal + noise * scale
    return noisy

noisy = add_noise(clean, snr_db=0)
sf.write(os.path.join(BASE_DIR, "noisy.wav"), noisy, sr)


n_fft = 512
hop = 256

noisy_stft = librosa.stft(noisy, n_fft=n_fft, hop_length=hop)
mag = np.abs(noisy_stft)
phase = np.angle(noisy_stft)


noise_mag = np.mean(mag[:, :5], axis=1, keepdims=True)


alpha = 2.0
beta = 0.02

spec_sub = np.maximum(mag - alpha * noise_mag, beta * noise_mag)


wiener = spec_sub**2 / (spec_sub**2 + noise_mag**2)
final_mag = wiener * mag

enhanced_stft = final_mag * np.exp(1j * phase)
denoised = librosa.istft(enhanced_stft, hop_length=hop, length=len(clean))


denoised_path = os.path.join(BASE_DIR, "denoised.wav")
sf.write(denoised_path, denoised, sr)

print("✔ denoised.wav 已生成：", denoised_path)


def snr(clean, enhanced):
    noise = clean - enhanced
    return 10 * np.log10(np.sum(clean**2) / np.sum(noise**2))

print("SNR noisy:", snr(clean, noisy))
print("SNR denoised:", snr(clean, denoised))


plt.figure(figsize=(10, 5))

plt.plot(clean[:2000], label="clean")
plt.plot(noisy[:2000], label="noisy")
plt.plot(denoised[:2000], label="denoised")

plt.legend()
plt.title("Speech Enhancement Result")
plt.show()