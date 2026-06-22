import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import json
import time
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import i18n
from converter import (
    check_ffmpeg, INPUT_EXTS, SUPPORTED_FORMATS,
    get_output_extension, _do_convert
)
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APP_DIR = get_app_dir()
CONFIG_FILE = os.path.join(APP_DIR, "config.json")


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.ffmpeg_available = check_ffmpeg()

        saved_lang = self.config.get("language", "auto")
        if saved_lang == "auto":
            i18n.init()
        else:
            i18n.init(saved_lang)

        win_w = self.config.get("window_width", 800)
        win_h = self.config.get("window_height", 700)
        self.geometry(f"{win_w}x{win_h}")
        self.minsize(700, 600)

        self.input_files = []
        self.output_dir = self.config.get("output_dir", "")
        if self.output_dir and not os.path.isdir(self.output_dir):
            self.output_dir = ""
        self.is_converting = False
        self.cancel_event = threading.Event()

        theme = self.config.get("theme", "system")
        mode_map = {"dark": "Dark", "light": "Light", "system": "System"}
        ctk.set_appearance_mode(mode_map.get(theme, "System"))

        self._build_ui()
        self._refresh_file_list()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if not self.ffmpeg_available:
            self.after(500, self._show_ffmpeg_warning)

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main = ctk.CTkScrollableFrame(self)
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(
            main, text=i18n.t("app.subtitle"),
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 15))

        # ── 顶栏 ──
        top = ctk.CTkFrame(main, fg_color="transparent")
        top.pack(fill="x", padx=5, pady=(0, 10))

        self.ffmpeg_label = ctk.CTkLabel(
            top,
            text=i18n.t("app.ffmpeg_ready") if self.ffmpeg_available else i18n.t("app.ffmpeg_missing"),
            text_color="#4CAF50" if self.ffmpeg_available else "#F44336",
            font=ctk.CTkFont(size=12)
        )
        self.ffmpeg_label.pack(side="left")

        ctk.CTkLabel(top, text=i18n.t("app.theme"), font=ctk.CTkFont(size=12)).pack(side="right", padx=(0, 5))
        self.theme_var = ctk.StringVar(value={
            "dark": "Dark", "light": "Light", "system": "System"
        }.get(self.config.get("theme", "system"), "System"))
        ctk.CTkOptionMenu(
            top, variable=self.theme_var,
            values=["Dark", "Light", "System"],
            command=self._on_theme_change, width=100
        ).pack(side="right")

        # ── 输入文件 ──
        inf = ctk.CTkFrame(main)
        inf.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(inf, text=i18n.t("app.input_files"),
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).pack(anchor="w", padx=15, pady=(10, 5))

        lf = ctk.CTkFrame(inf, fg_color="transparent")
        lf.pack(fill="x", padx=15, pady=(0, 5))

        self.file_text = ctk.CTkTextbox(lf, height=80, state="disabled")
        self.file_text.pack(side="left", fill="both", expand=True)

        bs = ctk.CTkFrame(lf, fg_color="transparent", width=60)
        bs.pack(side="right", fill="y", padx=(5, 0))
        bs.pack_propagate(False)

        self.delete_btn = ctk.CTkButton(
            bs, text=i18n.t("file.delete"), command=self._delete_selected,
            height=30, fg_color="#F44336", hover_color="#D32F2F",
            font=ctk.CTkFont(size=11), state="disabled"
        )
        self.delete_btn.pack(fill="x", pady=(0, 3))

        bf = ctk.CTkFrame(inf, fg_color="transparent")
        bf.pack(fill="x", padx=15, pady=(0, 10))

        self.select_file_btn = ctk.CTkButton(
            bf, text=i18n.t("app.select_files"), command=self._select_files, width=120
        )
        self.select_file_btn.pack(side="left", padx=(0, 8))

        self.select_folder_btn = ctk.CTkButton(
            bf, text=i18n.t("app.select_folder"), command=self._select_folder, width=120
        )
        self.select_folder_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            bf, text=i18n.t("app.clear_list"), command=self._clear_files, width=120,
            fg_color="gray", hover_color="darkgray"
        )
        self.clear_btn.pack(side="left")

        # ── 输出目录 ──
        outf = ctk.CTkFrame(main)
        outf.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(outf, text=i18n.t("app.output_dir"),
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).pack(anchor="w", padx=15, pady=(10, 5))

        df = ctk.CTkFrame(outf, fg_color="transparent")
        df.pack(fill="x", padx=15, pady=(0, 10))

        self.dir_entry = ctk.CTkEntry(
            df, placeholder_text=i18n.t("app.placeholder_dir"), state="readonly"
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.select_dir_btn = ctk.CTkButton(
            df, text=i18n.t("app.select_dir"), command=self._select_output_dir, width=100
        )
        self.select_dir_btn.pack(side="right")

        if self.output_dir:
            self._set_dir(self.output_dir)

        # ── 输出参数 ──
        pf = ctk.CTkFrame(main)
        pf.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(pf, text=i18n.t("app.output_params"),
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).pack(anchor="w", padx=15, pady=(10, 5))

        pi = ctk.CTkFrame(pf, fg_color="transparent")
        pi.pack(fill="x", padx=15, pady=(0, 10))

        # format
        ctk.CTkLabel(pi, text=i18n.t("app.output_format")).grid(
            row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        fmt_keys = ["wav", "mp3", "flac", "aac", "ogg", "m4a", "wma"]
        fmt_labels = [SUPPORTED_FORMATS[k]["name"].lstrip(".").upper() for k in fmt_keys]
        self._fmt_key_map = dict(zip(fmt_labels, fmt_keys))
        self.fmt_var = ctk.StringVar(value="WAV")
        self.fmt_menu = ctk.CTkOptionMenu(
            pi, values=fmt_labels, width=100, command=self._on_format_change
        )
        self.fmt_menu.grid(row=0, column=1, padx=(0, 15), pady=5)

        # sample rate
        ctk.CTkLabel(pi, text=i18n.t("app.sample_rate")).grid(
            row=0, column=2, padx=(0, 5), pady=5, sticky="w")
        self.sr_var = ctk.StringVar(value="44100")
        ctk.CTkOptionMenu(pi, variable=self.sr_var,
                          values=["22050", "44100", "48000", "96000"], width=100
                          ).grid(row=0, column=3, padx=(0, 15), pady=5)

        # bit depth
        ctk.CTkLabel(pi, text=i18n.t("app.bit_depth")).grid(
            row=0, column=4, padx=(0, 5), pady=5, sticky="w")
        self.bd_var = ctk.StringVar(value="16")
        self.bd_menu = ctk.CTkOptionMenu(pi, variable=self.bd_var,
                                         values=["16", "24", "32"], width=80)
        self.bd_menu.grid(row=0, column=5, padx=(0, 15), pady=5)

        # channels
        ctk.CTkLabel(pi, text=i18n.t("app.channels")).grid(
            row=0, column=6, padx=(0, 5), pady=5, sticky="w")
        self.ch_var = ctk.StringVar(value=i18n.t("app.channel_original"))
        ctk.CTkOptionMenu(pi, variable=self.ch_var,
                          values=[i18n.t("app.channel_original"),
                                  i18n.t("app.channel_mono"),
                                  i18n.t("app.channel_stereo")], width=90
                          ).grid(row=0, column=7, pady=5)

        # ── 进度 ──
        prf = ctk.CTkFrame(main)
        prf.pack(fill="x", pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(prf)
        self.progress_bar.pack(fill="x", padx=15, pady=(10, 5))
        self.progress_bar.set(0)

        sr2 = ctk.CTkFrame(prf, fg_color="transparent")
        sr2.pack(fill="x", padx=15, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            sr2, text=i18n.t("app.status_ready"), font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left")

        self.time_label = ctk.CTkLabel(
            sr2, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.time_label.pack(side="right")

        # ── 操作按钮 ──
        af = ctk.CTkFrame(main, fg_color="transparent")
        af.pack(fill="x", pady=(0, 5))

        self.convert_btn = ctk.CTkButton(
            af, text=i18n.t("app.convert"), command=self._start_conversion,
            height=40, font=ctk.CTkFont(size=16, weight="bold")
        )
        self.convert_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            af, text=i18n.t("app.cancel"), command=self._cancel_conversion,
            height=40, width=80, fg_color="#F44336", hover_color="#D32F2F",
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(0, 8))

        self.open_folder_btn = ctk.CTkButton(
            af, text=i18n.t("app.open_folder"), command=self._open_output_folder,
            height=40, width=130, fg_color="gray", hover_color="darkgray"
        )
        self.open_folder_btn.pack(side="left")

        # ── 署名 ──
        ctk.CTkLabel(main, text=i18n.t("app.about"),
                     font=ctk.CTkFont(size=11), text_color="gray"
                     ).pack(pady=(15, 5))

        self._on_format_change("WAV")

    # ── 界面回调 ────────────────────────────────────────

    def _on_theme_change(self, value):
        ctk.set_appearance_mode(value)
        key_map = {"Dark": "dark", "Light": "light", "System": "system"}
        self.config["theme"] = key_map.get(value, "system")
        save_config(self.config)

    def _on_format_change(self, value):
        fmt = self._fmt_key_map.get(value, "wav")
        if fmt == "wav":
            self.bd_menu.configure(state="normal")
        else:
            self.bd_menu.configure(state="disabled")

    def _on_close(self):
        self.config["window_width"] = self.winfo_width()
        self.config["window_height"] = self.winfo_height()
        if self.output_dir:
            self.config["output_dir"] = self.output_dir
        save_config(self.config)
        self.destroy()

    def _set_dir(self, path):
        self.dir_entry.configure(state="normal")
        self.dir_entry.delete(0, "end")
        self.dir_entry.insert(0, path)
        self.dir_entry.configure(state="readonly")

    def _update_title(self):
        c = len(self.input_files)
        t = i18n.t("app.title")
        if c > 0:
            t += f" - {i18n.t('app.file_count', count=c)}"
        self.title(t)

    # ── 文件操作 ────────────────────────────────────────

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title=i18n.t("app.select_files"),
            filetypes=[
                (i18n.t("app.subtitle"),
                 " ".join(f"*{e}" for e in INPUT_EXTS)),
                ("All files", "*.*")
            ]
        )
        if files:
            for f in files:
                if f not in self.input_files:
                    self.input_files.append(f)
            self._refresh_file_list()

    def _select_folder(self):
        folder = filedialog.askdirectory(title=i18n.t("app.select_folder"))
        if folder:
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(INPUT_EXTS):
                        full = os.path.join(root, f)
                        if full not in self.input_files:
                            self.input_files.append(full)
            self._refresh_file_list()

    def _refresh_file_list(self):
        self.file_text.configure(state="normal")
        self.file_text.delete("1.0", "end")
        if self.input_files:
            for f in self.input_files:
                p = Path(f)
                try:
                    sz = p.stat().st_size
                    sz_str = self._fmt_size(sz)
                except Exception:
                    sz_str = i18n.t("file.no_info")
                self.file_text.insert("end", f"{p.name}  ({sz_str})\n")
            self.file_text.insert(
                "end",
                f"\n{i18n.t('app.file_count', count=len(self.input_files))}"
            )
        else:
            self.file_text.insert("end", i18n.t("app.placeholder_filelist"))
        self.file_text.configure(state="disabled")
        self.delete_btn.configure(
            state="normal" if self.input_files else "disabled")
        self._update_title()

    def _delete_selected(self):
        try:
            idx = self.file_text.index("insert")
            line = int(idx.split(".")[0])
            if 1 <= line <= len(self.input_files):
                name = Path(self.input_files[line - 1]).name
                if messagebox.askyesno(
                    i18n.t("file.delete"),
                    i18n.t("file.delete_confirm", name=name)
                ):
                    self.input_files.pop(line - 1)
                    self._refresh_file_list()
        except Exception:
            if self.input_files:
                self.input_files.pop()
                self._refresh_file_list()

    def _clear_files(self):
        self.input_files = []
        self._refresh_file_list()

    def _select_output_dir(self):
        d = filedialog.askdirectory(title=i18n.t("app.select_dir"))
        if d:
            self.output_dir = d
            self._set_dir(d)

    @staticmethod
    def _fmt_size(b):
        for u in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"

    # ── ffmpeg ──────────────────────────────────────────

    def _show_ffmpeg_warning(self):
        messagebox.showwarning(
            i18n.t("warning.ffmpeg_title"),
            i18n.t("warning.ffmpeg_msg")
        )

    # ── 转换 ────────────────────────────────────────────

    def _start_conversion(self):
        if not self.ffmpeg_available:
            self._show_ffmpeg_warning()
            return
        if not self.input_files:
            messagebox.showwarning(
                i18n.t("warning.no_files"),
                i18n.t("warning.no_files_msg"))
            return
        if not self.output_dir:
            messagebox.showwarning(
                i18n.t("warning.no_output"),
                i18n.t("warning.no_output_msg"))
            return
        if self.is_converting:
            return

        self.config["output_dir"] = self.output_dir
        save_config(self.config)

        self._set_ui_busy(True)
        self.is_converting = True
        self.cancel_event.clear()
        self._start_time = time.time()
        threading.Thread(target=self._convert_worker, daemon=True).start()

    def _cancel_conversion(self):
        self.cancel_event.set()
        self.status_label.configure(text=i18n.t("app.cancelling"))

    def _set_ui_busy(self, busy):
        state_n = "disabled" if busy else "normal"
        state_c = "normal" if busy else "disabled"
        self.convert_btn.configure(
            state=state_n,
            text=i18n.t("app.converting") if busy else i18n.t("app.convert"))
        self.cancel_btn.configure(state=state_c)
        self.select_file_btn.configure(state=state_n)
        self.select_folder_btn.configure(state=state_n)
        self.clear_btn.configure(state=state_n)
        self.select_dir_btn.configure(state=state_n)
        if busy:
            self.progress_bar.set(0)
            self.time_label.configure(text="")

    def _convert_worker(self):
        total = len(self.input_files)
        fmt_label = self.fmt_menu.get()
        fmt = self._fmt_key_map.get(fmt_label, "wav")
        sr = self.sr_var.get()
        bd = self.bd_var.get()
        ch = self.ch_var.get()

        params = {
            "sample_rate": sr,
            "output_format": fmt,
            "bit_depth": bd,
            "channels": ch,
        }

        ext = get_output_extension(fmt)
        tasks = []
        for f in self.input_files:
            out = os.path.join(self.output_dir, Path(f).stem + ext)
            tasks.append((f, out, params))

        total = len(tasks)
        success_count = 0
        failed_files = []

        def _progress(task, done, total, success):
            name = Path(task[0]).name
            self._safe_status(
                i18n.t("app.completed", name=name, done=done, total=total))
            self._safe_progress(done / total)

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_map = {
                executor.submit(_do_convert, task): task
                for task in tasks
            }
            done = 0
            for future in as_completed(future_map):
                if self.cancel_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                task = future_map[future]
                name = Path(task[0]).name
                done += 1
                try:
                    future.result()
                    success_count += 1
                except Exception as e:
                    failed_files.append((name, str(e)))
                self._safe_status(
                    i18n.t("app.completed", name=name, done=done, total=total))
                self._safe_progress(done / total)

        elapsed = time.time() - self._start_time
        m, s = divmod(int(elapsed), 60)
        is_zh = i18n.get_lang() == "zh_CN"
        ts = f"{m}{'分' if is_zh else 'm'}{s}{'秒' if is_zh else 's'}" if m else f"{s}{'秒' if is_zh else 's'}"

        if self.cancel_event.is_set():
            self._safe_status(
                i18n.t("app.cancelled", success=success_count, total=total))
            self._safe_time(i18n.t("app.time_elapsed", time=ts))
        else:
            self._safe_progress(1.0)
            self._safe_status(
                i18n.t("app.finished", success=success_count, total=total))
            self._safe_time(i18n.t("app.time_elapsed", time=ts))

            if failed_files:
                details = "\n".join(f"{n}: {e[:100]}" for n, e in failed_files)
                self.after(100, lambda: messagebox.showwarning(
                    i18n.t("error.title"),
                    i18n.t("error.msg", details=details)))
            else:
                self.after(100, lambda: messagebox.showinfo(
                    i18n.t("success.title"),
                    i18n.t("success.msg", total=total, time=ts)))

        self.is_converting = False
        self._set_ui_busy(False)

    def _open_output_folder(self):
        if self.output_dir and os.path.isdir(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showinfo(
                i18n.t("app.open_folder"),
                i18n.t("app.placeholder_dir"))

    def _safe_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))

    def _safe_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value))

    def _safe_time(self, text):
        self.after(0, lambda: self.time_label.configure(text=text))
