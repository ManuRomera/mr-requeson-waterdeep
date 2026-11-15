#!/usr/bin/env python3
"""Convierte las pistas descargadas de Incompetech (art_src/musica/*.mp3, CC BY 4.0) en bucles Ogg Opus a -26 LUFS.
Uso: python3 tools/musica.py [clave ...]. El final se solapa con el principio (fundido de potencia constante) para que el bucle no tenga corte."""
import json, pathlib, re, subprocess, sys, tempfile, wave
import numpy as np

R = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
CF = 4.0   # segundos de solape

def lee(mp3):
    t = pathlib.Path(tempfile.mkdtemp()) / "t.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", str(SR), "-ac", "2", str(t)], check=True)
    with wave.open(str(t)) as w: x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, 2) / 32768.0
    return x

def recorta(x, umbral=0.004):
    e = np.abs(x).max(axis=1); idx = np.where(e > umbral)[0]
    return x[idx[0]: idx[-1] + 1] if len(idx) else x

def bucle(x, cf=CF):
    c = int(cf * SR)
    if len(x) < c * 4: return x
    w = np.linspace(0, np.pi / 2, c)[:, None]; entra, sale = np.sin(w), np.cos(w)
    y = x[:-c].copy(); y[:c] = y[:c] * entra + x[-c:] * sale
    return y

def guarda(y, ruta, lufs=-26.0, kbps=96):
    f = pathlib.Path(tempfile.mkdtemp()) / "t.wav"
    def wav(a):
        with wave.open(str(f), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
    wav(y)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", str(f), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?\d+\.?\d*) LUFS", o)[-1])
    y = np.clip(y * 10 ** ((lufs - I) / 20), -0.97, 0.97); wav(y)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-c:a", "libopus", "-b:a", f"{kbps}k", str(ruta)], check=True)
    return I

if __name__ == "__main__":
    man = {a["id"].split(".", 1)[1]: a for a in json.load(open(R / "asset-manifest.json"))["assets"] if a["kind"] in ("music", "mood")}
    for k in (sys.argv[1:] or list(man)):
        mp3 = R / "art_src" / "musica" / f"{k}.mp3"
        y = bucle(recorta(lee(mp3)))
        I = guarda(y, R / man[k]["path"])
        print(f"{k:34s} {len(y)/SR:6.1f}s  {(R / man[k]['path']).stat().st_size//1024:5d} KB  (medido {I:.1f} LUFS)", flush=True)
