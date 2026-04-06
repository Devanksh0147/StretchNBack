import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import customtkinter as ctk
    print("ctk ok")
    import win32api
    print("win32api ok")
    from ui import build_ui
    print("ui ok")
except Exception as e:
    print(f"FAILED: {e}")

input("press enter to close")