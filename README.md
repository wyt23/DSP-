# Speech Enhancement — 项目说明

这是一个用于演示经典语音增强流程（谱减法 + 维纳滤波）的轻量级示例工程。它会从一段干净语音生成带噪音频，随后进行谱域去噪并保存结果；另有绘图脚本将生成对比图用于论文或报告。

**主要功能**
- 从 `clean.wav` / `clean.wav.m4a` / `clean.mp3` 读取输入音频（自动选择存在的第一个）。
- 如果输入不是 WAV，则使用 `imageio_ffmpeg` 转码为 16 kHz 单声道 WAV 再处理。
- 向干净语音添加高斯噪声并保存为 `noisy.wav`。
- 基于 STFT 的谱减法与维纳滤波得到增强语音，保存为 `denoised.wav`，并打印 SNR 指标。
- `draw_figures.py` 用于绘制频谱图和 SNR 对比图，输出到 `figures/` 目录。

**目录结构（简要）**

```text
project/
├── main.py            # 去噪主脚本：生成 noisy.wav、denoised.wav 并展示波形
├── draw_figures.py    # 绘图脚本：生成 spectrogram 与 SNR 比较图，输出到 figures/
├── requirements.txt   # 依赖列表
├── figures/           # 绘图脚本输出目录（脚本运行后生成）
├── clean.wav*         # 用户提供的干净音频（clean.wav / clean.wav.m4a / clean.mp3）
└── README.md          # 本文档（你正在阅读）
```

依赖与安装
---------------
建议使用 Python 3.8 或更新版本。安装依赖：

```bash
pip install -r requirements.txt
```

requirements.txt 中包含：

```
numpy
librosa
soundfile
matplotlib
imageio-ffmpeg
```

快速开始（运行示例）
--------------------
1. 将你的干净语音文件放到项目根目录，文件名任选：`clean.wav`、`clean.wav.m4a` 或 `clean.mp3`。项目会自动选择第一个存在的文件。
2. 运行去噪脚本：

```bash
python main.py
```

运行后会在当前目录生成：
- `noisy.wav`：向干净语音添加的带噪音频。
- `denoised.wav`：去噪后输出的音频。

如果你想生成用于论文的图像（频谱图、SNR 对比图）：

```bash
python draw_figures.py
```

该脚本会在 `figures/` 目录下保存：`spectrogram_clean.png`（若存在 clean 文件）、`spectrogram_noisy.png`、`spectrogram_enhanced.png`（若存在对应音频）以及 `snr_compare.png`。

实现细节（简述）
------------------
- 声音读取：使用 `librosa.load(..., sr=16000)` 将音频加载为 16 kHz 单声道（若不是 WAV，先用 `imageio_ffmpeg` 转码）。
- 噪声添加：对信号添加高斯白噪声（可在 `main.py` 中调整 SNR）。
- 谱处理：计算 STFT，使用前几帧平均估计噪声谱；使用谱减法（带 floor 参数）得到估计幅度谱，之后用维纳滤波进一步平滑；最后与原相位合成并 ISTFT 重建时域音频。
- 评估指标：计算简单的 SNR（10 * log10(sum(clean^2)/sum(noise^2)）并打印对比。

注意事项
------------
- 脚本假定有一个“干净”参考信号 `clean.*` 用于生成 noisy 与评估 SNR。如果你只有被污染的语音，请自行准备干净参考以复现示例流程。
- 转码与临时文件：当输入为非 WAV 文件时，脚本会生成临时 WAV 文件用于处理，脚本完成后会尝试删除临时文件。
- 该实现为教学/演示用途，未考虑所有边界情况或工业级鲁棒性；在真实应用中请使用更严格的噪声建模和评估指标。

想做的扩展（建议）
------------------
- 替换或补充更先进的噪声估计方法
- 使用掩码/深度学习模型（如 conv-TasNet、SEGAN、DNS 等）替代谱减
- 增加批处理功能以处理文件夹中多个音频

许可证
------
项目包含一个 `LICENSE` 文件，请参阅其中的授权条款。

