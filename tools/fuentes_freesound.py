#!/usr/bin/env python3
"""Descarga los efectos CC0 elegidos de Freesound (previews HQ) a «Trabajo RW/audio-fuentes/freesound» y escribe lista.txt con los créditos."""
import re, subprocess, sys, time
from pathlib import Path
DEST = Path("/Volumes/Datos_Dock/FoundryVTT/Trabajo RW/audio-fuentes/freesound")
BUSQ = [Path("/Volumes/Datos_Dock/FoundryVTT/Trabajo RW/audio-fuentes") / f for f in ("busqueda.txt", "busqueda2.txt")]
ELEGIDOS = {"molinillo": 503427, "timbre": 879808, "puerta": 452609, "fichas": 633997, "ruleta": 482663, "sello": 470710, "cadena": 593458, "granos": 539319,
            "saco": 497916, "goteo": 740288, "campana": 511681, "maquina": 360603, "tuberia": 677722, "crujido": 878048, "latido": 877805, "magia": 877981,
            "carrito": 635488, "sizzle": 351406, "tos": 743360}
info = {}
for f in BUSQ:
    for ln in f.read_text(encoding="utf8").splitlines():
        m = re.match(r"\s+(\d+) \| (.*?) \| ([\d.]+) \| (.*?) \| (https\S+)", ln)
        if m: info[int(m.group(1))] = (m.group(2), m.group(4), m.group(5))
DEST.mkdir(parents=True, exist_ok=True); lista = []
for nombre, i in ELEGIDOS.items():
    t, autor, url = info[i]; url = url.replace("-hq.mp3", "-hq.ogg")
    r = subprocess.run(["curl", "-sL", "-o", str(DEST / f"{nombre}.ogg"), "-w", "%{http_code}", url], capture_output=True, text=True)
    sz = (DEST / f"{nombre}.ogg").stat().st_size
    print(f"{nombre:10s} {r.stdout} {sz // 1024:5d} KB  {i} {t[:40]} ({autor})", flush=True)
    lista.append(f"{nombre} {i} {autor} {t}"); time.sleep(1)
(DEST / "lista.txt").write_text("\n".join(lista) + "\n", encoding="utf8")
