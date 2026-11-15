"""Escenas, diarios y tablas a partir de aventura/*.md y asset-manifest.json."""
import re,sys,markdown
sys.path.insert(0,'/Volumes/Datos_Dock/FoundryVTT/Trabajo LOGO/marca')
import marca
from datos_items import I
MD=markdown.Markdown(extensions=['tables','sane_lists'])
def html(md):
    MD.reset();return MD.convert(md)
def lee(R,n):
    return (R/'aventura'/n).read_text(encoding='utf8')
def secciones(txt,nivel):
    """Divide por encabezados del nivel dado. Devuelve [(titulo, cuerpo)]; cada nivel superior corta la sección."""
    pre='#'*nivel+' ';sup=['#'*k+' ' for k in range(1,nivel+1)]
    out=[];cur=None
    for ln in txt.split('\n'):
        if any(ln.startswith(p) for p in sup):
            if ln.startswith(pre):
                cur=[ln[len(pre):].strip(),[]];out.append(cur)
            else:cur=None
        elif cur is not None:cur[1].append(ln)
    return [(t,'\n'.join(b).strip()) for t,b in out]
def tabla(md):
    filas=[l for l in md.split('\n') if l.startswith('|')]
    if len(filas)<3:return None
    cel=lambda l:[c.strip() for c in l.strip().strip('|').split('|')]
    return cel(filas[0]),[cel(l) for l in filas[2:]]

def firma(uid,ID,n):
    x,y,w,h=marca.caja_animada(2560,1440)
    return dict(_id=uid('tile:firma:'+n),texture=dict(src=f'modules/{ID}/assets/brand/mr-marca.webm',scaleX=1,scaleY=1,tint='#ffffff',fit='fill'),x=x,y=y,width=w,height=h,elevation=0,sort=0,rotation=0,alpha=1,hidden=False,locked=True,
      restrictions=dict(light=False,weather=False),occlusion=dict(mode=0,alpha=0),video=dict(loop=True,autoplay=True,volume=0),flags={})

def build(uid,M,img,ID,R):
    c1,c2,c3,c4=[lee(R,n) for n in('01-introduccion.md','02-personajes.md','03-escenas.md','04-herramientas.md')]
    S1={t:b for t,b in secciones(c1,2)};S4={t:b for t,b in secciones(c4,2)};S2={t:b for t,b in secciones(c2,2)}
    H3_4={t:b for t,b in secciones(S4['Handouts'].join(['## x\n','']),3)} if False else None
    carpetas={}
    def car(n,tipo,o):
        f=dict(_id=uid('folder:'+tipo+n),name=n,type=tipo,folder=None,sorting='a',sort=o,color=None,flags={},description='');carpetas[(tipo,n)]=f;return f
    for i,n in enumerate(['Dirección','Localizaciones','Fichas confidenciales','Handouts']):car(n,'JournalEntry',i)
    car('Escenas','Scene',0)
    ficha=lambda t,e:uid('journal:'+t+e)
    diarios=[]
    def pag(nom,cont,i):
        return dict(_id=uid('page:'+nom+str(i)),name=nom,type='text',title=dict(show=True,level=1),text=dict(format=1,content=cont),sort=(i+1)*100000,ownership=dict(default=-1),flags={})
    def ppag(nom,src,cap,i):
        return dict(_id=uid('page:'+nom+str(i)),name=nom,type='image',title=dict(show=True,level=1),src=src,image=dict(caption=cap),sort=(i+1)*100000,ownership=dict(default=-1),flags={})
    def dia(nom,paginas,carp,orden=0):
        d=dict(_id=uid('journal:'+nom),name=nom,pages=paginas,folder=carpetas[('JournalEntry',carp)]['_id'],sort=orden,ownership=dict(default=0),flags={ID:dict(tipo=carp)})
        diarios.append(d);return d
    def md_pags(pares):
        return [pag(t,html(b),i) for i,(t,b) in enumerate(pares)]
    # ---- Dirección
    dia('Portada y cómo dirigir',md_pags([(t,S1[t]) for t in('La aventura en una página','Zardoz y la Manada Midespinas','Nixyus, Maerla y la pulsera','La noche perdida, en resumen','La verdad en siete frases','Cómo usar esta aventura','Panel de dirección')]),'Dirección',0)
    dia('Los cuatro frentes',md_pags([('Los cuatro frentes y la regla motor',S1['Los cuatro frentes y la regla motor'])]),'Dirección',1)
    dia('Cronología canónica',md_pags([('Cronología canónica',S1['Cronología canónica'])]),'Dirección',2)
    dia('Las tres revelaciones',md_pags([('Las tres revelaciones',S1['Las tres revelaciones'])]),'Dirección',3)
    reglas=['Resaca narrativa','Confesión con precio','Fracaso con avance','La pulsera: escala y reglas físicas','Princesa y la tubería','El ritual: preguntas frecuentes','La laguna de anoche','Farmacología de mesa: por qué ellos no recuerdan y los testigos sí','Condiciones','Violencia, daño y muerte','Geografía de la suite: cómo se llega a los sitios','Humanos como desastres naturales']
    dia('Reglas especiales',md_pags([(t,S1[t]) for t in reglas]),'Dirección',4)
    dia('Guía de PNJ',md_pags([('PNJ principales',S2['PNJ principales']),('Reparto de la mesa',S2['Reparto de la mesa con tres, cuatro o seis jugadores'])]),'Dirección',5)
    dia('Cómo dirigir la comedia',md_pags([(t,S4[t]) for t in('Cómo dirigir la comedia','Duración, ritmo y formatos')]),'Dirección',6)
    dia('Hoja de referencia rápida',md_pags([('Hoja de referencia rápida',S4['Hoja de referencia rápida'])]),'Dirección',7)
    dia('Ratover Express',md_pags([('Ratover Express',S4['APÉNDICE · Ratover Express'] if 'APÉNDICE · Ratover Express' in S4 else '')]),'Dirección',8) if False else None
    ex=[(t,b) for t,b in secciones(c4,1) if t.startswith('APÉNDICE')]
    dia('Ratover Express',[pag('Ratover Express',html(ex[0][1]),0)],'Dirección',8)
    dia('Epílogos',md_pags([('Culpa y epílogos',S4['Culpa y epílogos']),('Pago, botín y facturas',S4['Pago, botín y facturas'])]),'Dirección',9)
    # ---- Localizaciones (nueve)
    H1=secciones(c3,1);loc={}
    claves=[('01','ESCENA 1'),('02','DADO DE NÁCAR'),('03','BULEVAR'),('04','CAPILLA'),('05','NOTARÍA'),('06','ALMACÉN'),('07','ESCENA OBLIGATORIA'),('08','ESCENA 5'),('09','ESCENA 6')]
    for n,k in claves:
        t,b=[x for x in H1 if x[0].startswith(k)][0]
        nombre=re.sub(r'^(ESCENA( OBLIGATORIA| \d)? · )','',t).strip().title().replace(' De ',' de ').replace(' Del ',' del ').replace(' Y ',' y ').replace(' La ',' la ')
        loc[n]=dia(f'{n} · {nombre}',[pag('Texto',html(b),0)],'Localizaciones',int(n))
    # ---- Fichas confidenciales (cinco)
    for t in('Zardoz Midespinas','El Guapo','El Dentista','El Colgado','El Novio'):
        b=S2[t];i=b.index('> **CONFIDENCIAL');conf=b[i:].split('\n---')[0]
        dia(f'Ficha confidencial · {t}',[pag('Confidencial',html(conf),0)],'Fichas confidenciales',0)
    # ---- Handouts
    textos={t:b for t,b in secciones(S4['Handouts'].join(['## Handouts\n','']),3)}
    textos={t:b for t,b in secciones('## Handouts\n'+S4['Handouts'],3)}
    mapa=[('recibo-del-intercambio','Recibo del intercambio',None),('nota-de-nixyus','Nota de Nixyus','Nota de Nixyus'),('inscripcion-del-aro','Inscripción del aro','Inscripción del aro'),
     ('etiqueta-de-calma-comadrejas','Etiqueta de Calma-Comadrejas','Etiqueta de Calma-Comadrejas'),('pagare-de-parmesano','Pagaré de parmesano','Pagaré de parmesano'),('acta-de-boda','Acta de boda','Acta de boda'),
     ('parte-de-incidencias','Parte de incidencias de la Guardia','Parte de incidencias de la Guardia'),('plano-de-pazos','Plano de Pazos','Plano de Pazos'),('manual-de-la-mandibula-negra','Manual de La Mandíbula Negra','Manual de La Mandíbula Negra'),
     ('dos-cintas','Las dos cintas','Las dos cintas'),('pared-de-la-villa','Pared de la Villa','Pared de la Villa'),('lista-del-rastro-dorado','La lista del Rastro Dorado','La lista del Rastro Dorado')]
    for k,(slug,nom,sec) in enumerate(mapa):
        a=M['handout.'+slug];fuente=M[a['reuse_of']] if a.get('reuse_of') else a
        txt=html(textos[sec]) if sec else f"<p>{I['recibo-del-intercambio']['d']}</p>"
        dia(nom,[ppag('Imagen',img(fuente['path'],fuente['kind']),nom,0),pag('Texto',txt,1)],'Handouts',k)
    dia('Acuerdo de mesa: líneas y velos',[pag('Acuerdo',html(textos['Acuerdo de mesa: líneas y velos']),0)],'Handouts',20)
    # fotografías
    t=tabla(S4['Las fotografías de la noche'].split('### Cierre')[0].split('\n\n',3)[-1]) if False else None
    bloque=[l for l in S4['Las fotografías de la noche'].split('\n') if l.startswith('| ') and l[2:3].isdigit()]
    pf=[]
    for i,l in enumerate(bloque):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        a=M['photo.'+[k.split('.',1)[1] for k in M if k.startswith('photo.') and k.split('.',1)[1].startswith(c[0].zfill(2))][0]]
        pf.append(ppag(f'{c[0]}. {c[1]}',img(a['path'],'photo'),f'{c[1]} (paso {c[2]})',i*2));pf.append(pag(f'{c[0]}. {c[1]}, pie',f'<p>{c[3]}</p>',i*2+1))
    cierre=S4['Las fotografías de la noche'].split('### Cierre para leer en mesa')[1]
    pf.append(pag('Cierre para leer en mesa',html(cierre),len(pf)))
    dia('Fotografías de la noche',pf,'Handouts',30)
    # ---- Escenas
    esc=[]
    enlace={'00':'Portada y cómo dirigir'}
    for k,a in M.items():
        if a['kind']!='scene':continue
        n=a['id'].split('.',1)[1][:2]
        j=[d for d in diarios if d['name']==enlace[n]][0] if n in enlace else loc[n]
        esc.append(dict(_id=uid('scene:'+n),name=a['title'],navigation=True,navOrder=int(n),navName=a['title'],background=dict(src=img(a['path'],'scene')),
          width=2560,height=1440,padding=0,initial=dict(x=None,y=None,scale=None),backgroundColor='#000000',grid=dict(type=0,size=100,distance=1,units='',alpha=0.2),
          thumb=f"modules/{ID}/{a['thumb']}" if (R/a['thumb']).exists() else None,tiles=[firma(uid,ID,n)],tokenVision=False,fog=dict(exploration=False),journal=j['_id'],journalEntryPage=None,folder=carpetas[('Scene','Escenas')]['_id'],sort=int(n),ownership=dict(default=0),flags={ID:dict(escena=n)}))
    # ---- Tablas
    tablas=[];nombres={'Quién llega':'Follones de Resaca','Peligro humano o del edificio':'Peligros del edificio','Señal del ritual':'Señales del ritual','Complicación inmediata':'Complicación inmediata',
      'Frase de Pazos':'Frases de Pazos','En la bolsa del Colgado':'Bolsa del Colgado','Coste':'Fracaso con avance','Reacción':'Reacción de los fieles de Chispa'}
    tc=car('Tablas','RollTable',0)
    for txt in(c3,c4):
        for blq in re.findall(r'(?:^\|.*\n)+',txt,re.M):
            t=tabla(blq)
            if not t or t[0][0] not in('d6','d8','d10') or t[0][1] not in nombres:continue
            cab,filas=t;nom=nombres[cab[1]]
            if any(x['name']==nom for x in tablas):continue
            caras=int(cab[0][1:]);res=[]
            for f in filas:
                n=int(f[0]);cuerpo=f[1] if len(f)==2 else f"<strong>{f[1].replace('**','')}</strong>. "+' '.join(f[2:])
                res.append(dict(_id=uid(f'res:{nom}:{n}'),type='text',text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',cuerpo),img='icons/svg/d20-black.svg',weight=1,range=[n,n],drawn=False,flags={}))
            tablas.append(dict(_id=uid('table:'+nom),name=nom,img='icons/svg/d20-grey.svg',description='',results=res,formula=f'1d{caras}',replacement=True,displayRoll=True,folder=tc['_id'],sort=len(tablas),ownership=dict(default=0),flags={}))
    return diarios,esc,tablas,list(carpetas.values())
