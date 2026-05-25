import tkinter as tk
from tkinter import ttk, messagebox
import keymouse as km
import pyperclip


class KeymouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🖱️ 键鼠模拟工具")
        self.geometry("900x620")
        self.resizable(True, True)

        # ── Header ──
        header = tk.Canvas(self, height=42, bg="#2962ff", highlightthickness=0)
        header.pack(fill="x")
        header.create_text(16, 21, text="🖱️ 键鼠模拟 — 录制回放·自动点击·快捷键", fill="white",
                           font=("微软雅黑", 12, "bold"), anchor="w")

        main = ttk.Frame(self, padding=8)
        main.pack(fill="both", expand=True)

        paned = ttk.PanedWindow(main, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        # ── Left ──
        ttk.Label(left, text="宏录制 / 回放", font=("", 11, "bold")).pack(anchor="w", pady=(0, 4))

        self.btn_record = ttk.Button(left, text="🔴 开始录制", command=self._toggle_record)
        self.btn_record.pack(fill="x", pady=2)
        self.rec_status = ttk.Label(left, text="空闲", foreground="gray")
        self.rec_status.pack(anchor="w")

        ttk.Label(left, text="回放速度:").pack(anchor="w")
        self.play_speed = ttk.Scale(left, from_=0.1, to=5, value=1.0, orient="horizontal")
        self.play_speed.pack(fill="x", pady=2)
        self.speed_label = ttk.Label(left, text="1.0x")
        self.speed_label.pack(anchor="w")
        self.play_speed.configure(command=lambda v: self.speed_label.config(text=f"{float(v):.1f}x"))

        self.btn_play = ttk.Button(left, text="▶️ 回放录制", command=self._play_macro)
        self.btn_play.pack(fill="x", pady=2)
        self.btn_stop_play = ttk.Button(left, text="⏹ 停止回放", command=self._stop_play, state="disabled")
        self.btn_stop_play.pack(fill="x", pady=2)

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(left, text="保存 / 加载宏", font=("", 10, "bold")).pack(anchor="w")
        self.entry_macro_name = ttk.Entry(left)
        self.entry_macro_name.pack(fill="x", pady=2)
        self.entry_macro_name.insert(0, "我的宏")

        ttk.Button(left, text="💾 保存宏", command=self._save_macro).pack(fill="x", pady=2)

        self.macro_list = tk.Listbox(left, height=5)
        self.macro_list.pack(fill="x", pady=2)
        self.macro_list.bind("<<ListboxSelect>>", self._on_macro_select)
        ttk.Button(left, text="🗑 删除宏", command=self._del_macro).pack(fill="x", pady=2)
        self._refresh_macros()

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(left, text="自动点击器", font=("", 10, "bold")).pack(anchor="w")
        f_click = ttk.Frame(left)
        f_click.pack(fill="x")
        ttk.Label(f_click, text="间隔(秒):").pack(side="left")
        self.click_interval = ttk.Spinbox(f_click, from_=0.01, to=10, increment=0.01, width=8)
        self.click_interval.pack(side="left", padx=4)
        self.click_interval.insert(0, "0.1")
        self.btn_autoclick = ttk.Button(left, text="🖱 开始自动点击", command=self._toggle_autoclick)
        self.btn_autoclick.pack(fill="x", pady=2)

        # ── Right ──
        ttk.Label(right, text="鼠标信息", font=("", 11, "bold")).pack(anchor="w")
        self.mouse_pos_label = ttk.Label(right, text="X: 0  Y: 0", font=("Consolas", 14))
        self.mouse_pos_label.pack(anchor="w", pady=4)
        self._update_mouse_pos()

        ttk.Label(right, text="鼠标操作", font=("", 10, "bold")).pack(anchor="w")
        mf = ttk.Frame(right)
        mf.pack(fill="x", pady=4)
        ttk.Button(mf, text="单击", command=lambda: km.click()).pack(side="left", padx=2)
        ttk.Button(mf, text="双击", command=lambda: km.double_click()).pack(side="left", padx=2)
        ttk.Button(mf, text="右键", command=lambda: km.right_click()).pack(side="left", padx=2)
        ttk.Button(mf, text="滚动 ↑", command=lambda: km.scroll(3)).pack(side="left", padx=2)
        ttk.Button(mf, text="滚动 ↓", command=lambda: km.scroll(-3)).pack(side="left", padx=2)

        ttk.Label(right, text="键盘操作", font=("", 10, "bold")).pack(anchor="w")
        kf = ttk.Frame(right)
        kf.pack(fill="x", pady=4)
        ttk.Label(kf, text="输入文本:").pack(side="left")
        self.entry_type = ttk.Entry(kf)
        self.entry_type.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(kf, text="输入", command=lambda: km.type_text(self.entry_type.get())).pack(side="left")

        kf2 = ttk.Frame(right)
        kf2.pack(fill="x")
        ttk.Label(kf2, text="按键:").pack(side="left")
        self.entry_key = ttk.Entry(kf2, width=12)
        self.entry_key.pack(side="left", padx=4)
        self.entry_key.insert(0, "enter")
        ttk.Button(kf2, text="按下", command=lambda: km.press_key(self.entry_key.get())).pack(side="left", padx=2)
        ttk.Button(kf2, text="Ctrl+C", command=lambda: km.hotkey("ctrl", "c")).pack(side="left", padx=2)
        ttk.Button(kf2, text="Ctrl+V", command=lambda: km.hotkey("ctrl", "v")).pack(side="left", padx=2)

        ttk.Label(right, text="快捷操作", font=("", 10, "bold")).pack(anchor="w")
        sf = ttk.Frame(right)
        sf.pack(fill="x", pady=4)
        ttk.Button(sf, text="截图", command=self._take_screenshot).pack(side="left", padx=2)
        ttk.Button(sf, text="全选删除", command=km.select_all_and_delete).pack(side="left", padx=2)

        ttk.Label(right, text="事件列表", font=("", 10, "bold")).pack(anchor="w", pady=(8, 0))
        self.event_text = tk.Text(right, height=12)
        self.event_text.pack(fill="both", expand=True, pady=2)
        sb = ttk.Scrollbar(self.event_text, command=self.event_text.yview)
        sb.pack(side="right", fill="y")
        self.event_text.config(yscrollcommand=sb.set)

        self._recorder = km.get_recorder()
        self._auto_clicker = None
        self._macro_player = None

    def _update_mouse_pos(self):
        x, y = km.mouse_position()
        self.mouse_pos_label.config(text=f"X: {x:>4}  Y: {y:>4}")
        self.after(200, self._update_mouse_pos)

    def _toggle_record(self):
        if self._recorder and self._recorder.is_alive():
            self._recorder.stop_recording()
            self.btn_record.config(text="🔴 开始录制")
            count = len(self._recorder.get_events())
            self.rec_status.config(text=f"已停止 - 记录 {count} 个事件", foreground="blue")
            self._show_events()
        else:
            self._recorder = km.MacroRecorder()
            km._recorder = self._recorder
            self._recorder.start_recording()
            self.btn_record.config(text="⏹ 停止录制")
            self.rec_status.config(text="录制中...", foreground="red")
            self.event_text.delete("1.0", tk.END)

    def _show_events(self):
        self.event_text.delete("1.0", tk.END)
        for e in self._recorder.get_events()[:200]:
            line = f"[{e['time']:>6.2f}s] "
            if e["type"] == "mouse":
                line += f"鼠标 {e['event_type']} {e['button']} @({e['x']},{e['y']})"
            else:
                line += f"按键 {e['event_type']} {e['name']}"
            self.event_text.insert(tk.END, line + "\n")

    def _play_macro(self):
        events = self._recorder.get_events()
        if not events:
            messagebox.showinfo("提示", "没有录制的事件")
            return
        speed = self.play_speed.get()
        self._macro_player = km.MacroPlayer(events, speed=speed, callback=lambda: self.after(0, self._play_done))
        self._macro_player.start()
        self.btn_play.config(state="disabled")
        self.btn_stop_play.config(state="normal")

    def _stop_play(self):
        if self._macro_player and self._macro_player.is_alive():
            self._macro_player.stop()
        self._play_done()

    def _play_done(self):
        self.btn_play.config(state="normal")
        self.btn_stop_play.config(state="disabled")

    def _save_macro(self):
        name = self.entry_macro_name.get().strip()
        events = self._recorder.get_events()
        if not events:
            messagebox.showwarning("提示", "没有录制的事件可以保存")
            return
        if not name:
            name = f"宏_{len(km.load_macros()) + 1}"
        km.save_macro(name, events)
        self._refresh_macros()
        messagebox.showinfo("成功", f"宏「{name}」已保存")

    def _del_macro(self):
        sel = self.macro_list.curselection()
        if not sel:
            messagebox.showwarning("提示", "请先在宏列表中选择一项")
            return
        idx = sel[0]
        km.delete_macro(idx)
        self._refresh_macros()

    def _on_macro_select(self, event):
        sel = self.macro_list.curselection()
        if not sel:
            return
        idx = sel[0]
        macros = km.load_macros()
        if 0 <= idx < len(macros):
            self.entry_macro_name.delete(0, tk.END)
            self.entry_macro_name.insert(0, macros[idx]["name"])

    def _refresh_macros(self):
        self.macro_list.delete(0, tk.END)
        for m in km.load_macros():
            self.macro_list.insert(tk.END, m["name"])

    def _toggle_autoclick(self):
        if self._auto_clicker and self._auto_clicker.is_alive():
            self._auto_clicker.stop()
            self.btn_autoclick.config(text="🖱 开始自动点击")
        else:
            try:
                interval = float(self.click_interval.get())
            except ValueError:
                interval = 0.1
            self._auto_clicker = km.AutoClicker(interval=interval)
            self._auto_clicker.start()
            self.btn_autoclick.config(text="⏹ 停止自动点击")

    def _take_screenshot(self):
        path = km.screenshot()
        pyperclip.copy(path)
        messagebox.showinfo("截图", f"已保存: {path}\n路径已复制到剪贴板")


if __name__ == "__main__":
    app = KeymouseApp()
    app.mainloop()
