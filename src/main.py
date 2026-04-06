import os
import sys
import webbrowser
import customtkinter as ctk
import configparser
import win32api
import threading
import time
import ctypes
import urllib.request
import json

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


from ui import build_ui

# ---------------- VERSION ----------------

APP_VERSION = "v1.2.1"
GITHUB_API_URL = "https://api.github.com/repos/Devanksh0147/StretchNBack/releases/latest"

# ---------------- PATH ----------------

def get_qres():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "QRes.exe")

def get_icon():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "assets", "Icon.ico")

QRES = get_qres()

# ---------------- CONFIG ----------------

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

    ctk.CTkLabel(popup, text=f"Is {res} @ {hz} Hz your native resolution?").pack(pady=15)
    ctk.CTkLabel(popup, text=f"{res} @ {hz} Hz", font=("Segoe UI", 13, "bold")).pack(pady=5)
    ctk.CTkButton(popup, text="Yes", command=yes).pack(side="left", padx=40, pady=20)
    ctk.CTkButton(popup, text="No", command=no).pack(side="right", padx=40, pady=20)

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
        if popup.winfo_exists():
            popup.destroy()

    threading.Thread(target=timer, daemon=True).start()

def apply_safe(x, y, r):
    prev_res, prev_hz = get_current()
    apply_res(x, y, r)
    app.after(400, lambda: confirm_popup(prev_res, prev_hz))

def apply_safe_with_dm(x, y, r):
    """Opens Device Manager first, then applies the resolution safely."""
    os.system("start devmgmt.msc")
    apply_safe(x, y, r)

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
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

# ---------------- AUTO UPDATE ----------------

def check_for_update():
    """Fetch latest release tag from GitHub and notify user if newer version exists."""
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": "StretchNBack-UpdateChecker"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_tag = data.get("tag_name", "").strip()
            release_url = data.get("html_url", "https://github.com/Devanksh0147/StretchNBack/releases")

            if latest_tag and latest_tag != APP_VERSION:
                # Schedule UI update on main thread
                app.after(0, lambda: show_update_banner(latest_tag, release_url))
    except Exception:
        pass  # Silent fail — no internet or API issue, don't bother user

def show_update_banner(latest_tag, release_url):
    """Shows a non-blocking top banner informing user of a new version."""
    banner = ctk.CTkFrame(app, fg_color="#1565C0", corner_radius=0)
    banner.place(relx=0, rely=0, relwidth=1)

    inner = ctk.CTkFrame(banner, fg_color="transparent")
    inner.pack(pady=6)

    ctk.CTkLabel(
        inner,
        text=f"🔔  Update available: {latest_tag}  —  You have {APP_VERSION}",
        text_color="white",
        font=("Segoe UI", 12)
    ).pack(side="left", padx=10)

    def open_release():
        webbrowser.open(release_url)

    ctk.CTkButton(
        inner,
        text="Download",
        width=90,
        height=26,
        corner_radius=6,
        fg_color="#0D47A1",
        hover_color="#1976D2",
        text_color="white",
        command=open_release
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        inner,
        text="✕",
        width=26,
        height=26,
        corner_radius=6,
        fg_color="transparent",
        hover_color="#1976D2",
        text_color="white",
        command=banner.destroy
    ).pack(side="left", padx=2)

# ---------------- UI ----------------

ctk.set_appearance_mode(config["SETTINGS"].get("theme", "System"))

app = ctk.CTk()
app.title(f"StretchNBack - {APP_VERSION}")
app.resizable(False, False)

try:
    app.iconbitmap(get_icon())
except:
    pass

app.geometry("860x480")
app.resizable(False, False)

res_var = ctk.StringVar(value=resolutions[0])
refresh_var = ctk.StringVar(value=refresh_map[resolutions[0]][0])

# pass all functions to UI
functions = {
    "apply_safe": apply_safe,
    "apply_safe_with_dm": apply_safe_with_dm,
    "reset_only": reset_only,
    "set_theme": set_theme,
    "reset_dm": reset_dm,
    "save_preset": save_preset,
    "delete_preset": delete_preset,
    "load_presets": load_presets,
    "apply_custom": lambda: apply_safe(*res_var.get().split("x"), refresh_var.get()),
    "resolutions": resolutions,
    "refresh_map": refresh_map,
    "res_var": res_var,
    "refresh_var": refresh_var,
    "update_refresh": update_refresh,
    "app_version": APP_VERSION,
}

build_ui(app, config, functions)

ensure_native()
sync_ui()

# Run update check in background after UI is ready
threading.Thread(target=check_for_update, daemon=True).start()

app.mainloop()