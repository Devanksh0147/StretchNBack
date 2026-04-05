import os
import sys
import webbrowser
import customtkinter as ctk
import configparser
import win32api
import threading
import time
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()


from src.ui import build_ui

# ---------------- PATH ----------------

def get_qres():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, "QRes.exe")

def get_icon():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        return os.path.join(os.path.dirname(__file__), "assets", "Icon.ico")

QRES = get_qres()

# ---------------- CONFIG ----------------

def set_theme(mode):
    ctk.set_appearance_mode(mode)
    config["SETTINGS"] = {"theme": "System", "native_res": "", "native_hz": ""}
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()

if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)
else:
    config["SETTINGS"] = {"theme": "System", "native_res": "", "native_hz": ""}
    config["PRESETS"] = {}
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

if "PRESETS" not in config:
    config["PRESETS"] = {}

# ---------------- DISPLAY ----------------

def get_current():
    m = win32api.EnumDisplaySettings(None, -1)
    return f"{m.PelsWidth}x{m.PelsHeight}", str(m.DisplayFrequency)

def get_modes():
    modes = []
    i = 0
    while True:
        try:
            m = win32api.EnumDisplaySettings(None, i)
            modes.append((f"{m.PelsWidth}x{m.PelsHeight}", str(m.DisplayFrequency)))
            i += 1
        except:
            break
    return modes

def process_modes():
    res_set = set()
    refresh_map = {}

    for r, h in get_modes():
        res_set.add(r)
        refresh_map.setdefault(r, set()).add(h)

    res_list = sorted(res_set, key=lambda x: int(x.split("x")[0]), reverse=True)

    for k in refresh_map:
        refresh_map[k] = sorted(refresh_map[k], key=int, reverse=True)

    return res_list, refresh_map

resolutions, refresh_map = process_modes()

# ---------------- CORE ----------------

def apply_res(x, y, r):
    os.system(f'"{QRES}" /x:{x} /y:{y} /r:{r}')

def sync_ui():
    res, hz = get_current()
    if res in resolutions:
        res_var.set(res)
        refresh_var.set(hz)

# ---------------- FIRST TIME SETUP ----------------

def manual_native_popup():
    popup = ctk.CTkToplevel(app)
    popup.geometry("360x260")
    popup.grab_set()
    popup.attributes("-topmost", True)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    res_var_setup = ctk.StringVar(value=resolutions[0])
    hz_var_setup = ctk.StringVar()

    def save_native():
        config["SETTINGS"]["native_res"] = res_var_setup.get()
        config["SETTINGS"]["native_hz"] = hz_var_setup.get()

        with open(CONFIG_FILE, "w") as f:
            config.write(f)

        popup.destroy()

    ctk.CTkOptionMenu(popup, values=resolutions, variable=res_var_setup).pack(pady=10)
    ctk.CTkOptionMenu(popup, values=refresh_map[resolutions[0]], variable=hz_var_setup).pack(pady=10)
    ctk.CTkButton(popup, text="Save", command=save_native).pack(pady=10)

def ask_native_popup(res, hz):
    popup = ctk.CTkToplevel(app)
    popup.geometry("360x220")
    popup.grab_set()
    popup.attributes("-topmost", True)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    def yes():
        config["SETTINGS"]["native_res"] = res
        config["SETTINGS"]["native_hz"] = hz
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
        popup.destroy()

    def no():
        popup.destroy()
        app.after(100, manual_native_popup)

    ctk.CTkLabel(popup, text=f"{res} @ {hz} Hz").pack(pady=10)
    ctk.CTkButton(popup, text="Yes", command=yes).pack(side="left", padx=20)
    ctk.CTkButton(popup, text="No", command=no).pack(side="right", padx=20)

def ensure_native():
    res = config["SETTINGS"].get("native_res", "").strip()
    hz = config["SETTINGS"].get("native_hz", "").strip()

    if res and hz:
        return

    r, h = get_current()
    ask_native_popup(r, h)

# ---------------- SAFE APPLY ----------------

def update_refresh(res):
    if res in refresh_map:
        refresh_var.set(refresh_map[res][0])

def confirm_popup(prev_res, prev_hz):
    popup = ctk.CTkToplevel(app)
    popup.geometry("300x150")
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)

    state = {"done": False}

    def keep():
        state["done"] = True
        popup.destroy()

    def revert():
        state["done"] = True
        x, y = prev_res.split("x")
        apply_res(x, y, prev_hz)
        popup.destroy()

    ctk.CTkLabel(popup, text="Confirm Resolution").pack(pady=10)
    ctk.CTkButton(popup, text="Keep", command=keep).pack(side="left", padx=10)
    ctk.CTkButton(popup, text="Revert", command=revert).pack(side="right", padx=10)

    def timer():
        time.sleep(15)
        if not state["done"]:
            x, y = prev_res.split("x")
            apply_res(x, y, prev_hz)
        popup.destroy()

    threading.Thread(target=timer, daemon=True).start()

def apply_safe(x, y, r):
    prev_res, prev_hz = get_current()
    apply_res(x, y, r)
    app.after(400, lambda: confirm_popup(prev_res, prev_hz))

# ---------------- RESET ----------------

def reset_only():
    ensure_native()
    res = config["SETTINGS"]["native_res"]
    hz = config["SETTINGS"]["native_hz"]

    x, y = res.split("x")
    apply_res(x, y, hz)

def reset_dm():
    reset_only()
    os.system("start devmgmt.msc")

# ---------------- PRESETS ----------------

def save_preset(name):
    if not name:
        return
    config["PRESETS"][name] = f"{res_var.get()}@{refresh_var.get()}"
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def delete_preset(name):
    if name in config["PRESETS"]:
        del config["PRESETS"][name]
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

def load_presets():
    return config["PRESETS"]

# ---------------- THEME ----------------

def set_theme(mode):
    ctk.set_appearance_mode(mode)
    config["SETTINGS"]["theme"] = mode
    with open("config.ini", "w") as f:
        config.write(f)

# ---------------- UI ----------------

ctk.set_appearance_mode(config["SETTINGS"].get("theme", "System"))

app = ctk.CTk()
app.title("StretchNBack - v1.0.0")
app.resizable(False, False)

try:
    app.iconbitmap(get_icon())
except:
    pass

app.geometry("720x480")
app.resizable(False, False)

res_var = ctk.StringVar(value=resolutions[0])
refresh_var = ctk.StringVar(value=refresh_map[resolutions[0]][0])

# pass all functions to UI
functions = {
    "apply_safe": apply_safe,
    "reset_only": reset_only,
    "set_theme": set_theme,
    "reset_dm": reset_dm,
    "save_preset": save_preset,
    "delete_preset": delete_preset,
    "load_presets": load_presets,
    "apply_custom": lambda: apply_safe(*res_var.get().split("x"), refresh_var.get()),
    "set_theme": set_theme,
    "resolutions": resolutions,
    "refresh_map": refresh_map,
    "res_var": res_var,
    "refresh_var": refresh_var,
    "update_refresh": update_refresh   # ✅ THIS WAS MISSING
}

build_ui(app, config, functions)

ensure_native()
sync_ui()

app.mainloop()