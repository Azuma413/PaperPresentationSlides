import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np, sys
fp = font_manager.FontProperties(fname='/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf')
matplotlib.rcParams['font.family'] = fp.get_name()
font_manager.fontManager.addfont('/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf')
matplotlib.rcParams['font.family'] = 'IPAPGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

T = {
 'ja': dict(rows=['毎フレーム VLM に問う\n(DoReMi)','サブゴール完了時だけ問う\n(Inner Monologue)','Code-as-Monitor'],
            vlm='VLM 呼び出し', code='コードで検査（毎フレーム）', fail='失敗の予兆', det='検知', late='完了まで気づかない', xlabel='時間（1つのサブゴール）',
            s='遅い・誤判定が増える', s2='検知が遅れる', s3='VLM は1回、検知は即時'),
 'en': dict(rows=['Query the VLM every frame\n(DoReMi)','Query only at subgoal end\n(Inner Monologue)','Code-as-Monitor'],
            vlm='VLM call', code='code check (every frame)', fail='failure onset', det='detected', late='unnoticed until the end', xlabel='time (one subgoal)',
            s='slow, more misjudgments', s2='detected late', s3='one VLM call, immediate detection'),
}
def cam_timeline(lang):
    t=T[lang]
    fig,ax=plt.subplots(figsize=(11,3.6),dpi=200)
    ax.set_xlim(0,10.8); ax.set_ylim(-0.7,2.7); ax.axis('off')
    ys=[2,1,0]; tf=6.2
    for y,lab in zip(ys,t['rows']):
        ax.plot([0,10],[y,y],color='#BFBFBF',lw=2,zorder=1)
        ax.text(-0.15,y,lab,ha='right',va='center',fontsize=11)
    # row0: VLM every frame
    for x in np.arange(0.3,10,0.45): ax.plot(x,ys[0],marker='o',ms=9,color='#9673A6',zorder=3)
    ax.text(10.2,ys[0],t['s'],va='center',fontsize=10,color='#C00000')
    # row1: single call at end
    ax.plot(10,ys[1],marker='o',ms=11,color='#9673A6',zorder=3)
    ax.annotate('',xy=(10,ys[1]+0.08),xytext=(tf,ys[1]+0.08),arrowprops=dict(arrowstyle='<->',color='#C00000',lw=1.5))
    ax.text((10+tf)/2,ys[1]+0.2,t['late'],ha='center',fontsize=10,color='#C00000')
    ax.text(10.2,ys[1],t['s2'],va='center',fontsize=10,color='#C00000')
    # row2: CaM
    ax.plot(0.3,ys[2],marker='o',ms=11,color='#9673A6',zorder=3)
    for x in np.arange(0.9,10,0.3): ax.plot(x,ys[2],marker='s',ms=4,color='#82B366',zorder=3)
    ax.plot(tf+0.1,ys[2],marker='*',ms=16,color='#D79B00',zorder=4)
    ax.text(10.2,ys[2],t['s3'],va='center',fontsize=10,color='#2E7D32')
    # failure onset line
    ax.axvline(tf,color='#C00000',ls='--',lw=1.2,ymin=0.12,ymax=0.9)
    ax.text(tf,2.5,t['fail'],ha='center',fontsize=10,color='#C00000')
    ax.annotate('',xy=(10,-0.45),xytext=(0,-0.45),arrowprops=dict(arrowstyle='->',color='black',lw=1))
    ax.text(5,-0.65,t['xlabel'],ha='center',fontsize=10)
    # legend
    ax.plot(0.3,-0.2,marker='o',ms=9,color='#9673A6'); ax.text(0.5,-0.2,t['vlm'],va='center',fontsize=9)
    ax.plot(2.6,-0.2,marker='s',ms=5,color='#82B366'); ax.text(2.8,-0.2,t['code'],va='center',fontsize=9)
    ax.plot(5.6,-0.2,marker='*',ms=12,color='#D79B00'); ax.text(5.8,-0.2,t['det'],va='center',fontsize=9)
    fig.savefig(f'diag/cam_compare_{lang}.png',bbox_inches='tight',transparent=False,facecolor='white'); plt.close(fig)

V = {
 'ja': dict(titles=['(a) 誘導なし','(b) 報酬の勾配を足す','(c) 勾配 ＋ 報酬で選別'], base='学習済みポリシーの分布', reward='報酬（壁から遠いほど高い）', wall='壁', cand='行動候補',
            cap=['候補は学習時のモード（壁側）に集中','候補が報酬の高い側へ少しずつ動く','高報酬の候補を複製し、低い候補を間引く'], xlabel='行動（例：手先の横位置）'),
 'en': dict(titles=['(a) no steering','(b) add reward gradient','(c) gradient + reward resampling'], base='pretrained policy distribution', reward='reward (higher away from the wall)', wall='wall', cand='action candidates',
            cap=['candidates stay at the training mode (near the wall)','candidates move toward higher reward','high-reward candidates duplicated, low ones pruned'], xlabel='action (e.g., lateral hand position)'),
}
def vls_compare(lang):
    t=V[lang]; rng=np.random.default_rng(1)
    x=np.linspace(0,10,400)
    base=np.exp(-(x-3.2)**2/0.6)
    reward=1/(1+np.exp(-(x-5.2)*1.6))
    fig,axes=plt.subplots(1,3,figsize=(12,3.3),dpi=200,sharey=True)
    samples0=rng.normal(3.2,0.5,14)
    for i,ax in enumerate(axes):
        ax.fill_between(x,0,base,color='#DAE8FC',alpha=0.9,label=t['base'])
        ax.plot(x,reward,color='#D79B00',lw=2,label=t['reward'])
        ax.axvspan(2.7,3.7,color='#BFBFBF',alpha=0.7); ax.text(3.2,1.08,t['wall'],ha='center',fontsize=10,color='#555555')
        if i==0: s=samples0
        elif i==1: s=samples0+2.3+rng.normal(0,0.25,14)
        else:
            s1=samples0+2.3+rng.normal(0,0.25,14); w=1/(1+np.exp(-(s1-5.2)*1.6)); w=w/w.sum(); s=rng.choice(s1,size=14,p=w)+rng.normal(0,0.06,14)
        ax.scatter(s,np.full_like(s,0.06)+rng.uniform(-0.03,0.03,len(s)),s=36,color='#C00000',zorder=5,label=t['cand'])
        if i>0:
            ax.annotate('',xy=(5.8,0.3),xytext=(3.4,0.3),arrowprops=dict(arrowstyle='->',color='#C00000',lw=2))
        ax.set_title(t['titles'][i],fontsize=12)
        ax.text(5,-0.2,t['cap'][i],ha='center',fontsize=10)
        ax.set_xlim(0,10); ax.set_ylim(0,1.2); ax.set_yticks([]); ax.set_xticks([])
        for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
    axes[0].legend(loc='upper left',fontsize=8,frameon=False)
    fig.text(0.5,-0.02,t['xlabel'],ha='center',fontsize=9,color='#555555')
    fig.tight_layout()
    fig.savefig(f'diag/vls_compare_{lang}.png',bbox_inches='tight',facecolor='white'); plt.close(fig)

for lang in ['ja','en']:
    cam_timeline(lang); vls_compare(lang)
print('ok')
