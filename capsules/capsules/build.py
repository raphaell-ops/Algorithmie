#!/usr/bin/env python3
"""Génère les capsules reveal.js du cours d'algo (B1) dans ./site/."""
import html
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
CDN = sys.argv[1] if len(sys.argv) > 1 else "https://cdn.jsdelivr.net/npm"
# Les feuilles de style sont intégrées dans chaque fichier (lues depuis un
# `npm i reveal.js@5.1.0 highlight.js@11.9.0`) ; seuls les scripts viennent du CDN.
NM = os.environ.get("NODE_MODULES", "node_modules")


def vendor_css():
    import re
    parts = []
    for rel in ["reveal.js/dist/reset.css", "reveal.js/dist/reveal.css",
                "reveal.js/dist/theme/white.css", "highlight.js/styles/atom-one-dark.min.css"]:
        txt = open(os.path.join(NM, rel), encoding="utf-8").read()
        txt = re.sub(r"@import[^;]+;", "", txt)  # polices du thème non utilisées
        parts.append(txt)
    return "\n".join(parts)

# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(s, quote=False)


def code(src, lang="go", lines=None, sm=False):
    attr = f' data-line-numbers="{lines}"' if lines else ""
    return f'<pre{" class=sm" if sm else ""}><code class="language-{lang}" data-trim{attr}>{esc(src)}</code></pre>'


def stk(vals, label, hl=(), dim=False):
    cells = "".join(
        f'<div class="cell{" hl" if i in hl else ""}">{v}</div>' for i, v in enumerate(vals)
    ) or '<div class="cell empty">vide</div>'
    return (f'<div class="stk{" dim" if dim else ""}"><div class="top">sommet</div>'
            f'<div class="cells">{cells}</div><div class="lbl">{label}</div></div>')


def ab(a, b, hla=(), hlb=()):
    return f'<div class="ab">{stk(a, "A", hla)}{stk(b, "B", hlb)}</div>'


def trans(a0, b0, op, a1, b1, hl0=((), ()), hl1=((), ())):
    return (f'<div class="trans">{ab(a0, b0, *hl0)}'
            f'<div class="op"><span>{op}</span><div class="arrow">&rarr;</div></div>'
            f'{ab(a1, b1, *hl1)}</div>')


def ring(buf, head, n, caption=""):
    cap = len(buf)
    used = {(head + i) % cap: i for i in range(n)}
    cells = []
    for k, v in enumerate(buf):
        cls = "rc used" if (k in used or head < 0) else "rc free"
        if k == head and n > 0:
            cls += " head"
        pos = f'<div class="pos">{used[k]}</div>' if k in used else '<div class="pos">&nbsp;</div>'
        val = v if (k in used and v is not None) else ("" if v is None else v)
        mark = '<div class="hm">head</div>' if k == head else '<div class="hm">&nbsp;</div>'
        cells.append(f'<div class="rcol">{mark}<div class="{cls}">{val}</div><div class="ix">[{k}]</div>{pos}</div>')
    cap_html = f'<div class="rcap">{caption}</div>' if caption else ""
    return f'<div class="ring">{"".join(cells)}</div>{cap_html}'


def items(*xs):
    out = []
    for i, x in enumerate(xs, 1):
        out.append(f'<div class="item"><span class="num">{i:02d}</span><div>{x}</div></div>')
    return f'<div class="items">{"".join(out)}</div>'


def sol(body, label="Solution"):
    return f'<div class="fragment sol"><div class="sol-t">{label}</div>{body}</div>'


def cols(left, right, ratio="1fr 1fr"):
    return f'<div class="cols" style="grid-template-columns:{ratio}"><div>{left}</div><div>{right}</div></div>'


def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="t {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


ACCENTS = {1: ("#00eaff", "0,234,255", "Cyan"), 2: ("#859cff", "133,156,255", "Violet"),
           3: ("#ff84ef", "255,132,239", "Rose"), 4: ("#eeff57", "238,255,87", "Jaune"),
           5: ("#5affb6", "90,255,182", "Menthe"), 6: ("#4a8cff", "74,140,255", "Bleu"),
           7: ("#ff1a1a", "255,26,26", "Rouge")}


class Deck:
    def __init__(self, num, slug, title, subtitle, kicker):
        self.num, self.slug, self.title, self.subtitle, self.kicker = num, slug, title, subtitle, kicker
        self.accent, self.accent_rgb, _ = ACCENTS[num]
        self.slides = []

    def s(self, title, body, foot=None, notes=None, tag=None, cls=""):
        k = f"CAPSULE {self.num:02d} · {tag or self.kicker}"
        f = f'<div class="foot">{foot}</div>' if foot else ""
        n = f'<aside class="notes">{notes}</aside>' if notes else ""
        light = "exo" in cls or "recap" in cls
        bg = ' data-background-color="#eaf0eb"' if light else ""
        cls = (cls + " light").strip() if light else cls
        self.slides.append(
            f'<section class="{cls}"{bg}><div class="kicker">{k}</div><h2>{title}</h2>'
            f'<div class="body">{body}</div>{f}{n}</section>')

    def ex(self, n, title, body, solution, notes=None):
        self.s(f'<span class="exn">Exercice {n}</span> {title}', body + sol(solution),
               tag="PRATIQUE", notes=notes, cls="exo")

    def cover(self, goals, notes=None):
        g = items(*goals)
        self.slides.insert(0,
            f'<section class="cover"><div class="kicker">CAPSULE {self.num:02d} · ALGO B1 · PROJET PILES</div>'
            f'<h1>{self.title}</h1><div class="gradbar"></div><p class="sub">{self.subtitle}</p>'
            f'<div class="goals"><div class="gl">Objectifs</div>{g}</div>'
            + (f'<aside class="notes">{notes}</aside>' if notes else "") + '</section>')

    def recap(self, points, nxt=None):
        body = items(*points)
        if nxt:
            body += f'<p class="next">Capsule suivante : {nxt}</p>'
        self.s("À retenir", body, tag="SYNTHÈSE", cls="recap")

    def render(self, extra_js=""):
        return PAGE.format(
            title=f"Capsule {self.num:02d} – {self.title}", cdn=CDN, vendor=VENDOR,
            css=CSS + f":root{{--accent:{self.accent};--accent-rgb:{self.accent_rgb}}}",
            slides="\n".join(self.slides), extra_js=extra_js)


CSS = r"""
/* Charte Ynov : neutres noir #0a0006 / gris #eaf0eb (50/50), palette en accent,
   dégradé uniquement sur fond noir. Slides de cours sur noir, pratique et synthèse sur gris. */
:root{
 --noir:#0a0006;--gris:#eaf0eb;--blanc:#ffffff;
 --rouge:#ff1a1a;--rose:#ff84ef;--jaune:#eeff57;--menthe:#5affb6;--cyan:#00eaff;--violet:#859cff;--bleu:#4a8cff;--vert:#018e4d;
 --grad:linear-gradient(90deg,#ff1a1a,#ff84ef 18%,#859cff 36%,#4a8cff 50%,#00eaff 66%,#5affb6 82%,#eeff57);
 --f-display:"Newsreader","Source Serif 4",Georgia,"DejaVu Serif",serif;
 --f-body:"Inter","Helvetica Neue",Arial,"DejaVu Sans",sans-serif;
 --f-mono:"JetBrains Mono","DejaVu Sans Mono",Menlo,Consolas,monospace;
 --bg:var(--noir);--ink:var(--gris);--muted:#9ea39f;--line:#2b2530;--card:#16101b;
 --accent-ink:var(--accent);--accent-soft:rgba(var(--accent-rgb),.16);--hatch:#1d1722;
 --code-bg:#17111c;
}
section.light{--bg:var(--gris);--ink:var(--noir);--muted:#4f5450;--line:#c4ccc6;--card:var(--blanc);
 --accent-ink:var(--noir);--accent-soft:rgba(10,0,6,.07);--hatch:#dde3de}
html,body,.reveal-viewport{background:var(--noir)}
.reveal{font-family:var(--f-body);color:var(--ink);font-size:30px}
.reveal .slides{text-align:left}
.reveal .slides section{height:100%;padding:44px 64px 0 64px;box-sizing:border-box;color:var(--ink)}
.reveal h1,.reveal h2{font-family:var(--f-display);color:var(--ink);text-transform:none;letter-spacing:-.005em;font-weight:500;text-wrap:balance}
.reveal h1{font-size:2.6em;margin:.25em 0 .2em;line-height:1.05}
.reveal h2{font-size:1.65em;margin:.12em 0 .5em;line-height:1.12}
.reveal p{margin:.35em 0;line-height:1.45}
.reveal strong{color:var(--ink);font-weight:700}
.reveal code{font-family:var(--f-mono);font-size:.86em}
.reveal :not(pre)>code{background:var(--accent-soft);color:var(--accent-ink);padding:.05em .3em;border-radius:4px}
.reveal pre{width:100%;margin:.4em 0;box-shadow:none;font-size:.66em;border-radius:8px;overflow:hidden;border:1px solid #2b2530}
.reveal pre code,.reveal pre code.hljs{max-height:470px;padding:14px 18px;line-height:1.45;border-radius:8px;background:var(--code-bg)}
.kicker{color:var(--accent-ink);font-weight:700;font-size:.58em;letter-spacing:.1em;text-transform:uppercase}
.sub{font-size:1.05em;color:var(--muted)}
.body{font-size:.9em}
.foot{position:absolute;left:64px;right:64px;bottom:22px;border-top:1px solid var(--line);padding-top:12px;
 color:var(--ink);font-weight:700;font-size:.66em;line-height:1.35}
.foot::before{content:"";display:inline-block;width:.55em;height:.55em;border-radius:50%;background:var(--accent);margin-right:.5em;vertical-align:.05em}
.items{display:flex;flex-direction:column;gap:.45em}
.item{display:grid;grid-template-columns:2.4em 1fr;align-items:baseline;line-height:1.38}
.num{color:var(--accent-ink);font-weight:700;font-size:1em;font-family:var(--f-mono)}
/* cover : fond noir, dégradé */
.cover .gradbar{height:6px;border-radius:3px;background:var(--grad);width:220px;margin:.2em 0 .6em}
.cover h1{font-size:2.7em}
.cover .goals{margin-top:1em;font-size:.82em}
.cover .gl{font-weight:700;color:var(--muted);text-transform:uppercase;font-size:.66em;letter-spacing:.1em;margin-bottom:.5em}
.cols{display:grid;gap:36px;align-items:start}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:.3em 0}
.card h3{font-family:var(--f-body);font-size:.72em;margin:0 0 .35em;color:var(--accent-ink);text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.note{border:1px solid var(--line);border-left:5px solid var(--accent);background:var(--card);padding:10px 16px;border-radius:0 8px 8px 0;margin:.5em 0;font-size:.9em}
.warn{border-left-color:var(--jaune)}.bad{border-left-color:var(--rouge)}.good{border-left-color:var(--menthe)}
.tag{display:inline-block;font-weight:700;font-size:.68em;padding:.12em .5em;border-radius:5px;letter-spacing:.06em;font-family:var(--f-mono)}
.tag.ok{background:var(--menthe);color:var(--noir)}.tag.ko{background:var(--rouge);color:var(--blanc)}
.tag.err{background:var(--jaune);color:var(--noir)}
/* tables */
table.t{border-collapse:collapse;width:100%;font-size:.78em;margin:.3em 0}
table.t th{text-align:left;color:var(--muted);font-size:.8em;text-transform:uppercase;letter-spacing:.08em;border-bottom:1px solid var(--ink);padding:6px 10px;font-weight:700}
table.t td{border-bottom:1px solid var(--line);padding:7px 10px;vertical-align:top;color:var(--ink)}
table.t td:first-child{font-weight:700}
/* piles */
.ab{display:flex;gap:22px;align-items:flex-end}
.stk{display:flex;flex-direction:column;align-items:center;min-width:72px}
.stk .top{font-size:.48em;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:3px}
.stk .cells{display:flex;flex-direction:column;border:2px solid var(--ink);border-top:none;border-radius:0 0 8px 8px;padding:4px;gap:4px;min-height:40px;background:var(--card)}
.stk .cell{width:66px;height:40px;display:flex;align-items:center;justify-content:center;background:var(--accent-soft);color:var(--ink);border-radius:5px;font-weight:700;font-size:.8em;font-family:var(--f-mono)}
.stk .cell.hl{background:var(--accent);color:var(--noir)}
.stk .cell.empty{background:none;color:var(--muted);font-weight:400;font-style:italic;font-size:.6em;font-family:var(--f-body)}
.stk .lbl{font-weight:700;margin-top:4px;font-size:.85em}
.trans{display:flex;align-items:center;gap:22px;margin:.3em 0}
.trans .op{display:flex;flex-direction:column;align-items:center;color:var(--accent-ink);font-weight:700}
.trans .op span{font-family:var(--f-mono);font-size:.9em}
.trans .arrow{font-size:1.6em;line-height:1}
/* tampon circulaire */
.ring{display:flex;gap:6px;margin:.4em 0 .1em}
.rcol{display:flex;flex-direction:column;align-items:center}
.rc{width:70px;height:52px;display:flex;align-items:center;justify-content:center;border-radius:6px;font-weight:700;font-size:.85em;font-family:var(--f-mono)}
.rc.used{background:var(--accent-soft);border:2px solid var(--accent);color:var(--ink)}
.rc.free{background:repeating-linear-gradient(45deg,var(--hatch),var(--hatch) 6px,transparent 6px,transparent 12px);border:2px dashed var(--muted);color:var(--muted)}
.rc.head{background:var(--accent);color:var(--noir)}
.ix{font-family:var(--f-mono);font-size:.55em;color:var(--muted);margin-top:3px}
.pos{font-size:.55em;color:var(--accent-ink);font-weight:700;height:1.2em}
.hm{font-size:.55em;font-weight:700;color:var(--accent-ink);height:1.3em}
.rcap{font-size:.7em;color:var(--muted)}
/* exercices (fond gris) */
.exo h2 .exn{display:inline-block;background:var(--accent);color:var(--noir);border-radius:6px;padding:.08em .45em;font-size:.5em;vertical-align:middle;margin-right:.35em;font-family:var(--f-body);font-weight:700;letter-spacing:.02em}
.sol{margin-top:.5em;border:1px solid var(--line);border-left:6px solid var(--noir);background:var(--card);border-radius:0 10px 10px 0;padding:10px 16px}
.sol .sol-t{display:inline-block;background:var(--noir);color:var(--gris);font-weight:700;font-size:.58em;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.35em;padding:.15em .55em;border-radius:4px}
.sol pre{font-size:.72em}
.reveal pre.sm{font-size:.56em}.sol pre.sm{font-size:.6em}
.recap .next{margin-top:1.2em;color:var(--muted);font-size:.85em}
/* barres */
.bars{display:flex;flex-direction:column;gap:6px;font-size:.62em}
.bar{display:grid;grid-template-columns:170px 1fr 90px;align-items:center;gap:10px}
.bar .b{height:22px;min-width:5px;border-radius:4px;background:var(--accent)}
.bar .b.alt{background:var(--rouge)}
.bar .v{font-weight:700;text-align:right;font-family:var(--f-mono)}
/* étapes */
.pipe{display:flex;align-items:stretch;gap:10px;margin:.4em 0;font-size:.72em}
.pipe .st{flex:1;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.pipe .st b{display:block;color:var(--accent-ink);margin-bottom:.2em}
.pipe .st.alert{border-color:var(--rouge)}.pipe .st.alert b{color:var(--rouge)}
.pipe .ar{display:flex;align-items:center;color:var(--accent-ink);font-weight:700;font-size:1.4em}
/* simulateur */
.sim{display:grid;grid-template-columns:330px 1fr;gap:30px;font-size:.8em}
.sim input{font-family:var(--f-mono);font-size:.8em;padding:6px 10px;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:6px;width:100%;box-sizing:border-box}
.sim .btns{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}
.sim button{font-family:var(--f-mono);font-size:.75em;padding:7px 0;border-radius:6px;border:1px solid var(--accent);background:transparent;color:var(--accent);font-weight:700;cursor:pointer}
.sim button:hover,.sim button:focus-visible{background:var(--accent);color:var(--noir);outline:none}
.sim button.sec{border-color:var(--muted);color:var(--muted)}
.sim button.sec:hover{background:var(--muted);color:var(--noir)}
.sim .hist{font-family:var(--f-mono);font-size:.6em;color:var(--muted);margin-top:10px;min-height:3em;word-break:break-word}
.sim .verdict{margin-top:8px}
.sim .view{display:flex;justify-content:center;align-items:flex-end;min-height:420px}
.small{font-size:.75em}.muted{color:var(--muted)}
.reveal .slide-number{background:transparent;color:#8a8f8b;font-size:14px;top:14px;bottom:auto;right:20px;font-family:var(--f-mono)}
.reveal .progress{color:var(--accent);height:4px}
.reveal .controls{color:var(--accent)}
@media print{.foot{position:static}}
"""

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;700&family=Newsreader:opsz,wght@6..72,500&display=swap">
<style>{vendor}</style>
<style>{css}</style>
</head>
<body>
<div class="reveal"><div class="slides">
{slides}
</div></div>
<script src="{cdn}/reveal.js@5.1.0/dist/reveal.js"></script>
<script src="{cdn}/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
<script src="{cdn}/reveal.js@5.1.0/plugin/notes/notes.js"></script>
<script>
Reveal.initialize({{width:1280,height:720,margin:0.04,center:false,hash:true,slideNumber:'c/t',
  transition:'fade',transitionSpeed:'fast',plugins:[RevealHighlight,RevealNotes]}});
{extra_js}
</script>
</body>
</html>
"""

decks = []

# ====================================================================
# 01 — Piles et instructions
# ====================================================================
d = Deck(1, "01-piles-et-instructions", "Les piles et les onze instructions",
         "Lire un état, appliquer une instruction à la main", "PILES")
d.cover([
    "Comprendre ce qu'est une pile et pourquoi on ne touche qu'à ses extrémités.",
    "Lire et écrire un état <code>A</code> / <code>B</code> sans ambiguïté.",
    "Appliquer à la main les onze instructions, y compris quand elles n'ont aucun effet.",
], notes="Capsule d'ouverture : on pose le vocabulaire et la notation qu'on utilisera dans toutes les autres capsules.")

d.s("Une pile, c'est une pile d'assiettes",
    cols(items(
        "On <strong>pose</strong> toujours une assiette sur le dessus.",
        "On <strong>prend</strong> toujours l'assiette du dessus.",
        "Le dessus s'appelle le <strong>sommet</strong>. La dernière posée est la première reprise : c'est le principe <strong>LIFO</strong> (<em>Last In, First Out</em>).",
        "Dans ce projet, on a aussi le droit de faire passer le sommet au <strong>fond</strong> et inversement : ce sont les rotations."),
        f'<div style="display:flex;justify-content:center;gap:40px">{stk([7, 4, 9, 2], "pile", hl=(0,))}</div>'
        '<p class="small muted" style="text-align:center">La case colorée est le sommet : la seule qu\'on peut retirer directement.</p>',
        "1.4fr 1fr"),
    foot="Une pile n'est pas un tableau : on ne lit pas « l'élément 3 », on travaille par le sommet.",
    notes="Insister sur le fait qu'on ne fait pas d'accès aléatoire. Toutes les instructions partent du sommet ou du fond.")

d.s("Le terrain de jeu : deux piles A et B",
    cols(items(
        "Au départ, <code>A</code> contient les nombres à trier, <code>B</code> est vide.",
        "Le but : finir avec <code>B</code> vide et <code>A</code> triée, le plus petit au sommet.",
        "On écrit une pile <strong>du sommet vers le fond</strong> : <code>A = [2 1 3]</code> signifie que 2 est au sommet."),
        ab([2, 1, 3], [], hla=(0,)), "1.3fr 1fr")
    + '<div class="note">Convention pour tout le cours : <strong>le premier nombre écrit est le sommet</strong>. Si vous la changez en cours de route, tous vos tests deviennent faux.</div>',
    foot="Départ : A = valeurs, B = vide. Arrivée : B vide, A croissante du sommet au fond.")

d.s("Échanger : <code>sa</code>, <code>sb</code>, <code>ss</code>",
    trans([2, 1, 3], [], "sa", [1, 2, 3], [], hl0=((0, 1), ()), hl1=((0, 1), ()))
    + items("<code>sa</code> échange les <strong>deux premiers</strong> éléments de A. <code>sb</code> fait pareil sur B.",
            "<code>ss</code> = <code>sa</code> puis <code>sb</code>.",
            "Moins de deux éléments ? L'instruction est <strong>valide mais ne fait rien</strong>."),
    foot="Swap : seuls les deux éléments du sommet bougent.")

d.s("Pousser : <code>pa</code>, <code>pb</code>",
    trans([1, 2, 3], [], "pb", [2, 3], [1], hl0=((0,), ()), hl1=((), (0,)))
    + items("<code>pb</code> retire le sommet de A et le pose au sommet de B.",
            "<code>pa</code> fait l'inverse : sommet de B &rarr; sommet de A.",
            "Pile de départ vide ? Rien ne se passe."),
    foot="Push : le nom désigne la pile qui reçoit. pb = « push vers B ».",
    notes="Erreur classique : croire que pa veut dire « prendre dans A ». Le nom indique la destination.")

d.s("Tourner : <code>ra</code>, <code>rb</code>, <code>rr</code>",
    trans([1, 2, 3, 4], [], "ra", [2, 3, 4, 1], [], hl0=((0,), ()), hl1=((3,), ()))
    + items("<code>ra</code> : le <strong>premier</strong> élément de A devient le <strong>dernier</strong>. Tout le reste remonte d'un cran.",
            "<code>rb</code> fait pareil sur B, <code>rr</code> = <code>ra</code> puis <code>rb</code>."),
    foot="Rotate : le sommet part au fond.")

d.s("Tourner à l'envers : <code>rra</code>, <code>rrb</code>, <code>rrr</code>",
    trans([1, 2, 3, 4], [], "rra", [4, 1, 2, 3], [], hl0=((3,), ()), hl1=((0,), ()))
    + items("<code>rra</code> : le <strong>dernier</strong> élément de A devient le <strong>premier</strong>.",
            "<code>rrb</code> fait pareil sur B, <code>rrr</code> = <code>rra</code> puis <code>rrb</code>.",
            "<code>ra</code> puis <code>rra</code> ramène toujours à l'état de départ."),
    foot="Reverse rotate : le fond remonte au sommet.")

d.s("Les onze instructions en un tableau",
    table(["Instruction", "Effet", "Sans effet si…"], [
        ["<code>sa</code> · <code>sb</code>", "échange les 2 premiers de A · de B", "moins de 2 éléments"],
        ["<code>ss</code>", "<code>sa</code> puis <code>sb</code>", "chaque moitié a sa propre condition"],
        ["<code>pa</code>", "sommet de B &rarr; sommet de A", "B vide"],
        ["<code>pb</code>", "sommet de A &rarr; sommet de B", "A vide"],
        ["<code>ra</code> · <code>rb</code>", "le premier devient le dernier", "moins de 2 éléments"],
        ["<code>rr</code>", "<code>ra</code> puis <code>rb</code>", "chaque moitié a sa propre condition"],
        ["<code>rra</code> · <code>rrb</code>", "le dernier devient le premier", "moins de 2 éléments"],
        ["<code>rrr</code>", "<code>rra</code> puis <code>rrb</code>", "chaque moitié a sa propre condition"],
    ]),
    foot="2 swaps + 1 double, 2 pushes, 2 rotations + 1 double, 2 rotations inverses + 1 double = 11.")

d.ex(1, "Dérouler une suite à la main",
     "<p>Départ : <code>A = [3 1 2]</code>, <code>B = []</code>. Appliquez dans l'ordre <code>sa</code>, <code>pb</code>, <code>ra</code>. Notez l'état après chaque instruction.</p>",
     cols(table(["Après", "A", "B"], [
         ["<code>sa</code>", "[1 3 2]", "[]"],
         ["<code>pb</code>", "[3 2]", "[1]"],
         ["<code>ra</code>", "[2 3]", "[1]"]]),
         ab([2, 3], [1]), "1.4fr 1fr"))

d.ex(2, "Trier avec le moins d'instructions possible",
     "<p>Pour chaque pile A (B est vide), trouvez la suite la plus courte qui la trie.</p>"
     + items("<code>A = [2 3 1]</code>", "<code>A = [3 1 2]</code>", "<code>A = [3 2 1]</code>"),
     items("<code>rra</code> &rarr; [1 2 3] : une seule instruction.",
           "<code>ra</code> &rarr; [1 2 3] : une seule instruction.",
           "<code>sa</code> &rarr; [2 3 1], puis <code>rra</code> &rarr; [1 2 3] : deux instructions."))

d.ex(3, "Les instructions sans effet",
     "<p>Donnez l'état final et dites quelles instructions n'ont rien fait.</p>"
     "<p>Départ : <code>A = [5]</code>, <code>B = []</code>. Suite : <code>sa</code>, <code>pa</code>, <code>pb</code>, <code>rb</code>, <code>ss</code>, <code>pa</code>.</p>",
     items("<code>sa</code> : A n'a qu'un élément, <strong>rien</strong>. <code>pa</code> : B vide, <strong>rien</strong>.",
           "<code>pb</code> : A = [], B = [5]. <code>rb</code> : un seul élément, <strong>rien</strong>. <code>ss</code> : <strong>rien</strong> des deux côtés.",
           "<code>pa</code> : A = [5], B = []. État final identique au départ, et les six instructions restent <strong>valides</strong>."),
     notes="Point clé pour la capsule suivante : une instruction sans effet n'est pas une erreur.")

SIM = """
<div class="sim">
  <div>
    <label class="small muted">Valeurs de départ (sommet en premier)</label>
    <input id="sim-in" value="2 1 3 6 5 8">
    <div class="btns">
      <button data-op="sa">sa</button><button data-op="sb">sb</button><button data-op="ss">ss</button>
      <button data-op="pa">pa</button><button data-op="pb">pb</button><button class="sec" id="sim-undo">annuler</button>
      <button data-op="ra">ra</button><button data-op="rb">rb</button><button data-op="rr">rr</button>
      <button data-op="rra">rra</button><button data-op="rrb">rrb</button><button data-op="rrr">rrr</button>
    </div>
    <button class="sec" id="sim-reset" style="width:100%;margin-top:6px">recommencer</button>
    <div class="hist" id="sim-hist"></div>
    <div class="verdict" id="sim-verdict"></div>
  </div>
  <div class="view" id="sim-view"></div>
</div>"""
d.s("Simulateur : à vous de jouer", SIM,
    foot="Défi : triez 2 1 3 6 5 8 en 8 instructions maximum.",
    notes="Faire la démo en direct : sa, pb, pb, pb, sa, pa, pa, pa.")

d.recap([
    "Une pile se lit <strong>du sommet vers le fond</strong>. On n'agit que sur le sommet et le fond.",
    "Onze instructions : swap (<code>s</code>), push (<code>p</code>), rotate (<code>r</code>), reverse rotate (<code>rr</code>) sur A, sur B ou sur les deux.",
    "Le nom d'un push désigne la pile <strong>qui reçoit</strong>.",
    "Une instruction qui n'a rien à faire est <strong>valide</strong> : elle ne fait rien, elle n'échoue pas.",
], nxt="02 · Contrats et invariants")

SIM_JS = r"""
(function(){
  const $=id=>document.getElementById(id); if(!$('sim-view')) return;
  let A=[],B=[],hist=[],snaps=[];
  const parse=()=>$('sim-in').value.trim().split(/\s+/).filter(Boolean).map(Number).filter(n=>!isNaN(n));
  const sw=s=>{if(s.length>=2){[s[0],s[1]]=[s[1],s[0]]}};
  const up=s=>{if(s.length>=2)s.push(s.shift())};
  const down=s=>{if(s.length>=2)s.unshift(s.pop())};
  const ops={sa:()=>sw(A),sb:()=>sw(B),ss:()=>{sw(A);sw(B)},
    pa:()=>{if(B.length)A.unshift(B.shift())},pb:()=>{if(A.length)B.unshift(A.shift())},
    ra:()=>up(A),rb:()=>up(B),rr:()=>{up(A);up(B)},rra:()=>down(A),rrb:()=>down(B),rrr:()=>{down(A);down(B)}};
  const col=(v,l)=>'<div class="stk"><div class="top">sommet</div><div class="cells">'+
    (v.length?v.map(x=>'<div class="cell">'+x+'</div>').join(''):'<div class="cell empty">vide</div>')+
    '</div><div class="lbl">'+l+'</div></div>';
  const sorted=()=>B.length===0&&A.every((x,i)=>i===0||A[i-1]<x);
  function draw(){
    $('sim-view').innerHTML='<div class="ab">'+col(A,'A')+col(B,'B')+'</div>';
    $('sim-hist').textContent=hist.length?hist.length+' instr. : '+hist.join(' '):'aucune instruction';
    $('sim-verdict').innerHTML=sorted()?'<span class="tag ok">TRIÉ</span>':'<span class="tag ko">PAS ENCORE</span>';
  }
  function reset(){A=parse();B=[];hist=[];snaps=[];draw()}
  document.querySelectorAll('.sim button[data-op]').forEach(b=>b.addEventListener('click',()=>{
    snaps.push([A.slice(),B.slice()]);ops[b.dataset.op]();hist.push(b.dataset.op);draw()}));
  $('sim-undo').addEventListener('click',()=>{if(snaps.length){[A,B]=snaps.pop();hist.pop();draw()}});
  $('sim-reset').addEventListener('click',reset);
  $('sim-in').addEventListener('change',reset);
  reset();
})();
"""
decks.append((d, SIM_JS))

# ====================================================================
# 02 — Contrats et invariants
# ====================================================================
d = Deck(2, "02-contrats-et-invariants", "Contrats et invariants",
         "Dire précisément ce qu'une instruction promet", "CONTRATS")
d.cover([
    "Écrire le contrat d'une fonction : quand elle agit, ce qu'elle fait, ce qu'elle fait sinon.",
    "Distinguer un cas <strong>sans effet</strong> d'un cas <strong>d'erreur</strong>.",
    "Identifier les invariants du moteur et les vérifier dans le code.",
])

d.s("Un contrat, c'est une promesse écrite",
    cols(items(
        "<strong>Précondition</strong> : ce qui doit être vrai pour que l'instruction agisse.",
        "<strong>Effet</strong> (postcondition) : l'état exact après l'instruction.",
        "<strong>Sinon</strong> : ce qui se passe quand la précondition est fausse."),
        '<div class="card"><h3>Contrat de pa</h3>'
        '<p><strong>Précondition :</strong> B non vide.</p>'
        '<p><strong>Effet :</strong> le sommet de B est retiré et posé au sommet de A. Le reste ne bouge pas.</p>'
        '<p><strong>Sinon :</strong> aucun changement, l\'instruction reste valide.</p></div>'),
    foot="Sans contrat écrit, impossible de savoir si un comportement est un bug ou un choix.",
    notes="Le contrat est écrit avant le code. C'est lui qui sert de référence aux tests.")

d.s("Écrire l'effet avec précision",
    '<p>« Déplace un élément » ne suffit pas. Il faut pouvoir calculer l\'état d\'arrivée <strong>sans exécuter le code</strong>.</p>'
    + table(["Avant", "Instruction", "Après"], [
        ["A = [a₀ a₁ … aₙ], B = [b₀ b₁ … bₘ]", "<code>pa</code>", "A = [b₀ a₀ a₁ … aₙ], B = [b₁ … bₘ]"],
        ["A = [a₀ a₁ a₂ … aₙ]", "<code>ra</code>", "A = [a₁ a₂ … aₙ a₀]"],
        ["A = [a₀ … aₙ₋₁ aₙ]", "<code>rra</code>", "A = [aₙ a₀ … aₙ₋₁]"],
        ["A = [a₀ a₁ a₂ …]", "<code>sa</code>", "A = [a₁ a₀ a₂ …]"],
    ])
    + '<div class="note">Avec cette notation, on peut écrire les tests <strong>sur papier</strong>, avant même la première ligne de Go.</div>',
    foot="Un bon contrat permet de prédire le résultat à la main.")

d.s("Le contrat dans le code Go",
    code('''
// Apply exécute une instruction. Contrats :
//
//   sa  : échange les deux premiers éléments de A. Sans effet si |A| < 2.
//   pa  : retire le sommet de B et le pose au sommet de A. Sans effet si B est vide.
//   ra  : le premier élément de A devient le dernier. Sans effet si |A| < 2.
//   ...
//
// Une instruction sans effet reste valide.
// Une instruction inconnue renvoie ErrUnknownOp et ne modifie rien.
func (e *Engine) Apply(op Op) error {
	switch op {
	case PA:
		if e.b.Len() > 0 {          // précondition
			e.a.pushTop(e.b.popTop()) // effet
		}                             // sinon : rien
	// ...
	default:
		return fmt.Errorf("%w: %q", ErrUnknownOp, op)
	}
	return nil
}''', sm=True),
    foot="Le commentaire au-dessus de la fonction EST le contrat : go doc l'affiche.")

d.s("Sans effet ≠ erreur",
    cols('<div class="card"><h3><span class="tag ok">valide</span> sans effet</h3>'
         '<p><code>pa</code> avec B vide, <code>sa</code> avec 1 élément.</p>'
         '<p>L\'instruction existe. Sa précondition est fausse, donc elle ne fait rien. On continue normalement.</p>'
         '<p class="small muted">Retour : <code>nil</code></p></div>',
         '<div class="card"><h3><span class="tag err">erreur</span> inconnue</h3>'
         '<p><code>"xx"</code>, <code>"SA"</code>, <code>"sa "</code>.</p>'
         '<p>L\'instruction n\'existe pas. On refuse <strong>sans toucher à l\'état</strong>.</p>'
         '<p class="small muted">Retour : <code>ErrUnknownOp</code></p></div>')
    + '<div class="note warn">Une erreur ne doit jamais laisser l\'état à moitié modifié : on vérifie <strong>avant</strong> d\'agir.</div>',
    foot="Une erreur dit « je ne peux pas » ; une instruction sans effet dit « il n'y avait rien à faire ».")

d.s("Les invariants : ce qui reste vrai quoi qu'il arrive",
    cols(items(
        "<strong>Conservation</strong> : <code>|A| + |B| = N</code> en permanence.",
        "<strong>Permutation</strong> : l'ensemble des valeurs ne change jamais. Aucune n'apparaît, aucune ne disparaît.",
        "<strong>Pas d'allocation</strong> : aucune instruction ne crée de mémoire (voir capsule 06)."),
        trans([3, 1, 2], [], "pb", [1, 2], [3])
        + '<p class="small muted" style="text-align:center">N = 3 avant, 2 + 1 = 3 après. Valeurs {1, 2, 3} des deux côtés.</p>',
        "1fr 1.1fr"),
    foot="Un invariant est vrai avant ET après chaque instruction. S'il casse, il y a un bug.")

d.ex(1, "Écrire le contrat de <code>rra</code>",
     "<p>Rédigez la précondition, l'effet (avec la notation a₀ … aₙ) et le cas « sinon ».</p>",
     items("<strong>Précondition :</strong> A contient au moins 2 éléments.",
           "<strong>Effet :</strong> A = [a₀ … aₙ₋₁ aₙ] devient [aₙ a₀ … aₙ₋₁]. B ne change pas.",
           "<strong>Sinon :</strong> aucun changement, instruction valide."))

d.ex(2, "Quel état viole un invariant ?",
     "<p>Départ : <code>A = [4 2 1 3]</code>, <code>B = []</code> (N = 4). Après quelques instructions, on observe :</p>"
     + table(["", "A", "B"], [["a", "[1 2]", "[3 4]"], ["b", "[1 2 3]", "[3]"], ["c", "[]", "[4 3 2 1]"], ["d", "[1 2 3 4 5]", "[]"]]),
     items("<strong>a</strong> et <strong>c</strong> sont possibles.",
           "<strong>b</strong> : 3 apparaît deux fois et 4 a disparu. La permutation est cassée.",
           "<strong>d</strong> : 5 éléments au lieu de 4. La conservation est cassée."))

d.ex(3, "Le cas de <code>ss</code>",
     "<p><code>A = [7]</code>, <code>B = [1 2 3]</code>. Que donne <code>ss</code> ? Le contrat de <code>ss</code> est-il « sans effet si l'une des piles a moins de 2 éléments » ?</p>",
     "<p>Résultat : <code>A = [7]</code>, <code>B = [2 1 3]</code>. Non : <code>ss</code> = <code>sa</code> puis <code>sb</code>, et <strong>chacun vérifie sa propre précondition</strong>. Seul <code>sb</code> agit ici.</p>")

d.ex(4, "Vérifier les invariants en Go",
     "<p>Écrivez <code>checkInvariants(t, e, want)</code> : elle échoue si la taille totale change ou si les valeurs ne sont plus les mêmes que <code>want</code>.</p>",
     code('''
func checkInvariants(t *testing.T, e *Engine, want []int) {
	s := e.Snapshot()
	all := append(append([]int{}, s.A...), s.B...)
	if len(all) != len(want) {
		t.Fatalf("conservation : %d éléments, attendu %d", len(all), len(want))
	}
	got, exp := slices.Clone(all), slices.Clone(want)
	slices.Sort(got)
	slices.Sort(exp)
	if !slices.Equal(got, exp) {
		t.Fatalf("permutation cassée : %v, attendu %v", got, exp)
	}
}'''))

d.recap([
    "Un contrat = <strong>précondition</strong> + <strong>effet</strong> + <strong>sinon</strong>. On l'écrit avant le code.",
    "L'effet doit permettre de calculer l'état d'arrivée <strong>à la main</strong>.",
    "Instruction sans effet : valide. Instruction inconnue : erreur, et l'état n'est pas modifié.",
    "Invariants du moteur : <code>|A| + |B| = N</code> et mêmes valeurs. On peut les vérifier après chaque instruction.",
], nxt="03 · Tester : cas normaux, cas limites")
decks.append((d, ""))

# ====================================================================
# 03 — Tester
# ====================================================================
d = Deck(3, "03-tester", "Tester : cas normaux, cas limites",
         "Un test ne construit pas son résultat attendu avec la fonction testée", "TESTS")
d.cover([
    "Trouver les cas limites d'une instruction.",
    "Écrire des tests en tableau (<em>table-driven</em>) en Go.",
    "Comprendre pourquoi l'attendu doit venir d'ailleurs que de la fonction testée.",
    "Vérifier qu'un test attrape vraiment les bugs.",
])

d.s("Anatomie d'un test",
    '<div class="pipe"><div class="st"><b>1. État de départ</b>A = [2 1 3], B = []</div><div class="ar">&rarr;</div>'
    '<div class="st"><b>2. Action</b><code>Apply(SA)</code></div><div class="ar">&rarr;</div>'
    '<div class="st"><b>3. Attendu</b>A = [1 2 3], B = []<br><span class="small muted">écrit à la main</span></div><div class="ar">&rarr;</div>'
    '<div class="st"><b>4. Comparaison</b>obtenu == attendu ?</div></div>'
    + code('''
func TestSaNormal(t *testing.T) {
	e := New([]int{2, 1, 3})                       // 1
	e.Apply(SA)                                    // 2
	want := []int{1, 2, 3}                         // 3
	if got := e.Snapshot().A; !slices.Equal(got, want) { // 4
		t.Errorf("A = %v, attendu %v", got, want)
	}
}'''),
    foot="Chaque test vérifie UNE chose, avec un attendu écrit à la main.")

d.s("Cas normaux et cas limites",
    cols('<div class="card"><h3>Cas normal</h3><p>La situation habituelle : la précondition est vraie, avec des piles « confortables ».</p><p><code>sa</code> sur [2 1 3]</p></div>'
         '<div class="card"><h3>Cas limite</h3><p>Le bord du domaine : là où les bugs se cachent.</p></div>',
         table(["Limite", "Exemple pour sa"], [
             ["pile vide", "A = []"],
             ["1 élément", "A = [5]"],
             ["juste assez", "A = [9 4] (exactement 2)"],
             ["valeurs extrêmes", "−2147483648, 0, négatifs"],
             ["l'autre pile", "B non vide ne doit pas bouger"]]),
         "1fr 1.2fr"),
    foot="Pour chaque instruction : au moins un cas normal, et chaque frontière de sa précondition.")

d.s("La règle d'or",
    cols('<div class="note bad"><strong>Interdit</strong>' + code('''
e := New([]int{1, 2, 3, 4})
e.Apply(RA)

ref := New([]int{1, 2, 3, 4})
ref.Apply(RA)            // attendu calculé
want := ref.Snapshot().A // par la fonction testée !

if !slices.Equal(e.Snapshot().A, want) { ... }''') + '</div>',
         '<div class="note good"><strong>Correct</strong>' + code('''
e := New([]int{1, 2, 3, 4})
e.Apply(RA)

want := []int{2, 3, 4, 1} // écrit à la main
                          // depuis le contrat

if !slices.Equal(e.Snapshot().A, want) { ... }''') + '</div>'),
    foot="Un test ne doit pas construire son résultat attendu avec la fonction testée.",
    notes="C'est la phrase en bas de la slide du projet. Expliquer le pourquoi sur la slide suivante.")

d.s("Pourquoi ? Le test qui ne peut pas échouer",
    '<div class="pipe"><div class="st"><b>Bug dans ra</b>ra renvoie [1 2 3 4] (rien ne bouge)</div><div class="ar">&rarr;</div>'
    '<div class="st"><b>Attendu calculé par ra</b>[1 2 3 4]</div><div class="ar">&rarr;</div>'
    '<div class="st"><b>Obtenu</b>[1 2 3 4]</div><div class="ar">&rarr;</div>'
    '<div class="st alert"><b>Résultat</b>test vert, bug invisible</div></div>'
    + items("Si l'attendu vient du code testé, le test compare le code à <strong>lui-même</strong>. Il passe toujours.",
            "L'attendu doit venir d'une source <strong>indépendante</strong> : le contrat, un calcul à la main, une valeur du sujet.",
            "Même chose pour l'état de départ : on le construit sans passer par l'instruction qu'on teste."),
    foot="Un test qui ne peut pas échouer ne prouve rien.")

d.s("Tests en tableau (table-driven)",
    code('''
func TestInstructions(t *testing.T) {
	cases := []struct {
		name         string
		a, b         []int
		op           Op
		wantA, wantB []int
	}{
		{"sa normal", []int{2, 1, 3}, []int{}, SA, []int{1, 2, 3}, []int{}},
		{"sa 1 élément", []int{5}, []int{}, SA, []int{5}, []int{}},
		{"pa B vide", []int{1, 2}, []int{}, PA, []int{1, 2}, []int{}},
		{"ra normal", []int{1, 2, 3, 4}, []int{}, RA, []int{2, 3, 4, 1}, []int{}},
	}
	for _, c := range cases {
		e := build(c.a, c.b) // état posé directement, sans Apply
		e.Apply(c.op)
		s := e.Snapshot()
		if !slices.Equal(s.A, c.wantA) || !slices.Equal(s.B, c.wantB) {
			t.Errorf("%s : A=%v B=%v, attendu A=%v B=%v", c.name, s.A, s.B, c.wantA, c.wantB)
		}
	}
}''', sm=True),
    foot="Ajouter un cas = ajouter une ligne. Le nom du cas apparaît dans le message d'erreur.")

d.s("Tester ses tests : injecter un bug",
    cols(items(
        "On casse volontairement le code : on change un <code>&lt;</code> en <code>&lt;=</code>, on supprime une ligne, on inverse deux indices.",
        "On relance <code>go test</code>.",
        "Si les tests restent verts, il manque un cas. On l'ajoute."),
        table(["Bug injecté", "Attrapé par"], [
            ["garde <code>n &lt; 2</code> supprimée dans sa", "« sa 1 élément »"],
            ["rra recopie le mauvais élément", "« rra normal »"],
            ["pb oublie de décrémenter A", "« pb normal »"],
            ["Snapshot partage la mémoire", "test de stabilité (capsule 07)"]]),
        "1fr 1.2fr"),
    foot="Cette technique s'appelle le mutation testing : chaque bug injecté doit faire échouer au moins un test.")

d.ex(1, "Les cas limites de <code>pb</code>",
     "<p>Listez les situations à tester pour <code>pb</code>, avec l'attendu de chacune.</p>",
     table(["Cas", "Départ", "Attendu"], [
         ["normal", "A = [1 2 3], B = []", "A = [2 3], B = [1]"],
         ["A vide", "A = [], B = [1]", "inchangé"],
         ["A devient vide", "A = [4], B = [9]", "A = [], B = [4 9]"],
         ["B déjà rempli", "A = [4 5], B = [9]", "A = [5], B = [4 9]"]]))

d.ex(2, "Trouvez le problème",
     code('''
func TestRrr(t *testing.T) {
	e := New([]int{1, 2, 3})
	e.Apply(PB)
	e.Apply(RRR)
	want := New([]int{1, 2, 3})
	want.Apply(PB)
	want.Apply(RRA)
	want.Apply(RRB)
	if !reflect.DeepEqual(e.Snapshot(), want.Snapshot()) { t.Fail() }
}''', sm=True),
     items("L'attendu est calculé avec le moteur testé (<code>RRA</code>, <code>RRB</code>, et même <code>PB</code>). Si <code>rra</code> est faux, le test reste vert.",
           "Correction : écrire l'attendu à la main. Après <code>pb</code> : A = [2 3], B = [1]. Après <code>rrr</code> : <strong>A = [3 2], B = [1]</strong>.",
           "<code>t.Fail()</code> sans message : en cas d'échec, on ne sait pas ce qui ne va pas. Utiliser <code>t.Errorf</code>."))

d.ex(3, "Écrire la table de <code>rra</code>",
     "<p>Écrivez trois lignes de table : un cas normal, un cas « deux éléments », un cas « un élément ».</p>",
     code('''
{"rra normal",   []int{1, 2, 3, 4}, []int{}, RRA, []int{4, 1, 2, 3}, []int{}},
{"rra deux",     []int{1, 2},       []int{}, RRA, []int{2, 1},       []int{}},
{"rra un seul",  []int{1},          []int{7}, RRA, []int{1},         []int{7}},'''))

d.recap([
    "Un test = départ, action, <strong>attendu écrit à la main</strong>, comparaison avec un message clair.",
    "Cas limites : pile vide, 1 élément, exactement le minimum, valeurs extrêmes, l'autre pile.",
    "L'attendu et l'état de départ ne passent <strong>jamais</strong> par la fonction testée.",
    "Pour tester ses tests : injecter un bug, au moins un test doit échouer.",
], nxt="04 · Le vérificateur")
decks.append((d, ""))

# ====================================================================
# 04 — Vérificateur
# ====================================================================
d = Deck(4, "04-le-verificateur", "Le vérificateur",
         "Lire, valider, exécuter, juger : OK, KO ou Error", "VÉRIFICATEUR")
d.cover([
    "Comprendre le rôle du vérificateur et ses trois verdicts.",
    "Valider une entrée de façon stricte (arguments et instructions).",
    "Écrire le contrat d'arrivée et le tester.",
    "Concevoir un programme testable sans terminal.",
])

d.s("Le rôle du vérificateur",
    '<div class="pipe">'
    '<div class="st"><b>Arguments</b><code>./checker 3 2 1</code><br>&rarr; pile A</div><div class="ar">&rarr;</div>'
    '<div class="st"><b>Entrée standard</b>une instruction par ligne<br><code>sa</code><br><code>rra</code></div><div class="ar">&rarr;</div>'
    '<div class="st"><b>Moteur</b>exécute chaque instruction (capsules 01 à 03)</div><div class="ar">&rarr;</div>'
    '<div class="st"><b>Verdict</b><span class="tag ok">OK</span> <span class="tag ko">KO</span> <span class="tag err">Error</span></div></div>'
    + items("Le vérificateur ne trie rien. Il <strong>juge</strong> une suite écrite par quelqu'un d'autre.",
            "Il est <strong>indépendant</strong> du programme qui produit la suite : c'est l'arbitre."),
    foot="Le vérificateur répond à une seule question : cette suite trie-t-elle ces valeurs ?")

d.s("Trois verdicts, trois sens différents",
    table(["Verdict", "Signifie", "Exemples"], [
        ['<span class="tag err">Error</span>', "L'entrée est mal formée : impossible de juger.", "argument <code>abc</code>, doublon, <code>2147483648</code>, instruction <code>xx</code>, ligne vide"],
        ['<span class="tag ko">KO</span>', "L'entrée est correcte, mais l'arrivée ne respecte pas le contrat.", "suite incomplète, B non vide à la fin, A pas croissante"],
        ['<span class="tag ok">OK</span>', "B vide et A strictement croissante du sommet au fond.", "<code>3 2 1</code> + <code>sa</code>, <code>rra</code>"],
    ])
    + '<div class="note"><code>Error</code> s\'écrit sur la <strong>sortie d\'erreur</strong> (stderr) avec un code de sortie non nul. <code>OK</code> et <code>KO</code> s\'écrivent sur la sortie standard.</div>',
    foot="Error = « je ne peux pas juger ». KO = « j'ai jugé, c'est faux ».")

d.s("Valider les arguments",
    cols(code('''
func ParseArgs(args []string) ([]int, error) {
	var out []int
	seen := map[int]bool{}
	for _, arg := range args {
		fields := strings.Fields(arg) // "3 2 1" accepté
		if len(fields) == 0 {
			return nil, ErrBadArg      // argument vide
		}
		for _, f := range fields {
			n, err := strconv.ParseInt(f, 10, 32)
			if err != nil {
				return nil, ErrBadArg  // pas un int32
			}
			if seen[int(n)] {
				return nil, ErrDuplicate
			}
			seen[int(n)] = true
			out = append(out, int(n))
		}
	}
	return out, nil
}''', sm=True),
         items("<code>ParseInt(f, 10, 32)</code> refuse <code>1.5</code>, <code>abc</code> et tout ce qui dépasse int32.",
               "Une <code>map</code> détecte les doublons en une passe.",
               "On refuse <strong>tout</strong> au premier problème, sans exécuter quoi que ce soit."),
         "1.35fr 1fr"))

d.s("Lire les instructions : être strict",
    cols(items(
        "Une ligne = une instruction, comparée <strong>exactement</strong> aux onze noms.",
        "<code>SA</code>, <code>sa </code> (espace), ligne vide : refusés.",
        "Piège : <code>bufio.ScanLines</code> retire un <code>\\r</code> final. <code>\"sa\\r\\n\"</code> serait accepté. Pour un contrat strict, on découpe sur <code>\\n</code> uniquement."),
        code('''
func ParseOp(s string) (Op, error) {
	for _, op := range AllOps {
		if string(op) == s {
			return op, nil
		}
	}
	return "", fmt.Errorf("%w: %q", ErrUnknownOp, s)
}''')),
    foot="Être tolérant sur l'entrée, c'est accepter des suites que le sujet refuse.")

d.s("Le contrat d'arrivée",
    cols(code('''
// Sorted : B vide ET A strictement croissante
// du sommet vers le fond. Lecture seule.
func (e *Engine) Sorted() bool {
	if e.LenB() != 0 {
		return false
	}
	for i := 1; i < e.LenA(); i++ {
		if e.a.At(i-1) >= e.a.At(i) {
			return false
		}
	}
	return true
}'''),
         ab([1, 2, 3], [], hla=()) + '<p class="small"><span class="tag ok">OK</span></p>'
         + ab([1, 2], [3]) + '<p class="small"><span class="tag ko">KO</span> B non vide</p>'),
    foot="Les deux conditions sont obligatoires. A triée avec B non vide, c'est KO.")

d.s("Concevoir pour tester",
    cols(code('''
// main.go : 3 lignes
func main() {
	os.Exit(checker.Run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}

// checker_test.go : pas besoin de terminal
func TestKO(t *testing.T) {
	var out, errOut bytes.Buffer
	Run([]string{"1", "2", "3"}, strings.NewReader("pb\\n"), &out, &errOut)
	if out.String() != "KO\\n" {
		t.Errorf("stdout = %q", out.String())
	}
}'''),
         items("<code>Run</code> reçoit des <code>io.Reader</code> / <code>io.Writer</code> au lieu d'utiliser directement <code>os.Stdin</code>.",
               "En test, on lui passe une chaîne et des buffers.",
               "<code>main</code> ne contient plus aucune logique à tester."),
         "1.4fr 1fr"))

d.ex(1, "Donnez le verdict",
     table(["#", "Commande", "Entrée standard"], [
         ["1", "<code>./checker 2 1</code>", "<code>sa</code>"],
         ["2", "<code>./checker 2 1</code>", "<code>sa</code>, <code>sa</code>"],
         ["3", "<code>./checker 1 2 3</code>", "<code>pb</code>"],
         ["4", "<code>./checker 1 2 2</code>", "(rien)"],
         ["5", "<code>./checker 2 1</code>", "<code>Sa</code>"],
         ["6", "<code>./checker 1 2 3</code>", "(rien)"]]),
     '<p>1 <span class="tag ok">OK</span> · 2 <span class="tag ko">KO</span> (retour au départ) · 3 <span class="tag ko">KO</span> (B non vide) · '
     '4 <span class="tag err">Error</span> (doublon) · 5 <span class="tag err">Error</span> (majuscule) · 6 <span class="tag ok">OK</span> (déjà trié)</p>')

d.ex(2, "Suite incomplète ou arrivée hors contrat ?",
     "<p>La suite <code>sa pb pb pb sa pa pa pa</code> trie <code>2 1 3 6 5 8</code>. On retire la dernière ligne. Quel est le verdict, et quel est l'état final ?</p>",
     cols("<p><span class='tag ko'>KO</span>. Toutes les lignes sont valides, donc pas d'Error. Mais il reste 1 dans B.</p>",
          ab([2, 3, 5, 6, 8], [1]), "1.2fr 1fr"))

d.ex(3, "Écrire les tests du vérificateur",
     "<p>Écrivez une table de test pour <code>Run</code> qui couvre : une commande inconnue, une suite incomplète, une arrivée hors contrat, une suite correcte.</p>",
     code('''
{"inconnue",    []string{"2", "1"},    "sa\\nxx\\n",   "",     "Error\\n"},
{"incomplète",  []string{"2", "1", "3", "6", "5", "8"},
                "sa\\npb\\npb\\npb\\nsa\\npa\\npa\\n",    "KO\\n", ""},
{"hors contrat",[]string{"1", "2", "3"}, "pb\\n",      "KO\\n", ""},
{"correcte",    []string{"3", "2", "1"}, "sa\\nrra\\n", "OK\\n", ""},'''))

d.recap([
    "Le vérificateur juge une suite, il ne trie pas.",
    "<code>Error</code> : entrée mal formée. <code>KO</code> : entrée correcte, arrivée fausse. <code>OK</code> : B vide et A strictement croissante.",
    "Validation stricte : int32, doublons, onze noms exacts, pas d'espace ni de <code>\\r</code>.",
    "Passer <code>io.Reader</code> / <code>io.Writer</code> en paramètre rend le programme testable.",
], nxt="05 · Représenter les données")
decks.append((d, ""))

# ====================================================================
# 05 — Représentation
# ====================================================================
d = Deck(5, "05-representer-les-donnees", "Représenter les données",
         "Un même contrat, plusieurs façons de stocker une pile", "REPRÉSENTATION")
d.cover([
    "Séparer le <strong>comportement</strong> (le contrat) de la <strong>représentation</strong> (le stockage).",
    "Comparer tranche, liste chaînée et tampon circulaire.",
    "Calculer des indices avec le modulo, y compris en reculant.",
])

d.s("Le contrat ne dit pas comment stocker",
    items("Le contrat de <code>ra</code> dit : « le premier devient le dernier ». Il ne dit rien sur la mémoire.",
          "Plusieurs représentations respectent le même contrat, et passent les <strong>mêmes tests</strong>.",
          "Elles diffèrent par leur <strong>coût</strong> : nombre d'écritures, copies, allocations.")
    + '<div class="note">C\'est pour ça que les tests de la capsule 03 ne regardent que <code>Snapshot()</code> : ils restent valables si on change de représentation.</div>',
    foot="Choisir une représentation = choisir quelles opérations seront rapides.")

d.s("Option 1 : une tranche, sommet à l'indice 0",
    cols('<div class="ring">' + "".join(
        f'<div class="rcol"><div class="hm">{"sommet" if i == 0 else "&nbsp;"}</div><div class="rc used">{v}</div><div class="ix">[{i}]</div></div>'
        for i, v in enumerate([1, 2, 3, 4])) + '</div>'
        + '<p class="small"><code>pb</code> : on retire <code>s[0]</code>, puis <strong>tout le reste se décale</strong> d\'une case vers la gauche.</p>'
        + '<p class="small"><code>ra</code> : pareil, chaque élément est réécrit.</p>',
        table(["Instruction", "Écritures"], [["sa", "2"], ["pa / pb", "≈ n"], ["ra / rra", "≈ n"]])),
    foot="Simple à écrire, mais chaque push ou rotation coûte proportionnellement à la taille de la pile : O(n).")

d.s("Options 2 et 3",
    cols('<div class="card"><h3>Tranche, sommet à la fin</h3>'
         '<p><code>pa</code>/<code>pb</code> = <code>append</code> / retirer le dernier : rapide.</p>'
         '<p>Mais <code>ra</code>/<code>rra</code> déplacent toujours tout : O(n). Or les rotations sont les instructions les plus fréquentes.</p></div>',
         '<div class="card"><h3>Liste chaînée</h3>'
         '<p>Toutes les instructions en O(1) si on garde un pointeur sur le sommet et sur le fond.</p>'
         '<p>Mais <strong>une allocation par nœud</strong>, un pointeur en plus par valeur, et des éléments dispersés en mémoire.</p></div>'),
    foot="Aucune de ces deux options n'est rapide ET sans allocation.")

d.s("Option 4 : le tampon circulaire",
    ring([8, 6, None, 2, 4], 3, 4, "capacité 5, head = 3, n = 4 &rarr; la pile est [2 4 8 6]")
    + items("Un tableau de taille fixe N, alloué <strong>une seule fois</strong>.",
            "<code>head</code> = indice du sommet. <code>n</code> = nombre d'éléments.",
            "La pile « fait le tour » : après la dernière case, on revient à la case 0.",
            "Le petit numéro sous chaque case occupée donne sa position dans la pile (0 = sommet)."),
    foot="On ne déplace plus les éléments : on déplace l'indice head.",
    notes="Montrer le chemin : case 3, case 4, retour à 0, case 1. La case 2 est libre.")

d.s("Calculer un indice avec le modulo",
    cols(code('''
// position i (0 = sommet) -> case du tableau
func (d *deque) idx(i int) int {
	return (d.head + i) % len(d.buf)
}

// poser au sommet : head recule d'une case
func (d *deque) pushTop(v int) {
	d.head = (d.head - 1 + len(d.buf)) % len(d.buf)
	d.buf[d.head] = v
	d.n++
}'''),
         items("<code>(head + i) % cap</code> : avancer de i cases en faisant le tour.",
               "Pour reculer, on ajoute <code>cap</code> avant le modulo.",
               "Pourquoi ? En Go, <code>-1 % 5</code> vaut <strong>-1</strong>, pas 4. Le résultat garde le signe de la valeur de gauche.")),
    foot="Recul = (head − 1 + cap) % cap. Sans le « + cap », on obtient un indice négatif et le programme plante.")

d.s("<code>ra</code> sur une pile pleine : zéro écriture",
    '<p class="small muted">Pile pleine (n = cap = 4) : A = [1 2 3 4]</p>'
    + ring([1, 2, 3, 4], 0, 4)
    + '<p style="color:var(--accent);font-weight:800">ra : head = (0 + 1) % 4 = 1</p>'
    + ring([1, 2, 3, 4], 1, 4, "A = [2 3 4 1] : le 1 est maintenant au fond, sans qu'aucune case n'ait été réécrite"),
    foot="Si la pile n'est pas pleine, on recopie le sommet dans la case libre sous le fond : 1 seule écriture.")

d.s("Comparaison",
    table(["Représentation", "pa / pb", "ra / rra", "Allocations", "Mémoire"], [
        ["Tranche, sommet en 0", "O(n)", "O(n)", "aucune", "N par pile"],
        ["Tranche, sommet à la fin", "O(1)", "O(n)", "aucune*", "N par pile"],
        ["Liste chaînée", "O(1)", "O(1)", "1 par push", "N nœuds + pointeurs"],
        ["<strong>Tampon circulaire</strong>", "<strong>O(1)</strong>", "<strong>O(1)</strong>", "<strong>aucune</strong>", "N par pile"]])
    + '<p class="small muted">* si la capacité est réservée à N dès le départ.</p>',
    foot="Le tampon circulaire est le seul à être O(1) partout sans allouer. C'est la représentation retenue.")

d.ex(1, "Lire un tampon circulaire",
     "<p>Capacité 6, <code>head = 4</code>, <code>n = 4</code>. Le tableau vaut :</p>"
     + ring([10, 20, 30, 40, 50, 60], -1, 0)
     + "<p>Quelle est la pile, du sommet au fond ? Quelles cases sont libres ?</p>",
     "<p>Cases 4, 5, 0, 1 &rarr; <strong>[50 60 10 20]</strong>. Les cases 2 et 3 sont libres : leur contenu (30, 40) n'a pas de sens.</p>")

d.ex(2, "Poser un élément",
     "<p>Même tampon (head = 4, n = 4). On fait <code>pushTop(7)</code>. Que valent <code>head</code>, <code>n</code> et la pile ?</p>",
     "<p><code>head = (4 − 1 + 6) % 6 = 3</code>, <code>buf[3] = 7</code>, <code>n = 5</code>. Pile : <strong>[7 50 60 10 20]</strong>.</p>"
     + ring([10, 20, 30, 7, 50, 60], 3, 5))

d.ex(3, "Le modulo en Go",
     "<p>Que valent <code>-1 % 5</code>, <code>(-1 + 5) % 5</code> et <code>(3 + 4) % 5</code> en Go ? Que se passe-t-il si on écrit <code>head = (head - 1) % cap</code> avec <code>head = 0</code> ?</p>",
     "<p><code>-1</code>, <code>4</code>, <code>2</code>. Avec <code>head = 0</code>, on obtient <code>head = -1</code> et <code>buf[-1]</code> provoque un <strong>panic: index out of range</strong>.</p>")

d.recap([
    "Le contrat décrit le comportement, la représentation décide du coût.",
    "Tranche : simple, mais push ou rotation en O(n). Liste chaînée : O(1), mais une allocation par nœud.",
    "Tampon circulaire : tableau fixe + <code>head</code> + <code>n</code>. Tout en O(1), aucune allocation.",
    "Indices : <code>(head + i) % cap</code> pour avancer, <code>(head − 1 + cap) % cap</code> pour reculer.",
], nxt="06 · Mesurer les coûts")
decks.append((d, ""))

# ====================================================================
# 06 — Coûts
# ====================================================================
d = Deck(6, "06-mesurer-les-couts", "Mesurer les coûts",
         "Mutations, copies, allocations : compter au lieu de deviner", "COÛTS")
d.cover([
    "Savoir ce qu'on compte : mutations, copies, allocations.",
    "Instrumenter le code pour obtenir des chiffres reproductibles.",
    "Lire un benchmark Go et en tirer une conclusion.",
])

d.s("Deux codes corrects, deux coûts très différents",
    '<p>10 000 instructions aléatoires, même résultat final. Écritures en mémoire par instruction :</p>'
    '<div class="bars">'
    + "".join(f'<div class="bar"><span>N = {n} · {lbl}</span><div><div class="b{" alt" if alt else ""}" style="width:{w}%"></div></div><span class="v">{v}</span></div>'
              for n, lbl, w, v, alt in [
                  (3, "anneau", 0.5, "0,70", False), (3, "tranche", 0.8, "1,70", True),
                  (100, "anneau", 0.6, "1,45", False), (100, "tranche", 20, "54,23", True),
                  (500, "anneau", 0.6, "1,49", False), (500, "tranche", 100, "268,57", True)])
    + '</div>'
    + '<p class="small muted">Mesuré sur l\'implémentation du projet (graine aléatoire fixe).</p>',
    foot="Avec la tranche, le coût grandit avec N. Avec le tampon circulaire, il reste constant.")

d.s("Ce qu'on compte",
    table(["Mesure", "Définition", "Exemple"], [
        ["Mutation", "une écriture d'un élément dans une case", "<code>sa</code> = 2 mutations"],
        ["Copie", "un élément recopié en bloc vers une autre zone", "<code>Snapshot()</code> = N copies"],
        ["Allocation", "une demande de mémoire neuve au runtime Go", "<code>make</code>, <code>append</code> qui dépasse la capacité"]])
    + '<div class="note">On compte ce qui ne dépend pas de la machine. Le temps (ns) varie d\'un PC à l\'autre, le nombre de mutations ne varie jamais.</div>',
    foot="Un chiffre reproductible vaut mieux qu'une impression de lenteur.")

d.s("Instrumenter le code",
    cols(code('''
type Stats struct {
	Ops       int // instructions appliquées
	Mutations int // écritures de case
	Copies    int // éléments recopiés en bloc
}

func (d *deque) swapTop() {
	if d.n < 2 {
		return
	}
	i, j := d.idx(0), d.idx(1)
	d.buf[i], d.buf[j] = d.buf[j], d.buf[i]
	d.stats.Mutations += 2
}'''),
         items("Un compteur par type de coût, incrémenté <strong>là où l'écriture a lieu</strong>.",
               "Le compteur fait partie du moteur : on peut le vérifier dans les tests.",
               "Un test peut affirmer : « <code>sa</code> coûte exactement 2 mutations »."),
         "1.3fr 1fr"))

d.s("Benchmarks et allocations en Go",
    cols(code('''
func BenchmarkRing(b *testing.B) {
	e := New(values500)
	for i := 0; i < b.N; i++ {
		e.Apply(seq[i%len(seq)])
	}
}

func TestNoAllocationPerOp(t *testing.T) {
	e := New([]int{5, 4, 3, 2, 1, 0})
	allocs := testing.AllocsPerRun(100, func() {
		e.Apply(PB); e.Apply(RA); e.Apply(PA)
	})
	if allocs != 0 {
		t.Errorf("%v allocations", allocs)
	}
}'''),
         code('''
$ go test -bench=. -benchmem ./stack/
BenchmarkRing    9.709 ns/op   0 B/op   0 allocs/op
BenchmarkNaive  275.0  ns/op   0 B/op   0 allocs/op''', "text")
         + items("<code>ns/op</code> : temps moyen par itération.",
                 "<code>B/op</code>, <code>allocs/op</code> : mémoire allouée par itération.",
                 "<code>AllocsPerRun</code> transforme « zéro allocation » en test qui peut échouer.")),
    foot="Benchmark pour comparer, test d'allocation pour garantir.")

d.ex(1, "Compter à la main (tranche)",
     "<p>Représentation tranche, sommet en 0. <code>A</code> a 5 éléments, <code>B</code> en a 2. Combien de mutations pour <code>pb</code> ? Et avec le tampon circulaire ?</p>",
     items("Retirer de A : les 4 éléments restants se décalent &rarr; <strong>4</strong> mutations.",
           "Poser sur B : les 2 éléments se décalent, puis on écrit le nouveau &rarr; <strong>3</strong> mutations.",
           "Total tranche : <strong>7</strong>. Tampon circulaire : <strong>1</strong> (on écrit seulement la nouvelle case de B)."))

d.ex(2, "Compter les rotations",
     "<p>Combien de mutations pour <code>ra</code> sur une pile de 6 éléments, avec chaque représentation ?</p>",
     table(["Représentation", "Mutations", "Pourquoi"], [
         ["Tranche", "6", "5 décalages + 1 écriture au fond"],
         ["Anneau, pile pleine", "0", "seul head change"],
         ["Anneau, pile non pleine", "1", "on recopie le sommet sous le fond"]]))

d.ex(3, "Lire un benchmark",
     "<p>Résultats : <code>BenchmarkRing 9.7 ns/op</code>, <code>BenchmarkNaive 275 ns/op</code>, avec N = 500. Combien de fois le tampon est-il plus rapide ? Pourquoi le chiffre exact change-t-il sur votre PC ?</p>",
     "<p>275 / 9,7 &asymp; <strong>28 fois</strong> plus rapide. Le temps dépend du processeur, de la charge et du cache : c'est pour ça qu'on compte aussi les mutations, qui elles ne changent pas.</p>")

d.recap([
    "On compte les <strong>mutations</strong>, les <strong>copies</strong> et les <strong>allocations</strong> : des chiffres reproductibles.",
    "On instrumente le code avec des compteurs, et on vérifie ces compteurs dans les tests.",
    "<code>go test -bench=. -benchmem</code> mesure le temps et la mémoire. <code>testing.AllocsPerRun</code> garantit zéro allocation.",
    "Une mesure sert à <strong>justifier</strong> un choix de représentation, pas à le deviner.",
], nxt="07 · Copies et stabilité des états")
decks.append((d, ""))

# ====================================================================
# 07 — Copies et stabilité
# ====================================================================
d = Deck(7, "07-copies-et-stabilite", "Copies et stabilité des états",
         "Quand un état conservé change sans prévenir", "STABILITÉ")
d.cover([
    "Comprendre qu'une tranche Go est une <strong>vue</strong> sur un tableau partagé.",
    "Repérer les situations d'aliasing (deux noms pour la même mémoire).",
    "Placer les copies aux bons endroits, et seulement là.",
])

d.s("Une tranche n'est pas un tableau",
    cols('<div class="card"><h3>En-tête de tranche</h3><p><code>ptr</code> &rarr; tableau</p><p><code>len</code> = 3</p><p><code>cap</code> = 3</p></div>'
         '<p class="small">Copier une tranche (<code>t := s</code>) copie seulement l\'en-tête. Le tableau derrière est <strong>le même</strong>.</p>',
         code('''
s := []int{1, 2, 3}
t := s       // même tableau
t[0] = 99
fmt.Println(s) // [99 2 3]'''),
         "1fr 1.2fr")
    + '<div class="note warn">Deux variables qui voient la même mémoire : c\'est l\'<strong>aliasing</strong>. Modifier l\'une modifie l\'autre.</div>',
    foot="Pour obtenir une vraie copie, il faut make + copy.")

d.s("Le danger pour le moteur",
    cols(items(
        "<strong>À l'entrée</strong> : si <code>New(values)</code> garde <code>values</code> tel quel, l'appelant peut modifier la pile A sans passer par une instruction.",
        "<strong>À la sortie</strong> : si <code>Snapshot()</code> renvoie le tableau interne, l'état « conservé » change à chaque instruction.",
        "Dans les deux cas, les invariants peuvent casser sans qu'aucune instruction ne soit fausse."),
        code('''
before := e.Snapshot()   // on garde l'état
e.Apply(PB)
fmt.Println(before.A)
// si Snapshot partage la mémoire :
// before.A a changé !'''),
        "1.1fr 1fr"),
    foot="Un état conservé doit rester figé, quoi que fasse le moteur ensuite.")

d.s("Copier aux frontières, pas ailleurs",
    cols(code('''
func New(values []int) *Engine {
	// ...
	copy(e.a.buf, values)    // copie à l'entrée
	e.Stats.Copies += len(values)
	return e
}

func (d *deque) snapshot() []int {
	out := make([]int, d.n)  // mémoire neuve
	for i := range out {
		out[i] = d.At(i)
	}
	d.stats.Copies += d.n    // copie à la sortie
	return out
}'''),
         items("On copie quand une donnée <strong>entre</strong> dans le moteur ou en <strong>sort</strong>.",
               "Les instructions ne copient jamais : elles travaillent dans le tampon interne.",
               "<code>Sorted()</code>, <code>LenA()</code> lisent sans copier. Le vérificateur ne paie qu'<strong>une</strong> copie, à la fin."),
         "1.3fr 1fr"),
    foot="Une copie coûte N. On la paie quand elle protège quelque chose, pas par réflexe.")

d.s("Prouver la stabilité par un test",
    code('''
func TestSnapshotIsStable(t *testing.T) {
	e := New([]int{1, 2, 3, 4})
	before := e.Snapshot()
	for _, op := range []Op{PB, PB, SA, SB, RA, RRB} {
		e.Apply(op)
	}
	if !slices.Equal(before.A, []int{1, 2, 3, 4}) || len(before.B) != 0 {
		t.Errorf("un instantané conservé a changé : %+v", before)
	}
	after := e.Snapshot()
	after.A[0] = -100                     // on abîme la copie
	if e.Snapshot().A[0] == -100 {
		t.Error("l'instantané partage la mémoire du moteur")
	}
}'''),
    foot="On teste les deux sens : le moteur ne modifie pas la copie, la copie ne modifie pas le moteur.")

d.ex(1, "Prédire la sortie",
     code('''
x := []int{1, 2, 3, 4}
y := x[1:3]
y[0] = 20
fmt.Println(x, len(y), cap(y))'''),
     "<p><code>[1 20 3 4] 2 3</code>. <code>y</code> commence à la case 1 de <code>x</code> : modifier <code>y[0]</code> modifie <code>x[1]</code>. La capacité va jusqu'à la fin du tableau : 4 − 1 = 3.</p>")

d.ex(2, "Le piège de <code>append</code>",
     code('''
a := make([]int, 3, 10)
b := append(a, 4)
c := append(a, 5)
fmt.Println(b[3], c[3])'''),
     "<p><code>5 5</code>. <code>a</code> a de la place (cap 10), donc les deux <code>append</code> écrivent dans <strong>la même case</strong> du même tableau. Le second écrase le premier.</p>")

d.ex(3, "Écrire un test pour <code>New</code>",
     "<p>Écrivez un test qui échoue si <code>New</code> garde une référence vers la tranche de l'appelant.</p>",
     code('''
func TestNewDoesNotAliasInput(t *testing.T) {
	in := []int{3, 1, 2}
	e := New(in)
	in[0] = 99 // l'appelant modifie sa tranche
	if got := e.Snapshot().A; !slices.Equal(got, []int{3, 1, 2}) {
		t.Errorf("le moteur partage la tranche : %v", got)
	}
}'''))

d.recap([
    "Une tranche Go est un en-tête (<code>ptr</code>, <code>len</code>, <code>cap</code>) sur un tableau qui peut être partagé.",
    "Aliasing : deux noms pour la même mémoire. <code>t := s</code>, <code>x[1:3]</code> et <code>append</code> peuvent en créer.",
    "Le moteur copie <strong>à l'entrée</strong> (<code>New</code>) et <strong>à la sortie</strong> (<code>Snapshot</code>), jamais dans les instructions.",
    "La stabilité se prouve par un test dans les deux sens.",
], nxt="retour au projet : le moteur testé, le vérificateur et l'analyse des coûts")
decks.append((d, ""))

# ---------------------------------------------------------------- index

INDEX = """<title>Capsules algo B1</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;700&family=Newsreader:opsz,wght@6..72,500&display=swap">
<style>
/* Charte Ynov, fond noir uniquement (le dégradé n'existe que sur noir) : liste verticale de capsules. */
:root{{--noir:#0a0006;--gris:#eaf0eb;--muted:#9ea39f;--line:#2b2530;--card:#16101b;
 --grad:linear-gradient(90deg,#ff1a1a,#ff84ef 18%,#859cff 36%,#4a8cff 50%,#00eaff 66%,#5affb6 82%,#eeff57);
 --f-display:"Newsreader","Source Serif 4",Georgia,serif;--f-body:"Inter","Helvetica Neue",Arial,sans-serif;
 --f-mono:"JetBrains Mono",Menlo,Consolas,monospace;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--noir);color:var(--gris);font-family:var(--f-body)}}
main{{max-width:920px;margin:0 auto;padding-block:56px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.k{{color:var(--muted);font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase}}
h1{{font-family:var(--f-display);font-weight:500;font-size:clamp(34px,6vw,56px);margin:.25em 0 .2em;line-height:1.05;text-wrap:balance}}
.gb{{height:5px;width:160px;border-radius:3px;background:var(--grad);margin:14px 0 18px}}
p.lead{{color:var(--muted);font-size:16px;max-width:620px;line-height:1.55;margin:0}}
ol{{list-style:none;padding:0;margin:36px 0 0;display:grid;gap:10px}}
a.c{{display:grid;grid-template-columns:52px 1fr auto;align-items:center;gap:14px;background:var(--card);border:1px solid var(--line);
 border-left:5px solid var(--a);border-radius:4px 12px 12px 4px;padding:16px 18px;color:inherit;text-decoration:none;transition:border-color .15s,transform .15s}}
a.c>span{{min-width:0}}
a.c:hover{{border-color:var(--a);transform:translateX(3px)}}
a.c:focus-visible{{outline:2px solid var(--a);outline-offset:3px}}
.n{{color:var(--a);font-weight:700;font-size:22px;font-family:var(--f-mono)}}
.t{{font-family:var(--f-display);font-weight:500;font-size:22px;line-height:1.2}}
.s{{color:var(--muted);font-size:14px;margin-top:4px;line-height:1.4}}
.m{{color:var(--muted);font-size:12px;white-space:nowrap;font-family:var(--f-mono)}}
.help{{margin-top:36px;color:var(--muted);font-size:14px;line-height:1.7;border-top:1px solid var(--line);padding-top:16px}}
kbd,code{{font-family:var(--f-mono);font-size:12px;border:1px solid var(--line);border-radius:4px;padding:0 5px;color:var(--gris)}}
@media (max-width:560px){{a.c{{grid-template-columns:40px 1fr}}.m{{display:none}}}}
@media (prefers-reduced-motion:reduce){{a.c{{transition:none}}a.c:hover{{transform:none}}}}
</style>
<main>
<div class="k">Ynov Toulouse · Algo B1 · Projet piles</div>
<h1>Capsules de cours</h1>
<div class="gb"></div>
<p class="lead">Une capsule par thème, à suivre dans l'ordre. Chacune contient des explications, des schémas et des exercices dont la solution s'affiche au clic suivant.</p>
<ol>{items}</ol>
<p class="help">Navigation : flèches ou <kbd>Espace</kbd>. <kbd>S</kbd> ouvre la vue orateur avec les notes. <kbd>Échap</kbd> donne la vue d'ensemble. Pour exporter en PDF, ajoutez <code>?print-pdf</code> à l'adresse puis imprimez.</p>
</main>"""


def main():
    global VENDOR
    VENDOR = vendor_css()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for deck, js in decks:
        fn = f"{deck.slug}.html"
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(deck.render(js))
        n_ex = sum(1 for s in deck.slides if 'class="exo"' in s)
        rows.append(f'<li><a class="c" href="{fn}" style="--a:{deck.accent}"><span class="n">{deck.num:02d}</span>'
                    f'<span><div class="t">{deck.title}</div><div class="s">{deck.subtitle}</div></span>'
                    f'<span class="m">{len(deck.slides)} slides · {n_ex} exercices</span></a></li>')
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX.format(items="".join(rows)))
    print(f"{len(decks)} capsules -> {OUT}")


main()
