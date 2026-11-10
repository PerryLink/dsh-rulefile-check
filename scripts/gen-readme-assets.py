#!/usr/bin/env python3
"""Generate the README image assets for dsh-rulefile-check.

Outputs (idempotent overwrite, docs/assets/):

  dsh-rulefile-check-hero-{zh,en}-{light,dark}.webp
      1440x576 hero. The left column is the pitch (kicker, title, two value
      lines, subtitle, meta chips, footer); the right half is this plugin's
      own semantic object: a rule-file ledger with two input tabs (material,
      rule pack), seven RF rows (field checked, check kind, severity cap) and
      one report slip carrying a real finding shape from the README.

  dsh-rulefile-check-flow-v5-{light,dark}.svg
      1100x660 structure diagram, hand-written SVG. Grammar: a dual-inlet
      clause ledger. Two inputs (rule-file material, validated rule pack with
      its load-time severity ceiling) feed one seven-row check table, which
      has two outlets: the issue list and the skipped list. Text is
      command-surface tokens plus English labels, so all five README
      languages share the same pair.

The diagram/hero only restate what the code does: src/model.ts (parseMaterial),
src/shared/ruleset.ts (loadRuleset, MAX_SEVERITY_BY_KIND), src/shared/rows.ts
(runTableCheck), src/view.ts (the report projection), rules/rulefile-check.yaml
(seven rules) and the severity ceiling the loader enforces.

The legacy single-skin flow SVG, hero.png, demo.gif/png and quickstart.* stay
on disk untouched: they may be linked from outside the repository.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (bundled Python has it: Pillow 12.x).
"""
from __future__ import annotations

import os
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_DIR = r"C:\Windows\Fonts"
FONT_REG = os.path.join(FONT_DIR, "msyh.ttc")      # Microsoft YaHei
FONT_BOLD = os.path.join(FONT_DIR, "msyhbd.ttc")   # Microsoft YaHei Bold
FONT_MONO = os.path.join(FONT_DIR, "consola.ttf")  # Consolas

HERO_W, HERO_H = 1440, 576
FLOW_W, FLOW_H = 1100, 660

# --- palette -----------------------------------------------------------------
# Light/dark page backgrounds exactly as the README family specifies; the
# family accent is #4B67B4 (dark counterpart #8496f5).
PAL = {
    "light": dict(
        bg1=(249, 246, 253), bg2=(228, 234, 248),
        ink=(26, 33, 48), sub=(91, 101, 128), muted=(123, 133, 156),
        accent=(75, 103, 180), accentText=(64, 88, 152),
        card=(255, 255, 255), card2=(247, 249, 254), border=(219, 226, 241),
        chip=(238, 242, 252), chipBorder=(219, 228, 247),
        warn=(180, 83, 9), warnBg=(253, 241, 227),
        tab=(233, 238, 251), tabText=(63, 85, 145),
        shadow=(30, 44, 90, 38), panel=(255, 255, 255, 86),
        panelBorder=(75, 103, 180, 42), hair=(75, 103, 180, 46),
    ),
    "dark": dict(
        bg1=(19, 26, 42), bg2=(12, 16, 22),
        ink=(238, 242, 251), sub=(154, 167, 194), muted=(127, 138, 163),
        accent=(132, 150, 245), accentText=(169, 184, 255),
        card=(26, 34, 51), card2=(30, 39, 57), border=(45, 56, 84),
        chip=(35, 46, 71), chipBorder=(52, 65, 95),
        warn=(232, 184, 120), warnBg=(46, 42, 34),
        tab=(32, 42, 66), tabText=(169, 184, 255),
        shadow=(0, 0, 0, 120), panel=(255, 255, 255, 7),
        panelBorder=(132, 150, 245, 40), hair=(132, 150, 245, 44),
    ),
}

# --- hero copy (zh/en) -------------------------------------------------------
COPY = {
    "zh": dict(
        kicker="DSH PLUGIN · CHECKER",
        title="规则库自检",
        v1="把规则库拆成库头与一行行规则，逐栏核对。",
        v2="只列哪一条、哪一栏、差什么，绝不改原件。",
        sub="七条规则，一份差异清单——判定始终留给人。",
        chips=["rulefile_check", "7 条规则", "JSON / YAML", "只读离线"],
        footer="Apache-2.0 · PerryLink · DeepSeek Harness ≥ 0.2.1 · v0.2.9",
        tab1="材料 · JSON / YAML",
        tab2="规则包 · 7 条 · 封顶 warn",
        cols=["规则", "核对栏", "判定", "封顶"],
        sheet_head="rules/rulefile-check.yaml",
        sheet_right="虚线 = 默认 skipped",
        slip_title="报告 · issues[]",
        slip_count="warn 1 · skipped 1",
        slip_main=("RF-001 ", "第 2 行 · ruleId —— 编号「XX-001」与第 1 行重复"),
        slip_sub=("expected ", "「ruleId」在材料内应唯一 · ", "fix ",
                  "核对是否重复登记"),
    ),
    "en": dict(
        kicker="DSH PLUGIN · CHECKER",
        title="Rulefile check",
        v1="Header + a row per rule, checked field by field.",
        v2="It names the rule, the field, the difference.",
        sub="Seven rules, one list — the verdict stays human.",
        chips=["rulefile_check", "7 rules", "JSON / YAML", "read-only"],
        footer="Apache-2.0 · PerryLink · DeepSeek Harness ≥ 0.2.1 · v0.2.9",
        tab1="material · JSON / YAML",
        tab2="rule pack · 7 rules · cap warn",
        cols=["RULE", "FIELD", "KIND", "CAP"],
        sheet_head="rules/rulefile-check.yaml",
        sheet_right="dashed = skipped by default",
        slip_title="report · issues[]",
        slip_count="warn 1 · skipped 1",
        slip_main=("RF-001 ", "row 2 · ruleId — 「XX-001」 repeats the id on row 1"),
        slip_sub=("expected ", "「ruleId」 unique within the material · ", "fix ",
                  "check for a duplicate entry"),
    ),
}

# The seven rules, exactly as rules/rulefile-check.yaml declares them.
# (id, field checked, check kind, severity cap)
ROWS = [
    ("RF-001", "ruleId", "unique", "warn"),
    ("RF-002", "document · clause", "presenceAny", "warn"),
    ("RF-003", "excerpt", "minLength ≥ 8", "warn"),
    ("RF-004", "source", "pattern", "warn"),
    ("RF-005", "basisKind → severity", "conditionalPresence", "warn"),
    ("RF-006", "checkKind", "enum (values empty)", "warn"),
    ("RF-007", "packName · plugin · version", "headerPresence", "warn"),
]

_FONTS: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    path = {"reg": FONT_REG, "bold": FONT_BOLD, "mono": FONT_MONO}[kind]
    key = (path, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]


def measure(f: ImageFont.FreeTypeFont, s: str, spacing: float = 0.0) -> float:
    if not spacing:
        return f.getlength(s)
    return sum(f.getlength(ch) for ch in s) + spacing * max(0, len(s) - 1)


def put(img: Image.Image, xy: tuple[float, float], s: str, f: ImageFont.FreeTypeFont,
        fill, anchor: str = "ls", spacing: float = 0.0,
        maxw: float | None = None, tag: str = "") -> float:
    """Draw text and refuse to overflow the box the layout promised it."""
    w = measure(f, s, spacing)
    if maxw is not None and w > maxw + 0.6:
        raise SystemExit(f"[overflow] {tag}: {w:.1f}px > {maxw:.1f}px :: {s!r}")
    d = ImageDraw.Draw(img)
    if spacing:
        x, y = xy
        for ch in s:
            d.text((x, y), ch, font=f, fill=fill, anchor="ls")
            x += f.getlength(ch) + spacing
    else:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
    return w


def runs(img: Image.Image, x: float, y: float,
         parts: Iterable[tuple[str, ImageFont.FreeTypeFont, object]],
         maxw: float, tag: str) -> float:
    total = sum(measure(f, s) for s, f, _ in parts)
    if total > maxw + 0.6:
        raise SystemExit(f"[overflow] {tag}: {total:.1f}px > {maxw:.1f}px")
    for s, f, fill in parts:
        x += put(img, (x, y), s, f, fill)
    return x


def mix(a, b, t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diag_gradient(w: int, h: int, c1, c2) -> Image.Image:
    n = 160
    small = Image.new("RGB", (n, n))
    px = small.load()
    for y in range(n):
        for x in range(n):
            px[x, y] = mix(c1, c2, 0.55 * (x / (n - 1)) + 0.45 * (y / (n - 1)))
    return small.resize((w, h), Image.Resampling.BICUBIC)


def glow(size: tuple[int, int], cx: float, cy: float, r: float, color, alpha: int,
         blur: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - r, cy - r, cx + r, cy + r),
                                  fill=(*color, alpha))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def shadow(img: Image.Image, box, radius: int, color, dy: int = 12,
           blur: int = 26) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        (box[0], box[1] + dy, box[2], box[3] + dy), radius, fill=color)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def card(img: Image.Image, box, radius: int, fill, outline, width: int = 1) -> None:
    """Translucent card: drawn on its own layer, then composited (ImageDraw
    replaces RGBA pixels instead of blending them)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius, fill=fill,
                                            outline=outline, width=width)
    img.alpha_composite(layer)


def hairline(img: Image.Image, xy, color, width: int = 1) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).line(xy, fill=color, width=width)
    img.alpha_composite(layer)


def dashed_box(img: Image.Image, box, radius: int, color, dash_len: int = 7,
               gap: int = 5, width: int = 1) -> None:
    """Rounded rectangle with a dashed outline (Pillow has no dash option)."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for ax, ay, bx, by in ((x0 + radius, y0, x1 - radius, y0),
                           (x0 + radius, y1, x1 - radius, y1),
                           (x0, y0 + radius, x0, y1 - radius),
                           (x1, y0 + radius, x1, y1 - radius)):
        length = max(abs(bx - ax), abs(by - ay))
        offset = 0
        while offset < length:
            end = min(offset + dash_len, length)
            if ax == bx:
                d.line((ax, ay + offset, ax, ay + end), fill=color, width=width)
            else:
                d.line((ax + offset, ay, ax + end, ay), fill=color, width=width)
            offset += dash_len + gap
    img.alpha_composite(layer)


# =============================================================================
# Hero
# =============================================================================
def hero(lang: str, skin: str) -> Image.Image:
    p = PAL[skin]
    c = COPY[lang]
    img = diag_gradient(HERO_W, HERO_H, p["bg1"], p["bg2"]).convert("RGBA")
    img.alpha_composite(glow((HERO_W, HERO_H), 1120, 220, 470, p["accent"], 26, 150))
    img.alpha_composite(glow((HERO_W, HERO_H), 240, 540, 300, p["accent"], 14, 120))

    # soft frame, so the 1440x576 plate reads as one card on the page
    card(img, (16, 16, HERO_W - 16, HERO_H - 16), 22, p["panel"],
         p["panelBorder"], 1)

    X = 88
    MAXW = 612

    # ---- left column --------------------------------------------------------
    put(img, (X, 98), c["kicker"], font("mono", 20), p["accent"], spacing=3.0,
        maxw=MAXW, tag="kicker")
    put(img, (X, 224), c["title"], font("bold", 80), p["ink"], maxw=MAXW,
        tag="title")
    ImageDraw.Draw(img).rounded_rectangle((X, 244, X + 92, 250), 3,
                                          fill=p["accent"])
    put(img, (X, 292), c["v1"], font("reg", 26), p["ink"], maxw=MAXW, tag="v1")
    put(img, (X, 330), c["v2"], font("reg", 26), p["ink"], maxw=MAXW, tag="v2")
    hairline(img, (X, 358, 700, 358), p["hair"], 1)
    put(img, (X, 398), c["sub"], font("reg", 25), p["sub"], maxw=MAXW, tag="sub")

    # meta chips
    cx = X
    for label in c["chips"]:
        f = font("mono", 20) if label == "rulefile_check" else font("reg", 20)
        w = measure(f, label)
        chip_w = w + 30
        if cx + chip_w > X + MAXW:
            raise SystemExit(f"[overflow] chips at {label!r}")
        ImageDraw.Draw(img).rounded_rectangle(
            (cx, 424, cx + chip_w, 458), 11, fill=p["chip"],
            outline=p["chipBorder"], width=1)
        put(img, (cx + 15, 447), label, f, p["accentText"])
        cx += chip_w + 10

    put(img, (X, 518), c["footer"], font("reg", 17), p["muted"], maxw=MAXW,
        tag="footer")

    # ---- right: tabs, sheet, slip ------------------------------------------
    SX0, SX1 = 724, 1368
    SY0, SY1 = 86, 432

    # tabs (drawn first; the sheet covers their lower edge)
    for box, label, tx in (((724, 54, 984, 96), c["tab1"], 748),
                           ((996, 54, SX1, 96), c["tab2"], 1020)):
        ImageDraw.Draw(img).rounded_rectangle(box, 12, fill=p["tab"],
                                              outline=p["border"], width=1)
        put(img, (tx, 82), label, font("reg", 15.5), p["tabText"],
            maxw=box[2] - box[0] - 48, tag="tab")

    shadow(img, (SX0, SY0, SX1, SY1), 20, p["shadow"], dy=14, blur=30)
    card(img, (SX0, SY0, SX1, SY1), 20, p["card"], p["border"], 1)

    # sheet header
    ImageDraw.Draw(img).rounded_rectangle((748, 98, 776, 126), 9,
                                          fill=p["accent"])
    put(img, (762, 118), "7", font("bold", 15), (255, 255, 255), anchor="ms")
    put(img, (788, 118), c["sheet_head"], font("mono", 15.5), p["ink"],
        maxw=560, tag="sheet_head")
    put(img, (1344, 118), c["sheet_right"],
        font("mono" if lang == "en" else "reg", 12), p["muted"],
        anchor="rs", maxw=300, tag="sheet_right")

    # column headers
    for x, label in zip((748, 840, 1092, 1264), c["cols"]):
        put(img, (x, 154), label, font("reg", 12.5), p["muted"], spacing=0.6)

    # rows. RF-006 is skipped by default (its `values` ships empty), so that row
    # gets a dashed outline: the one row that cannot run is marked, not hidden.
    for i, (rid, field, kind, cap) in enumerate(ROWS):
        top = 164 + i * 36
        base = top + 24
        dashed = rid == "RF-006"
        if dashed:
            ImageDraw.Draw(img).rounded_rectangle(
                (736, top + 4, 1356, top + 32), 9, fill=p["card2"])
            dashed_box(img, (736, top + 4, 1356, top + 32), 9,
                       (*p["accent"], 170), dash_len=7, gap=5)
        elif i % 2 == 1:
            ImageDraw.Draw(img).rounded_rectangle(
                (736, top + 2, 1356, top + 34), 8, fill=p["card2"])
        put(img, (748, base), rid, font("bold", 16), p["ink"])
        put(img, (840, base), field, font("mono", 14.5), p["ink"],
            maxw=248, tag=f"field {rid}")
        put(img, (1092, base), kind, font("mono", 14.5), p["sub"],
            maxw=168, tag=f"kind {rid}")
        chip_box = (1264, base - 15, 1316, base + 5)
        ImageDraw.Draw(img).rounded_rectangle(chip_box, 10, fill=p["chip"])
        put(img, (1272, base - 1), cap, font("mono", 11.5), p["accentText"])

    # report slip
    SL0, SL1 = 448, 526
    shadow(img, (SX0, SL0, SX1, SL1), 16, p["shadow"], dy=10, blur=24)
    card(img, (SX0, SL0, SX1, SL1), 16, p["card"], p["border"], 1)
    ImageDraw.Draw(img).rounded_rectangle((730, 460, 734, 514), 2,
                                          fill=p["accent"])

    put(img, (752, 472), c["slip_title"],
        font("mono" if lang == "en" else "bold", 12.5), p["accent"])
    put(img, (1344, 472), c["slip_count"], font("mono", 11.5), p["muted"],
        anchor="rs", maxw=420, tag="slip_count")
    runs(img, 752, 497,
         [(c["slip_main"][0], font("mono", 13), p["accent"]),
          (c["slip_main"][1], font("reg", 14.5), p["ink"])],
         maxw=592, tag="slip_main")
    runs(img, 752, 517,
         [(c["slip_sub"][0], font("mono", 11.5), p["muted"]),
          (c["slip_sub"][1], font("reg", 13.5), p["sub"]),
          (c["slip_sub"][2], font("mono", 11.5), p["muted"]),
          (c["slip_sub"][3], font("reg", 13.5), p["sub"])],
         maxw=592, tag="slip_sub")

    return img


# =============================================================================
# Flow diagram (hand-written SVG)
# =============================================================================
SANS = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',system-ui,"
        "sans-serif")
MONO = ("Consolas,'Cascadia Mono','SFMono-Regular',ui-monospace,"
        "'Microsoft YaHei',monospace")

SVG = {
    "light": dict(
        bg1="#f9f6fd", bg2="#e4eaf8", ink="#1a2130", sub="#5b6580",
        muted="#7b859c", accent="#4B67B4", accentText="#40588f",
        card="#ffffff", card2="#f7f9fe", border="#dbe2f1",
        chip="#eef2fc", chipText="#40588f", shadow="#1a2545", shadow_op="0.10",
        hair="#d9e1f0", dashed="#4B67B4",
    ),
    "dark": dict(
        bg1="#131a2a", bg2="#0c1016", ink="#eef2fb", sub="#9aa7c2",
        muted="#7f8ba6", accent="#8496f5", accentText="#a9b8ff",
        card="#1a2233", card2="#1e2739", border="#2d3854",
        chip="#232e47", chipText="#a9b8ff", shadow="#000000", shadow_op="0.45",
        hair="#2a3550", dashed="#8496f5",
    ),
}

FLOW_ROWS = [
    ("RF-001", "ruleId", "unique",
     "a duplicate id (whitespace ignored)"),
    ("RF-002", "document · clause", "presenceAny",
     "both basis fields are empty"),
    ("RF-003", "excerpt", "minLength ≥ 8", "shorter than 8 characters"),
    ("RF-004", "source", "pattern", "not an http(s) link"),
    ("RF-005", "basisKind → severity", "conditionalPresence",
     "a derived/config basis has no severity"),
    ("RF-006", "checkKind", "enum (values empty)",
     "values empty → skipped, with a reason"),
    ("RF-007", "packName · plugin · version", "headerPresence",
     "the header misses any of the three"),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def est(s: str, size: float, mono: bool = False) -> float:
    """Conservative text-width estimate, only used for overflow warnings."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80:
            w += size
        elif ch == " ":
            w += size * (0.33 if mono else 0.30)
        else:
            w += size * (0.62 if mono else 0.56)
    return w


WARN: list[str] = []


def chk(s: str, size: float, maxw: float, mono: bool, tag: str) -> None:
    w = est(s, size, mono)
    if w > maxw:
        WARN.append(f"{tag}: {w:.0f}px > {maxw:.0f}px :: {s!r}")


def svg_text(x: float, y: float, s: str, size: float, fill: str, *,
             mono: bool = False, weight: int | None = None, anchor: str | None = None,
             spacing: float | None = None, opacity: float | None = None,
             maxw: float | None = None, tag: str = "") -> str:
    if maxw is not None:
        chk(s, size, maxw, mono, tag or "text")
    attrs = [
        f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"',
        f'font-family="{MONO if mono else SANS}"', f'font-size="{size:g}"',
    ]
    if weight is not None:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{esc(s)}</text>'


def svg_card(box, radius, fill, stroke, s, shadow: bool = True) -> list[str]:
    x0, y0, x1, y1 = box
    f = ' filter="url(#sh)"' if shadow else ""
    return [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1"{f}/>']


def svg_arrow(x1: float, y1: float, x2: float, y2: float, color: str) -> list[str]:
    return [
        f'<path d="M{x1} {y1}V{y2 - 8}" fill="none" stroke="{color}" '
        f'stroke-width="1.6" stroke-linecap="round"/>',
        f'<path d="M{x1 - 4.5} {y2 - 9}L{x1} {y2 - 1}L{x1 + 4.5} {y2 - 9}" '
        f'fill="none" stroke="{color}" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round"/>',
    ]


def flow(skin: str) -> str:
    s = SVG[skin]
    o: list[str] = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{FLOW_W}" '
             f'height="{FLOW_H}" viewBox="0 0 {FLOW_W} {FLOW_H}" '
             f'role="img" aria-labelledby="t d">')
    o.append('<title id="t">dsh-rulefile-check structure: material and rule pack → '
             'seven-rule ledger → issues and skipped</title>')
    o.append('<desc id="d">Two inputs (the material rule file and the validated '
             'rule pack) feed one seven-row check table; each rule checks one '
             'field and is capped at warn; the report has two outlets, issues and '
             'skipped.</desc>')
    o.append("<defs>")
    o.append(f'<linearGradient id="bg" x1="0" y1="0" x2="0.95" y2="1">'
             f'<stop offset="0" stop-color="{s["bg1"]}"/>'
             f'<stop offset="1" stop-color="{s["bg2"]}"/></linearGradient>')
    o.append(f'<radialGradient id="glow" cx="0.82" cy="0.16" r="0.62">'
             f'<stop offset="0" stop-color="{s["accent"]}" stop-opacity="0.10"/>'
             f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/>'
             f'</radialGradient>')
    o.append(f'<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
             f'<feDropShadow dx="0" dy="8" stdDeviation="12" '
             f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/>'
             f'</filter>')
    o.append("</defs>")
    o.append(f'<rect width="{FLOW_W}" height="{FLOW_H}" rx="20" fill="url(#bg)"/>')
    o.append(f'<rect width="{FLOW_W}" height="{FLOW_H}" rx="20" fill="url(#glow)"/>')

    # ---- header -------------------------------------------------------------
    o.append(svg_text(48, 34, "DSH PLUGIN · RULEFILE CHECK", 11, s["accent"],
                      mono=True, spacing=1.6))
    o.append(svg_text(48, 68, "Seven rules, one rule file", 26, s["ink"],
                      weight=700, maxw=620, tag="title"))
    o.append(svg_text(48, 92,
                      "material + rule pack → runTableCheck → issues · skipped · "
                      "the original is never modified",
                      12, s["sub"], mono=True, maxw=760, tag="subtitle"))
    o.append(svg_text(1052, 68, "7 rules · 12 material columns", 12, s["accent"],
                      mono=True, anchor="end", maxw=300, tag="headstat"))
    o.append(f'<line x1="48" y1="104" x2="1052" y2="104" stroke="{s["hair"]}" '
             f'stroke-width="1"/>')

    # ---- inputs -------------------------------------------------------------
    o += svg_card((40, 112, 520, 240), 16, s["card"], s["border"], s)
    o.append(svg_text(64, 136, "MATERIAL · JSON / YAML", 11, s["accent"],
                      mono=True, spacing=1.2))
    o.append(svg_text(64, 162, "The rule file: header + one row per rule", 16.5,
                      s["ink"], weight=700, maxw=432, tag="mat_title"))
    o.append(svg_text(64, 186, "header  packName · plugin · version · engineKinds",
                      11.5, s["sub"], mono=True, maxw=432, tag="mat_l1"))
    o.append(svg_text(64, 206, "row     ruleId · basisKind · excerpt · source · checkKind",
                      11.5, s["sub"], mono=True, maxw=432, tag="mat_l2"))
    o.append(svg_text(64, 228,
                      "→ parseMaterial · aliases folded · missing fields become findings",
                      11, s["accent"], mono=True, maxw=432, tag="mat_l3"))

    o += svg_card((544, 112, 1060, 240), 16, s["card"], s["border"], s)
    o.append(svg_text(568, 136, "RULE PACK · LOAD-TIME", 11, s["accent"],
                      mono=True, spacing=1.2))
    o.append(svg_text(568, 162, "rules/rulefile-check.yaml · 7 rules", 16.5,
                      s["ink"], weight=700, maxw=468, tag="pack_title"))
    o.append(svg_text(568, 186,
                      "cap by basis.kind: direct ≤ error · derived-from-principle ≤ warn",
                      11.5, s["sub"], mono=True, maxw=468, tag="pack_l1"))
    o.append(svg_text(568, 206, "institutional-configuration ≤ info", 11.5,
                      s["sub"], mono=True, maxw=468, tag="pack_l2"))
    o.append(svg_text(568, 228,
                      "over the cap → loader rejects: strongest permitted severity",
                      11, s["accent"], mono=True, maxw=468, tag="pack_l3"))

    # ---- arrows into the ledger --------------------------------------------
    o += svg_arrow(280, 242, 280, 270, s["sub"])
    o += svg_arrow(802, 242, 802, 270, s["sub"])

    # ---- ledger card --------------------------------------------------------
    o += svg_card((40, 272, 1060, 554), 18, s["card"], s["border"], s)
    o.append(svg_text(64, 297, "runTableCheck", 13, s["accent"], mono=True,
                      weight=700, maxw=200, tag="led_head"))
    o.append(svg_text(64 + 118, 297, "· 7 rules, one check each", 12, s["sub"],
                      maxw=420, tag="led_head2"))
    o.append(svg_text(1036, 297, "pure · no I/O · no model", 11, s["muted"],
                      mono=True, anchor="end", maxw=240, tag="led_right"))

    for x, label in ((64, "RULE"), (160, "FIELD CHECKED"), (404, "CHECK KIND"),
                     (596, "WHEN IT FIRES"), (984, "CAP")):
        o.append(svg_text(x, 326, label, 11.5, s["muted"], mono=True,
                          spacing=1.1, maxw=180 if x != 596 else 300,
                          tag=f"colhdr {label}"))

    for i, (rid, field, kind, fires) in enumerate(FLOW_ROWS):
        top = 336 + i * 30
        base = top + 20
        if i % 2 == 1:
            if i == 5:  # the dashed (skipped) row fills its whole band
                o.append(f'<rect x="52" y="{top}" width="996" height="30" '
                         f'rx="10" fill="{s["card2"]}"/>')
            else:
                o.append(f'<rect x="52" y="{top + 2}" width="996" height="26" '
                         f'rx="7" fill="{s["card2"]}"/>')
        if i < len(FLOW_ROWS) - 1 and i not in (4, 5):
            o.append(f'<line x1="64" y1="{top + 30}" x2="1036" y2="{top + 30}" '
                     f'stroke="{s["hair"]}" stroke-width="1"/>')
        o.append(svg_text(64, base, rid, 13.5, s["ink"], mono=True, weight=700,
                          maxw=92, tag=f"id {rid}"))
        o.append(svg_text(160, base, field, 13, s["ink"], mono=True, maxw=240,
                          tag=f"field {rid}"))
        o.append(svg_text(404, base, kind, 13, s["sub"], mono=True, maxw=188,
                          tag=f"kind {rid}"))
        o.append(svg_text(596, base, fires, 13, s["sub"], maxw=380,
                          tag=f"fires {rid}"))
        o.append(f'<rect x="980" y="{top + 9}" width="46" height="20" rx="10" '
                 f'fill="{s["chip"]}"/>')
        o.append(svg_text(986, top + 23, "warn", 11, s["chipText"], mono=True,
                          maxw=40, tag=f"cap {rid}"))

    # RF-006 row: skipped by default, marked with a dashed outline (no fill, so
    # the row's own text and alternating band stay visible). The solid
    # separators above/below this row are skipped, so the dashed edge is the
    # row boundary rather than a line crossing it.
    o.append(f'<rect x="52" y="486" width="996" height="30" rx="9" '
             f'fill="none" stroke="{s["dashed"]}" stroke-width="1.1" '
             f'stroke-dasharray="6 4"/>')

    # ---- outlets ------------------------------------------------------------
    o += svg_card((40, 566, 684, 646), 16, s["card"], s["border"], s)
    o.append(svg_text(64, 590, "↳ REPORT · issues[]", 12.5, s["accent"], mono=True,
                      weight=700, maxw=200, tag="rep_title"))
    o.append(svg_text(64 + 160, 590, "one entry per difference", 12, s["sub"],
                      maxw=300, tag="rep_title2"))
    o.append(svg_text(64, 613,
                      "ruleId · severity · locator{row, field} · found / expected / fix · basis",
                      11.5, s["sub"], mono=True, maxw=596, tag="rep_l1"))
    o.append(svg_text(64, 633,
                      "lists differences only — no compliance, liability or correctness verdict",
                      11.5, s["muted"], maxw=596, tag="rep_l2"))

    o += svg_card((708, 566, 1060, 646), 16, s["card"], s["border"], s)
    o.append(svg_text(732, 590, "↳ skipped[] · did not run", 12.5, s["accent"],
                      mono=True, weight=700, maxw=304, tag="skip_title"))
    o.append(svg_text(732, 613, "rule · reason — RF-006 ships values empty", 11.5,
                      s["sub"], mono=True, maxw=304, tag="skip_l1"))
    o.append(svg_text(732, 633, "an empty list is never 'nothing is wrong'", 11.5,
                      s["accent"], maxw=304, tag="skip_l2"))

    o.append("</svg>")
    return "\n".join(o) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            img = hero(lang, skin).convert("RGB")
            path = os.path.join(OUT, f"dsh-rulefile-check-hero-{lang}-{skin}.webp")
            img.save(path, "WEBP", quality=92, method=6)
            print(f"hero  {os.path.basename(path)}  {img.width}x{img.height}")

    for skin in ("light", "dark"):
        text = flow(skin)
        path = os.path.join(OUT, f"dsh-rulefile-check-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"flow  {os.path.basename(path)}  {FLOW_W}x{FLOW_H}  "
              f"{len(text):,} bytes")

    if WARN:
        print("\nwidth warnings (check the Chrome render before committing):")
        for w in WARN:
            print("  " + w)
    else:
        print("\nall estimated text widths fit their columns")


if __name__ == "__main__":
    main()
