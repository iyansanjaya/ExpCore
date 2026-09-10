"""The local desktop workspace. Tk widgets are only accessed on the UI thread."""

import os
import queue
import threading
import logging
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from expcore_updates import APP_VERSION, UpdateChecker, UpdateResult


class Workspace(ctk.CTk):
    C = {
        "bg": "#f4f4f5", "surface": "#ffffff", "surface_hover": "#ececee",
        "border": "#e4e4e7", "border_focus": "#71717a", "accent": "#09090b",
        "accent_hover": "#27272a", "text": "#09090b", "text_sub": "#52525b",
        "text_muted": "#71717a", "orange": "#ff5a00", "dark": "#18181b",
    }
    MODULES = {
        "bupot": {
            "title": "Bukti Potong 2026", "tag": "CORETAX", "number": "01",
            "description": "Dari bukti potong ke rekap Excel yang siap digunakan.",
            "detail": "Formulir BPPU · Nomor bukti, identitas, DPP & PPh",
            "hint": "Gunakan PDF Bukti Potong berformat BPPU dari Coretax.",
            "output": "!Hasil_Rekap_Bupot.xlsx", "method": "process_bupot",
        },
        "bupot2024": {
            "title": "Bukti Potong 2024", "tag": "PRA-CORETAX", "number": "02",
            "description": "Rapikan bukti potong lama dalam satu rekap terstruktur.",
            "detail": "Formulir BPBS · Identitas, objek pajak & pemotong",
            "hint": "Gunakan PDF formulir BPBS (pra-Coretax), dengan bagian H.1–H.5.",
            "output": "!Hasil_Rekap_Bupot_2024.xlsx", "method": "process_bupot_2024",
        },
        "pm": {
            "title": "Pajak Masukan", "tag": "FAKTUR PAJAK", "number": "03",
            "description": "Satukan rincian faktur pajak, tanpa menyalin satu per satu.",
            "detail": "Faktur PDF · Pembeli, barang, DPP, PPN & netto",
            "hint": "Gunakan faktur dengan teks yang dapat diseleksi. Perhitungan PPN pada modul ini menggunakan tarif tetap 12%.",
            "output": "Hasil_Pajak_Masukan.xlsx", "method": "process_pm",
        },
        "rename": {
            "title": "Penamaan Bupot", "tag": "PENGELOLAAN PDF", "number": "04",
            "description": "Nama file yang konsisten. Dokumen lebih mudah ditemukan.",
            "detail": "BPPU Coretax · Pratinjau nama & log audit CSV",
            "hint": "Nama memakai pemotong/pemungut (C.3). Periksa pratinjau sebelum menerapkan; PDF dengan data tidak lengkap dilewati.",
            "output": "Log penamaan .csv", "method": "process_rename_bupot",
        },
    }

    def __init__(self, *, check_updates=True):
        ctk.set_appearance_mode("light")
        super().__init__()
        self.title(f"ExpCore {APP_VERSION} — Toolkit PDF Coretax")
        scale = self._get_window_scaling()
        width = max(960, min(1180, int(self.winfo_screenwidth() / scale) - 80))
        height = max(620, min(800, int(self.winfo_screenheight() / scale) - 100))
        self.geometry(f"{width}x{height}")
        self.minsize(960, 620)
        self.configure(fg_color=self.C["bg"])
        self._events = queue.Queue()
        self._busy = None
        self._current = "home"
        self._closing = False
        self._views = {}
        self._scrolls = {}
        self._folders = {key: ctk.StringVar(self, value="") for key in self.MODULES}
        self._outputs = {}
        self._preview_folder = None
        self._update_checker = UpdateChecker()
        self._update_checking = False
        self._available_update = None
        self._auto_update_id = None
        self._build()
        self._navigate("home")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Control-o>", lambda e: self._browse(self._current) if self._current in self.MODULES else None)
        for index, key in enumerate(("home", *self.MODULES)):
            self.bind(f"<Alt-Key-{index}>", lambda e, k=key: self._navigate(k))
        for sequence, direction in (("<Next>", 1), ("<Prior>", -1)):
            self.bind(sequence, lambda e, d=direction: self._scroll_page_key(e, d))
        self._poll_id = self.after(60, self._drain_events)
        self._set_icon()
        if check_updates:
            self._auto_update_id = self.after(1800, self._start_update_check)

    def _set_icon(self):
        # Keep the existing packaged app identity and icon.
        import sys
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iyansanjaya.expcore.1.0")
        except (AttributeError, OSError):
            pass
        base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
        ico = os.path.join(base, "icon.ico")
        if os.path.exists(ico):
            self.iconbitmap(ico)

    def _font(self, size=14, bold=False):
        return ctk.CTkFont(family="Segoe UI", size=size, weight="bold" if bold else "normal")

    def _label(self, parent, text, size=14, bold=False, color=None, **kwargs):
        return ctk.CTkLabel(parent, text=text, font=self._font(size, bold),
                            text_color=color or self.C["text"], **kwargs)

    def _button(self, parent, text, command, primary=False, **kwargs):
        btn = ctk.CTkButton(
            parent, text=text, command=command, height=42, corner_radius=14,
            font=self._font(14, True), border_width=2,
            border_color=self.C["accent"] if primary else self.C["border"],
            fg_color=self.C["accent"] if primary else self.C["surface"],
            hover_color=self.C["accent_hover"] if primary else self.C["surface_hover"],
            text_color="white" if primary else self.C["text"],
            text_color_disabled="#a1a1aa", **kwargs,
        )
        # CTkButton does not provide keyboard activation by default.
        btn._canvas.configure(takefocus=1)
        btn._canvas.bind("<Return>", lambda e: btn.invoke())
        btn._canvas.bind("<space>", lambda e: btn.invoke())
        btn._resting_border = self.C["accent"] if primary else self.C["border"]
        def focus_button(event):
            btn.configure(border_color=self.C["orange"])
            self._reveal_control(btn)
        btn._canvas.bind("<FocusIn>", focus_button)
        btn._canvas.bind("<FocusOut>", lambda e: btn.configure(border_color=btn._resting_border))
        return btn

    def _scroll_page_key(self, event, direction):
        # Preserve native text selection/navigation when an editor has focus.
        if event.widget.winfo_class() not in ("Entry", "Text"):
            self._scrolls[self._current]._parent_canvas.yview_scroll(direction, "pages")
            return "break"

    def _scroll_log_edge(self, event, key):
        """Let the page continue scrolling when the log reaches either end."""
        first, last = self._views[key]["log"].yview()
        if event.delta and ((event.delta > 0 and first <= 0) or (event.delta < 0 and last >= 0.999)):
            pixels = -int(event.delta / 6) or (-1 if event.delta > 0 else 1)
            self._scrolls[key]._parent_canvas.yview_scroll(pixels, "units")
            return "break"

    def _reveal_control(self, widget):
        parent = widget.master
        while parent is not None and not isinstance(parent, ctk.CTkScrollableFrame):
            parent = parent.master
        if parent is None:
            return
        canvas = parent._parent_canvas
        top = widget.winfo_rooty() - canvas.winfo_rooty()
        bottom = top + widget.winfo_height()
        delta = top - 12 if top < 0 else max(0, bottom - canvas.winfo_height() + 12)
        bounds = canvas.bbox("all")
        if delta and bounds and bounds[3] > bounds[1]:
            canvas.yview_moveto(canvas.yview()[0] + delta / (bounds[3] - bounds[1]))

    def _card(self, parent, dark=False):
        return ctk.CTkFrame(parent, corner_radius=28, border_width=1,
                            border_color=self.C["dark"] if dark else self.C["border"],
                            fg_color=self.C["dark"] if dark else self.C["surface"])

    def _badge(self, parent, text, orange=False):
        return self._label(parent, text, 11, True,
                           color=self.C["text"] if orange else self.C["text_sub"],
                           fg_color=self.C["orange"] if orange else self.C["bg"],
                           corner_radius=10, height=26, padx=12)

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="white")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(9, weight=1)
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=24, pady=(32, 28), sticky="ew")
        self._label(brand, "e", 26, True, color="white", fg_color=self.C["accent"],
                    corner_radius=14, width=42, height=42).pack(side="left", padx=(0, 10))
        self._label(brand, "ExpCore", 24, True).pack(side="left")
        self._label(self.sidebar, "RUANG KERJA", 10, True, self.C["text_muted"]).grid(
            row=1, column=0, padx=26, pady=(8, 10), sticky="w")
        self.nav = {}
        self.nav["home"] = self._button(self.sidebar, "Beranda", lambda: self._navigate("home"), anchor="w")
        self.nav["home"].grid(row=2, column=0, padx=16, pady=3, sticky="ew")
        self._label(self.sidebar, "TOOLKIT DOKUMEN", 10, True, self.C["text_muted"]).grid(
            row=3, column=0, padx=26, pady=(26, 10), sticky="w")
        for row, (key, info) in enumerate(self.MODULES.items(), 4):
            self.nav[key] = self._button(self.sidebar, info["title"], lambda k=key: self._navigate(k), anchor="w")
            self.nav[key].grid(row=row, column=0, padx=16, pady=3, sticky="ew")
        note = ctk.CTkFrame(self.sidebar, fg_color=self.C["bg"], corner_radius=20)
        note.grid(row=10, column=0, padx=18, pady=16, sticky="ew")
        self._label(note, "Tetap di perangkat Anda.", 12, True).pack(anchor="w", padx=16, pady=(16, 3))
        self._label(note, "PDF diproses secara lokal.\nTanpa unggah, tanpa akun.", 12,
                    color=self.C["text_sub"], justify="left").pack(anchor="w", padx=16, pady=(0, 16))
        self._label(self.sidebar, f"v{APP_VERSION}   /   by Iyan Sanjaya", 11, color=self.C["text_muted"]).grid(
            row=11, column=0, padx=24, pady=(0, 24), sticky="w")

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(self.content, fg_color="transparent", height=66)
        top.grid(row=0, column=0, padx=32, sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        self.breadcrumb = self._label(top, "Ruang kerja  /  Beranda", 12, color=self.C["text_sub"])
        self.breadcrumb.grid(row=0, column=0, sticky="w", pady=20)
        self.update_check_button = self._button(top, "Periksa update", lambda: self._start_update_check(True),
                                                width=144)
        self.update_check_button.grid(row=0, column=1, padx=(8, 12))
        self._badge(top, "●  LOKAL & PRIVAT").grid(row=0, column=2, sticky="e")
        self.update_banner = ctk.CTkFrame(self.content, fg_color="white", corner_radius=16,
                                         border_width=1, border_color=self.C["border"])
        self.update_banner.grid_columnconfigure(0, weight=1)
        self.update_notice = self._label(self.update_banner, "", 13, True, justify="left", anchor="w")
        self.update_notice.grid(row=0, column=0, padx=16, pady=12, sticky="ew")
        self.update_banner.bind("<Configure>", lambda e: self.update_notice.configure(
            wraplength=max(150, self.update_banner._reverse_widget_scaling(e.width) - 300)), add="+")
        self.update_download = self._button(self.update_banner, "Unduh update", self._open_update, primary=True, width=130)
        self.update_download.grid(row=0, column=1, padx=(0, 8), pady=12)
        self.update_later = self._button(self.update_banner, "Nanti", self.update_banner.grid_remove, width=70)
        self.update_later.grid(row=0, column=2, padx=(0, 16), pady=12)
        self.pages = {}
        self._build_home()
        for key in self.MODULES:
            self._build_workspace(key)

    def _page(self, key):
        page = ctk.CTkFrame(self.content, fg_color="transparent", corner_radius=0)
        page.grid_columnconfigure(0, weight=1)
        self.pages[key] = page
        return page

    def _build_home(self):
        outer = self._page("home")
        outer.grid_rowconfigure(0, weight=1)
        page = ctk.CTkScrollableFrame(outer, fg_color="transparent", corner_radius=0,
                                      scrollbar_fg_color="#e4e4e7",
                                      scrollbar_button_color="#71717a", scrollbar_button_hover_color="#52525b")
        self._scrolls["home"] = page
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        hero = ctk.CTkFrame(page, fg_color="transparent")
        hero.grid(row=0, column=0, sticky="ew", pady=(6, 24))
        hero.grid_columnconfigure(0, weight=1)
        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nw")
        self._badge(left, "SEDIKIT KLIK. LEBIH RAPI.", True).pack(anchor="w", pady=(0, 14))
        self.hero_title = self._label(left, "Dokumen pajak.\nBeres, lebih cepat.", 43, True, justify="left")
        self.hero_title.pack(anchor="w")
        self._label(left, "Ekstrak, rekap, dan rapikan PDF Anda.\nSatu ruang kerja untuk pekerjaan yang lebih ringan.",
                    14, color=self.C["text_sub"], justify="left").pack(anchor="w", pady=(14, 0))
        guide = self._card(hero, dark=True)
        guide.grid(row=0, column=1, sticky="nse", padx=(20, 0))
        self._label(guide, "Alur sederhana.", 20, True, "white").grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))
        steps = []
        for number, text in (("01", "Pilih alat"), ("02", "Pilih folder PDF"), ("03", "Proses & buka hasil")):
            step = self._label(guide, f"{number}    {text}", 13, color="#e4e4e7")
            step.grid(row=len(steps) + 1, column=0, sticky="w", padx=20, pady=5)
            steps.append(step)
        guide_footer = self._label(guide, "PDF  →  pekerjaan selesai", 12, color="#a1a1aa")
        guide_footer.grid(row=4, column=0, columnspan=3, sticky="w", padx=20, pady=(12, 20))

        heading = ctk.CTkFrame(page, fg_color="transparent")
        heading.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self._label(heading, "Mulai dari sini", 22, True).pack(side="left")
        self._label(heading, "4 alat. Satu alur yang rapi.", 12, color=self.C["text_muted"]).pack(side="right")
        cards = ctk.CTkFrame(page, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="nsew")
        cards.grid_columnconfigure((0, 1), weight=1, uniform="tools")
        cards.grid_rowconfigure((0, 1), weight=1, uniform="tools", minsize=208)
        self._home_cards = []
        for index, (key, info) in enumerate(self.MODULES.items()):
            card = self._card(cards)
            self._home_cards.append(card)
            card.grid(row=index // 2, column=index % 2, sticky="nsew",
                      padx=(0, 8) if index % 2 == 0 else (8, 0),
                      pady=(0, 8) if index < 2 else (8, 0))
            card.grid_columnconfigure(0, weight=1)
            self._badge(card, info["tag"]).grid(row=0, column=0, padx=22, pady=(20, 8), sticky="w")
            self._label(card, info["number"], 12, color=self.C["text_muted"]).grid(row=0, column=1, padx=22, pady=(20, 8))
            self._label(card, info["title"], 20, True).grid(row=1, column=0, columnspan=2, padx=22, sticky="w")
            detail = self._label(card, info["detail"], 13, color=self.C["text_sub"], anchor="w", justify="left")
            detail.grid(row=2, column=0, columnspan=2, padx=22, pady=(2, 8), sticky="ew")
            card.bind("<Configure>", lambda e, lbl=detail, c=card: lbl.configure(wraplength=max(150, c._reverse_widget_scaling(e.width) - 48)))
            card.grid_rowconfigure(2, weight=1)
            self._button(card, "Buka alat  ↗", lambda k=key: self._navigate(k), width=128).grid(
                row=3, column=0, columnspan=2, padx=22, pady=(0, 20), sticky="w")
        self._label(page, "Dibuat untuk dokumen Anda. Dirancang untuk waktu Anda.", 11,
                    color=self.C["text_muted"]).grid(row=3, column=0, pady=(20, 0), sticky="w")
        def resize_home(event):
            width = page._reverse_widget_scaling(event.width)
            self.hero_title.cget("font").configure(size=34 if width < 840 else 40)
            if width < 690:
                guide.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=(20, 0))
                guide.grid_columnconfigure((0, 1, 2), weight=1)
                for index, step in enumerate(steps):
                    step.grid(row=1, column=index, padx=16, pady=(0, 20))
                guide_footer.grid_remove()
            else:
                guide.grid(row=0, column=1, columnspan=1, sticky="nse", padx=(20, 0), pady=0)
                guide.grid_columnconfigure((0, 1, 2), weight=0)
                for index, step in enumerate(steps):
                    step.grid(row=index + 1, column=0, padx=20, pady=5)
                guide_footer.grid()
            columns = 1 if width < 600 else 2
            cards.grid_columnconfigure(1, weight=0 if columns == 1 else 1, uniform="tools" if columns == 2 else "")
            for index, card in enumerate(self._home_cards):
                card.grid(row=index // columns, column=index % columns, sticky="nsew",
                          padx=0 if columns == 1 else ((0, 8) if index % 2 == 0 else (8, 0)), pady=(0, 16))
        # CTkScrollableFrame owns a Configure binding that maintains scrollregion.
        # Append our responsive layout handler; replacing it disables scrolling.
        page.bind("<Configure>", resize_home, add="+")

    def _build_workspace(self, key):
        info = self.MODULES[key]
        outer = self._page(key)
        outer.grid_rowconfigure(0, weight=1)
        page = ctk.CTkScrollableFrame(outer, fg_color="transparent", corner_radius=0,
                                      scrollbar_fg_color="#e4e4e7",
                                      scrollbar_button_color="#71717a", scrollbar_button_hover_color="#52525b")
        self._scrolls[key] = page
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        view = self._views[key] = {}
        view["scroll"] = page
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(4, 18))
        self._badge(header, info["tag"], key == "bupot").pack(anchor="w", pady=(0, 8))
        self._label(header, info["title"], 36, True).pack(anchor="w")
        description = self._label(header, info["description"], 14, color=self.C["text_sub"], anchor="w", justify="left")
        description.pack(fill="x", pady=(3, 0))
        header.bind("<Configure>", lambda e: description.configure(wraplength=max(250, header._reverse_widget_scaling(e.width))))

        picker = self._card(page)
        picker.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        picker.grid_columnconfigure(0, weight=1)
        self._label(picker, "01   Pilih sumber dokumen", 16, True).grid(row=0, column=0, padx=24, pady=(20, 4), sticky="w")
        self._badge(picker, "TERMASUK SUBFOLDER").grid(row=0, column=1, padx=24, pady=(20, 4))
        view["folder_label"] = self._label(picker, "Belum ada folder dipilih", 12, color=self.C["text_muted"])
        view["folder_label"].grid(row=1, column=0, columnspan=2, padx=24, pady=(0, 10), sticky="w")
        view["entry"] = ctk.CTkEntry(picker, textvariable=self._folders[key], height=44,
                                     corner_radius=14, font=self._font(14), border_width=2,
                                     border_color=self.C["border"], fg_color="#fafafa",
                                     text_color=self.C["text"])
        # Font-based corner glyphs can leave seams in the focus outline at
        # fractional Windows DPI. Draw this field as continuous canvas shapes.
        view["entry"]._draw_engine.preferred_drawing_method = "polygon_shapes"
        view["entry"]._canvas.delete("all")
        view["entry"]._draw()
        view["entry"].grid(row=2, column=0, padx=(24, 12), sticky="ew")
        def focus_entry(event):
            view["entry"].configure(border_color=self.C["border_focus"])
            self._reveal_control(view["entry"])
        view["entry"].bind("<FocusIn>", focus_entry)
        view["entry"].bind("<FocusOut>", lambda e, k=key: self._views[k]["entry"].configure(border_color=self.C["border"]))
        view["browse"] = self._button(picker, "Pilih folder", lambda: self._browse(key), width=130)
        view["browse"].configure(height=44)
        view["browse"].grid(row=2, column=1, padx=(0, 24))
        hint = self._label(picker, info["hint"], 13, color=self.C["text_sub"], justify="left", anchor="w")
        hint.grid(row=3, column=0, columnspan=2, padx=24, pady=(12, 20), sticky="ew")
        picker.bind("<Configure>", lambda e: hint.configure(wraplength=max(200, picker._reverse_widget_scaling(e.width) - 52)))
        self._folders[key].trace_add("write", lambda *args, k=key: self._folder_changed(k))

        activity = self._card(page)
        activity.grid(row=2, column=0, sticky="nsew")
        activity.grid_columnconfigure(0, weight=1)
        activity.grid_rowconfigure(3, weight=1)
        self._label(activity, "02   Aktivitas & hasil", 16, True).grid(row=0, column=0, padx=24, pady=(20, 8), sticky="w")
        view["status"] = self._badge(activity, "MENUNGGU FOLDER")
        view["status"].grid(row=0, column=1, padx=24, pady=(20, 8), sticky="e")
        view["progress"] = ctk.CTkProgressBar(activity, height=4, corner_radius=2,
                                             progress_color=self.C["accent"], fg_color=self.C["bg"])
        view["progress"].set(0)
        view["progress"].grid(row=1, column=0, columnspan=2, padx=24, pady=(0, 10), sticky="ew")
        view["summary"] = self._label(activity, "Pilih folder untuk memulai. Aktivitas akan tampil di sini.",
                                      13, color=self.C["text_sub"], anchor="w", justify="left")
        view["summary"].grid(row=2, column=0, columnspan=2, padx=24, pady=(0, 6), sticky="ew")
        activity.bind("<Configure>", lambda e: view["summary"].configure(wraplength=max(200, activity._reverse_widget_scaling(e.width) - 52)))
        view["log"] = ctk.CTkTextbox(activity, height=130, corner_radius=14, fg_color=self.C["bg"],
                                     text_color=self.C["text_sub"], font=self._font(13), wrap="word",
                                     scrollbar_button_color="#d4d4d8", scrollbar_button_hover_color="#a1a1aa")
        view["log"].grid(row=3, column=0, columnspan=2, padx=24, pady=(0, 12), sticky="nsew")
        view["log"].insert("1.0", "Belum ada aktivitas.\nPDF asli tetap tersimpan di folder sumber.")
        view["log"].configure(state="disabled")
        view["log"].bind("<MouseWheel>", lambda e: self._scroll_log_edge(e, key), add="+")
        def scroll_log_surface(event):
            # The rounded padding is a separate canvas, not the native Text widget.
            view["log"]._textbox.event_generate("<MouseWheel>", delta=event.delta)
            return "break"
        view["log"]._canvas.bind("<MouseWheel>", scroll_log_surface, add="+")
        tools = ctk.CTkFrame(activity, fg_color="transparent")
        tools.grid(row=4, column=0, columnspan=2, padx=24, pady=(0, 20), sticky="ew")
        view["copy"] = self._button(tools, "Salin log", lambda: self._copy_log(key), width=96)
        view["copy"].pack(side="left")
        view["open"] = self._button(tools, "Buka hasil  ↗", lambda: self._open_output(key), width=130, state="disabled")
        view["open"].pack(side="right")

        footer = ctk.CTkFrame(outer, fg_color="transparent")
        footer.grid(row=1, column=0, pady=(16, 0), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        output = "Pratinjau → periksa CSV → terapkan" if key == "rename" else f"Hasil Excel di folder sumber\n{info['output']}"
        self._label(footer, output, 11, color=self.C["text_sub"], justify="left").grid(row=0, column=0, sticky="w")
        view["run"] = self._button(footer, "Pratinjau nama  →" if key == "rename" else "Mulai ekstraksi  →",
                                    lambda: self._start_task(key), primary=True, width=176, state="disabled")
        view["run"].grid(row=0, column=1, sticky="e")
        if key == "rename":
            view["apply"] = self._button(footer, "Terapkan nama", lambda: self._start_task(key, True), width=142, state="disabled")
            view["apply"].grid(row=0, column=2, padx=(10, 0))

    def _navigate(self, key):
        self._current = key
        self.breadcrumb.configure(text="Ruang kerja  /  " + ("Beranda" if key == "home" else self.MODULES[key]["title"]))
        for name, button in self.nav.items():
            button._resting_border = self.C["accent"] if name == key else "white"
            button.configure(fg_color=self.C["accent"] if name == key else "white",
                             text_color="white" if name == key else self.C["text_sub"],
                             border_color=self.C["accent"] if name == key else "white",
                             hover_color=self.C["accent_hover"] if name == key else self.C["bg"])
        for name, page in self.pages.items():
            if name == key:
                page.grid(row=2, column=0, padx=32, pady=(0, 26), sticky="nsew")
            else:
                page.grid_remove()

    def _browse(self, key):
        if self._busy:
            return
        path = filedialog.askdirectory(parent=self, title="Pilih folder PDF — subfolder ikut diproses",
                                       initialdir=self._folders[key].get() or None)
        if path:
            self._folders[key].set(path)

    def _folder_changed(self, key):
        view = self._views[key]
        folder = self._folders[key].get().strip()
        view["folder_label"].configure(text="Folder sumber · dapat diketik atau dipilih" if folder else "Belum ada folder dipilih")
        view["status"].configure(text="SIAP DIPROSES" if folder else "MENUNGGU FOLDER")
        view["summary"].configure(text="Semua PDF dalam folder dan subfolder akan diperiksa." if folder else "Pilih folder untuk memulai.")
        view["progress"].set(0)
        self._outputs.pop(key, None)
        view["open"].configure(state="disabled")
        if key == "rename":
            self._preview_folder = None
        self._refresh_controls()

    def _refresh_controls(self):
        for key, view in self._views.items():
            view["entry"].configure(state="disabled" if self._busy else "normal")
            view["browse"].configure(state="disabled" if self._busy else "normal")
            ready = bool(self._folders[key].get().strip()) and not self._busy
            view["run"].configure(state="normal" if ready else "disabled")
            if key == "rename":
                view["apply"].configure(state="normal" if ready and self._preview_folder == self._folders[key].get().strip() else "disabled")

    def _start_task(self, key, apply_changes=False):
        if self._busy:
            return
        folder = self._folders[key].get().strip()
        if not os.path.isdir(folder):
            messagebox.showwarning("Folder tidak ditemukan", "Pilih folder yang tersedia di perangkat Anda.", parent=self)
            return
        if apply_changes:
            if self._preview_folder != folder:
                return
            if not messagebox.askyesno("Terapkan penamaan?", "Nama PDF di folder sumber akan diubah.\n\n"
                                      "Pastikan Anda telah memeriksa CSV pratinjau. Folder akan dipindai ulang; "
                                      "file baru atau yang berubah juga diperiksa. File dengan data tidak lengkap "
                                      "dilewati dan setiap perubahan dicatat dalam log CSV.\n\nLanjutkan?", parent=self):
                return
        elif key != "rename" and os.path.exists(os.path.join(folder, self.MODULES[key]["output"])):
            if not messagebox.askyesno("Ganti rekap sebelumnya?", "File hasil dengan nama yang sama sudah tersedia.\n"
                                      "Lanjutkan untuk menggantinya dengan rekap baru?", parent=self):
                return
        self._busy = key
        self._outputs.pop(key, None)
        if key == "rename":
            self._preview_folder = None
        view = self._views[key]
        view["open"].configure(state="disabled")
        view["status"].configure(text="MEMPROSES")
        view["summary"].configure(text="Memindai folder dan subfolder… Anda tetap dapat membuka halaman lain.")
        view["log"].configure(state="normal")
        view["log"].delete("1.0", "end")
        view["log"].configure(state="disabled")
        view["progress"].configure(mode="indeterminate")
        view["progress"].start()
        view["scroll"]._parent_canvas.yview_moveto(1.0)
        self._refresh_controls()
        self.nav[key].configure(text=self.MODULES[key]["title"] + "  ···")
        threading.Thread(target=self._run_job, args=(key, folder, apply_changes), daemon=True).start()

    def _run_job(self, key, folder, apply_changes):
        try:
            method = getattr(self, self.MODULES[key]["method"])
            result = method(folder, apply_changes=apply_changes) if key == "rename" else method(folder)
            self._events.put(("done", key, folder, apply_changes, result, None))
        except Exception as error:
            self._events.put(("done", key, folder, apply_changes, None, str(error)))

    def _drain_events(self):
        if self._closing:
            return
        # Bounded draining keeps navigation responsive even for very large batches.
        for _ in range(150):
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            if event[0] == "log":
                self._append_log(event[1], event[2])
            elif event[0] == "progress":
                _, done, total = event
                if self._busy:
                    view = self._views[self._busy]
                    view["progress"].stop()
                    view["progress"].configure(mode="determinate")
                    view["progress"].set(done / total if total else 0)
                    view["summary"].configure(text=f"Memeriksa PDF {done + 1} dari {total}…")
            elif event[0] == "done":
                self._finish_job(*event[1:])
            elif event[0] == "update":
                self._finish_update_check(*event[1:])
        if not self._closing:
            self._poll_id = self.after(60, self._drain_events)

    def _start_update_check(self, manual=False):
        if self._closing or self._update_checking:
            return
        if self._auto_update_id is not None:
            self.after_cancel(self._auto_update_id)
            self._auto_update_id = None
        self._update_checking = True
        self.update_check_button.configure(text="Memeriksa…", state="disabled")
        threading.Thread(target=self._run_update_check, args=(manual,), daemon=True).start()

    def _run_update_check(self, manual):
        # As with PDF workers, background code only writes to the queue, never Tk.
        try:
            result = self._update_checker.check(force=manual)
        except Exception:
            logging.exception("Unexpected update check failure")
            result = UpdateResult("error", error="server")
        self._events.put(("update", manual, result))

    def _finish_update_check(self, manual, result):
        if self._closing:
            return
        self._update_checking = False
        self.update_check_button.configure(text="Periksa update", state="normal")
        if result.status == "available":
            self._available_update = result
            self.update_notice.configure(text=f"ExpCore {result.version} tersedia.\nVersi Anda: {APP_VERSION}")
            self.update_banner.grid(row=1, column=0, padx=32, pady=(0, 12), sticky="ew")
            return
        if result.status in ("current", "unpublished", "pending"):
            self._available_update = None
            self.update_banner.grid_remove()
        if not manual:
            return
        if result.status == "current":
            messagebox.showinfo("Pembaruan ExpCore", f"Anda memakai ExpCore {APP_VERSION}.\n"
                                "Tidak ada versi stabil yang lebih baru.", parent=self)
        elif result.status == "unpublished":
            messagebox.showinfo("Pembaruan ExpCore", "Rilis publik belum tersedia atau tidak dapat diakses.", parent=self)
        elif result.status == "pending":
            messagebox.showinfo("Pembaruan ExpCore", "Versi baru sudah tercatat, tetapi installernya belum siap.\n"
                                "Silakan periksa kembali nanti.", parent=self)
        else:
            messages = {
                "network": "Tidak dapat terhubung. Periksa koneksi internet Anda.",
                "rate_limit": "Batas pemeriksaan GitHub tercapai.",
                "invalid": "Informasi rilis yang diterima tidak valid.",
                "server": "Layanan pembaruan sedang tidak tersedia.",
            }
            message = messages.get(result.error, messages["server"])
            if result.retry_at:
                message += "\nCoba lagi setelah " + datetime.fromtimestamp(result.retry_at).strftime("%H:%M") + "."
            messagebox.showwarning("Pembaruan belum dapat diperiksa", message + "\nAplikasi tetap dapat digunakan.", parent=self)

    def _open_update(self):
        if self._closing or self._available_update is None:
            return
        try:
            if not webbrowser.open(self._available_update.url, new=2):
                raise OSError("Browser tidak tersedia")
        except (OSError, ValueError, webbrowser.Error):
            messagebox.showerror("Unduhan belum dapat dibuka", "Tidak dapat membuka browser. "
                                 "Coba kembali setelah browser tersedia.", parent=self)

    def _finish_job(self, key, folder, apply_changes, result, error):
        view = self._views[key]
        view["progress"].stop()
        view["progress"].configure(mode="determinate")
        self._busy = None
        self.nav[key].configure(text=self.MODULES[key]["title"])
        if error:
            view["status"].configure(text="PERLU DIPERIKSA")
            view["summary"].configure(text="Proses belum selesai. Periksa log lalu coba kembali.")
            self._append_log(key, "GAGAL: " + error)
        else:
            path, summary = result
            view["progress"].set(1)
            view["status"].configure(text="SELESAI" if path else "TIDAK ADA HASIL")
            view["summary"].configure(text=summary)
            if path:
                self._outputs[key] = folder if key == "rename" else path
                view["open"].configure(state="normal")
                if key == "rename" and not apply_changes:
                    self._preview_folder = folder
            self._append_log(key, summary)
        self._refresh_controls()

    def _append_log(self, key, message):
        box = self._views[key]["log"]
        box.configure(state="normal")
        box.insert("end", datetime.now().strftime("%H:%M:%S") + "   " + message + "\n")
        box.see("end")
        box.configure(state="disabled")

    def _progress(self, done, total):
        self._events.put(("progress", done, total))

    def log_bupot(self, message):
        self._events.put(("log", "bupot", message))

    def log_bupot2024(self, message):
        self._events.put(("log", "bupot2024", message))

    def log_pm(self, message):
        self._events.put(("log", "pm", message))

    def log_rename(self, message):
        self._events.put(("log", "rename", message))

    def _copy_log(self, key):
        self.clipboard_clear()
        self.clipboard_append(self._views[key]["log"].get("1.0", "end-1c"))
        self._views[key]["copy"].configure(text="Disalin ✓")
        self.after(1600, lambda: self._views[key]["copy"].configure(text="Salin log"))

    def _open_output(self, key):
        path = self._outputs.get(key)
        if not path:
            return
        try:
            os.startfile(path)
        except OSError as error:
            messagebox.showerror("Hasil tidak dapat dibuka", f"{path}\n\n{error}", parent=self)

    def _close(self):
        if self._busy:
            messagebox.showinfo("Proses masih berjalan", "Tunggu pemrosesan selesai sebelum menutup aplikasi "
                                "agar hasil dan log tersimpan lengkap.", parent=self)
            return
        self._closing = True
        if self._auto_update_id is not None:
            self.after_cancel(self._auto_update_id)
        self.after_cancel(self._poll_id)
        self.destroy()
