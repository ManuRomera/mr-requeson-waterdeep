#!/usr/bin/env python3
"""Sintetizador de la banda sonora de Ratover. Cittern, viol grave, tambor de mano, dulcimer y armonio, con bucles sin costura.
Uso: python3 tools/audio.py [clave ...]   claves = sufijo del id del manifiesto (music.00-portada-ratover -> 00-portada-ratover).
Es música procedural de sustitución: los prompts de Suno del manifiesto siguen valiendo para reemplazarla (misma ruta)."""
import json, sys, zlib, subprocess, re, wave, pathlib, tempfile
import numpy as np

R = pathlib.Path(__file__).resolve().parent.parent
SR = 48000
ESC = {"dor": [0, 2, 3, 5, 7, 9, 10], "men": [0, 2, 3, 5, 7, 8, 10], "mix": [0, 2, 4, 5, 7, 9, 10], "fri": [0, 1, 3, 5, 7, 8, 10], "may": [0, 2, 4, 5, 7, 9, 11]}
MOTIVO = [0, 2, 4, 2, 1, 0]   # grados del tema de la Manada

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def adsr(n, a, r):
    e = np.ones(n); na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:min(na, n)] = np.linspace(0, 1, min(na, n)); e[max(0, n - nr):] *= np.linspace(1, 0, min(nr, n))
    return e
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))

# ---- instrumentos
def pluck(f, d, br, rng):
    t = tt(d); y = np.zeros(len(t))
    for k in range(1, 11):
        if f * k > 9000: break
        y += (1 / k ** (1.0 + (1 - br))) * np.sin(2 * np.pi * f * k * t * (1 + rng.uniform(-2e-4, 2e-4))) * np.exp(-t / (d * 0.30 / k ** 0.55))
    y[:int(.004 * SR)] += rng.standard_normal(int(.004 * SR)) * 0.08
    return y
def viol(f, d, rng):
    t = tt(d); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.6)
    y = sum((1 / k) * np.sin(2 * np.pi * f * k * t * vib + k) for k in range(1, 9) if f * k < 3000)
    return y * adsr(len(t), 0.18, 0.25)
def armonio(f, d, rng):
    t = tt(d); y = sum((1 / k) * np.sin(2 * np.pi * f * k * t * (1 + dt)) for k in (1, 2, 3, 4) for dt in (-0.003, 0.003))
    return y * adsr(len(t), 0.08, 0.2)
def campana(f, d, rng):
    t = tt(d); y = np.zeros(len(t))
    for r, a, tau in ((1, 1, .5), (2.76, .5, .3), (5.4, .3, .18), (8.93, .15, .1)):
        if f * r < 12000: y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (d * tau))
    return y
def bombo(vol=1.0):
    t = tt(.35); ph = 2 * np.pi * np.cumsum(48 + 90 * np.exp(-t * 28)) / SR
    return np.sin(ph) * np.exp(-t * 11) * vol
def tan(vol=1.0, rng=None):
    t = tt(.22); ph = 2 * np.pi * np.cumsum(190 + 70 * np.exp(-t * 40)) / SR
    ru = filt(rng.standard_normal(len(t)), 300, 3500) * np.exp(-t * 35)
    return (np.sin(ph) * np.exp(-t * 22) * .8 + ru * .6) * vol
def tick(rng, vol=1.0, f=5000):
    t = tt(.04); return filt(rng.standard_normal(len(t)), f, None) * np.exp(-t * 130) * vol
def seco(rng, vol=1.0):
    t = tt(.05); return filt(rng.standard_normal(len(t)), 5500, None) * np.exp(-t * 90) * vol

def mezcla(buf, sig, pos, pan=0.0, g=1.0):
    p = int(pos * SR)
    if p >= buf.shape[0] or p < 0: return
    n = min(len(sig), buf.shape[0] - p); a = np.sqrt((1 - pan) / 2); b = np.sqrt((1 + pan) / 2)
    buf[p:p + n, 0] += sig[:n] * g * a; buf[p:p + n, 1] += sig[:n] * g * b

def reverb(buf, rng, t60=1.8, mezcla_=0.22):
    n = int(t60 * SR); out = np.zeros_like(buf)
    for c in range(2):
        ir = filt(rng.standard_normal(n), 200, 5500) * np.exp(-6.9 * np.arange(n) / n)
        N = 1 << int(np.ceil(np.log2(len(buf) + n)))
        out[:, c] = np.fft.irfft(np.fft.rfft(buf[:, c], N) * np.fft.rfft(ir, N), N)[:len(buf)]
    return buf * (1 - mezcla_ * .5) + out * mezcla_ * 0.015 * (np.abs(buf).max() / (np.abs(out).max() + 1e-9)) * 12

# ---- recetas: bpm, compás, tónica MIDI, escala, progresión (grados), intensidad, bajo, cuerda, percusión, campanas, motivo, swing, extras
REC = {
 "00-portada-ratover":           dict(bpm=80, c=4, root=50, esc="dor", prog=[0, 3, 0, 4], I=1.5, bajo="sost", cuerda="arp", perc="lento", camp=.25, motivo="tranquilo", swing=.18, ex=[]),
 "01-la-villa-del-cielo-caido":  dict(bpm=83, c=4, root=50, esc="men", prog=[0, 5, 3, 4], I=2, bajo="sost", cuerda="torcido", perc="torcido", camp=.35, motivo="fragmento", swing=.22, ex=["tarde"]),
 "02-dado-de-nacar":             dict(bpm=105, c=4, root=52, esc="dor", prog=[0, 3, 4, 3], I=2.5, bajo="pulso", cuerda="arp", perc="swing", camp=.8, motivo="elegante", swing=.3, ex=["fichas"]),
 "03-bulevar-precintado":        dict(bpm=91, c=4, root=47, esc="men", prog=[0, 0, 5, 4], I=2.5, bajo="pulso", cuerda="nervioso", perc="contenido", camp=.2, motivo="fragmento", swing=.05, ex=[]),
 "04-capilla-del-ultimo-chillido": dict(bpm=75, c=3, root=53, esc="mix", prog=[0, 3, 4, 0], I=2, bajo="vals", cuerda="vals", perc="vals", camp=.9, motivo="tranquilo", swing=0, ex=["armonio", "cajita"]),
 "05-notaria-del-parmesano":     dict(bpm=89, c=4, root=45, esc="men", prog=[0, 0, 3, 0], I=2, bajo="pulso", cuerda="seco", perc="metronomo", camp=.15, motivo="fragmento", swing=0, ex=["maquina"]),
 "06-almacen-de-don-chispa":     dict(bpm=112, c=4, root=52, esc="dor", prog=[0, 4, 3, 4], I=3, bajo="pulso", cuerda="rapido", perc="inquieto", camp=.5, motivo="elegante", swing=.12, ex=["granos"]),
 "07-atico-de-rat-tyson":        dict(bpm=88, c=4, root=43, esc="men", prog=[0, 0, 5, 0], I=2.5, bajo="sost", cuerda="disperso", perc="mediotiempo", camp=.1, motivo="fragmento", swing=0, ex=["respira", "estallido"]),
 "08-el-bano-de-princesa":       dict(bpm=87, c=4, root=46, esc="fri", prog=[0, 0, 1, 0], I=3, bajo="pulso", cuerda="ostinato", perc="lento", camp=.2, motivo="fragmento", swing=0, ex=["goteo"]),
 "09-la-mandibula-negra":        dict(bpm=130, c=4, root=45, esc="dor", prog=[0, 0, 3, 4], I=5, bajo="riff", cuerda="riff", perc="marcha", camp=.3, motivo="completo", swing=0, ex=["engranajes"]),
 "investigacion-resaca":         dict(bpm=81, c=4, root=50, esc="dor", prog=[0, 3, 0, 5], I=1.5, bajo="sost", cuerda="disperso", perc="lento", camp=.3, motivo="fragmento", swing=.15, ex=[]),
 "comedia-caotica":              dict(bpm=120, c=4, root=52, esc="mix", prog=[0, 3, 4, 0], I=4, bajo="pulso", cuerda="rapido", perc="inquieto", camp=.6, motivo="elegante", swing=.2, ex=["granos"]),
 "tension-ritual":               dict(bpm=91, c=4, root=47, esc="fri", prog=[0, 0, 1, 0], I=2.5, bajo="sost", cuerda="ostinato", perc="mediotiempo", camp=.4, motivo="seis", swing=0, ex=["respira"]),
 "sigilo-peligro":               dict(bpm=85, c=4, root=43, esc="men", prog=[0, 0, 0, 5], I=2, bajo="sost", cuerda="disperso", perc="contenido", camp=.1, motivo="fragmento", swing=0, ex=["respira"]),
 "persecucion":                  dict(bpm=139, c=4, root=45, esc="dor", prog=[0, 4, 3, 4], I=4.5, bajo="riff", cuerda="rapido", perc="marcha", camp=.2, motivo="completo", swing=0, ex=[]),
 "combate":                      dict(bpm=120, c=4, root=43, esc="men", prog=[0, 0, 5, 4], I=4, bajo="riff", cuerda="riff", perc="marcha", camp=.2, motivo="completo", swing=.08, ex=[]),
 "revelacion-flashback":         dict(bpm=72, c=4, root=50, esc="may", prog=[0, 5, 3, 0], I=1.5, bajo="sost", cuerda="disperso", perc="ninguna", camp=.6, motivo="tranquilo", swing=0, ex=["armonio"]),
 "triunfo-agridulce":            dict(bpm=126, c=4, root=48, esc="may", prog=[0, 3, 4, 5], I=4, bajo="pulso", cuerda="rapido", perc="inquieto", camp=.7, motivo="completo", swing=.1, ex=["fichas"]),
}

def pista(clave, seg=135):
    r = REC[clave]; rng = np.random.default_rng(zlib.crc32(clave.encode()))
    bpm, c, esc = r["bpm"], r["c"], ESC[r["esc"]]; beat = 60 / bpm; barra = c * beat
    nb = max(4, int(round(seg / barra / 4)) * 4); L = nb * barra; cola = 5.0
    buf = np.zeros((int((L + cola) * SR), 2)); I = r["I"] / 3
    nota = lambda g, o=0: r["root"] + 12 * (g // 7 + o) + esc[g % 7]
    def poner(m, d, br, pos, pan, g, kind="pluck"):
        f = hz(m)
        s = {"pluck": lambda: pluck(f, d, br, rng), "viol": lambda: viol(f, d, rng), "arm": lambda: armonio(f, d, rng), "camp": lambda: campana(f, d, rng)}[kind]()
        mezcla(buf, s, pos, pan, g)
    corto = lambda b: b * (1 + r["swing"] / 2.5) if (b * 2) % 2 == 1 else b   # swing: las corcheas de contratiempo llegan tarde
    for b in range(nb):
        t0 = b * barra; g = r["prog"][b % len(r["prog"])]
        resp = 0.85 + 0.15 * np.sin(2 * np.pi * b / 8)
        tonos = [g, g + 2, g + 4, g + 2]
        # bajo
        if r["bajo"] == "sost" or "respira" in r["ex"]:
            poner(nota(g, -2), barra * 1.02, 1, t0, -.1, .55 * resp, "viol")
        if r["bajo"] == "pulso":
            for k in range(c):
                if k % 2 == 0 or c == 4 and r["I"] > 2.2:
                    poner(nota(g, -2), beat * .8, .5, t0 + k * beat, -.1, .6, "pluck")
        if r["bajo"] == "vals":
            poner(nota(g, -2), beat * .9, .5, t0, -.1, .6, "pluck")
        if r["bajo"] == "riff":
            for k, gg in enumerate([0, None, 0, 3, None, 0, 5, None]):
                if gg is not None: poner(nota(g + gg, -2), beat * .45, .6, t0 + k * beat / 2, -.1, .7)
            poner(nota(g, -2), barra, 1, t0, -.1, .35, "viol")
        # cuerda de adorno
        cu = r["cuerda"]; pasos = c * 2
        for k in range(pasos):
            pos = t0 + corto(k / 2) * beat
            if "tarde" in r["ex"]: pos += rng.uniform(0, .05) if k % 3 == 0 else 0
            if cu == "arp" and k % 2 == 0: poner(nota(tonos[(k // 2) % 4], 1), beat * 1.4, .8, pos, .3, .3 * I)
            if cu == "torcido" and rng.random() < .55: poner(nota(tonos[k % 4], 1), beat, .6, pos + rng.uniform(0, .07), .3, .28 * I)
            if cu == "nervioso" and k % 2 == 1: poner(nota(tonos[1], 1), beat * .4, .9, pos, .3, .3 * I)
            if cu == "vals" and k % 2 == 0 and k > 0: poner(nota(tonos[1], 1), beat * .8, .6, pos, .3, .3)
            if cu == "seco" and k % 2 == 0: poner(nota(tonos[(k // 2) % 3], 1), beat * .3, 1, pos, .3, .3)
            if cu == "rapido" and rng.random() < .7: poner(nota(tonos[k % 4] + (7 if k % 5 == 0 else 0), 1), beat * .5, .9, pos, .3 if k % 2 else -.3, .3 * I)
            if cu == "disperso" and rng.random() < .12: poner(nota(rng.choice(tonos), 1), beat * 2.5, .5, pos, .3, .3)
            if cu == "ostinato" and k % 2 == 0: poner(nota(0 if (k // 2) % 2 == 0 else 1, 1), beat * .6, .7, pos, .3, .32)
            if cu == "riff" and k % 2 == 0: poner(nota(g + [0, 3, 5, 3][k // 2 % 4], 1), beat * .45, 1, pos, .3, .3)
        # campanas (dulcimer)
        if rng.random() < r["camp"] * .8:
            for _ in range(1 + int(r["camp"] * 2)):
                poner(nota(rng.choice(tonos) + 7, 1), 2.0, 1, t0 + rng.uniform(0, barra), rng.uniform(-.6, .6), .22, "camp")
        # percusión
        p = r["perc"]
        def golpe(sig, pos, pan=0, gg=1.0): mezcla(buf, sig, pos, pan, gg)
        for k in range(c):
            tk = t0 + k * beat
            if p in ("lento", "torcido", "swing", "inquieto", "marcha", "mediotiempo", "contenido"):
                if k == 0 or (p in ("marcha", "inquieto") and k in (0, 2)) or (p == "swing" and k == 2): golpe(bombo(.9 * I), tk + (rng.uniform(0, .03) if p == "torcido" else 0), 0, .7)
                if k in (1, 3) and p not in ("mediotiempo",) and I > .4: golpe(tan(.8, rng), tk + (beat * r["swing"] / 2 if p == "swing" else 0), .2, .6 * I)
                if p == "mediotiempo" and k == 2: golpe(tan(1, rng), tk, .2, .5)
                if p in ("marcha", "inquieto", "swing"):
                    for h in (0, .5): golpe(seco(rng, .5), tk + beat * (h + (r["swing"] / 3 if h else 0)), .5, .35 * I)
            if p == "vals":
                golpe(bombo(.8), tk, 0, .5) if k == 0 else golpe(tan(.6, rng), tk, .2, .35)
            if p == "metronomo":
                golpe(tick(rng, 1, 3500), tk, .4, .45); golpe(bombo(.7), tk, 0, .5) if k == 0 else None
            if p == "contenido" and k in (0, 2): golpe(tick(rng, 1, 4500), tk + beat / 2, .4, .35)
    # extras
    for e in r["ex"]:
        if e == "fichas":
            for _ in range(int(nb * 1.6)): mezcla(buf, tick(rng, 1, rng.uniform(5000, 8000)) * 1.2, rng.uniform(0, L), rng.uniform(-.8, .8), .5)
        if e == "maquina":
            for _ in range(int(nb * 3)): mezcla(buf, tick(rng, 1, 2500) * 1.5, rng.uniform(0, L), .5, .4)
        if e == "goteo":
            for _ in range(int(nb * .9)): mezcla(buf, campana(rng.uniform(900, 1500), .7, rng) * .25, rng.uniform(0, L), rng.uniform(-.7, .7), .5)
        if e == "granos":
            for _ in range(int(nb * 5)): mezcla(buf, seco(rng, 1), rng.uniform(0, L), rng.uniform(-.8, .8), .35)
        if e == "armonio":
            for b in range(0, nb, 2): poner(nota(r["prog"][b % len(r["prog"])], -1), barra * 2.1, 1, b * barra, 0, .22, "arm")
        if e == "cajita":
            for _ in range(int(nb)): poner(nota(rng.choice([0, 2, 4, 7, 9]) + 7, 2), 1.6, 1, rng.uniform(0, L), .5, .2, "camp")
        if e == "engranajes":
            for k in range(int(L / (beat / 2))): mezcla(buf, tick(rng, 1, 1800) * 1.2, k * beat / 2, -.5, .35)
        if e == "estallido":
            b0 = (nb * 3) // 4; tq = b0 * barra
            for k in range(8): mezcla(buf, tan(1, rng), tq + (c - 1) * beat + k * beat / 8, 0, .3 + .08 * k)
            for k, o in enumerate((0, beat * .5, beat)):
                mezcla(buf, bombo(1.4), tq + barra + o, 0, 1.0); mezcla(buf, tan(1.3, rng), tq + barra + o, .2, .8)
    # motivo de la Manada
    m = r["motivo"]; idx = MOTIVO if m != "seis" else MOTIVO
    for b in range(0, nb, 4 if m in ("tranquilo", "elegante") else 8 if m == "fragmento" else 2):
        notas = idx if m not in ("fragmento",) else idx[:3 + rng.integers(0, 2)]
        v = {"tranquilo": (beat * 1.6, .4), "elegante": (beat * 1.0, .5), "fragmento": (beat * 1.3, .35), "completo": (beat * .5, .6), "seis": (beat * .75, .5)}[m]
        for i, gd in enumerate(notas): poner(nota(gd, 2 if m != "completo" else 1), v[0] * 1.5, 1, b * barra + (barra * .1) + i * v[0], .15, v[1], "pluck")
    # reverb y bucle sin costura: la cola se pliega sobre el principio
    buf = reverb(buf, rng, 1.8 if r["c"] == 4 else 2.2, .25)
    n = int(L * SR); out = buf[:n].copy(); cc = buf[n:]; out[:len(cc)] += cc
    return out

def sfx(clave):
    rng = np.random.default_rng(zlib.crc32(clave.encode()))
    if clave == "tuberia-cede":
        D = 4.0; y = np.zeros((int(D * SR), 2)); t = tt(D)
        f = 80 + 45 * np.sin(2 * np.pi * 0.7 * t) + 60 * t; ph = 2 * np.pi * np.cumsum(f) / SR
        y[:, 0] += filt(np.sign(np.sin(ph)) * .3, 60, 900) * np.minimum(1, t / 1.5) * (t < 2.2)
        for k in range(30): a = rng.uniform(.3, 1.9); mezcla(y, tick(rng, 1, 600) * 3, a, 0, .6)
        mezcla(y, filt(rng.standard_normal(int(.25 * SR)), 200, 5000) * np.exp(-tt(.25) * 25) * 2, 2.2, 0, 1.2)
        ag = filt(rng.standard_normal(int(1.8 * SR)), 300, 4500) * np.linspace(0, 1, int(1.8 * SR)) ** 1.5
        mezcla(y, ag, 2.2, 0, .9); y[:, 1] = y[:, 0] * .9
        return y
    if clave == "mandibula-negra":
        D = 5.0; y = np.zeros((int(D * SR), 2))
        for k in range(14):
            mezcla(y, tick(rng, 1, 900) * 3, k * .3, 0, .6); mezcla(y, bombo(.5), k * .3, 0, .6)
            mezcla(y, filt(np.sign(np.sin(2 * np.pi * (55 + 8 * (k % 3)) * tt(.28))) * np.exp(-tt(.28) * 9), 40, 1500), k * .3, 0, .5)
        mezcla(y, filt(rng.standard_normal(int(.9 * SR)), 150, 3500) * np.exp(-tt(.9) * 5) * 2, 4.0, 0, 1.0)
        mezcla(y, bombo(2), 4.0, 0, 1.0)
        return y
    if clave == "ritual-pulso":
        D = 3.0; y = np.zeros((int(D * SR), 2))
        for o in (0, .35, 1.4, 1.75): mezcla(y, bombo(1.3) * np.sin(2 * np.pi * 58 * tt(.35)), o, 0, .8)
        t = tt(D); sh = sum(np.sin(2 * np.pi * f * t) / (i + 1) for i, f in enumerate((880, 1318, 1760, 2637))) * np.exp(-t / 1.2) * .08
        y[:, 0] += sh; y[:, 1] += sh * .8
        return y
    if clave == "timbre-recepcion":
        D = 2.2; y = np.zeros((int(D * SR), 2))
        for o in (0, .55): mezcla(y, campana(2350, 1.5, rng) * .7 + campana(3520, 1.5, rng) * .3, o, 0, .8)
        return y
    if clave == "queso-guindilla":
        D = 2.2; y = np.zeros((int(D * SR), 2))
        mezcla(y, filt(rng.standard_normal(int(.8 * SR)), 3500, None) * np.exp(-tt(.8) * 3), 0, 0, 1.0)
        t = tt(.18); mezcla(y, np.sin(2 * np.pi * np.cumsum(260 - 150 * t / .18) / SR) * np.exp(-t * 8), .85, 0, .9)
        t = tt(.35); mezcla(y, np.sin(2 * np.pi * np.cumsum(500 + 1700 * (t / .35) ** 2) / SR) * adsr(len(t), .02, .08), 1.35, 0, .6)
        return y
    if clave == "puerta-de-tyson":
        D = 3.0; y = np.zeros((int(D * SR), 2))
        mezcla(y, filt(rng.standard_normal(int(.25 * SR)), 80, 2500) * np.exp(-tt(.25) * 14) * 3, 0, 0, 1.0); mezcla(y, bombo(2), 0, 0, 1.0)
        for _ in range(26): mezcla(y, tick(rng, 1, rng.uniform(800, 3000)) * 2, rng.uniform(.05, 1.3), rng.uniform(-.7, .7), .5)
        mezcla(y, bombo(1.5), 1.6, 0, .8)
        return y

def guardar(y, ruta, lufs, kbps):
    y = np.tanh(y / (np.abs(y).max() + 1e-9) * 1.3) * 0.9
    fx = pathlib.Path(tempfile.mkdtemp()) / "t.wav"
    def wav(a):
        with wave.open(str(fx), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
    wav(y)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", str(fx), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?\d+\.?\d*) LUFS", o)[-1])
    g = 10 ** ((lufs - I) / 20); y = np.clip(y * g, -.97, .97)
    wav(y); ruta.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(fx), "-c:a", "libopus", "-b:a", f"{kbps}k", str(ruta)], check=True)
    return I

if __name__ == "__main__":
    man = json.load(open(R / "asset-manifest.json"))["assets"]
    por = {a["id"].split(".", 1)[1]: a for a in man if a["kind"] in ("music", "mood", "sfx")}
    pedidas = sys.argv[1:] or [k for k, a in por.items() if a["kind"] == "sfx"]   # la música son pistas de Kevin MacLeod (tools/musica.py)
    for k in pedidas:
        a = por[k]; ruta = R / a["path"]
        if a["kind"] == "sfx": I = guardar(sfx(k), ruta, -20, 64)
        else: I = guardar(pista(k), ruta, -26, 96)
        print(f"{k:34s} {ruta.stat().st_size // 1024:5d} KB  (medido {I:.1f} LUFS)", flush=True)
