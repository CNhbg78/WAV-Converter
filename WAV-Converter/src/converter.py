import subprocess
import os
import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_app_dir():
    """获取程序所在目录（兼容打包后的exe）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # 当从 src/converter.py 调用时，项目根在父目录
    src_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(src_dir)


SUPPORTED_FORMATS = {
    "mp3": {"name": ".mp3", "codec": "libmp3lame", "desc": "MPEG Audio Layer 3"},
    "wav": {"name": ".wav", "codec": "pcm_s16le", "desc": "Waveform Audio"},
    "flac": {"name": ".flac", "codec": "flac", "desc": "Free Lossless Audio Codec"},
    "aac": {"name": ".aac", "codec": "aac", "desc": "Advanced Audio Coding"},
    "ogg": {"name": ".ogg", "codec": "libvorbis", "desc": "Ogg Vorbis"},
    "m4a": {"name": ".m4a", "codec": "aac", "desc": "MPEG-4 Audio"},
    "wma": {"name": ".wma", "codec": "wmav2", "desc": "Windows Media Audio"},
}

INPUT_EXTS = tuple("." + fmt for fmt in SUPPORTED_FORMATS.keys())


def check_ffmpeg():
    """检查ffmpeg是否可用"""
    if shutil.which("ffmpeg"):
        return True
    app_dir = get_app_dir()
    for p in [
        os.path.join(app_dir, "ffmpeg.exe"),
        os.path.join(app_dir, "ffmpeg_bin", "ffmpeg.exe"),
    ]:
        if os.path.isfile(p):
            return True
    return False


def _get_ffmpeg_path():
    """获取ffmpeg可执行文件路径"""
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    app_dir = get_app_dir()
    for p in [
        os.path.join(app_dir, "ffmpeg.exe"),
        os.path.join(app_dir, "ffmpeg_bin", "ffmpeg.exe"),
    ]:
        real = os.path.abspath(p)
        if os.path.isfile(real):
            return real
    return "ffmpeg"


def get_output_extension(output_format):
    """获取输出格式的文件扩展名"""
    if output_format in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[output_format]["name"]
    return ".wav"


def get_input_label(ext):
    """根据扩展名返回格式标签"""
    ext = ext.lower().lstrip(".")
    if ext in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[ext]["name"]
    return f".{ext}"


def _do_convert(task):
    """内部转换函数
    task: (input_file, output_file, params_dict)
    params_dict: {sample_rate, output_format, bit_depth, channels}
    """
    input_file, output_file, params = task
    ffmpeg_path = _get_ffmpeg_path()
    cmd = [ffmpeg_path, "-i", input_file, "-y"]

    if params:
        sr = params.get("sample_rate", "44100")
        fmt = params.get("output_format", "wav")
        bd = params.get("bit_depth", "16")
        ch = params.get("channels", "")

        cmd += ["-ar", sr]

        if fmt != "wav":
            # Compressed formats
            codec_map = {k: v["codec"] for k, v in SUPPORTED_FORMATS.items()}
            cmd += ["-acodec", codec_map.get(fmt, "libmp3lame")]
            if fmt == "mp3":
                cmd += ["-ab", "320k"]
            elif fmt in ("aac", "m4a"):
                cmd += ["-ab", "256k"]
            elif fmt == "ogg":
                cmd += ["-aq", "200"]
        else:
            # WAV - use bit depth
            codec_map = {"16": "pcm_s16le", "24": "pcm_s24le", "32": "pcm_s32le"}
            cmd += ["-acodec", codec_map.get(bd, "pcm_s16le")]

        # Handle channels with i18n-aware matching
        ch_lower = ch.lower()
        if ch_lower in ("mono", "单声道", "1"):
            cmd += ["-ac", "1"]
        elif ch_lower in ("stereo", "立体声", "2"):
            cmd += ["-ac", "2"]

    cmd.append(output_file)

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8", errors="ignore")[-300:])


def batch_convert(tasks, max_workers=4, cancel_event=None, progress_callback=None):
    """批量转换文件
    返回: (success_count, failed_files, was_cancelled)
    """
    total = len(tasks)
    success_count = 0
    failed_files = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_do_convert, task): task
            for task in tasks
        }
        done = 0
        for future in as_completed(future_map):
            if cancel_event and cancel_event.is_set():
                executor.shutdown(wait=False, cancel_futures=True)
                break

            task = future_map[future]
            done += 1
            try:
                future.result()
                success_count += 1
            except Exception as e:
                failed_files.append((Path(task[0]).name, str(e)))

            if progress_callback:
                progress_callback(task, done, total, success_count)

    cancelled = cancel_event.is_set() if cancel_event else False
    return success_count, failed_files, cancelled
