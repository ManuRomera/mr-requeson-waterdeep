#!/usr/bin/env python3
"""Banda sonora de Requesón en Waterdeep a partir de grabaciones con licencia libre (ver NOTICE.md):
música de Kevin MacLeod (incompetech.com, CC BY 4.0) y efectos de Freesound (CC0).
Todo pasa por el mismo master de la casa (EQ + compresión suave) y los efectos comparten la misma sala, para que suene a una sola película.
Los bucles se cortan a compás (inicio y final lo más parecidos posible) con fundido circular y loudnorm -26 LUFS.
Fuentes en «Trabajo RW/audio-fuentes» (macleod/<clave>.mp3, freesound/*.ogg; efectos en tools/efectos_fuentes.json).
Uso: python3 tools/banda.py [clave ...]   (claves: music/<id>, moods/<id>, sfx/<id>)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent.parent
SRC = Path("/Volumes/Datos_Dock/FoundryVTT/Trabajo RW/audio-fuentes")
OUT = R / "assets" / "audio"
SR = 48000
CINTA = "highpass=f=45,lowpass=f=13500,acompressor=threshold=-20dB:ratio=2:attack=15:release=250"
SALA = "aecho=0.85:0.55:38|83:0.16|0.09"

MAN = {a["id"]: a for a in json.load(open(R / "asset-manifest.json"))["assets"] if a["kind"] in ("music", "mood", "sfx")}
EFECTOS = json.load(open(R / "tools" / "efectos_fuentes.json")) if (R / "tools" / "efectos_fuentes.json").exists() else {}

def lee(ruta, ini=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ini)] + (["-t", str(dur)] if dur else []) + ["-i", str(ruta), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()


def fundidos(x, a=0.005, b=0.08):
    n, na, nb = len(x), int(a * SR), int(b * SR)
    x[:na] *= np.linspace(0, 1, na)[:, None]
    x[n - nb:] *= np.linspace(1, 0, nb)[:, None]
    return x


def bucle(x, xf=4.0):
    """Fundido circular de potencia constante: la cola se funde con el arranque y el archivo empieza donde acaba."""
    n = int(xf * SR)
    t = np.linspace(0, np.pi / 2, n)[:, None]
    cabeza, cola = x[:n], x[-n:]
    return np.concatenate([cola * np.cos(t) + cabeza * np.sin(t), x[n:-n]])


def corte_en_compas(x, n, intro=20):
    """Bucle x[s0:c] con s0 en los primeros `intro` s (para saltar una intro distinta) y c en los últimos ~45 s, elegidos
    para que x[c:] ≈ x[s0:] y el fundido circular no descuadre el ritmo: envolvente de energía a 10 ms y ajuste fino
    por correlación de la onda."""
    from numpy.lib.stride_tricks import sliding_window_view as ventanas
    h = SR // 100
    mono = x.mean(axis=1)
    L = len(mono) // h * h
    env = np.sqrt(np.add.reduceat(mono[:L] ** 2, np.arange(0, L, h)) / h)
    m = 2 * n // h
    norm = lambda W: (W - W.mean(axis=-1, keepdims=True)) / (W.std(axis=-1, keepdims=True) + 1e-9)
    c0 = max(m + intro * 100, len(env) - 4500)
    W = norm(ventanas(env[c0:], m))
    S = norm(ventanas(env[: intro * 100 + m], m)[::10])            # inicios cada 0,1 s
    R = S @ W.T / m
    R[0] += 0.05                                                     # a igualdad, mejor no saltarse nada
    a, b = np.unravel_index(np.argmax(R), R.shape)
    s0, c = a * 10 * h, (c0 + b) * h
    w = mono[s0:s0 + n // 2]
    lo, hi = max(0, c - h), min(len(mono) - n // 2, c + h)
    c = lo + int(np.argmax([float(np.dot(w, mono[k:k + n // 2])) for k in range(lo, hi)]))
    return s0, c, float(R[a, b])


def sin_cola(x, umbral=-50):
    e = np.abs(x).max(axis=1)
    sonido = np.where(e > 10 ** (umbral / 20))[0]
    return x[: sonido[-1] + 1] if len(sonido) else x


def escribe(x, destino, es_bucle, filtro):
    destino.parent.mkdir(parents=True, exist_ok=True)
    ln = "loudnorm=I=-26:TP=-2:LRA=11" if es_bucle else "loudnorm=I=-18:TP=-1.5"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", f"{filtro},{ln}", "-ar", "48000", "-c:a", "libopus", "-b:a", "96k" if es_bucle else "80k", str(destino)],
                   input=x.astype(np.float32).tobytes(), check=True)
    print("hecho", destino.relative_to(R))


def musica(clave):
    carpeta, nombre = clave.split("/")
    x = sin_cola(lee(SRC / "macleod" / f"{nombre}.mp3"))
    x = x[: len(x) - int(3 * SR)]   # fuera los últimos 3 s (el final con ritardando)
    n = int(1.5 * SR)
    s0, c, r = corte_en_compas(x, n)
    t = np.linspace(0, np.pi / 2, n)[:, None]
    y = np.concatenate([x[c:c + n] * np.cos(t) + x[s0:s0 + n] * np.sin(t), x[s0 + n:c]])
    print(f"  {clave}: bucle {s0 / SR:.1f}–{c / SR:.1f} s de {len(x) / SR:.1f} s (parecido {r:.2f})")
    escribe(y, OUT / carpeta / f"{nombre}.ogg", True, CINTA)


def mezcla(capas):
    pistas = []
    for nombre, db, ini, dur, ret in capas:
        x = fundidos(lee(SRC / "freesound" / f"{nombre}.ogg", ini, dur)) * 10 ** (db / 20)
        if ret: x = np.concatenate([np.zeros((int(ret * SR), 2), np.float32), x])
        pistas.append(x)
    n = max(len(p) for p in pistas)
    return sum(np.pad(p, ((0, n - len(p)), (0, 0))) for p in pistas)


def efecto(nombre):
    x = np.concatenate([mezcla(EFECTOS[nombre]), np.zeros((int(0.6 * SR), 2), np.float32)])   # sitio para la cola de sala
    escribe(fundidos(x, 0.002, 0.3), OUT / "sfx" / f"{nombre}.ogg", False, f"{CINTA},{SALA}")


def todo():
    return [f"music/{k.split('.',1)[1]}" for k, a in MAN.items() if a["kind"] == "music"] + [f"moods/{k.split('.',1)[1]}" for k, a in MAN.items() if a["kind"] == "mood"] + [f"sfx/{k}" for k in EFECTOS]


if __name__ == "__main__":
    for clave in sys.argv[1:] or todo():
        musica(clave) if clave.startswith(("music/", "moods/")) else efecto(clave.split("/")[-1])
