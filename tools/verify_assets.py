#!/usr/bin/env python3
"""Comprueba en disco cada ruta de asset-manifest.json."""
import json,pathlib,collections
R=pathlib.Path(__file__).resolve().parent.parent
m=json.load(open(R/'asset-manifest.json'))
lista=[a for a in m['assets'] if a.get('path') and not a.get('reuse_of')]
falta=collections.Counter();tot=collections.Counter()
for a in lista:
    tot[a['kind']]+=1
    if not (R/a['path']).exists():falta[a['kind']]+=1
for k in sorted(tot):print(f"{k:12s} {tot[k]-falta[k]:3d}/{tot[k]:3d}")
print(f"TOTAL {len(lista)-sum(falta.values())}/{len(lista)}")
