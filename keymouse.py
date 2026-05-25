import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path

import pyautogui
import keyboard as kb
import mouse

CONFIG_DIR = Path(__file__).resolve().parent / "config"
MACROS_FILE = CONFIG_DIR / "macros.json"

os.makedirs(CONFIG_DIR, exist_ok=True)

pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True

def mouse_position():
    return pyautogui.position()

def mouse_position_str():
    x, y = pyautogui.position()
    return f"X: {x:>4}  Y: {y:>4}"

def click(x=None, y=None, button="left", clicks=1, interval=0.0):
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
    else:
        pyautogui.click(button=button, clicks=clicks, interval=interval)

def double_click(x=None, y=None):
    click(x, y, clicks=2, interval=0.1)

def right_click(x=None, y=None):
    click(x, y, button="right")

def drag(start_x, start_y, end_x, end_y, duration=0.3):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)

def scroll(clicks, x=None, y=None):
    pyautogui.scroll(clicks, x, y)

def move_to(x, y, duration=0.2):
    pyautogui.moveTo(x, y, duration=duration)

def type_text(text, interval=0.05):
    pyautogui.write(text, interval=interval)

def press_key(key, presses=1):
    for _ in range(presses):
        pyautogui.press(key)

def hotkey(*keys):
    pyautogui.hotkey(*keys)

def key_down(key):
    pyautogui.keyDown(key)

def key_up(key):
    pyautogui.keyUp(key)

def select_all_and_delete():
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")

def copy_selected():
    pyautogui.hotkey("ctrl", "c")

def paste():
    pyautogui.hotkey("ctrl", "v")

def screenshot(filename=None):
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{ts}.png"
    save_dir = Path(__file__).resolve().parent / "screenshots"
    os.makedirs(save_dir, exist_ok=True)
    path = str(save_dir / filename)
    pyautogui.screenshot(path)
    return path


class MacroRecorder(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.recorded = []
        self._stop_event = threading.Event()
        self._start_time = None
        self._listeners = []

    def start_recording(self):
        self.recorded = []
        self._start_time = time.time()
        self._stop_event.clear()
        self._listeners = []
        mouse.hook(self._on_mouse_event)
        kb.hook(self._on_kb_event)

    def stop_recording(self):
        self._stop_event.set()
        mouse.unhook(self._on_mouse_event)
        kb.unhook(self._on_kb_event)

    def _on_mouse_event(self, event):
        if self._stop_event.is_set():
            return
        elapsed = time.time() - self._start_time
        if isinstance(event, mouse.ButtonEvent):
            self.recorded.append({
                "type": "mouse",
                "event_type": event.event_type,
                "button": event.button,
                "x": event.x,
                "y": event.y,
                "time": round(elapsed, 3),
            })
        elif isinstance(event, mouse.MoveEvent):
            pass

    def _on_kb_event(self, event):
        if self._stop_event.is_set():
            return
        elapsed = time.time() - self._start_time
        self.recorded.append({
            "type": "keyboard",
            "event_type": event.event_type,
            "name": event.name,
            "scan_code": event.scan_code,
            "time": round(elapsed, 3),
        })

    def get_events(self):
        return self.recorded

    def clear(self):
        self.recorded = []


class MacroPlayer(threading.Thread):
    def __init__(self, events, speed=1.0, callback=None):
        super().__init__(daemon=True)
        self.events = events
        self.speed = speed
        self.callback = callback
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        if not self.events:
            return
        base_time = self.events[0]["time"]
        for i, event in enumerate(self.events):
            if self._stop_event.is_set():
                break
            if i > 0:
                delta = (event["time"] - self.events[i - 1]["time"]) / self.speed
                if delta > 0:
                    self._wait(delta)
            try:
                self._replay_event(event)
            except Exception:
                pass
        if self.callback:
            self.callback()

    def _wait(self, seconds):
        interval = 0.05
        elapsed = 0
        while elapsed < seconds:
            if self._stop_event.is_set():
                break
            time.sleep(interval)
            elapsed += interval

    @staticmethod
    def _replay_event(event):
        if event["type"] == "mouse":
            if event["event_type"] == "down":
                mouse.press(button=event["button"])
            elif event["event_type"] == "up":
                mouse.release(button=event["button"])
        elif event["type"] == "keyboard":
            if event["event_type"] == "down":
                kb.press(event["name"])
            elif event["event_type"] == "up":
                kb.release(event["name"])


def save_macro(name, events):
    macros = load_macros()
    macros.append({
        "name": name,
        "events": events,
        "created_at": datetime.now().isoformat(),
    })
    with open(MACROS_FILE, "w", encoding="utf-8") as f:
        json.dump(macros, f, ensure_ascii=False, indent=2)


def load_macros():
    if not MACROS_FILE.exists():
        return []
    try:
        with open(MACROS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def delete_macro(index):
    macros = load_macros()
    if 0 <= index < len(macros):
        macros.pop(index)
        with open(MACROS_FILE, "w", encoding="utf-8") as f:
            json.dump(macros, f, ensure_ascii=False, indent=2)


class AutoClicker(threading.Thread):
    def __init__(self, interval=0.1, button="left", clicks=1, x=None, y=None):
        super().__init__(daemon=True)
        self.interval = interval
        self.button = button
        self.clicks = clicks
        self.x = x
        self.y = y
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if self.x is not None and self.y is not None:
                pyautogui.click(self.x, self.y, button=self.button, clicks=self.clicks)
            else:
                pyautogui.click(button=self.button, clicks=self.clicks)
            time.sleep(self.interval)


_recorder = MacroRecorder()

def get_recorder():
    return _recorder
