import customtkinter as ctk
import webbrowser

def enhance_button(btn):
    def on_enter(e):
        btn.configure(border_width=2)

    def on_leave(e):
        btn.configure(border_width=0)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def build_ui(app, config, functions):

    apply_safe = functions["apply_safe"]
    reset_only = functions["reset_only"]
    reset_dm = functions["reset_dm"]
    save_preset = functions["save_preset"]
    delete_preset = functions["delete_preset"]
    load_presets = functions["load_presets"]
    update_refresh = functions["update_refresh"]
    set_theme = functions["set_theme"]

    resolutions = functions["resolutions"]
    refresh_map = functions["refresh_map"]
    res_var = functions["res_var"]
    refresh_var = functions["refresh_var"]

    main = ctk.CTkFrame(app, corner_radius=20)
    main.pack(fill="both", expand=True, padx=20, pady=15)

    # LEFT
    preset_frame = ctk.CTkFrame(main, corner_radius=15)
    preset_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

    ctk.CTkLabel(preset_frame, text="Presets", font=("Segoe UI", 16, "bold")).pack(pady=10)

    preset_entry = ctk.CTkEntry(preset_frame, placeholder_text="Preset name")
    preset_entry.pack(pady=5, padx=10, fill="x")

    def save_and_refresh():
        name = preset_entry.get()
        if name:
            save_preset(name)
            refresh_presets()
            preset_entry.delete(0, "end")

    save_btn = ctk.CTkButton(preset_frame, text="Save", corner_radius=10, command=save_and_refresh)
    save_btn.pack(pady=5)
    enhance_button(save_btn)

    preset_list = ctk.CTkScrollableFrame(preset_frame)
    preset_list.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_presets():
        for w in preset_list.winfo_children():
            w.destroy()

        for name, val in load_presets().items():
            res, hz = val.split("@")

            row = ctk.CTkFrame(preset_list)
            row.pack(fill="x", pady=5)

            preset_btn = ctk.CTkButton(
                row,
                text=f"{name}\n{res}@{hz}",
                height=45,
                corner_radius=10,
                command=lambda r=res, h=hz: apply_safe(*r.split("x"), h)
            )
            preset_btn.pack(side="left", expand=True, fill="x")
            enhance_button(preset_btn)

            del_btn = ctk.CTkButton(
                row,
                text="X",
                width=30,
                fg_color="#b71c1c",
                hover_color="#7f0000",
                command=lambda n=name: [delete_preset(n), refresh_presets()]
            )
            del_btn.pack(side="right")
            enhance_button(del_btn)

    refresh_presets()

    # CENTER
    center = ctk.CTkFrame(main, corner_radius=15)
    center.pack(side="left", fill="both", expand=True, padx=12, pady=10)

    ctk.CTkLabel(center, text="Reset Options", font=("Segoe UI", 16, "bold")).pack(pady=10)

    reset_btn = ctk.CTkButton(
        center,
        text="RESET",
        height=80,
        corner_radius=14,
        font=("Segoe UI", 18, "bold"),
        fg_color="#d32f2f",
        hover_color="#b71c1c",
        command=reset_only
    )
    reset_btn.pack(pady=25, padx=20, fill="x")
    enhance_button(reset_btn)

    reset_dm_btn = ctk.CTkButton(
        center,
        text="Reset + Device Manager",
        height=40,
        corner_radius=10,
        command=reset_dm
    )
    reset_dm_btn.pack(pady=5, padx=40, fill="x")
    enhance_button(reset_dm_btn)

    # RIGHT
    right = ctk.CTkFrame(main, corner_radius=15)
    right.pack(side="right", fill="both", expand=True, padx=12, pady=10)

    ctk.CTkLabel(right, text="Custom", font=("Segoe UI", 16, "bold")).pack(pady=10)

    def on_res_change(choice):
        update_refresh(choice)
        refresh_menu.configure(values=refresh_map[choice])

    res_menu = ctk.CTkOptionMenu(right, values=resolutions, variable=res_var, command=on_res_change)
    res_menu.pack(pady=5)

    refresh_menu = ctk.CTkOptionMenu(right, values=refresh_map[resolutions[0]], variable=refresh_var)
    refresh_menu.pack(pady=5)

    apply_btn = ctk.CTkButton(
        right,
        text="Apply",
        height=40,
        corner_radius=10,
        command=lambda: apply_safe(*res_var.get().split("x"), refresh_var.get())
    )
    apply_btn.pack(pady=15, padx=30, fill="x")
    enhance_button(apply_btn)

    # FOOTER
    footer = ctk.CTkFrame(app)
    footer.pack(fill="x", side="bottom")

    left_footer = ctk.CTkFrame(footer, fg_color="transparent")
    left_footer.pack(side="left", padx=10)

    ctk.CTkLabel(left_footer, text="created by Devanksh Sarkar ~ ").pack(side="left")

    link = ctk.CTkLabel(left_footer, text="GitHub", text_color="#4da3ff", cursor="hand2")
    link.pack(side="left")
    link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Devanksh0147"))

    theme_menu = ctk.CTkOptionMenu(
        footer,
        values=["Light", "Dark", "System"],
        command=set_theme,
        width=120
    )
    theme_menu.pack(side="right", padx=10)

    theme_menu.set(config["SETTINGS"].get("theme", "System"))