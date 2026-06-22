#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP3 to WAV 转换器 - 全能音频格式转换工具
XTS 工作室 出品
"""

import os
import sys

# 确保能找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
