import re,json,sys
OLD='/Volumes/Datos_Dock/FoundryVTT/Data/modules/ratover-requeson-waterdeep/'
def entries(text,pat):
    out=[];cur=None
    for ln in text.split('\n'):
        m=re.match(pat,ln)
        if m:
            cur={'file':m.group(1),'title':m.group(2),'lines':[]};out.append(cur)
        elif cur is not None: cur['lines'].append(ln)
    return out
a=open(OLD+'ASSETS.md',encoding='utf8').read()
sec={}
for part in re.split(r'\n## ',a)[1:]:
    name,body=part.split('\n',1); sec[name.strip()]=body
res={}
for k,b in sec.items():
    es=entries(b,r'### `([^`]+)` — (.*)')
    for e in es:
        t='\n'.join(e['lines']);r=re.search(r'Ruta: `([^`]+)`',t)
        e['path']=r.group(1) if r else None
        e['prompt']=re.sub(r'Ruta: `[^`]+`','',t).strip()
    res[k]=es
s=open(OLD+'SUNO_PROMPTS.md',encoding='utf8').read()
au=entries(s,r'## `([^`]+)` — (.*)')
for e in au:
    t='\n'.join(e['lines']);e['path']=re.search(r'Ruta: `([^`]+)`',t).group(1)
    e['func']=(re.search(r'\*\*Función en mesa:\*\*\s*(.*)',t) or [0,''])[1]
    e['design']=(re.search(r'\*\*Diseño:\*\*\s*(.*)',t) or [0,''])[1]
    e['dur']=(re.search(r'\*\*Duración objetivo:\*\*\s*(.*)',t) or [0,''])[1]
    m=re.search(r'\*\*Prompt Suno\*\*\s*(.*?)(\n---|\Z)',t,re.S)
    e['prompt']=m.group(1).strip() if m else ''
res['audio']=au
json.dump(res,open('/Volumes/Datos_Dock/FoundryVTT/Data/modules/mr-requeson-waterdeep/tools/catalogo_antiguo.json','w'),ensure_ascii=False,indent=1)
for k,v in res.items():print(k,len(v))
G='mouse-scale prop for a dark fantasy criminal-comedy'
print([e['file'] for e in res['Ítems y condiciones'] if G in e['prompt']])
print([ (e['file'],len(e['prompt'])) for e in res['audio'] if len(e['prompt'])<200])
