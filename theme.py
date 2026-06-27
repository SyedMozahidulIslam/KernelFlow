"""
ui/theme.py
===========
Single source of truth for all visual design in KernelFlow.
Every color, font, spacing constant, and widget style lives here.
Changing one value here changes it everywhere in the application.
"""

import tkinter as tk
from tkinter import ttk


# ─────────────────────────────────────────────
#  Color Palette
# ─────────────────────────────────────────────

class Colors:
    # Backgrounds
    BG_PRIMARY    = "#0F1117"   # main window background
    BG_SECONDARY  = "#1A1D2E"   # panel / card background
    BG_TERTIARY   = "#232640"   # input fields, table rows
    BG_HOVER      = "#2A2F52"   # hover state
    BG_SELECTED   = "#3D4475"   # selected row

    # Accent
    ACCENT        = "#6C63FF"   # primary purple accent
    ACCENT_LIGHT  = "#8B85FF"   # lighter purple for hover
    ACCENT_DARK   = "#4B44CC"   # darker purple for press

    # Semantic
    SUCCESS       = "#2ECC71"   # green — good metric
    WARNING       = "#F39C12"   # amber — moderate metric
    DANGER        = "#E74C3C"   # red — error / bad metric
    INFO          = "#3498DB"   # blue — info

    # Text
    TEXT_PRIMARY   = "#EAEAEA"   # main text
    TEXT_SECONDARY = "#9BA3C2"   # muted labels
    TEXT_MUTED     = "#5C6380"   # very muted hints
    TEXT_ON_ACCENT = "#FFFFFF"   # text on colored backgrounds

    # Borders
    BORDER        = "#2E3354"
    BORDER_LIGHT  = "#3D4475"

    # Process colors (for Gantt chart bars + table row highlights)
    # 12 distinct colors — enough for up to 20 processes with cycling
    PROCESS_COLORS = [
        "#6C63FF",  # purple
        "#FF6584",  # pink
        "#43D9AD",  # teal
        "#FFB347",  # orange
        "#56CCF2",  # sky blue
        "#F7971E",  # amber
        "#A78BFA",  # violet
        "#34D399",  # emerald
        "#F472B6",  # rose
        "#60A5FA",  # blue
        "#FBBF24",  # yellow
        "#C084FC",  # purple-light
    ]

    # Gantt chart
    GANTT_BG      = "#0F1117"
    GANTT_GRID    = "#1E2235"
    GANTT_TEXT    = "#EAEAEA"
    GANTT_LABEL   = "#9BA3C2"

    @classmethod
    def get_process_color(cls, index: int) -> str:
        """Returns a cycling process color for the given process index."""
        return cls.PROCESS_COLORS[index % len(cls.PROCESS_COLORS)]


# ─────────────────────────────────────────────
#  Typography
# ─────────────────────────────────────────────

class Fonts:
    FAMILY       = "Segoe UI"       # Windows
    FAMILY_MONO  = "Consolas"       # monospace for values
    FAMILY_ALT   = "Helvetica"      # macOS / Linux fallback

    # Sizes
    SIZE_XS   = 9
    SIZE_SM   = 10
    SIZE_BASE = 11
    SIZE_MD   = 12
    SIZE_LG   = 14
    SIZE_XL   = 16
    SIZE_2XL  = 20
    SIZE_3XL  = 24

    # Pre-built tuples for widget font= params
    HEADING_1    = (FAMILY, SIZE_3XL, "bold")
    HEADING_2    = (FAMILY, SIZE_2XL, "bold")
    HEADING_3    = (FAMILY, SIZE_XL,  "bold")
    LABEL        = (FAMILY, SIZE_MD,  "normal")
    LABEL_BOLD   = (FAMILY, SIZE_MD,  "bold")
    BODY         = (FAMILY, SIZE_BASE,"normal")
    BODY_BOLD    = (FAMILY, SIZE_BASE,"bold")
    CAPTION      = (FAMILY, SIZE_SM,  "normal")
    MONO         = (FAMILY_MONO, SIZE_BASE, "normal")
    MONO_SM      = (FAMILY_MONO, SIZE_SM,   "normal")
    BUTTON       = (FAMILY, SIZE_MD,  "bold")
    STAT_VALUE   = (FAMILY_MONO, SIZE_2XL, "bold")
    STAT_LABEL   = (FAMILY, SIZE_SM,  "normal")


# ─────────────────────────────────────────────
#  Spacing & Geometry
# ─────────────────────────────────────────────

class Spacing:
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 24
    XXL = 32

    CARD_PAD    = 16
    PANEL_PAD   = 12
    INPUT_PAD   = 8
    BUTTON_PAD  = (10, 20)   # (vertical, horizontal)

    CORNER      = 8    # border radius hint (used in Canvas-drawn elements)


# ─────────────────────────────────────────────
#  Widget Style Constants (for direct config)
# ─────────────────────────────────────────────

class Styles:
    # Entry field
    ENTRY = dict(
        bg              = Colors.BG_TERTIARY,
        fg              = Colors.TEXT_PRIMARY,
        insertbackground= Colors.ACCENT,
        relief          = "flat",
        bd              = 0,
        font            = Fonts.BODY,
        highlightthickness= 1,
        highlightcolor  = Colors.ACCENT,
        highlightbackground= Colors.BORDER,
    )

    # Standard label
    LABEL = dict(
        bg   = Colors.BG_SECONDARY,
        fg   = Colors.TEXT_SECONDARY,
        font = Fonts.LABEL,
    )

    # Section heading label
    LABEL_HEADING = dict(
        bg   = Colors.BG_SECONDARY,
        fg   = Colors.TEXT_PRIMARY,
        font = Fonts.HEADING_3,
    )

    # Card frame
    CARD = dict(
        bg     = Colors.BG_SECONDARY,
        relief = "flat",
        bd     = 0,
    )

    # Subtle divider
    DIVIDER = dict(
        bg     = Colors.BORDER,
        height = 1,
        bd     = 0,
    )


# ─────────────────────────────────────────────
#  ttk Style Application
# ─────────────────────────────────────────────

def apply_theme(root: tk.Tk) -> ttk.Style:
    """
    Applies the KernelFlow dark theme to a Tk root window.
    Must be called once after root is created, before any widgets.

    Returns:
        The configured ttk.Style instance.
    """
    root.configure(bg=Colors.BG_PRIMARY)

    style = ttk.Style(root)

    # Use 'clam' as the base — most customisable cross-platform theme
    style.theme_use("clam")

    # ── Frame & Labelframe ─────────────────────────────────
    style.configure(
        "TFrame",
        background  = Colors.BG_PRIMARY,
        borderwidth = 0,
    )
    style.configure(
        "Card.TFrame",
        background  = Colors.BG_SECONDARY,
        borderwidth = 0,
    )
    style.configure(
        "TLabelframe",
        background  = Colors.BG_SECONDARY,
        bordercolor = Colors.BORDER,
        borderwidth = 1,
        relief      = "flat",
    )
    style.configure(
        "TLabelframe.Label",
        background  = Colors.BG_SECONDARY,
        foreground  = Colors.TEXT_PRIMARY,
        font        = Fonts.LABEL_BOLD,
    )

    # ── Labels ─────────────────────────────────────────────
    style.configure(
        "TLabel",
        background  = Colors.BG_PRIMARY,
        foreground  = Colors.TEXT_PRIMARY,
        font        = Fonts.BODY,
    )
    style.configure(
        "Card.TLabel",
        background  = Colors.BG_SECONDARY,
        foreground  = Colors.TEXT_SECONDARY,
        font        = Fonts.LABEL,
    )
    style.configure(
        "Heading.TLabel",
        background  = Colors.BG_PRIMARY,
        foreground  = Colors.TEXT_PRIMARY,
        font        = Fonts.HEADING_3,
    )
    style.configure(
        "Muted.TLabel",
        background  = Colors.BG_SECONDARY,
        foreground  = Colors.TEXT_MUTED,
        font        = Fonts.CAPTION,
    )

    # ── Buttons ────────────────────────────────────────────
    style.configure(
        "TButton",
        background  = Colors.BG_TERTIARY,
        foreground  = Colors.TEXT_PRIMARY,
        font        = Fonts.BUTTON,
        borderwidth = 0,
        focuscolor  = Colors.ACCENT,
        padding     = Spacing.BUTTON_PAD,
        relief      = "flat",
    )
    style.map(
        "TButton",
        background  = [("active", Colors.BG_HOVER), ("pressed", Colors.BG_SELECTED)],
        foreground  = [("active", Colors.TEXT_PRIMARY)],
    )
    style.configure(
        "Accent.TButton",
        background  = Colors.ACCENT,
        foreground  = Colors.TEXT_ON_ACCENT,
        font        = Fonts.BUTTON,
        borderwidth = 0,
        padding     = Spacing.BUTTON_PAD,
        relief      = "flat",
    )
    style.map(
        "Accent.TButton",
        background  = [("active", Colors.ACCENT_LIGHT), ("pressed", Colors.ACCENT_DARK)],
    )
    style.configure(
        "Danger.TButton",
        background  = Colors.DANGER,
        foreground  = Colors.TEXT_ON_ACCENT,
        font        = Fonts.BUTTON,
        borderwidth = 0,
        padding     = Spacing.BUTTON_PAD,
        relief      = "flat",
    )
    style.map(
        "Danger.TButton",
        background  = [("active", "#C0392B"), ("pressed", "#96281B")],
    )

    # ── Notebook (tabs) ────────────────────────────────────
    style.configure(
        "TNotebook",
        background  = Colors.BG_PRIMARY,
        borderwidth = 0,
        tabmargins  = [0, 0, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background  = Colors.BG_SECONDARY,
        foreground  = Colors.TEXT_SECONDARY,
        font        = Fonts.LABEL_BOLD,
        padding     = [Spacing.MD, Spacing.SM],
        borderwidth = 0,
    )
    style.map(
        "TNotebook.Tab",
        background  = [("selected", Colors.ACCENT), ("active", Colors.BG_HOVER)],
        foreground  = [("selected", Colors.TEXT_ON_ACCENT), ("active", Colors.TEXT_PRIMARY)],
    )

    # ── Treeview (results table) ───────────────────────────
    style.configure(
        "Treeview",
        background       = Colors.BG_SECONDARY,
        foreground       = Colors.TEXT_PRIMARY,
        fieldbackground  = Colors.BG_SECONDARY,
        font             = Fonts.MONO_SM,
        rowheight        = 30,
        borderwidth      = 0,
        relief           = "flat",
    )
    style.configure(
        "Treeview.Heading",
        background  = Colors.BG_TERTIARY,
        foreground  = Colors.TEXT_SECONDARY,
        font        = Fonts.LABEL_BOLD,
        borderwidth = 0,
        relief      = "flat",
    )
    style.map(
        "Treeview",
        background  = [("selected", Colors.BG_SELECTED)],
        foreground  = [("selected", Colors.TEXT_PRIMARY)],
    )
    style.map(
        "Treeview.Heading",
        background  = [("active", Colors.BG_HOVER)],
    )

    # ── Combobox (dropdown) ────────────────────────────────
    style.configure(
        "TCombobox",
        background        = Colors.BG_TERTIARY,
        foreground        = Colors.TEXT_PRIMARY,
        fieldbackground   = Colors.BG_TERTIARY,
        selectbackground  = Colors.ACCENT,
        selectforeground  = Colors.TEXT_ON_ACCENT,
        arrowcolor        = Colors.ACCENT,
        borderwidth       = 0,
        font              = Fonts.BODY,
        padding           = Spacing.SM,
    )
    style.map(
        "TCombobox",
        fieldbackground   = [("readonly", Colors.BG_TERTIARY)],
        foreground        = [("readonly", Colors.TEXT_PRIMARY)],
    )

    # ── Scrollbar ──────────────────────────────────────────
    style.configure(
        "TScrollbar",
        background  = Colors.BG_TERTIARY,
        troughcolor = Colors.BG_SECONDARY,
        borderwidth = 0,
        arrowsize   = 12,
        relief      = "flat",
    )
    style.map(
        "TScrollbar",
        background  = [("active", Colors.BORDER_LIGHT)],
    )

    # ── Separator ──────────────────────────────────────────
    style.configure(
        "TSeparator",
        background  = Colors.BORDER,
    )

    # ── PanedWindow ────────────────────────────────────────
    style.configure(
        "TPanedwindow",
        background  = Colors.BG_PRIMARY,
    )
    style.configure(
        "Sash",
        sashthickness = 4,
        background    = Colors.BORDER,
    )

    # ── Spinbox ────────────────────────────────────────────
    style.configure(
        "TSpinbox",
        background       = Colors.BG_TERTIARY,
        foreground       = Colors.TEXT_PRIMARY,
        fieldbackground  = Colors.BG_TERTIARY,
        arrowcolor       = Colors.ACCENT,
        borderwidth      = 0,
        font             = Fonts.BODY,
    )

    return style
