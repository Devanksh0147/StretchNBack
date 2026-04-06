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

    apply_safe         = functions["apply_safe"]
    apply_safe_with_dm = functions["apply_safe_with_dm"]
    reset_only         = functions["reset_only"]
    reset_dm           = functions["reset_dm"]
    save_preset        = functions["save_preset"]
    delete_preset      = functions["delete_preset"]
    load_presets       = functions["load_presets"]
    update_refresh     = functions["update_refresh"]
    set_theme          = functions["set_theme"]
    app_version        = functions.get("app_version", "")

    resolutions  = functions["resolutions"]
    refresh_map  = functions["refresh_map"]
    res_var      = functions["res_var"]
    refresh_var  = functions["refresh_var"]

    # ── MAIN CONTAINER ───────────────────────────────────────────────────────────
    main = ctk.CTkFrame(app, corner_radius=20)
    main.pack(fill="both", expand=True, padx=20, pady=(15, 8))

    # configure 3 equal columns
    main.columnconfigure(0, weight=1, uniform="col")
    main.columnconfigure(1, weight=1, uniform="col")
    main.columnconfigure(2, weight=1, uniform="col")
    main.rowconfigure(0, weight=1)

    # ── LEFT — PRESETS ───────────────────────────────────────────────────────────
    preset_frame = ctk.CTkFrame(main, corner_radius=15)
    preset_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    ctk.CTkLabel(preset_frame, text="Presets", font=("Segoe UI", 16, "bold")).pack(pady=(12, 6))

    preset_entry = ctk.CTkEntry(preset_frame, placeholder_text="Preset name")
    preset_entry.pack(pady=4, padx=12, fill="x")

    def save_and_refresh():
        name = preset_entry.get().strip()
        if name:
            save_preset(name)
            refresh_presets()
            preset_entry.delete(0, "end")

    save_btn = ctk.CTkButton(
        preset_frame, text="Save Preset",
        corner_radius=10, height=34,
        command=save_and_refresh
    )
    save_btn.pack(pady=(4, 8), padx=12, fill="x")
    enhance_button(save_btn)

    preset_list = ctk.CTkScrollableFrame(preset_frame)
    preset_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_presets():
        for w in preset_list.winfo_children():
            w.destroy()

        for name, val in load_presets().items():
            res, hz = val.split("@")

            card = ctk.CTkFrame(preset_list, corner_radius=10)
            card.pack(fill="x", pady=4)

            ctk.CTkLabel(
                card,
                text=f"{name}",
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            ).pack(fill="x", padx=10, pady=(6, 0))

            ctk.CTkLabel(
                card,
                text=f"{res} @ {hz} Hz",
                font=("Segoe UI", 10),
                text_color=("gray40", "gray60"),
                anchor="w"
            ).pack(fill="x", padx=10, pady=(0, 4))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=8, pady=(0, 8))

            apply_btn = ctk.CTkButton(
                btn_row,
                text="▶ Apply",
                height=30,
                corner_radius=8,
                font=("Segoe UI", 11),
                command=lambda r=res, h=hz: apply_safe(*r.split("x"), h)
            )
            apply_btn.pack(side="left", expand=True, fill="x", padx=(0, 3))
            enhance_button(apply_btn)

            apply_dm_btn = ctk.CTkButton(
                btn_row,
                text="⚙ +DM",
                height=30,
                corner_radius=8,
                font=("Segoe UI", 11),
                fg_color="#37474F",
                hover_color="#263238",
                command=lambda r=res, h=hz: apply_safe_with_dm(*r.split("x"), h)
            )
            apply_dm_btn.pack(side="left", expand=True, fill="x", padx=(0, 3))
            enhance_button(apply_dm_btn)

            del_btn = ctk.CTkButton(
                btn_row,
                text="✕",
                width=30,
                height=30,
                corner_radius=8,
                fg_color="#b71c1c",
                hover_color="#7f0000",
                command=lambda n=name: [delete_preset(n), refresh_presets()]
            )
            del_btn.pack(side="right")
            enhance_button(del_btn)

    refresh_presets()

    # ── CENTER — RESET ───────────────────────────────────────────────────────────
    center = ctk.CTkFrame(main, corner_radius=15)
    center.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    ctk.CTkLabel(center, text="Reset Options", font=("Segoe UI", 16, "bold")).pack(pady=(12, 6))

    reset_btn = ctk.CTkButton(
        center,
        text="RESET",
        height=90,
        corner_radius=14,
        font=("Segoe UI", 20, "bold"),
        fg_color="#d32f2f",
        hover_color="#b71c1c",
        command=reset_only
    )
    reset_btn.pack(pady=20, padx=20, fill="x")
    enhance_button(reset_btn)

    reset_dm_btn = ctk.CTkButton(
        center,
        text="⚙  Reset + Device Manager",
        height=42,
        corner_radius=10,
        font=("Segoe UI", 12),
        command=reset_dm
    )
    reset_dm_btn.pack(pady=6, padx=20, fill="x")
    enhance_button(reset_dm_btn)

    # ── RIGHT — CUSTOM ───────────────────────────────────────────────────────────
    right = ctk.CTkFrame(main, corner_radius=15)
    right.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

    ctk.CTkLabel(right, text="Custom", font=("Segoe UI", 16, "bold")).pack(pady=(12, 6))

    def on_res_change(choice):
        update_refresh(choice)
        refresh_menu.configure(values=refresh_map[choice])

    res_menu = ctk.CTkOptionMenu(
        right, values=resolutions, variable=res_var,
        command=on_res_change, width=180
    )
    res_menu.pack(pady=(8, 4), padx=20)

    refresh_menu = ctk.CTkOptionMenu(
        right, values=refresh_map[resolutions[0]],
        variable=refresh_var, width=180
    )
    refresh_menu.pack(pady=4, padx=20)

    apply_btn = ctk.CTkButton(
        right,
        text="▶  Apply",
        height=40,
        corner_radius=10,
        font=("Segoe UI", 13),
        command=lambda: apply_safe(*res_var.get().split("x"), refresh_var.get())
    )
    apply_btn.pack(pady=(16, 4), padx=20, fill="x")
    enhance_button(apply_btn)

    apply_dm_btn = ctk.CTkButton(
        right,
        text="⚙  Apply + Device Manager",
        height=40,
        corner_radius=10,
        font=("Segoe UI", 12),
        fg_color="#37474F",
        hover_color="#263238",
        command=lambda: apply_safe_with_dm(*res_var.get().split("x"), refresh_var.get())
    )
    apply_dm_btn.pack(pady=(0, 16), padx=20, fill="x")
    enhance_button(apply_dm_btn)

    # ── FOOTER ───────────────────────────────────────────────────────────────────
    footer = ctk.CTkFrame(app, fg_color="transparent")
    footer.pack(fill="x", side="bottom", padx=20, pady=(0, 8))

    left_footer = ctk.CTkFrame(footer, fg_color="transparent")
    left_footer.pack(side="left")

    ctk.CTkLabel(left_footer, text="created by Devanksh Sarkar ~ ").pack(side="left")

    link = ctk.CTkLabel(left_footer, text="GitHub", text_color="#4da3ff", cursor="hand2")
    link.pack(side="left")
    link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Devanksh0147"))

    if app_version:
        ctk.CTkLabel(
            left_footer,
            text=f"  {app_version}",
            text_color=("gray50", "gray60")
        ).pack(side="left")

    theme_menu = ctk.CTkOptionMenu(
        footer,
        values=["Light", "Dark", "System"],
        command=set_theme,
        width=120
    )
    theme_menu.pack(side="right")
    theme_menu.set(config["SETTINGS"].get("theme", "System"))