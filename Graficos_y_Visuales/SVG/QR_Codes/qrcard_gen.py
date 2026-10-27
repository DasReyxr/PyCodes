"""
qrcard_gen.py - Tarjeta QR parametrizable a partir de una plantilla SVG (pensado para Jupyter).

Cómo funciona el color
----------------------
Todo el contenido (QR, logos y textos) se dibuja en BLANCO dentro de un <mask> SVG.
Después se pinta UN solo rectángulo del color elegido a través de esa máscara:

    contenido blanco  ->  máscara  ->  rect(color)  ->  tarjeta de un solo color

Consecuencias:
  * Cambiar de color es cambiar un atributo: no se recolorea ningún PNG.
  * El fondo es transparente (fuera del contenido la máscara vale 0), salvo que pidas `background`.
  * El canal alfa de los logos y el antialiasing de los textos se respetan.

Uso
---
    from qrcard_gen import QRCard

    card = QRCard(
        repo="UAA-F14/ComplexCalc-SW",
        developers=[("Das Reyes", "DasReyxr"), ("Iker Garcia", "IKGB105")],
        color="#3366cc",
    )
    card                      # en Jupyter se muestra inline
    card.color = "#ffffff"    # cambia todo a blanco
    card.save("card.svg")
    card.save_png("card.png", scale=3)

Dependencias: pip install segno pillow   (cairosvg solo para exportar PNG)
"""
from __future__ import annotations

import base64
import copy
import io
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

import segno
from PIL import Image

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
INK = "http://www.inkscape.org/namespaces/inkscape"
SODI = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
for _p, _u in {"": SVG, "xlink": XLINK, "inkscape": INK, "sodipodi": SODI}.items():
    ET.register_namespace(_p, _u)

BULLET = "\u2022"   # •
CHAR_W = 0.61       # ancho de carácter monoespaciado (em), con un poco de margen
MASK_ON = "#ffffff"  # color del contenido dentro de la máscara (luminancia = 1)


def _q(tag: str) -> str:
    return f"{{{SVG}}}{tag}"


def _default_template() -> Path:
    try:
        base = Path(__file__).parent          # como módulo .py
    except NameError:
        base = Path.cwd()                     # pegado en una celda de Jupyter
    for cand in (base / "qrcard.svg", Path.cwd() / "qrcard.svg"):
        if cand.exists():
            return cand
    raise FileNotFoundError("No encontré qrcard.svg; pasa template='ruta/qrcard.svg'")


class QRCard:
    """Tarjeta QR de repositorio. Los atributos son editables y `svg` siempre refleja su estado."""

    def __init__(
        self,
        repo: str,
        developers: list[tuple[str, str]],
        color: str = "#3366cc",
        label: str = "Developers",
        background: str | None = None,
        qr_data: str | None = None,
        template: str | Path | None = None,
    ):
        self.repo = repo
        self.developers = list(developers)
        self.color = color
        self.label = label
        self.background = background      # None = transparente
        self.qr_data = qr_data            # None = https://github.com/<repo>
        self._mask_id = "m" + uuid.uuid4().hex[:8]   # único: evita choques al mostrar varias en un notebook
        self._template = ET.parse(template or _default_template()).getroot()
        self._logos = self._prepare_logos()           # PNGs ya pasados a blanco (se hace una vez)

    # ------------------------------------------------------------------ #
    # Preparación (una sola vez)
    # ------------------------------------------------------------------ #
    def _prepare_logos(self) -> dict[str, str]:
        """Devuelve {id: data-URI} con cada PNG incrustado convertido a blanco conservando el alfa."""
        out = {}
        for img in self._template.iter(_q("image")):
            if img.get("id") == "qr":
                continue
            raw = re.sub(r"\s+", "", img.get(f"{{{XLINK}}}href").split("base64,", 1)[1])
            im = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGBA")
            white = Image.new("RGBA", im.size, (255, 255, 255, 0))
            white.putalpha(im.getchannel("A"))
            buf = io.BytesIO()
            white.save(buf, "PNG", optimize=True)
            out[img.get("id")] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        return out

    # ------------------------------------------------------------------ #
    # Construcción del SVG
    # ------------------------------------------------------------------ #
    @property
    def slug(self) -> str:
        return re.sub(r"^https?://(www\.)?github\.com/", "", self.repo.strip()).strip("/")

    @property
    def svg(self) -> str:
        """SVG completo como string."""
        return self._build()

    def _build(self) -> str:
        root = copy.deepcopy(self._template)
        W = float(root.get("width"))
        layer = next(el for el in root if el.tag == _q("g"))   # capa "Image" de Inkscape

        # 1) contenido -> blanco, sin contornos (la máscara solo necesita luminancia)
        for el in layer.iter():
            st = el.get("style")
            if st:
                st = re.sub(r"(?<![-\w])fill:[^;]+", f"fill:{MASK_ON}", st)
                st = re.sub(r"(?<![-\w])stroke:[^;]+", "stroke:none", st)
                st = re.sub(r"(?<![-\w])(inline-size|white-space):[^;]+;?", "", st)  # wrapping SVG2 de Inkscape
                el.set("style", st)
        for img in layer.iter(_q("image")):
            if img.get("id") in self._logos:
                img.set(f"{{{XLINK}}}href", self._logos[img.get("id")])

        # 2) QR real y vectorial en lugar del PNG
        qr_img = next(e for e in layer.iter() if e.get("id") == "qr")
        side = min(float(qr_img.get("width")), float(qr_img.get("height")))
        qr_g = self._qr_group(float(qr_img.get("x")), float(qr_img.get("y")), side)
        layer.insert(list(layer).index(qr_img), qr_g)
        layer.remove(qr_img)

        # 3) textos
        by_id = {e.get("id"): e for e in layer.iter() if e.get("id")}
        text1 = by_id["text1"]
        repo_text = "/" + self.slug
        avail = W - (float(text1.get("x")) + 31.458763) - 8       # + translate() de la plantilla
        fs_repo = min(37.3333, avail / len(repo_text) / CHAR_W)
        t = by_id["tspan6"]
        t.text = repo_text
        t.set("style", re.sub(r"font-size:[^;]+", f"font-size:{fs_repo:.4f}px", t.get("style")))

        by_id["tspan5-9"].text = self.label

        H = self._fill_developers(by_id["Dev-Name"], by_id["Dev-GH"], W)

        # 4) ensamblado: contenido -> <mask>, y un rect del color pintado a través de ella
        H = max(float(root.get("height")), H)
        out = ET.Element(_q("svg"), {
            "version": "1.1", "width": root.get("width"), "height": str(H),
            "viewBox": f"0 0 {root.get('width')} {H}",
        })
        defs = ET.SubElement(out, _q("defs"))
        mask = ET.SubElement(defs, _q("mask"), {
            "id": self._mask_id, "maskUnits": "userSpaceOnUse",
            "x": "0", "y": "0", "width": root.get("width"), "height": str(H),
        })
        mask.append(layer)
        if self.background:
            ET.SubElement(out, _q("rect"), {"width": "100%", "height": "100%", "fill": self.background})
        ET.SubElement(out, _q("rect"), {
            "width": "100%", "height": "100%", "fill": self.color, "mask": f"url(#{self._mask_id})",
        })
        return ET.tostring(out, encoding="unicode")

    def _qr_group(self, x: float, y: float, size: float, border: int = 1):
        url = self.qr_data or f"https://github.com/{self.slug}"
        matrix = [list(r) for r in segno.make(url, error="m").matrix]
        n = len(matrix)
        d = []
        for r, row in enumerate(matrix):               # runs horizontales: menos nodos que un rect por módulo
            c = 0
            while c < n:
                if row[c]:
                    s = c
                    while c < n and row[c]:
                        c += 1
                    d.append(f"M{s + border} {r + border}h{c - s}v1h-{c - s}z")
                else:
                    c += 1
        g = ET.Element(_q("g"), {
            "id": "qr", "transform": f"translate({x} {y}) scale({size / (n + 2 * border):.6f})",
        })
        ET.SubElement(g, _q("path"), {"d": "".join(d), "fill": MASK_ON, "shape-rendering": "crispEdges"})
        return g

    def _fill_developers(self, name_el, user_el, W: float) -> float:
        """Rellena las dos columnas (nombres con bullet y @usuarios). Devuelve el alto necesario."""
        names = [f"{BULLET} {n}" for n, _ in self.developers]
        users = ["@" + u.lstrip("@") for _, u in self.developers]
        name_x = float(name_el.get("x"))
        y0, step0, fs0, gap = 264.22604, 26.40, 26.6667, 2

        cols = max(map(len, names)) + gap + max(map(len, users))
        fs = min(fs0, (W - name_x - 8) / cols / CHAR_W)        # se encoge si no cabe a lo ancho
        step = step0 * fs / fs0
        user_x = name_x + (max(map(len, names)) + gap) * CHAR_W * fs

        def rows(el, x, items):
            for ch in list(el):
                el.remove(ch)
            for i, txt in enumerate(items):
                ts = ET.SubElement(el, _q("tspan"), {
                    f"{{{SODI}}}role": "line", "x": f"{x:.4f}", "y": f"{y0 + i * step:.4f}",
                    "style": f"font-size:{fs:.4f}px;font-family:Monospace",
                })
                ts.text = txt

        rows(name_el, name_x, names)
        rows(user_el, user_x, users)
        user_el.set("x", f"{user_x:.4f}")
        return round(y0 + (len(names) - 1) * step + 31, 2)

    # ------------------------------------------------------------------ #
    # Salidas
    # ------------------------------------------------------------------ #
    def _repr_svg_(self) -> str:          # Jupyter lo muestra inline al evaluar `card`
        return self.svg

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + self.svg, encoding="utf-8")
        return path

    def png_bytes(self, scale: float = 2.0) -> bytes:
        import cairosvg   # import perezoso: solo si exportas PNG
        return cairosvg.svg2png(bytestring=self.svg.encode(), scale=scale)   # fondo transparente

    def save_png(self, path: str | Path, scale: float = 2.0) -> Path:
        path = Path(path)
        path.write_bytes(self.png_bytes(scale))
        return path