#!/usr/bin/env python3
"""Genera las dos portadas con Codex, en serie: cover (módulo, vertical) y world (mundo, 16:9, sin personajes ni rótulos)."""
import os, subprocess, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTILO = ("Art direction for the 'Ratover' series: dark-fantasy criminal comedy in a mouse-scale macro world inside a luxurious human hotel suite. "
          "Warm candlelight with magenta and cyan neon accents, plum purple and antique gold palette, painterly gritty realism, rich detail. "
          "Do not draw any text, letters, logos or watermarks.")
P = {
 "cover": ("1024x1536", "Book-cover key art, vertical composition. Five anthropomorphic mice in rumpled purple velvet outfits lie and sit in a hungover heap on a plush carpet under a giant human bed, "
           "dedales and cigar boxes around them. In the center, standing on its edge like a portal, a huge heavy human gold bangle glows. Far behind them a bathroom door is slightly ajar with a faint pink eye glinting in the dark gap. "
           "Neon magenta and cyan light from Rat Vegas signs. Funny but dangerous mood. Leave the top fifth of the image calm and darker, empty of detail."),
 "world": ("1536x1024", "Wide cinematic establishing shot of Rat Vegas, a secret mouse nightlife district hidden inside a luxurious human hotel suite at night. In the middle distance a giant human gold bangle stands on its edge like a glowing triumphal arch. "
           "Neon signs built from thimbles, jewelry and casino chips, a velvet sofa boulevard, a coffee-tin warehouse and a cigar-box penthouse. At the far end a bathroom door is ajar with a dangling chain. "
           "No characters, no animals, no people, empty set. Leave the center slightly calmer: a game title will be placed over it."),
}
for k, (tam, desc) in P.items():
    out = os.path.join("art_src", "raw", f"{k}.png")
    if os.path.exists(os.path.join(ROOT, out)): continue
    prompt = (f"Usa tu herramienta de generación de imágenes para crear UNA sola imagen, tamaño {tam}. Descripción: {desc} {ESTILO}\n"
              f"Después copia EL PNG QUE TU HERRAMIENTA ACABA DE DEVOLVER EN ESTA SESIÓN (usa su ruta exacta; nunca busques el archivo más reciente de la carpeta, puede ser de otra sesión) a {out}. No generes más de una imagen ni modifiques otros archivos.")
    for _ in range(3):
        subprocess.run(["codex", "exec", "-m", "gpt-6.1-sol", "-c", 'model_reasoning_effort="low"', "--skip-git-repo-check", "-s", "workspace-write", prompt],
                       cwd=ROOT, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
        if os.path.exists(os.path.join(ROOT, out)): break
    print(k, "OK" if os.path.exists(os.path.join(ROOT, out)) else "ERR", flush=True)
print("Hecho", flush=True)
