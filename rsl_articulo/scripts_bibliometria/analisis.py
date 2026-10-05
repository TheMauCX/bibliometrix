# -*- coding: utf-8 -*-
import json, re, collections, itertools, random, math
import networkx as nx
import numpy as np
D=json.load(open('recs.json')); R={x['id']:x for x in D['recs']}; TEM=[R[i] for i in D['tem']]
INC=[x for x in D['recs'] if x['inc']]            # 34 de bases (A17 no esta en las bases)
SYN={
 'unlearnable examples':['unlearnable examples','unlearnable example','unlearnable data','unlearnable'],
 'face recognition':['face recognition','facial recognition','face recognition systems','facial recognition systems'],
 'facial privacy protection':['facial privacy protection','facial privacy'],
 'privacy protection':['privacy protection','privacy-preserving techniques','privacy concerns','privacy risks','data privacy','privacy','sensitive data','privacy preservation'],
 'diffusion models':['diffusion model','diffusion models','diffusion'],
 'adversarial examples':['adversarial example','adversarial examples','adversarial attack','adversarial attacks','adversarial machine learning'],
 'poisoning attacks':['poisoning attacks','data poisoning','availability poisoning','poisoning attack','availability attack'],
 'contrastive learning':['contrastive learning','self-supervised learning'],
 'protective perturbation':['protective perturbation','perturbation techniques','perturbation methods','noise','adversarial perturbation','adversarial perturbations'],
 'purification':['purification','image purification'],
 'data augmentation':['data augmentation','augmentation'],
 'copyright protection':['copyright protection','copyrights','copyright'],
 'image classification':['image classification','classification'],
 'generative adversarial networks':['generative adversarial networks','gan'],
 'differential privacy':['differential privacy'],
 'surrogate model':['surrogate modeling','surrogate model'],
 'black-box setting':['black boxes','black-box','black box'],
 'data protection':['data protection','protection methods','data usage'],
}
REV={v:k for k,vs in SYN.items() for v in vs}
STOP={'article','human','current',"'current",'learn+','performance','learning systems','learning models','recognition models','artificial intelligence','computer vision','deep learning','machine learning','machine learning models','neural-networks','deep neural networks','deep neural network','neural networks','training','training data','model training','training sample','real-world','high frequency hf','visual qualities','image enhancement','semantics','network security','benchmarking','alignment','textures','facial images','recognition','images','image','distributed computer systems','iterative methods','data models'}
def kws(x):
    out=[]
    for f in (x['akw'],x['ikw']):
        if f: out+=[k.strip().lower() for k in re.split(r';|\|',f) if k.strip()]
    res=set()
    for k in out:
        k=REV.get(k,k)
        if k in STOP: continue
        res.add(k)
    return res
FACIAL=re.compile(r'\bfac(e|es|ial)\b|cloak|fawkes|makeup|identity|portrait',re.I)
def line(x):
    return 'Facial' if FACIAL.search((x['title'] or '')+' '+(x['akw'] or '')+' '+(x['ikw'] or '')) else 'Clasificación y otros'
for x in D['recs']: x['line']=line(x); x['kw']=sorted(kws(x))
TEM=[R[i] for i in D['tem']]
out={}
def netstats(S,minf,label):
    cnt=collections.Counter(k for x in S for k in x['kw'])
    terms={k for k,v in cnt.items() if v>=minf}
    G=nx.Graph(); 
    for k in terms: G.add_node(k,freq=cnt[k])
    for x in S:
        ks=[k for k in x['kw'] if k in terms]
        for a,b in itertools.combinations(sorted(ks),2):
            w=G[a][b]['weight']+1 if G.has_edge(a,b) else 1
            G.add_edge(a,b,weight=w)
    return cnt,G
# ---- AB1: produccion anual
yrs=range(2020,2027)
out['AB1']={'tem':{y:sum(1 for x in TEM if x['year']==y) for y in yrs},
            'tem_facial':{y:sum(1 for x in TEM if x['year']==y and x['line']=='Facial') for y in yrs},
            'inc34':{y:sum(1 for x in INC if x['year']==y) for y in yrs}}
# la fraccion de 2026 corresponde a un anio incompleto
# ---- AB2: co-palabras en el corpus tematico
S=[x for x in TEM if x['kw']]
out['cobertura']={'tem':len(TEM),'tem_con_kw':len(S),'inc34':len(INC),'inc34_con_kw':sum(1 for x in INC if x['kw'])}
cnt,G=netstats(S,2,'T')
# aristas con peso >=2 para la red
H=nx.Graph(); H.add_nodes_from(G.nodes(data=True)); H.add_edges_from((a,b,d) for a,b,d in G.edges(data=True) if d['weight']>=2)
H.remove_nodes_from([n for n in list(H) if H.degree(n)==0])
comm=nx.algorithms.community.louvain_communities(H,weight='weight',seed=42,resolution=1.0)
comm=sorted(comm,key=lambda c:-sum(H.nodes[n]['freq'] for n in c))
mod=nx.algorithms.community.modularity(H,comm,weight='weight')
out['AB2']={'nodos':H.number_of_nodes(),'aristas':H.number_of_edges(),'modularidad':round(mod,3),'terminos_freq':cnt.most_common(15),
            'comunidades':[sorted(c,key=lambda n:-H.nodes[n]['freq']) for c in comm]}
# mapa tematico: centralidad (Callon) y densidad por comunidad, con indice de equivalencia
co={}
for a,b,d in G.edges(data=True): co[(a,b)]=co[(b,a)]=d['weight']
def eq(a,b): 
    c=co.get((a,b),0); return c*c/(cnt[a]*cnt[b])
tm=[]
for i,c in enumerate(comm):
    c=list(c); n=len(c)
    if n<3: continue
    internal=sum(eq(a,b) for a,b in itertools.combinations(c,2))
    dens=100*internal/n
    ext=sum(eq(a,b) for a in c for b in H.nodes if b not in c)
    cent=10*ext
    tm.append(dict(id=len(tm),terms=sorted(c,key=lambda t:-cnt[t])[:5],n=n,freq=sum(cnt[t] for t in c),cent=cent,dens=dens))
out['mapa']=tm
# ---- AB3: separacion clasificacion/facial
terms=set(H.nodes)
fshare={t:sum(1 for x in S if t in x['kw'] and x['line']=='Facial')/cnt[t] for t in terms}
def assort(attr):
    # correlacion ponderada entre la proporcion facial de los extremos de cada arista (ambas direcciones)
    xs=[];ys=[];ws=[]
    for a,b,d in H.edges(data=True):
        xs+= [attr[a],attr[b]]; ys+=[attr[b],attr[a]]; ws+=[d['weight']]*2
    xs=np.array(xs);ys=np.array(ys);ws=np.array(ws,float)
    mx=np.average(xs,weights=ws); my=np.average(ys,weights=ws)
    cov=np.average((xs-mx)*(ys-my),weights=ws)
    return cov/math.sqrt(np.average((xs-mx)**2,weights=ws)*np.average((ys-my)**2,weights=ws))
obs=assort(fshare)
random.seed(7); nodes=list(fshare); vals=[fshare[n] for n in nodes]; perm=[]
for _ in range(5000):
    random.shuffle(vals); perm.append(assort(dict(zip(nodes,vals))))
p=(1+sum(1 for v in perm if v>=obs))/5001
out['AB3']={'n_facial':sum(1 for x in S if x['line']=='Facial'),'n_clas':sum(1 for x in S if x['line']!='Facial'),
  'asort_obs':round(obs,3),'asort_perm_media':round(float(np.mean(perm)),3),'p_mayor':round(p,4),
  'term_facial_share':sorted(((t,round(fshare[t],2),cnt[t]) for t in terms),key=lambda z:-z[1]),
  'comunidad_facial_media':[round(float(np.mean([fshare[t] for t in c])),2) for c in comm]}
# terminos puente: aparecen en >=2 registros de cada linea
br=[]
for t in terms:
    f=sum(1 for x in S if t in x['kw'] and x['line']=='Facial'); c=sum(1 for x in S if t in x['kw'] and x['line']!='Facial')
    if f>=2 and c>=2: br.append((t,f,c))
bc=nx.betweenness_centrality(H,weight=None)
out['AB3']['puente']=sorted(br,key=lambda z:-(z[1]+z[2]))
out['AB3']['betweenness_top']=sorted(((t,round(v,3)) for t,v in bc.items()),key=lambda z:-z[1])[:8]
# ---- comprobacion con los 35: AB1 y AB2 sobre el subconjunto incluido
S35=[x for x in INC if x['kw']]
cnt35,G35=netstats(S35,2,'35')
out['AB2_35']={'n':len(S35),'top':cnt35.most_common(12)}
top_t={t for t,_ in cnt.most_common(12)}; top_35={t for t,_ in cnt35.most_common(12)}
out['AB2_35']['solape_top12']=sorted(top_t&top_35)
# tendencia por termino (top 10 terminos del corpus tematico)
top10=[t for t,_ in cnt.most_common(10)]
out['tendencia']={t:{y:sum(1 for x in S if x['year']==y and t in x['kw']) for y in range(2021,2027)} for t in top10}
json.dump(out,open('stats.json','w'),ensure_ascii=False,indent=1,default=str)
import pickle; pickle.dump(dict(H=H,comm=comm,cnt=cnt,fshare=fshare,tm=tm,G35=G35,cnt35=cnt35,S=S,INC=INC,TEM=TEM,out=out),open('state.pkl','wb'))
print(json.dumps(out,ensure_ascii=False,indent=1,default=str)[:6000])
