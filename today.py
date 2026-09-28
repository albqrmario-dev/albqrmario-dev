import os
import re
import requests

USERNAME = os.environ.get("GH_USERNAME", "albqrmario-dev")
TOKEN = os.environ.get("GH_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

HOST = "albqrmario@GitHub"
PATH = "~/dev/profile"
COMMAND = "profilefetch"

# ---------- cores (tema terminal azul) ----------
BG = "#0b1622"
BORDER = "#1d3350"
TITLEBAR = "#10202f"
FG = "#c5d3e0"
DIM = "#7f93a8"
BLUE = "#5bbcff"
GREEN = "#c3e040"
WORD = "#eaf6ff"                      # destaque para o texto dentro da arte
HEAVY, MID, LIGHT = "#5bbcff", "#3a8fd9", "#25679f"
PALETTE = ["#4c5566", "#ff3b3b", "#b8d84a", "#ff9040", "#5bbcff", "#ffee99", "#99e6cc", "#b0b0b0"]

FONT = "'JetBrains Mono','Fira Code','DejaVu Sans Mono',Consolas,Menlo,monospace"
FS = 15                               # tamanho da fonte
CW = FS * 0.602                       # largura de um caractere monoespaçado
LH = 21                               # altura da linha da arte
IFS = 17                              # fonte dos dados e dos prompts
ICW = IFS * 0.602                     # largura de um caractere nos dados
ILH = 23                              # altura da linha dos dados
PAD = 36                              # margem lateral


def load_art():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "art.txt"), encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f.read().split("\n") if l.strip() != ""]


def gh_get(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_stats():
    stats = {"repos": "?", "stars": "?", "followers": "?", "commits": "?"}
    try:
        user = gh_get(f"https://api.github.com/users/{USERNAME}")
        stats["repos"] = user.get("public_repos", "?")
        stats["followers"] = user.get("followers", "?")
        repos, page = [], 1
        while True:
            batch = gh_get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}")
            if not batch:
                break
            repos.extend(batch)
            page += 1
        stats["stars"] = sum(r["stargazers_count"] for r in repos)
    except Exception as e:
        print(f"Aviso: falha ao buscar perfil/repos ({e}).")
    try:
        c = gh_get(f"https://api.github.com/search/commits?q=author:{USERNAME}&per_page=1")
        stats["commits"] = c.get("total_count", "?")
    except Exception as e:
        print(f"Aviso: falha ao buscar commits ({e}).")
    return stats


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def info_rows(stats):
    """('title',txt) | ('sep',) | ('kv',chave,valor) | ('head',txt) | ('blank',)"""
    return [
        ("title", HOST),
        ("sep",),
        ("kv", "OS", "Fedora Linux 44 (Workstation Edition)"),
        ("kv", "Shell", "bash"),
        ("kv", "Terminal", "Ptyxis"),
        ("kv", "Editor", "VSCode / Neovim"),
        ("blank",),
        ("kv", "Curso", "ADS @ IFPE Garanhuns"),
        ("kv", "Local", "Garanhuns, Pernambuco, Brasil"),
        ("kv", "Linguagens", "Python, Java, JavaScript, SQL"),
        ("kv", "Idiomas", "Português, Inglês"),
        ("kv", "Hobbies", "Desenvolvimento, DevOps"),
        ("blank",),
        ("head", "Contato"),
        ("kv", "Email", "marioalbuquerque.dev@gmail.com"),
        ("kv", "LinkedIn", "linkedin.com/in/albqrmario"),
        ("kv", "GitHub", f"github.com/{USERNAME}"),
        ("blank",),
        ("head", "GitHub Stats"),
        ("kv", "Repos", stats["repos"]),
        ("kv", "Stars", stats["stars"]),
        ("kv", "Followers", stats["followers"]),
        ("kv", "Commits", stats["commits"]),
    ]


WORDS = re.compile(r"(?<![A-Za-z])(NOT|MY|CUP|OF|TEA)(?![A-Za-z])")


def char_color(ch):
    if ch in "SYHDNMO":
        return HEAVY
    if ch in ":/+":
        return MID
    return LIGHT


def art_line_svg(line, x, y):
    colors = [char_color(c) for c in line]
    for m in WORDS.finditer(line):        # palavras dentro da xícara
        for i in range(m.start(), m.end()):
            colors[i] = WORD
    spans, i = [], 0
    while i < len(line):
        j = i
        while j < len(line) and colors[j] == colors[i] and (line[j] == " ") == (line[i] == " "):
            j += 1
        run = line[i:j]
        if run.strip() == "":
            spans.append(f"<tspan>{run}</tspan>")
        else:
            bold = ' font-weight="bold"' if colors[i] == WORD else ""
            spans.append(f'<tspan fill="{colors[i]}"{bold}>{esc(run)}</tspan>')
        i = j
    return (f'<text x="{x}" y="{y}" xml:space="preserve" font-family="{FONT}" font-size="{FS}" '
            f'textLength="{len(line) * CW:.1f}" lengthAdjust="spacing">{"".join(spans)}</text>')


def build_svg(stats, filename):
    art = load_art()
    rows = info_rows(stats)
    art_cols = max(len(l) for l in art)
    info_cols = max(max(len(r[1]) + 2 + len(str(r[2])) for r in rows if r[0] == "kv"), 31)
    gap = 9                                           # espaço entre a arte e os dados

    art_x = PAD
    info_x = PAD + (art_cols + gap) * CW
    W = int(round(info_x + info_cols * ICW + PAD + ICW / 2))
    x_end = W - PAD                                   # onde terminam as linhas ----- (antes da borda)

    top = 126                                         # y da 1ª linha da arte
    art_bottom = top + (len(art) - 1) * LH
    info_h = (len(rows) - 1) * ILH
    info_top = top + max(0, ((len(art) - 1) * LH - info_h) / 2)   # dados centralizados ao lado da arte
    bottom = max(art_bottom, info_top + info_h)
    gap_v = top - 76                                  # distância prompt 1 -> conteúdo
    prompt2_y = bottom + gap_v                        # mesma distância conteúdo -> prompt 2
    H = int(prompt2_y + 36)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
         f'<path d="M0.5 12.5 a12 12 0 0 1 12 -12 h{W-25} a12 12 0 0 1 12 12 v32 h-{W-1} z" fill="{TITLEBAR}"/>',
         f'<text x="{W/2}" y="28" text-anchor="middle" font-family="{FONT}" font-size="13" '
         f'font-weight="bold" fill="{FG}">{esc(HOST)}:{esc(PATH)}</text>']

    prompt = (f'<tspan fill="{GREEN}" font-weight="bold">{esc(HOST)}</tspan><tspan fill="{FG}">:</tspan>'
              f'<tspan fill="{BLUE}" font-weight="bold">{esc(PATH)}</tspan><tspan fill="{FG}">$')
    o.append(f'<text x="{PAD}" y="78" xml:space="preserve" font-family="{FONT}" font-size="{IFS}">'
             f'{prompt} {esc(COMMAND)}</tspan></text>')

    for i, line in enumerate(art):
        o.append(art_line_svg(line, art_x, top + i * LH))

    def rule(x0, y, dashed):
        """Linha desenhada (não texto): vai exatamente até x_end, com qualquer fonte."""
        ly = y - IFS * 0.30
        dash = f' stroke-dasharray="{ICW * 0.64:.1f} {ICW * 0.36:.1f}"' if dashed else ""
        return (f'<line x1="{x0:.1f}" y1="{ly:.1f}" x2="{x_end:.1f}" y2="{ly:.1f}" '
                f'stroke="{DIM}" stroke-width="1.4"{dash}/>')

    for i, row in enumerate(rows):
        y = info_top + i * ILH
        kind = row[0]
        base = f'<text x="{info_x:.1f}" y="{y:.1f}" xml:space="preserve" font-family="{FONT}" font-size="{IFS}"'
        if kind == "title":
            cx_title = (info_x + x_end) / 2               # centro da linha ----- logo abaixo
            o.append(f'<text x="{cx_title:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="{IFS}" font-weight="bold" fill="{FG}">{esc(row[1])}</text>')
        elif kind == "sep":
            o.append(rule(info_x, y, True))
        elif kind == "head":
            o.append(f'{base} fill="{DIM}">─ <tspan fill="{FG}" font-weight="bold">{esc(row[1])}</tspan></text>')
            o.append(rule(info_x + (len(row[1]) + 3) * ICW, y, False))
        elif kind == "kv":
            o.append(f'{base}><tspan fill="{BLUE}" font-weight="bold">{esc(row[1])}</tspan>'
                     f'<tspan fill="{FG}">: {esc(row[2])}</tspan></text>')

    o.append(f'<text x="{PAD}" y="{prompt2_y:.1f}" xml:space="preserve" font-family="{FONT}" font-size="{IFS}">{prompt}</tspan></text>')
    cx = PAD + ICW * (len(HOST) + len(PATH) + 3)
    o.append(f'<rect x="{cx:.1f}" y="{prompt2_y - IFS:.1f}" width="{ICW * 0.9:.1f}" height="{IFS * 1.15:.1f}" fill="#f0b840">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" repeatCount="indefinite"/></rect>')
    o.append("</svg>")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def main():
    build_svg(fetch_stats(), "terminal.svg")
    print("terminal.svg gerado com sucesso.")


if __name__ == "__main__":
    main()
