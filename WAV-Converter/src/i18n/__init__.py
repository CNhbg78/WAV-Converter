import json
import locale
import os
from pathlib import Path

I18N_DIR = os.path.dirname(os.path.abspath(__file__))

_lang = None
_strings = {}


def _detect_system_language():
    """检测系统语言，返回语言代码"""
    try:
        code, _ = locale.getdefaultlocale()
        if code:
            code = code.replace("-", "_")
            if code.startswith("zh"):
                return "zh_CN"
            elif code.startswith("en"):
                return "en_US"
    except Exception:
        pass
    return "zh_CN"


def _load_translations(lang_code):
    """加载指定语言的翻译"""
    filepath = os.path.join(I18N_DIR, f"{lang_code}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        if lang_code != "zh_CN":
            return _load_translations("zh_CN")
        return {}


def init(lang=None):
    """初始化i18n系统。lang=None时自动检测系统语言"""
    global _lang, _strings
    if lang is None:
        lang = _detect_system_language()
    _lang = lang
    _strings = _load_translations(lang)


def t(key, **kwargs):
    """获取翻译文本，支持占位符替换"""
    text = _strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def get_lang():
    return _lang


def get_available_languages():
    """获取可用语言列表"""
    langs = []
    for f in os.listdir(I18N_DIR):
        if f.endswith(".json"):
            code = f[:-5]
            name_map = {"zh_CN": "中文", "en_US": "English"}
            langs.append((code, name_map.get(code, code)))
    return langs
