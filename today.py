import os
from datetime import datetime, timedelta, timezone

import requests

import terminal_font   # fontes embutidas (JetBrains Mono e Fira Code)

USERNAME = os.environ.get("GH_USERNAME", "albqrmario-dev")
TOKEN = os.environ.get("GH_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

HOST = "albqrmario@GitHub"
PATH = "~/dev/profile"
COMMAND = "profilefetch"
TERMINAL_FONT = "JetBrains Mono"
SHOW_DOTS = True          # bolinhas de cor (tons de azul) no fim, como no print de referência
BRT = timezone(timedelta(hours=-3))

# ---------- caixas de informação (título na borda, como no print do PowerShell) ----------
# {repos}, {stars}, {commits}, {followers} e {agora} são preenchidos pelo script com dados do GitHub.
SECTIONS = [
    ("Sobre", [
        ("Curso", "ADS @ IFPE Garanhuns"),
        ("Foco", "Desenvolvimento Backend"),
        ("Local", "Garanhuns, Pernambuco, Brasil"),
        ("Idiomas", "Português, Inglês"),
        # ("Status", "Aberto a estágio / oportunidades"),
    ]),
    ("Stack", [
        ("Linguagens", "Python, Java, JavaScript, SQL"),
        ("Frameworks", "React Native, Node.js, Express"),
        ("Ferramentas", "Firebase, Git, Linux, VSCode"),
    ]),
    ("Contato", [
        ("Email", "marioalbuquerque.dev@gmail.com"),
        ("LinkedIn", "linkedin.com/in/albqrmario"),
        ("GitHub", f"github.com/{USERNAME}"),
    ]),
    ("GitHub", [
        ("Atividade", "{commits} commits · {repos} repos"),
        ("Comunidade", "{stars} stars · {followers} seguidores"),
        # ("Atualizado", "{agora}"),
    ]),
]

# ---------- cores: paleta do GitHub com bastante azul ----------
THEMES = {
    "dark": dict(
        WIN_BORDER="#30363d", TITLEBAR="#161b22", BG1="#0d1117", BG2="#0a1a30", GLOW="#1f6feb", GLOW_OP=0.16,
        FG="#e6edf3", VAL="#c9d1d9", KEY="#58a6ff", TITLE="#79c0ff", BOX="#2b5ea8", DIM="#7d8590",
        USER="#79c0ff", PATHC="#388bfd", CURSOR="#58a6ff",
        DOT_LOW="#10315f", DOT_HIGH="#a5d6ff",
        ART_HI="#a5d6ff", ART_MID="#58a6ff", ART_LO="#2b5ea8"),
    "light": dict(
        WIN_BORDER="#d0d7de", TITLEBAR="#f6f8fa", BG1="#ffffff", BG2="#eef5ff", GLOW="#54aeff", GLOW_OP=0.12,
        FG="#1f2328", VAL="#24292f", KEY="#0969da", TITLE="#0550ae", BOX="#8cb8f0", DIM="#656d76",
        USER="#0550ae", PATHC="#0969da", CURSOR="#0969da",
        DOT_LOW="#cfe3fb", DOT_HIGH="#0550ae",
        ART_HI="#0550ae", ART_MID="#0969da", ART_LO="#9ec6f5"),
}

_OTHER = "Fira Code" if TERMINAL_FONT == "JetBrains Mono" else "JetBrains Mono"
FONT = f"'{TERMINAL_FONT}','{_OTHER}','DejaVu Sans Mono',Consolas,Menlo,monospace"
IFS = 15             # fonte dos textos
ICW = IFS * 0.6      # largura de um caractere (JetBrains Mono: 0,6 em)
ILH = 22             # altura de cada linha
PAD = 34             # margem lateral
GAP = 44             # espaço entre o logo e as caixas
TICK = 20            # recuo do texto dentro das caixas
BOX_TOP, BOX_BOT, BOX_GAP = 25, 11, 18
ART_CELL_W = 6.0     # largura de cada caractere do logo (altura = 2x)


# ============================ dados do GitHub ============================
def gh_get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fmt(n):
    if n is None:
        return "?"
    if isinstance(n, (int, float)) and n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def fetch_stats():
    s = dict(repos=None, stars=None, commits=None, followers=None)
    try:
        user = gh_get(f"https://api.github.com/users/{USERNAME}")
        s["repos"], s["followers"] = user.get("public_repos"), user.get("followers")
        repos, page = [], 1
        while True:
            batch = gh_get(f"https://api.github.com/users/{USERNAME}/repos", {"per_page": 100, "page": page})
            if not batch:
                break
            repos.extend(batch)
            page += 1
        s["stars"] = sum(r["stargazers_count"] for r in repos)
    except Exception as e:
        print(f"Aviso: perfil/repos ({e}).")
    try:
        s["commits"] = gh_get("https://api.github.com/search/commits",
                              {"q": f"author:{USERNAME}", "per_page": 1}).get("total_count")
    except Exception as e:
        print(f"Aviso: commits ({e}).")
    return s


# ============================ utilidades ============================
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def load_art():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "art.txt"), encoding="utf-8") as f:
        lines = f.read().split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def resolve_sections(stats):
    values = {k: fmt(v) for k, v in stats.items()}
    values["agora"] = datetime.now(BRT).strftime("%d/%m/%Y %H:%M")
    return [(title, [(k, v.format(**values)) for k, v in rows]) for title, rows in SECTIONS]


def font_css():
    regular, bold = terminal_font.FONTS[TERMINAL_FONT]      # só a fonte escolhida entra no SVG
    return (f"@font-face{{font-family:'{TERMINAL_FONT}';font-weight:400;font-style:normal;"
            f"src:url(data:font/woff2;base64,{regular}) format('woff2');}}"
            f"@font-face{{font-family:'{TERMINAL_FONT}';font-weight:700;font-style:normal;"
            f"src:url(data:font/woff2;base64,{bold}) format('woff2');}}")


def box_height(n):
    return BOX_TOP + (n - 1) * ILH + BOX_BOT


# ============================ desenho ============================
def build_svg(stats, filename, theme):
    T = THEMES[theme]
    art = load_art()
    sections = resolve_sections(stats)

    key_cols = max(len(k) for _, rws in sections for k, _ in rws) + 2    # alinha os valores em todas as caixas
    val_cols = max(len(v) for _, rws in sections for _, v in rws)
    box_w = TICK + (key_cols + val_cols) * ICW + 16

    art_cols = max(len(l) for l in art)
    cell_w, cell_h = ART_CELL_W, ART_CELL_W * 2
    art_w, art_h = art_cols * cell_w, len(art) * cell_h
    art_fs = cell_w / 0.6

    x_art = PAD
    x_box = PAD + art_w + GAP
    W = int(round(x_box + box_w + PAD))

    y0 = 112
    boxes_h = sum(box_height(len(r)) for _, r in sections) + BOX_GAP * (len(sections) - 1)
    boxes_bottom = y0 + boxes_h
    dots_y = boxes_bottom + 34
    prompt2_y = (dots_y if SHOW_DOTS else boxes_bottom) + 44
    H = int(prompt2_y + 30)

    area_top, area_bottom = y0 - 10, (dots_y + 6 if SHOW_DOTS else boxes_bottom)
    y_art = area_top + ((area_bottom - area_top) - art_h) / 2

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs><style>{font_css()}</style>'
         f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["BG1"]}"/>'
         f'<stop offset="1" stop-color="{T["BG2"]}"/></linearGradient>'
         f'<radialGradient id="glow" cx="0.88" cy="0.95" r="0.8"><stop offset="0" stop-color="{T["GLOW"]}" '
         f'stop-opacity="{T["GLOW_OP"]}"/><stop offset="1" stop-color="{T["GLOW"]}" stop-opacity="0"/></radialGradient>'
         '</defs>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="url(#bg)"/>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="url(#glow)"/>',
         f'<path d="M0.5 12.5 a12 12 0 0 1 12 -12 h{W-25} a12 12 0 0 1 12 12 v28 h-{W-1} z" fill="{T["TITLEBAR"]}"/>',
         f'<line x1="0.5" y1="40.5" x2="{W-0.5}" y2="40.5" stroke="{T["WIN_BORDER"]}"/>',
         f'<text x="{W/2}" y="26" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="700" '
         f'fill="{T["FG"]}">{esc(HOST)}:{esc(PATH)}</text>',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{T["WIN_BORDER"]}"/>']

    def text(x, y, content, fill, bold=False, anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        b = ' font-weight="700"' if bold else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" xml:space="preserve" font-family="{FONT}" '
                f'font-size="{IFS}"{a}{b} fill="{fill}">{esc(content)}</text>')

    prompt = (f'<tspan fill="{T["USER"]}" font-weight="700">{esc(HOST)}</tspan><tspan fill="{T["FG"]}">:</tspan>'
              f'<tspan fill="{T["PATHC"]}" font-weight="700">{esc(PATH)}</tspan><tspan fill="{T["FG"]}">$')
    o.append(f'<text x="{PAD}" y="76" xml:space="preserve" font-family="{FONT}" font-size="{IFS}">'
             f'{prompt} {esc(COMMAND)}</tspan></text>')

    # logo </>: cada caractere em posição exata da grade, na fonte do terminal; 3 tons de azul por densidade
    tiers = {"hi": T["ART_HI"], "mid": T["ART_MID"], "lo": T["ART_LO"]}
    for r, line in enumerate(art):
        groups = {"hi": [], "mid": [], "lo": []}
        for c, ch in enumerate(line):
            if ch != " ":
                groups["hi" if ch in "S$@#%" else "mid" if ch in "iI?+*=" else "lo"].append((c, ch))
        for tier, pts in groups.items():
            if pts:
                xs = " ".join(f"{x_art + c * cell_w:.2f}" for c, _ in pts)
                o.append(f'<text x="{xs}" y="{y_art + (r + 0.78) * cell_h:.2f}" font-family="{FONT}" '
                         f'font-size="{art_fs:.2f}" font-weight="700" fill="{tiers[tier]}">'
                         f'{esc("".join(ch for _, ch in pts))}</text>')

    # caixas com título na borda e tracinhos em cada linha
    y = y0
    for title, rws in sections:
        n = len(rws)
        ybot = y + box_height(n)
        tw = len(title) * ICW + 16
        cx = x_box + box_w / 2
        seg = [f'M{x_box:.1f},{ybot:.1f} V{y:.1f} H{cx - tw / 2:.1f}',
               f'M{cx + tw / 2:.1f},{y:.1f} H{x_box + box_w:.1f} v5',
               f'M{x_box:.1f},{ybot:.1f} H{x_box + box_w:.1f} v-5']
        for i in range(n):
            ty = y + BOX_TOP + i * ILH - IFS * 0.32
            seg.append(f'M{x_box:.1f},{ty:.1f} h10')
        o.append(f'<path d="{" ".join(seg)}" fill="none" stroke="{T["BOX"]}" stroke-width="1.2"/>')
        o.append(text(cx, y + IFS * 0.32, title, T["TITLE"], anchor="middle"))
        for i, (k, v) in enumerate(rws):
            by = y + BOX_TOP + i * ILH
            o.append(text(x_box + TICK, by, k, T["KEY"], bold=True))
            o.append(text(x_box + TICK + key_cols * ICW, by, v, T["VAL"]))
        y = ybot + BOX_GAP

    if SHOW_DOTS:
        for i in range(8):
            o.append(f'<circle cx="{x_box + 8 + i * 17:.1f}" cy="{dots_y:.1f}" r="3.8" '
                     f'fill="{mix(T["DOT_LOW"], T["DOT_HIGH"], i / 7)}"/>')

    # rodapé: segundo prompt com cursor piscando
    o.append(f'<text x="{PAD}" y="{prompt2_y:.1f}" xml:space="preserve" font-family="{FONT}" font-size="{IFS}">{prompt}</tspan></text>')
    cx = PAD + ICW * (len(HOST) + len(PATH) + 3)
    o.append(f'<rect x="{cx:.1f}" y="{prompt2_y - IFS:.1f}" width="{ICW * 0.9:.1f}" height="{IFS * 1.15:.1f}" fill="{T["CURSOR"]}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" repeatCount="indefinite"/></rect>')
    o.append("</svg>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def main():
    stats = fetch_stats()
    build_svg(stats, "terminal-dark.svg", "dark")
    build_svg(stats, "terminal-light.svg", "light")
    build_svg(stats, "terminal.svg", "dark")  # mantém o arquivo antigo (compatível com o workflow atual)
    print("terminal-dark.svg, terminal-light.svg e terminal.svg gerados com sucesso.")


if __name__ == "__main__":
    main()
