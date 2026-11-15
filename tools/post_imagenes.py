#!/usr/bin/env python3
"""Convierte art_src/raw/<id>.png en los archivos finales del manifiesto: recorte, tamaño, marca MR y webp.
Uso: python3 tools/post_imagenes.py [--only id,...]"""
import argparse, json, os, sys
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, "/Volumes/Datos_Dock/FoundryVTT/Trabajo LOGO/marca")
import marca  # noqa: E402

def recorta_alfa(im, margen=0.04):
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bb: return im
    im = im.crop(bb); m = int(max(im.size) * margen)
    out = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (0, 0, 0, 0)); out.paste(im, (m, m)); return out

def encaja(im, w, h):
    im = im.copy(); im.thumbnail((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im); return out

def redondo(im, lado=400):
    s = min(im.size); im = im.crop(((im.width - s) // 2, 0, (im.width + s) // 2, s)).resize((lado, lado), Image.LANCZOS)
    m = Image.new("L", (lado, lado), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).ellipse((2, 2, lado - 3, lado - 3), fill=255)
    out = Image.new("RGBA", (lado, lado), (0, 0, 0, 0)); out.paste(im, (0, 0), m); return out

def guarda(im, ruta, q=86):
    ruta = R / ruta; ruta.parent.mkdir(parents=True, exist_ok=True); im.save(ruta, "WEBP", quality=q, method=6)

def figura(im, lado=1024, visible=0.885, pie=0.055):
    im = recorta_alfa(im, 0); alto = round(lado * visible); ancho = round(im.width * alto / im.height)
    if ancho > lado: ancho, alto = lado, round(im.height * lado / im.width)
    im = im.resize((ancho, alto), Image.LANCZOS); out = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    out.alpha_composite(im, ((lado - ancho) // 2, round(lado * (1 - pie)) - alto)); return marca.hombro(out)

def proceso(a):
    if a["kind"] == "figure":
        raw = R / "art_src" / "raw" / (a["derivado_de"] + ".png")
        if not raw.exists(): return None
        guarda(figura(Image.open(raw).convert("RGBA")), a["path"], 88); return a["id"]
    raw = R / "art_src" / "raw" / (a["id"] + ".png")
    if not raw.exists(): return None
    im = Image.open(raw).convert("RGBA"); k = a["kind"]
    if k == "scene":
        w, h = im.size; nh = round(w * 9 / 16); y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh)).convert("RGB").resize((2560, 1440), Image.LANCZOS)
        guarda(marca.esquina(im), a["path"], 84)
        t = im.resize((400, 225), Image.LANCZOS); guarda(t, a["thumb"], 80)
    elif k == "photo":
        guarda(marca.esquina(im.convert("RGB").resize((1536, 1024), Image.LANCZOS)), a["path"], 86)
    elif k == "token":
        t = encaja(recorta_alfa(im), 800, 1200); t = marca.hombro(t); guarda(t, a["path"])
        cab = recorta_alfa(Image.open(raw).convert("RGBA")); cab = cab.crop((0, 0, cab.width, int(cab.width * 1.0)))
        r = marca.discreta(redondo(cab), 329, 329, 17, contraste=.22); guarda(r, a["round_token"])
    elif k == "portrait":
        p = encaja(recorta_alfa(im, .06), 512, 512); guarda(marca.esquina(p), a["path"])
    elif k in ("item", "condition", "ui"):
        w, h = a["px"]; p = encaja(recorta_alfa(im, .06), w, h)
        if k != "ui": p = marca.discreta(p, int(w * .76), int(h * .86), max(14, int(w * .09)))
        guarda(p, a["path"])
    elif k == "handout":
        w, h = a["px"]; guarda(marca.esquina(encaja(recorta_alfa(im, .05), w, h), sube=0.0), a["path"])
    return a["id"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); o = ap.parse_args()
    man = json.load(open(R / "asset-manifest.json"))["assets"]; only = set(o.only.split(",")) if o.only else None
    n = 0
    for a in man:
        if a.get("reuse_of") or (only and a["id"] not in only): continue
        r = proceso(a)
        if r: print("hecho", r); n += 1
    print(n, "imágenes procesadas")
