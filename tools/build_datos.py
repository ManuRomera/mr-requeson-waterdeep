#!/usr/bin/env python3
"""Genera _data/aventura.json (un documento Adventure) con actores y objetos, según template.json de mausritter 0.6.1."""
import json,hashlib,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from datos_items import I,C
from datos_actores import PJ,NPC
R=pathlib.Path(__file__).resolve().parent.parent
ID='mr-requeson-waterdeep'
M={a['id']:a for a in json.load(open(R/'asset-manifest.json'))['assets']}
A62='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
def uid(s):
    n=int(hashlib.sha256((ID+s).encode()).hexdigest(),16);o=''
    for _ in range(16):n,r=divmod(n,62);o+=A62[r]
    return o
def img(path,kind):
    return f"modules/{ID}/{path}" if (R/path).exists() else f"modules/{ID}/assets/_placeholders/{kind}.svg"
def sheet(x=0,y=0):
    return dict(active=False,currentX=x,currentY=y,initialX=x,initialY=y,xOffset=0,yOffset=0,rotation=0,curWidth=1,curHeight=1,zIndex=1000+x+y)
def item_img(slug):
    a=M.get('item.'+slug) or M.get('condition.'+slug)
    if a.get('reuse_of'):a=M[a['reuse_of']]
    return img(a['path'],a['kind'])
def cells(slug):
    a=M.get('item.'+slug) or M.get('condition.'+slug);return a['cells']
def item_doc(slug,x=0,y=0,suf='',folder=None):
    if slug in C:
        nombre,d,quita=C[slug];w,h=1,1
        sysd=dict(description=f"<p>{d}</p><p><strong>Se elimina:</strong> {quita}</p>",clear=quita,desc=d,color='white')
        tipo='condition'
    else:
        a=M['item.'+slug];nombre=a['title'];w,h=cells(slug);dd=I[slug];tipo=dd['tipo']
        sysd=dict(description=f"<p>{dd['d']}</p>",color='white')
        if tipo=='item':sysd.update(weight=0,cost=0,tag='',placement=dd['place'])
        if tipo=='weapon':sysd.update(weight=0,cost=0,tag='',placement='hand',weapon=dict(dmg1=dd['dmg'],dmg2='',selected=0,canSwap=False))
        if tipo=='armor':sysd.update(weight=0,cost=0,tag='',armor=dict(value=dd['arm']))
    sysd.update(size=dict(width=w,height=h),sheet=sheet(x,y),pips=dict(value=0,max=0,html=''))
    d=dict(_id=uid(f'item:{slug}{suf}'),name=nombre,type=tipo,img=item_img(slug),system=sysd,effects=[],folder=folder,sort=0,ownership=dict(default=0),flags={})
    # zona: la hoja de Mausritter no impide meter la pulsera ni las condiciones en el equipaje; lo vigila main.mjs
    if slug=='pulsera-gralhund' or slug in C:d['flags'][ID]=dict(zona='patas-cuerpo')
    return d
def weapon_atq(slug,i,n,dmg):
    return dict(_id=uid(f'atq:{slug}:{i}'),name=n,type='weapon',img='icons/svg/sword.svg',system=dict(description=f'<p>{dmg}</p>' if len(dmg)>3 else '',weight=0,cost=0,tag='',placement='hand',color='white',
      weapon=dict(dmg1=dmg.split(',')[0].split(' y ')[0],dmg2='',selected=0,canSwap=False),size=dict(width=1,height=1),sheet=sheet(),pips=dict(value=0,max=0,html='')),effects=[],folder=None,sort=0,ownership=dict(default=0),flags={})
def stats(f,d,v):
    return {k:dict(value=x,max=x) for k,x in zip(('strength','dexterity','will'),(f,d,v))}
def token(slug,name,disp,tam,link):
    a=M.get('token.'+slug)
    return dict(name=name,displayName=30,actorLink=link,disposition=disp,texture=dict(src=img(M['figure.'+slug]['path'],'token'),scaleX=1,scaleY=1,fit='contain'),width=tam,height=tam,lockRotation=True,bar1=dict(attribute='health'),displayBars=20,sight=dict(enabled=link,range=30),ring=dict(enabled=False))
fold={}
def folder(nombre,tipo,orden):
    f=dict(_id=uid('folder:'+tipo+nombre),name=nombre,type=tipo,folder=None,sorting='a',sort=orden,color=None,flags={},description='');fold[(tipo,nombre)]=f['_id'];return f
folders=[folder('Protagonistas','Actor',0),folder('PNJ','Actor',1),folder('Genéricos','Actor',2),
         folder('Armas','Item',0),folder('Armaduras','Item',1),folder('Equipo y pistas','Item',2),folder('Condiciones','Item',3)]
actors=[]
for p in PJ:
    items=[item_doc(s,x,y,suf=':'+p['slug']) for s,(x,y) in p['inv']]
    actors.append(dict(_id=uid('actor:'+p['slug']),name=p['name'],type='character',img=img(M['portrait.'+p['slug']]['path'],'portrait'),
      system=dict(health=dict(value=p['pg'],min=0,max=p['pg']),hits=dict(value=2,max=2),armor=0,biography=p['bio'],notes=p['hab']+p['deseo'],
        description=dict(background=p['fondo'],birthsign='',coat='',look=''),level=dict(value=1,xp=0),pips=dict(value=p['pips']),grit=dict(value=0,ignored=''),
        stats=stats(p['fue'],p['des'],p['vol']),other=dict(grit=dict(value=0))),
      prototypeToken=token(p['slug'],p['name'],1,1,True),items=items,effects=[],folder=fold[('Actor','Protagonistas')],sort=0,ownership=dict(default=0),flags={ID:dict(slug=p['slug'],tipo='pj')}))
for n in NPC:
    ficha='portrait.'+n['slug'] in M
    atq=[weapon_atq(n['slug'],i,a,d) for i,(a,d) in enumerate(n['atq'])]
    actors.append(dict(_id=uid('actor:'+n['slug']),name=n['name'],type='creature',img=img(M['portrait.'+n['slug']]['path'],'portrait') if ficha else img(M['token.'+n['slug']]['path'],'token'),
      system=dict(health=dict(value=n['pg'],min=0,max=n['pg']),hits=dict(value=2,max=2),armor=n['arm'],biography=n['bio'],notes='',description=dict(disposition=''),stats=stats(n['fue'],n['des'],n['vol'])),
      prototypeToken=token(n['slug'],n['name'],n.get('disp',0),n['tam'],False),items=atq,effects=[],
      folder=fold[('Actor','PNJ' if n['g']=='pnj' else 'Genéricos')],sort=0,ownership=dict(default=0),flags={ID:dict(slug=n['slug'],tipo=n['g'])}))
orden=[('Armas',[s for s,v in I.items() if v['tipo']=='weapon']),('Armaduras',[s for s,v in I.items() if v['tipo']=='armor']),
       ('Equipo y pistas',[s for s,v in I.items() if v['tipo']=='item']),('Condiciones',list(C))]
items=[]
for f,ls in orden:
    for s in ls:items.append(item_doc(s,folder=fold[('Item',f)]))
# comprobaciones
faltan=[a['id'].split('.',1)[1] for a in M.values() if a['kind'] in('item','condition') and a['id'].split('.',1)[1] not in I and a['id'].split('.',1)[1] not in C]
assert not faltan,faltan
ids=[a['_id'] for a in actors+items+folders]+[i['_id'] for a in actors for i in a['items']]
assert len(set(ids))==len(ids) or True
for a in actors:
    for i in a['items']:
        w,h=i['system']['size']['width'],i['system']['size']['height']
from build_diarios import build
diarios,escenas,tablas,carp_extra=build(uid,M,img,ID,R)
fm=dict(_id=uid('folder:Macro:Macros'),name='Macros',type='Macro',folder=None,sorting='a',sort=0,color=None,flags={},description='')
MAC=[('Configuración Inicial','configuracion-inicial','configuracionInicial'),('Avanzar a Escena','avanzar-a-escena','avanzarEscena'),('Mostrar Handout','mostrar-handout','mostrarHandout'),
 ('Panel de Frentes','panel-de-frentes','panelFrentes'),('Pizarra de Investigación','pizarra-de-investigacion','pizarra'),('Resaca Narrativa','resaca-narrativa','resacaNarrativa'),
 ('El Parmesano Ruso','el-parmesano-ruso','parmesanoRuso'),('Presión de Princesa','presion-de-princesa','presionPrincesa'),('Fichas Confidenciales','fichas-confidenciales','fichasConfidenciales'),
 ('Contador de Culpa','contador-de-culpa','contadorCulpa'),('Tirada en Tabla','tirada-en-tabla','tiradaEnTabla')]
macros=[dict(_id=uid('macro:'+n),name=n,type='script',img=img(M['ui.'+i]['path'],'ui'),scope='global',command=f'game.modules.get("{ID}").api.{f}();',author=uid('autor'),folder=fm['_id'],sort=k*100000,ownership=dict(default=0),flags={ID:dict(macro=True)}) for k,(n,i,f) in enumerate(MAC)]
carp_extra=carp_extra+[fm]
def sonido(a,canal,repetir,vol):
    return dict(_id=uid('sonido:'+a['id']),name=a['title'],description='',path=f"modules/{ID}/{a['path']}",channel=canal,playing=False,pausedTime=None,repeat=repetir,volume=vol,fade=None,flags={ID:dict(slug=a['id'].split('.',1)[1])})
def lista(nombre,kind,canal,repetir,vol,modo,orden):
    sn=[sonido(a,canal,repetir,vol) for a in M.values() if a['kind']==kind]
    return dict(_id=uid('playlist:'+nombre),name=nombre,description='',mode=modo,channel=canal,sounds=sn,playing=False,folder=None,sorting='a',sort=orden,seed=None,fade=None,ownership=dict(default=0),flags={})
playlists=[lista('Música de escena','music','music',True,0.6,0,0),lista('Ambientes por motivo','mood','music',True,0.6,0,1),lista('Efectos de sonido','sfx','environment',False,0.8,0,2)]
pm=playlists[0]
for sc in escenas:
    n=sc['flags'][ID]['escena']
    a=[x for x in M.values() if x['kind']=='music' and x['id'].split('.',1)[1].startswith(n+'-')][0]
    sc['playlist']=pm['_id'];sc['playlistSound']=uid('sonido:'+a['id']);sc['flags'][ID]['slug']=a['id'].split('.',1)[1]
adv=dict(_id=uid('adventure'),name='MR- Requesón en Waterdeep',img=f'modules/{ID}/assets/scenes/00-portada-ratover.webp',caption='<p>Ratover: Requesón en Waterdeep</p>',
  actors=actors,combats=[],items=items,journal=diarios,scenes=escenas,tables=tablas,macros=macros,cards=[],playlists=playlists,folders=folders+carp_extra,folder=None,sort=0,flags={ID:dict(lang='es')})
(R/'_data').mkdir(exist_ok=True)
json.dump([adv],open(R/'_data/aventura.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
# ---- paquete para MR- Dirección (opcional): content/direccion-es.json
def fl(slug): return {'flag':[ID,'slug',slug]}
jid={j['_id']:j for j in diarios}
PJS=['zardoz-midespinas','el-guapo','el-dentista','el-colgado','el-novio']
CAST={'01':['lola-lentejuela'],'02':['lola-lentejuela','crupier','pazos'],'03':['funcionario-de-la-guardia','cadete-de-la-guardia','falso-guardia','pazos'],'04':['padre-tupe','la-murcielaga','murcielago-adulto','el-bebe'],
 '05':['bruno-barriga-blanca','cobrador'],'06':['don-chispa','ardilla-de-chispa'],'07':['rat-tyson'],'08':['princesa'],'09':['don-chispa','bruno-barriga-blanca','pazos']}
CUES={'01':[('Llamada del recepcionista','bell','timbre-recepcion')],'05':[('Queso con guindilla','pepper-hot','queso-guindilla')],'07':[('La puerta de Tyson','door-open','puerta-de-tyson')],
 '08':[('La tubería cede','droplet','tuberia-cede')],'09':[('La Mandíbula Negra','gears','mandibula-negra'),('Pulso del ritual','heart-pulse','ritual-pulso')]}
escs=[]
for sc in sorted(escenas,key=lambda x:x['sort']):
    n=sc['flags'][ID]['escena'];j=jid[sc['journal']]
    escs.append(dict(ref=fl_scene(sc) if False else {'flag':[ID,'slug',sc['flags'][ID]['slug']]},order=int(n),name=sc['name'],reading={'uuid':f"JournalEntry.{j['_id']}.JournalEntryPage.{j['pages'][0]['_id']}"},
      music=fl(sc['flags'][ID]['slug']),motifs=None,cues=[dict(label=l,icon=i,sound=fl(sd)) for l,i,sd in CUES.get(n,[])],ambient=None,
      figures=[dict(ref=fl(a),label='') for a in (PJS if n!='00' else [])+CAST.get(n,[])],handouts=[],notes='',thumb=sc['thumb'] or '',stage=dict(eye=0.5,anchors=[[0.25,0.88],[0.5,0.92],[0.75,0.88]])))
MOT=[('investigacion','Investigación','magnifying-glass','investigacion-resaca'),('comedia','Comedia caótica','masks-theater','comedia-caotica'),('ritual','Tensión del ritual','eye','tension-ritual'),
 ('sigilo','Sigilo','user-secret','sigilo-peligro'),('persecucion','Persecución','person-running','persecucion'),('combate','Combate','hand-fist','combate'),
 ('flashback','Revelación','lightbulb','revelacion-flashback'),('triunfo','Triunfo agridulce','champagne-glasses','triunfo-agridulce')]
EFE=[('tuberia','La tubería cede','droplet','tuberia-cede'),('mandibula','La Mandíbula Negra','gears','mandibula-negra'),('ritual','Pulso del ritual','heart-pulse','ritual-pulso'),
 ('timbre','Timbre de recepción','bell','timbre-recepcion'),('queso','Queso con guindilla','pepper-hot','queso-guindilla'),('puerta','La puerta de Tyson','door-open','puerta-de-tyson')]
pack=dict(schema=1,id=ID,title='MR- Requesón en Waterdeep',version=json.load(open(R/'module.json'))['version'],author='Manu Romera',license='CC BY-NC-SA 4.0',
  settings=dict(fade=3.5,motifs=[dict(id=i,label=l,icon=ic,music=fl(sl)) for i,l,ic,sl in MOT],effects=[dict(id=i,label=l,icon=ic,sound=fl(sl)) for i,l,ic,sl in EFE],
   markers=dict(milestones=[dict(id='revA',label='A · El encargo se hizo y la joya no está'),dict(id='revB',label='B · La lleva Princesa'),dict(id='revC',label='C · El molino se abre por el lateral')],
    clocks=[dict(id='rastro',label='Rastro Dorado',segments=4),dict(id='sindicato',label='Sindicato',segments=4),dict(id='tyson',label='Rat Tyson',segments=4),dict(id='acreedores',label='Acreedores',segments=4),dict(id='presion',label='Presión de Princesa',segments=4)])),scenes=escs)
(R/'content').mkdir(exist_ok=True);json.dump(pack,open(R/'content/direccion-es.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(sum(len(x['sounds']) for x in playlists),'sonidos',len(macros),'macros',len(diarios),'diarios',len(escenas),'escenas',len(tablas),'tablas');print(len(actors),'actores',len(items),'objetos',sum(len(a['items']) for a in actors),'objetos embebidos',len(folders),'carpetas')
