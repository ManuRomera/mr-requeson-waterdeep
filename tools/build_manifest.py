#!/usr/bin/env python3
"""asset-manifest.json según PASO-0: solo rutas, specs y prompts, nunca binarios. Uso: build_manifest.py old.json"""
import json,re,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from prompts_base import ICO,NEW,HANDOUT_PROMPTS
ROOT=pathlib.Path(__file__).resolve().parent.parent
old=json.load(open(sys.argv[1]))
O={k:{e['file'].rsplit('.',1)[0]:e for e in v} for k,v in old.items() if k!='Formatos'}
ITEMS,ACT,HAND,PHO,SC,AU=O['Ítems y condiciones'],O['Actores'],O['Handouts'],O['Fotografías de la noche'],O['Escenas'],O['audio']
M=lambda s:s.replace('—',',')
def clean(p): return re.sub(r'\s+',' ',re.sub(r'\s*--(ar|v|no)\b[^-]*(?=--|$)','',p)).strip().rstrip('.').strip()
NOBG=" --no humans, mice, rats, animals, characters"
A=[]
def add(kind,id_,title,path,prompt,ar,px,marca,**x):
    suf=f" --ar {ar} --v 6.0"+(NOBG if kind=='scene' else '')
    A.append({'id':f"{kind}.{id_}",'kind':kind,'title':title,'path':path,'ar':ar,'px':px,'marca':marca,
      'fallback':f"assets/_placeholders/{kind}.svg",'prompt':M(clean(prompt))+suf,'status':'pendiente',**x})
# ---------- escenas (10, en orden de juego)
SCN=[('00-portada-ratover','00-portada-ratover','Portada con panel del ritual'),('02-la-villa-del-cielo-caido','01-la-villa-del-cielo-caido',None),
 ('03-dado-de-nacar-y-camerino-de-lola','02-dado-de-nacar',None),('04-bulevar-de-los-muelles-rojos-y-la-rendija-azul','03-bulevar-precintado','Bulevar precintado'),
 ('05-capilla-del-ultimo-chillido','04-capilla-del-ultimo-chillido',None),('06-notaria-del-parmesano','05-notaria-del-parmesano',None),
 ('07-almacen-de-don-chispa','06-almacen-de-don-chispa',None),('08-atico-de-rat-tyson','07-atico-de-rat-tyson',None),
 ('09-el-bano-de-princesa','08-el-bano-de-princesa',None),('10-la-mandibula-negra','09-la-mandibula-negra',None)]
for o,n,t in SCN:
    e=SC[o];p=e['prompt'].replace(', 16:9.','.')
    if 'bulevar' in n: p=p.replace('Empty scene','Red ribbon crime-scene tape and sealing strips stretched across the avenue, a sealed-off cordoned set. Empty scene')
    if 'portada' in n: p=p.replace('Empty scene','')+" Empty scene"
    if 'Empty scene' not in p: p+=" Empty scene"
    add('scene',n,t or M(e['title']),f"assets/scenes/{n}.webp",p,'16:9',[2560,1440],'esquina+tile',thumb=f"assets/scenes/thumbs/{n}.webp",grid=False,fog=False,playlist=n)
# ---------- tokens (22) y retratos (15)
FICHA=['zardoz-midespinas','el-guapo','el-dentista','el-colgado','el-novio','lola-lentejuela','pazos','rat-tyson','princesa','el-bebe','don-chispa','bruno-barriga-blanca','padre-tupe','la-murcielaga','agente-del-sindicato']
GEN=['crupier','cobrador','falso-guardia','murcielago-adulto','ardilla-de-chispa','funcionario-de-la-guardia','cadete-de-la-guardia']
EXTRA={ # prompts del manuscrito que el catálogo anterior no traía con ese nombre
'agente-del-sindicato':("Agente del Sindicato de la Zarpa Fina","Full body shot from head to toe of an elegant anthropomorphic mouse fixer wearing immaculate fine gloves. Entire body, tail, and feet fully visible inside frame. Dark tailored coat, no visible weapon, looking down at his own hands rather than forward, unsettling calm. Dark fantasy, gritty realism, centered. Isolated on a pure solid black background"),
'funcionario-de-la-guardia':("Funcionario de la Guardia","Full body shot from head to toe of an elderly anthropomorphic mouse civil servant in a real Waterdeep Guard uniform. Entire body, tail, and feet fully visible inside frame. Ink-stained fingers, portable writing desk strapped to his chest, extremely slow patient expression. Dark fantasy, gritty realism, centered. Isolated on a pure solid black background"),
'cadete-de-la-guardia':("Cadete de la Guardia","Full body shot from head to toe of a very young anthropomorphic mouse guard cadet in an oversized uniform. Entire body, tail, and feet fully visible inside frame. Helmet too big, eager bored energy, holding a training baton, standing far too straight. Dark fantasy, gritty realism, centered. Isolated on a pure solid black background")}
OLDN={'cobrador':'cobrador','crupier':'crupier','falso-guardia':'falso-guardia'}
def tok(st):
    if st in EXTRA:return EXTRA[st]
    e=ACT[st];return M(e['title']),e['prompt']
for st in FICHA+GEN:
    t,p=tok(st)
    if st=='pazos':p=p.replace('anthropomorphic rat assassin','anthropomorphic mouse assassin')
    grp='pcs' if st in FICHA[:5] else ('npcs' if st in FICHA else 'generic')
    add('token',st,t,f"assets/actors/{grp}/{st}.webp",p,'2:3',[800,1200],'discreta',group=grp,transparent_bg=True,round_token=f"assets/actors/tokens/{st}.webp")
def portrait(p):
    ss=[x for x in re.split(r'(?<=\.) ',clean(p)+'.') if 'fully visible' not in x and 'Isolated on' not in x]
    ss[0]=re.sub(r'^Full body shot (from head to toe |from nose to tail )?of','Close-up head and shoulders portrait of',ss[0])
    ss[0]=re.sub(r'^Full body shot of','Close-up portrait of',ss[0])
    return ' '.join(ss).rstrip('.')+'. Isolated on a pure solid black background'
for st in FICHA:
    t,p=tok(st)
    if st=='pazos':p=p.replace('anthropomorphic rat assassin','anthropomorphic mouse assassin')
    add('portrait',st,t,f"assets/actors/portraits/{st}.webp",portrait(p),'1:1',[512,512],'discreta',para_ficha=True)
# ---------- items (28) + condiciones (6)
NUEVOS={
'baston-de-escenario':ICO("a slim lacquered stage cane with a chipped silver ferrule and a gaudy tassel, mouse-sized, used as a club"),
'chaleco-de-contable':ICO("a tight leather accountant vest with brass buttons and a tiny watch chain, mouse-sized, studded with ink stains"),
'vendas-con-plomo':ICO("a coil of grubby linen bandages with small lead fishing weights sewn into the layers, mouse-sized armor"),
'cafe-de-chispa':ICO("a tiny cup of black coffee with a silver spoon standing in it, steam curling, a bean on the saucer"),
}
CEL={'pulsera-gralhund':(2,2),'maza-de-boton':(1,2),'chaleco-ciruela':(1,2),'capa-purpura':(1,2),'maletin-quirurgico':(1,2),'peto-de-chapa-de-lata':(1,2)}
GRP=[('macguffin',['pulsera-gralhund']),('arma',['daga-de-aguja','maza-de-boton','bisturi-de-lata','cuchillo-de-mesa','navaja-corta','baston-de-escenario']),
 ('armadura',['peto-de-chapa-de-lata','chaleco-de-contable','vendas-con-plomo']),
 ('equipo',['pinza-fina','el-bebe-carga','etiqueta-de-calma-comadrejas','capa-purpura','fajin-lila-de-la-manada','bufanda-purpura-de-la-manada','casco-de-agente-abollado','cuerda-corta','alianza-de-alambre','chaleco-ciruela','maletin-quirurgico','monoculo-roto','carrete-de-hilo-resistente','sales-aromaticas','cuentagotas-vacio','portabebes-de-fieltro','bolsa-de-objetos-inutiles']),
 ('consumible',['calma-comadrejas','cafe-de-chispa','macadamia-imperial']),
 ('pista',['recibo-del-intercambio','llave-de-jaula','llave-de-mantenimiento','ficha-de-camerino','dos-cintas-de-botella-intercambiadas','paper-bird','medio-contrato-del-sindicato','nota-lacrada-de-nixyus','panuelo-con-sello-gralhund','recibo-de-una-segunda-jarra','tarjeta-vip-del-dado','foto-nupcial-borrosa']),
 ('condicion',['resaca','ardido','deuda','buscado','mordido','compromiso-familiar'])]
TITLES={'baston-de-escenario':'Bastón de escenario','chaleco-de-contable':'Chaleco de contable','vendas-con-plomo':'Vendas con plomo','cafe-de-chispa':'Café de Chispa','cuchillo-de-mesa':'Cuchillo de mesa','navaja-corta':'Navaja corta','peto-de-chapa-de-lata':'Peto de chapa de lata','carrete-de-hilo-resistente':'Carrete de hilo','sales-aromaticas':'Sales aromáticas','cuentagotas-vacio':'Cuentagotas vacío','bolsa-de-objetos-inutiles':'Bolsa de objetos inútiles','dos-cintas-de-botella-intercambiadas':'Las dos cintas','llave-de-jaula':'Llave de jaula (R.T.)','paper-bird':'Paper Bird'}
for g,ls in GRP:
    for st in ls:
        if st=='etiqueta-de-calma-comadrejas':
            A.append({'id':'item.etiqueta-de-calma-comadrejas','kind':'item','title':'Etiqueta de Calma-Comadrejas','path':'assets/items/etiqueta-de-calma-comadrejas.webp','reuse_of':'handout.etiqueta-de-calma-comadrejas','ar':'1:1','cells':[1,1],'categoria':g,'status':'reutiliza el arte del handout, no se genera'});continue
        if st=='nota-lacrada-de-nixyus':p=HANDOUT_PROMPTS['nota-de-nixyus']
        elif st in NUEVOS:p=NUEVOS[st]
        elif st in NEW:p=NEW[st]
        elif st in HANDOUT_PROMPTS:p=HANDOUT_PROMPTS[st]
        else:p=ITEMS[st]['prompt']
        w,h=CEL.get(st,(1,1));ar='1:2' if (w,h)==(1,2) else '1:1'
        t=TITLES.get(st) or (M(ITEMS[st]['title']) if st in ITEMS else st)
        cond=g=='condicion'
        add('condition' if cond else 'item',st,t,f"assets/{'conditions' if cond else 'items'}/{st}.webp",p,ar,[512*w,512*h],'discreta',
            cells=[w,h],categoria=g,**({'ocupa_casilla':'mano o cuerpo, no se descarga'} if cond else {}),
            **({'placement':'solo mano y cuerpo, nunca equipaje'} if st=='pulsera-gralhund' else {}),**({'cells_asumido':True} if st in ('chaleco-de-contable','vendas-con-plomo','baston-de-escenario') else {}))
# ---------- handouts: 11 documentos + 15 fotografías
DOC=[('recibo-del-intercambio','Recibo del intercambio',None,'item.recibo-del-intercambio'),
 ('nota-de-nixyus','Nota de Nixyus',None,None),
 ('inscripcion-del-aro','Inscripción del aro',"RPG game item icon of the inside surface of a heavy gold human bangle seen in close macro, a band of fine engraved noble script too small to read and a small family seal, lit from one side. Centered, dark fantasy, hyper-detailed metal, isolated on pure solid black background",None),
 ('etiqueta-de-calma-comadrejas','Etiqueta de Calma-Comadrejas',None,None),('pagare-de-parmesano','Pagaré de parmesano',None,None),('acta-de-boda','Acta de boda',None,None),
 ('parte-de-incidencias','Parte de incidencias de la Guardia','acta-de-redada',None),('plano-de-pazos','Plano de Pazos',None,None),
 ('manual-de-la-mandibula-negra','Manual de La Mandíbula Negra',None,None),('dos-cintas','Las dos cintas',None,'item.dos-cintas-de-botella-intercambiadas'),
 ('lista-del-rastro-dorado','La lista del Rastro Dorado',"RPG game item icon of a long scroll of aged parchment on which golden ink writes itself, rows of tiny unreadable names each followed by a tiny clock time, a Gralhund black and gold wax seal at the bottom. Centered, dark fantasy, magical glow, isolated on pure solid black background",None),
 ('pared-de-la-villa','Pared de la Villa',None,None)]
for st,t,p,reuse in DOC:
    ar='1:2' if st in ('pagare-de-parmesano','parte-de-incidencias','lista-del-rastro-dorado') else '1:1'
    if reuse:
        A.append({'id':f"handout.{st}",'kind':'handout','title':t,'path':f"assets/handouts/{st}.webp",'reuse_of':reuse,'ar':ar,'status':'reutiliza el arte del ítem, no se genera'});continue
    pr=p if (p and p.startswith('RPG')) else HANDOUT_PROMPTS[p or st if (p or st) in HANDOUT_PROMPTS else st]
    add('handout',st,t,f"assets/handouts/{st}.webp",pr,ar,[1024,1024*(2 if ar=='1:2' else 1)],'esquina',visible_a_jugadores=True)
for st,e in PHO.items():
    add('photo',st,M(e['title']),e['path'],e['prompt'],'3:2',[1536,1024],'esquina',orden=int(st[:2]),estilo='cámara desechable con flash')
# ---------- iconos de macro (11)
UI=[('configuracion-inicial','a brass gear over an open travel trunk'),('avanzar-a-escena','a wooden stage curtain half drawn with a spotlight'),('mostrar-handout','an open hand holding up a folded letter'),
 ('panel-de-frentes','four small clock faces arranged in a square, each with one hand'),('pizarra-de-investigacion','a corkboard with pinned notes joined by red thread'),
 ('resaca-narrativa','a cracked thimble with a swirl of memory smoke rising from it'),('el-parmesano-ruso','a wedge of parmesan cheese with a red chili pepper and a small die'),
 ('presion-de-princesa','a rusty water pipe with a pressure gauge in the red zone'),('fichas-confidenciales','a sealed envelope with a keyhole and a wax seal'),
 ('frente-rastro-dorado','a golden footprint trail ending in a glowing wax seal'),('frente-sindicato','a fine-gloved hand holding out a velvet purse'),('frente-rat-tyson','a heavy boxing glove with a notched ear silhouette behind it'),('frente-acreedores','a ledger book with a tiny padlock and a quill'),
 ('contador-de-culpa','a small brass balance scale tipped to one side holding a tiny gold ring'),('tirada-en-tabla','a twenty-sided die resting on a ruled table scroll')]
for st,d in UI:
    add('ui',st,st.replace('-',' ').capitalize(),f"assets/ui/{st}.webp",f"Flat game UI icon of {d}. Bold simple silhouette, aged gold line art with deep plum shading, dark fantasy criminal-comedy mood, readable at small size, isolated on pure solid black background",'1:1',[256,256],'discreta')
# ---------- audio
def aud(kind,i,t,path,e,**x):
    A.append({'id':f"{kind}.{i}",'kind':kind,'title':t,'path':path,'format':'ogg opus','loudnorm_lufs':-26,'fallback':None,'status':'sintetizado con tools/audio.py; sustituible por la pista de Suno en la misma ruta',**x,'prompt':M(e['prompt']) if e else x.pop('prompt')})
for o,n,t in SCN:
    e=AU[o];aud('music',n,t or M(e['title']),f"assets/audio/music/{n}.ogg",e,loop=True,duracion_objetivo=e['dur'],funcion=M(e['func']),diseno=M(e['design']))
SFX=[('tuberia-cede',"Heavy old iron water pipe groaning, a sharp metallic crack and a rush of water bursting free, close and dry, no music",4),
 ('mandibula-negra',"Brass coffee grinder gears engaging, grinding teeth biting down with a heavy mechanical thunk, slightly greasy, no music",5),
 ('ritual-pulso',"A low magical heartbeat pulse with a thin golden shimmer on top, ominous and administrative, no melody",3),
 ('timbre-recepcion',"A hotel reception desk bell, two dry rings, small room reverb, a faint annoyed pause between them",2),
 ('queso-guindilla',"A sharp sizzle and a wet gulp followed by a strangled squeak, comic and quick, no music",2),
 ('puerta-de-tyson',"A massive wooden door being shouldered off its hinges, splintering and a heavy thud on the floor, no music",3)]
for i,p,d in SFX:
    A.append({'id':f"sfx.{i}",'kind':'sfx','title':i.replace('-',' ').capitalize(),'path':f"assets/audio/sfx/{i}.ogg",'format':'ogg opus','loop':False,'duracion_s':d,'fallback':None,'status':'sintetizado con tools/audio.py; sustituible en la misma ruta','prompt':p})
# opcional: ambientes por motivo del catálogo anterior (no cuentan en el total de PASO-0)
for st,e in AU.items():
    if '/moods/' in e['path']:
        aud('mood',st,M(e['title']),e['path'].replace('audio/moods','audio/moods'),e,loop=True,opcional=True,duracion_objetivo=e['dur'],funcion=M(e['func']),diseno=M(e['design']))
# ---------- validación
errs=[];ids=[a['id'] for a in A];assert len(set(ids))==len(ids),'ids duplicados'
paths=[a['path'] for a in A];assert len(set(paths))==len(paths),'rutas duplicadas'
for a in A:
    if 'reuse_of' in a:
        assert a['reuse_of'] in ids,a['id'];continue
    p=a['prompt']
    if a['kind'] in ('music','mood','sfx'):
        if '—' in p:errs.append((a['id'],'raya'))
        continue
    exp={'scene':'16:9','token':'2:3','photo':'3:2'}.get(a['kind'],a['ar']);m=re.search(r'--ar (\d+:\d+)',p)
    if not m or m.group(1)!=exp:errs.append((a['id'],'ar'))
    if a['kind']=='scene' and 'no humans, mice, rats, animals, characters' not in p:errs.append((a['id'],'no'))
    if '—' in p or 'Paper bird' in p or 'mouse-scale prop for a dark fantasy' in p or 'consistent Rat Vegas art direction' in p:errs.append((a['id'],'estilo/generico'))
    if a['kind']=='token' and 'fully visible inside frame' not in p and 'Entire' not in p:errs.append((a['id'],'encuadre'))
    if a['kind']=='portrait' and ('Close-up' not in p or 'fully visible' in p):errs.append((a['id'],'retrato'))
C={}
for a in A:C[a['kind']]=C.get(a['kind'],0)+1
gen=sum(1 for a in A if 'reuse_of' not in a and a['kind']!='mood')
out={'module':'mr-requeson-waterdeep','title':'MR- Requesón en Waterdeep','idioma':'es','version':'0.0.1-manifest','status':'BORRADOR para revisión','base':'PASO-0 + prompts del manuscrito y del catálogo anterior',
 'sistema':{'id':'mausritter','version':'0.6.1','foundry':'13'},'jugadores':'PJ genéricos, sin asignar a usuarios',
 'rules':{'binarios':'nunca en este archivo','escenas':'webp 2560x1440 16:9, sin grid ni niebla, miniatura webp 400 px en scenes/thumbs, tile animado assets/brand/mr-marca.webm',
  'tokens':'webp con alfa 800x1200 (2:3) y token redondo en actors/tokens','retratos':'webp 512x512 para la ficha','iconos':'1x1 y 2x2 en 1:1, 1x2 en 1:2','audio':'ogg opus, bucle sin costura, loudnorm -26 LUFS, máx. 10 min',
  'marca':'Trabajo LOGO/marca/marca.py: esquina en escenas, documentos y fotos; discreta en tokens, retratos, iconos','placeholders':'assets/_placeholders/<kind>.svg'},
 'counts':C,'generables':gen,'assets':A}
(ROOT/'asset-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=1),encoding='utf8')
print(C,'generables sin moods:',gen,'| errores:',errs)
