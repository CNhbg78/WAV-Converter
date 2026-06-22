# 🎵 音频转换器 / Audio Converter

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **XTS 工作室 出品 / Powered by XTS Studio**

---

## 中文介绍

### 📖 简介

**音频转换器** 是一款基于 Python 开发的全能音频格式转换工具，拥有现代化深色主题 UI，简单易用，无需专业知识即可快速完成音频格式转换。

### ✨ 功能特性

- **多格式互转** — 支持 7 种音频格式互转：MP3、WAV、FLAC、AAC、OGG、M4A、WMA
- **参数可调** — 自由设置采样率（22050~96000Hz）、位深（16/24/32bit）、声道（单声道/立体声）
- **批量处理** — 支持同时选择多个文件或整个文件夹，4线程并行加速
- **现代界面** — 深色/浅色/跟随系统三档主题，窗口可自由调整大小
- **多语言支持** — 自动跟随系统语言（中文/English）
- **智能检测** — 自动检测 ffmpeg 环境，支持将 ffmpeg.exe 放在 `ffmpeg_bin/` 目录
- **使用便捷** — 拖拽操作、进度显示、耗时统计、一键打开输出文件夹
- **配置记忆** — 记住上次的输出目录、窗口大小、主题设置

### 🚀 快速开始

#### 方法一：直接运行

1. 安装 Python 3.8+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 ffmpeg（任选其一）：
   - `winget install ffmpeg`
   - 或下载 ffmpeg.exe 放入 `ffmpeg_bin/` 目录
4. 运行程序：
   ```bash
   python src/main.py
   ```

#### 方法二：打包为 exe

```bash
# 安装 pyinstaller
pip install pyinstaller

# 打包
pyinstaller mp3_to_wav.spec --clean --noconfirm

# exe 输出到 dist/MP3转WAV转换器.exe
```

### 📁 项目结构

```
MP3-WAV-Converter/
├── src/                    # 源代码
│   ├── main.py             # 入口文件
│   ├── app.py              # UI 程序
│   ├── converter.py        # 转换引擎
│   ├── i18n/               # 多语言
│   │   ├── zh_CN.json      # 中文翻译
│   │   └── en_US.json      # 英文翻译
├── ffmpeg_bin/             # 放置 ffmpeg.exe（可选）
├── README.md               # 本文件
├── requirements.txt        # 依赖清单
├── build.bat               # 一键打包脚本
├── mp3_to_wav.spec         # PyInstaller 配置
└── version.txt             # exe 版本信息
```

### 🔧 环境要求

| 依赖 | 版本 |
|------|------|
| Python | >= 3.8 |
| customtkinter | >= 5.2.0 |
| ffmpeg | 任意版本 |

---

## English

### 📖 Introduction

**Audio Converter** is a versatile audio format conversion tool built with Python. It features a modern dark-themed UI that is intuitive and easy to use.

### ✨ Features

- **Multi-format Conversion** — Convert between 7 audio formats: MP3, WAV, FLAC, AAC, OGG, M4A, WMA
- **Adjustable Parameters** — Customize sample rate (22050~96000Hz), bit depth (16/24/32bit), channels (mono/stereo)
- **Batch Processing** — Process multiple files or entire folders with 4-thread parallel acceleration
- **Modern UI** — Dark/Light/System theme options, resizable window
- **Multi-language** — Auto-detects system language (中文/English)
- **Smart Detection** — Auto-detects ffmpeg; place ffmpeg.exe in `ffmpeg_bin/` directory
- **Easy to Use** — Drag & drop, progress display, time statistics, one-click open output folder
- **Config Memory** — Remembers output directory, window size, theme settings

### 🚀 Quick Start

#### Option 1: Run from Source

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install ffmpeg:
   - `winget install ffmpeg`
   - Or download ffmpeg.exe into `ffmpeg_bin/` folder
4. Run the program:
   ```bash
   python src/main.py
   ```

#### Option 2: Package as exe

```bash
pip install pyinstaller
pyinstaller mp3_to_wav.spec --clean --noconfirm
# exe output: dist/MP3转WAV转换器.exe
```

### 🔧 Requirements

| Dependency | Version |
|------------|---------|
| Python | >= 3.8 |
| customtkinter | >= 5.2.0 |
| ffmpeg | any |

---

## 📄 License

This project is licensed under the MIT License.

---

## 📬 Contact

**XTS 工作室 / XTS Studio**
