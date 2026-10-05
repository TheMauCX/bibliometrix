# -*- coding: utf-8 -*-
import pickle, json, math
import numpy as np, networkx as nx
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
S=pickle.load(open('state.pkl','rb')); H=S['H']; comm=S['comm']; cnt=S['cnt']; fshare=S['fshare']; tm=S['tm']; out=S['out']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
COL=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00']
def save(fig,name):
    fig.savefig(f'figuras/{name}.pdf',bbox_inches='tight'); fig.savefig(f'figuras/{name}.png',dpi=300,bbox_inches='tight'); plt.close(fig)
# ---------- AB1: produccion anual y tendencia por termino
ab1=out['AB1']; yrs=[2020,2021,2022,2023,2024,2025,2026]
tem=[ab1['tem'][y] for y in yrs]; fac=[ab1['tem_facial'][y] for y in yrs]; inc=[ab1['inc34'][y] for y in yrs]
cla=[t-f for t,f in zip(tem,fac)]
fig,ax=plt.subplots(1,2,figsize=(7.4,3.0),gridspec_kw={'width_ratios':[1,1.15]})
a=ax[0]; x=np.arange(len(yrs)); w=0.38
a.bar(x-w/2,cla,w,color='#0072B2',label='Clasificación y otros'); a.bar(x-w/2,fac,w,bottom=cla,color='#D55E00',label='Facial')
a.bar(x+w/2,inc,w,color='#7f7f7f',label='Incluidos (bases)')
for i,t in enumerate(tem): a.text(i-w/2,t+0.8,str(t),ha='center',fontsize=7.5)
a.set_xticks(x); a.set_xticklabels([str(y) if y<2026 else '2026*' for y in yrs],rotation=45,ha='right',fontsize=8); a.set_ylabel('Registros'); a.set_title('(a) Producción anual',loc='left',fontsize=9)
a.legend(frameon=False,fontsize=7.5,loc='upper left')
tt=out['tendencia']; terms=list(tt)[:8]; yy=list(range(2021,2027))
b=ax[1]
for i,t in enumerate(terms):
    for j,y in enumerate(yy):
        v=tt[t][y]
        if v: b.scatter(j,len(terms)-1-i,s=22*v+8,color='#0072B2',alpha=0.8,edgecolor='white',linewidth=0.5)
b.set_yticks(range(len(terms))); b.set_yticklabels(terms[::-1],fontsize=7.5); b.set_xticks(range(len(yy))); b.set_xticklabels([str(y) if y<2026 else '2026*' for y in yy],rotation=45,ha='right',fontsize=8)
b.set_title('(b) Tendencia de los términos más frecuentes',loc='left',fontsize=9); b.set_xlim(-0.5,len(yy)-0.5); b.set_ylim(-0.7,len(terms)-0.3)
fig.tight_layout(); save(fig,'AB1_produccion_y_tendencia')
# ---------- layout comun
import random
big_comm=[c for c in comm if len(c)>=3]
ncomm=len(big_comm); centers={}
for i,c in enumerate(big_comm):
    ang=2*math.pi*i/ncomm; centers[i]=np.array([math.cos(ang),math.sin(ang)])*2.6
pos={}
for i,c in enumerate(comm):
    sub=H.subgraph(c)
    if len(c)<3:
        for j,n in enumerate(c): pos[n]=np.array([3.4+0.4*j,-3.2])
        continue
    p=nx.spring_layout(sub,weight='weight',seed=3+i,k=0.9/math.sqrt(len(c)),iterations=200)
    for n,v in p.items(): pos[n]=centers[i]+v*(0.9+0.045*len(c))
def draw(ax,colors,title):
    sizes=[26+11*cnt[n] for n in H.nodes]
    ew=[0.15+0.2*H[a][b]['weight'] for a,b in H.edges]
    nx.draw_networkx_edges(H,pos,ax=ax,width=ew,edge_color='#9a9a9a',alpha=0.28)
    nx.draw_networkx_nodes(H,pos,ax=ax,node_size=sizes,node_color=colors,edgecolors='white',linewidths=0.6)
    lab=[n for n in H.nodes if cnt[n]>=5]
    P={n:np.array(pos[n],float) for n in lab}; T={n:P[n]+np.array([0,0.16]) for n in lab}
    for _ in range(300):
        for a in lab:
            for b in lab:
                if a>=b: continue
                d=T[a]-T[b]; dist=np.linalg.norm(d)+1e-6
                if abs(d[0])<0.95 and abs(d[1])<0.22:
                    push=d/dist*0.02; T[a]+=push; T[b]-=push
    for n in lab:
        ax.annotate(n,xy=P[n],xytext=T[n],textcoords='data',fontsize=6.5,ha='center',va='center',
                    bbox=dict(boxstyle='round,pad=0.12',fc='white',ec='none',alpha=0.85),
                    arrowprops=dict(arrowstyle='-',color='#777',lw=0.4,shrinkA=0,shrinkB=2))
    ax.set_title(title,loc='left',fontsize=9); ax.axis('off')
# ---------- AB2: red de co-palabras por comunidad
fig,ax=plt.subplots(figsize=(7.4,6.0))
cmap={}
for i,c in enumerate(comm):
    for n in c: cmap[n]='#999999' if len(c)<3 else COL[i%len(COL)]
draw(ax,[cmap[n] for n in H.nodes],'Red de co-palabras del corpus temático (términos en $\\geq$ 2 registros; aristas con $\\geq$ 2 co-ocurrencias)')
from matplotlib.lines import Line2D
names=[f'C{i+1}: '+', '.join(m['terms'][:3]) for i,m in enumerate(tm)]
ax.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=COL[i],markersize=8,label=names[i]) for i in range(len(tm))],loc='lower left',frameon=False,fontsize=7)
save(fig,'AB2_red_copalabras')
# ---------- AB2: mapa tematico
fig,ax=plt.subplots(figsize=(4.4,3.6))
c_med=np.median([m['cent'] for m in tm]); d_med=np.median([m['dens'] for m in tm])
for i,m in enumerate(tm):
    ax.scatter(m['cent'],m['dens'],s=40+4*m['freq'],color=COL[i%len(COL)],alpha=0.85,edgecolor='white')
    ax.annotate(f"C{i+1}",(m['cent'],m['dens']),ha='center',va='center',fontsize=8,color='white',fontweight='bold')
ax.axvline(c_med,color='#999',lw=0.8,ls='--'); ax.axhline(d_med,color='#999',lw=0.8,ls='--')
ax.text(0.98,0.98,'Temas motores',transform=ax.transAxes,ha='right',va='top',fontsize=7,color='#555')
ax.text(0.02,0.98,'Temas de nicho',transform=ax.transAxes,ha='left',va='top',fontsize=7,color='#555')
ax.text(0.98,0.02,'Temas básicos',transform=ax.transAxes,ha='right',va='bottom',fontsize=7,color='#555')
ax.text(0.02,0.02,'Emergentes o en declive',transform=ax.transAxes,ha='left',va='bottom',fontsize=7,color='#555')
ax.margins(0.18); ax.set_xlabel('Centralidad (grado de relevancia)'); ax.set_ylabel('Densidad (grado de desarrollo)')
save(fig,'AB2_mapa_tematico')
# ---------- AB3: red coloreada por proporcion facial
cm=LinearSegmentedColormap.from_list('fc',['#0072B2','#eeeeee','#D55E00'])
fig,ax=plt.subplots(figsize=(7.4,6.0))
draw(ax,[cm(fshare[n]) for n in H.nodes],'Misma red coloreada por la proporción de registros de la línea facial que contienen cada término')
sm=plt.cm.ScalarMappable(cmap=cm,norm=plt.Normalize(0,1)); cb=fig.colorbar(sm,ax=ax,fraction=0.03,pad=0.01); cb.set_label('Proporción de registros faciales',fontsize=8)
save(fig,'AB3_separacion_lineas')
print('ok')
