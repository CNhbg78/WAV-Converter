# 🔊 WAV 转换器 / WAV Converter

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **XTS 工作室 出品 / Powered by XTS Studio**

---

## 中文介绍

### 📖 简介

**WAV 转换器** 是一款将多种音频格式转换为 WAV 的桌面工具。支持 MP3、FLAC、AAC、OGG、M4A、WMA 等常见格式作为输入，统一输出为标准 WAV 文件。

拥有现代化深色主题 UI，简单易用，无需专业知识即可快速完成转换。

### ✨ 功能特性

- **多格式输入** — 支持 MP3、WAV、FLAC、AAC、OGG、M4A、WMA 等格式
- **统一输出 WAV** — 标准 PCM 16/24/32bit WAV 文件
- **参数可调** — 自由设置采样率（22050~96000Hz）、位深（16/24/32bit）、声道（单声道/立体声）
- **批量处理** — 支持同时选择多个文件或整个文件夹，4线程并行加速
- **现代界面** — 深色/浅色/跟随系统三档主题，窗口可自由调整大小
- **多语言支持** — 自动跟随系统语言（中文/English）
- **智能检测** — 自动检测 ffmpeg 环境，支持将 ffmpeg.exe 放在 `ffmpeg_bin/` 目录
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

#### 方法二：使用打包好的 exe

打包好的 `WAVConverter.exe` 在 [打包的程序](../%E6%89%93%E5%8C%85%E7%9A%84%E7%A8%8B%E5%BA%8F/WAVConverter.exe) 目录，双击即可运行。

#### 方法三：自行打包

```bash
pip install pyinstaller
pyinstaller src/main.py --onefile --windowed --name "WAVConverter" --add-data "src/i18n;./i18n" --version-file version.txt --distpath release --clean --noconfirm
```

### 📁 项目结构

```
WAV-Converter/
├── src/                    # 源代码
│   ├── main.py             # 入口文件
│   ├── app.py              # UI 程序
│   ├── converter.py        # 转换引擎
│   └── i18n/               # 多语言
├── ffmpeg_bin/             # 放置 ffmpeg.exe（可选）
├── README.md               # 本文件
├── requirements.txt        # 依赖清单
└── build.bat               # 一键打包脚本
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

**WAV Converter** is a desktop tool that converts various audio formats to WAV. It supports MP3, FLAC, AAC, OGG, M4A, WMA and more as input, producing standard WAV files as output.

Features a modern dark-themed UI that is intuitive and easy to use.

### ✨ Features

- **Multi-format Input** — Supports MP3, WAV, FLAC, AAC, OGG, M4A, WMA and more
- **WAV Output Only** — Standard PCM 16/24/32bit WAV files
- **Adjustable Parameters** — Customize sample rate (22050~96000Hz), bit depth (16/24/32bit), channels (mono/stereo)
- **Batch Processing** — Process multiple files or entire folders with 4-thread parallel acceleration
- **Modern UI** — Dark/Light/System theme options, resizable window
- **Multi-language** — Auto-detects system language (中文/English)
- **Smart Detection** — Auto-detects ffmpeg; place ffmpeg.exe in `ffmpeg_bin/` directory
- **Config Memory** — Remembers output directory, window size, theme settings

### 🚀 Quick Start

#### Option 1: Run from Source

```bash
pip install -r requirements.txt
python src/main.py
```

#### Option 2: Use Pre-built exe

The `WAVConverter.exe` is available at the [packaged program](../%E6%89%93%E5%8C%85%E7%9A%84%E7%A8%8B%E5%BA%8F/WAVConverter.exe) folder. Double-click to run.

#### Option 3: Build Yourself

```bash
pip install pyinstaller
pyinstaller src/main.py --onefile --windowed --name "WAVConverter" --add-data "src/i18n;./i18n" --version-file version.txt --distpath release --clean --noconfirm
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
