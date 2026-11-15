#!/usr/bin/env python3
"""Genera las imágenes del manifiesto delegando en Codex CLI. Reanudable: salta lo que ya existe en art_src/raw.
Uso: python3 tools/gen_imagenes.py [--only id1,id2] [--kind scene,token] [--force] [--jobs 2] [--modelo gpt-5.6-luna]"""
import argparse, hashlib, json, os, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "art_src", "raw")
ESTILO = ("Art direction for the 'Ratover' series: dark-fantasy criminal comedy in a mouse-scale macro world inside a luxurious human hotel suite. "
          "Warm candlelight with magenta and cyan neon accents, plum purple and antique gold palette, painterly gritty realism, rich detail, "
          "one coherent style across the whole series. Do not draw any readable text, letters, logos or watermarks unless the description explicitly asks for lettering.")
TAM = {"scene": "1536x1024", "photo": "1536x1024", "token": "1024x1536", "portrait": "1024x1024"}
TRANSPARENTE = {"token", "portrait", "item", "condition", "ui", "handout"}


def limpia(p):
    return re.sub(r"\s*--(ar|v|no)\b.*$", "", p).strip()


def tamano(a):
    if a["kind"] in TAM: return TAM[a["kind"]]
    return "1024x1536" if a["ar"] == "1:2" else "1024x1024"


def valida(path, size):
    try: w, h = Image.open(path).size
    except Exception: return False
    rw, rh = map(int, size.split("x"))
    return min(w, h) >= 900 and abs(w / h - rw / rh) < 0.15


def uno(a, modelo):
    sid = a["id"]; out = os.path.join("art_src", "raw", sid + ".png"); size = tamano(a)
    extra = " The background MUST be fully transparent (real alpha channel), no floor, no shadow plane, subject isolated." if a["kind"] in TRANSPARENTE else ""
    if a["kind"] == "scene": extra = " Do NOT include any character, animal or person: the room must be empty."
    prompt = ("Usa tu herramienta de generación de imágenes para crear UNA sola imagen, tamaño %s. Descripción: %s %s%s\n"
              "Después copia EL PNG QUE TU HERRAMIENTA ACABA DE DEVOLVER EN ESTA SESIÓN (usa su ruta exacta; nunca busques el archivo más reciente de la carpeta, "
              "puede ser de otra sesión) a %s. No generes más de una imagen ni modifiques otros archivos.") % (size, limpia(a["prompt"]), ESTILO, extra, out)
    t0 = time.time(); r = None
    for _ in range(2):
        r = subprocess.run(["codex", "exec", "-m", modelo, "-c", 'model_reasoning_effort="low"', "--skip-git-repo-check", "-s", "workspace-write", prompt],
                           cwd=ROOT, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
        p = os.path.join(ROOT, out)
        if os.path.exists(p) and not valida(p, size): os.remove(p)
        if os.path.exists(p): return "OK  %-44s %4.0fs" % (sid, time.time() - t0)
    return "ERR %-44s %s" % (sid, (r.stdout + r.stderr)[-200:].replace("\n", " "))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); ap.add_argument("--kind"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--modelo", default="gpt-5.6-luna"); a = ap.parse_args()
    man = json.load(open(os.path.join(ROOT, "asset-manifest.json")))["assets"]
    only = set(a.only.split(",")) if a.only else None; kinds = set(a.kind.split(",")) if a.kind else None
    todo = []
    for it in man:
        if it["kind"] not in ("scene", "token", "portrait", "item", "condition", "handout", "photo", "ui") or it.get("reuse_of"): continue
        if only and it["id"] not in only: continue
        if kinds and it["kind"] not in kinds: continue
        p = os.path.join(RAW, it["id"] + ".png")
        if os.path.exists(p) and not a.force: continue
        if os.path.exists(p): os.remove(p)
        todo.append(it)
    print("pendientes:", len(todo), flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for res in ex.map(lambda it: uno(it, a.modelo), todo): print(res, flush=True)
    # duplicados exactos: señal de que Codex copió la imagen de otra sesión
    h = {}
    for f in sorted(os.listdir(RAW)):
        d = hashlib.md5(open(os.path.join(RAW, f), "rb").read()).hexdigest(); h.setdefault(d, []).append(f)
    for fs in h.values():
        if len(fs) > 1: print("DUPLICADOS:", fs)
    print("Hecho", flush=True)


if __name__ == "__main__":
    main()
