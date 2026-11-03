import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['mathtext.fontset']='cm'
eqs = {
 'vls_guid': r"$\hat{v} = v(a^k,\,(o,l)_{OOD},\,k) + \lambda\, g,\qquad g := \nabla_{a^k}\log p\left((o,l)_{OOD}\,|\,a^k\right)$",
 'vls_surr': r"$g_s \approx \nabla_{a^k}\, R_s\left(a^k;\,\mathcal{P}\right),\qquad R_s = f_{\mathrm{VLM}}(a^k,\,\mathcal{P},\,s)$",
 'vls_rbf':  r"$g^{k}_{RBF}[i] = \nabla_{a^k[i]} \sum_{j\neq i} \frac{1}{\|a^k[i]-a^k[j]\|_2+\epsilon}$",
 'vls_fk':   r"$G_i^k = \exp\left(R_s(a^k[i])\right),\qquad w_i^k = G_i^k \,/\, \sum_{j=1}^{B} G_j^k$",
 'vls_lam':  r"$\lambda_t = \lambda_{\max}\cdot \mathrm{sigmoid}\left(1-\frac{R_s^{t}}{R_s^{base}}\right)$",
 'vls_q1':   r"$R_s^t > R_{high}:\ \mathrm{Advance}\quad\ \ R_{low}\leq R_s^t\leq R_{high}:\ \mathrm{Maintain}\quad\ \ R_s^t < R_{low}:\ \mathrm{Reinforce}$",
 'cam_gen':  r"$l_{next},\;\mathcal{C}_d,\;\mathcal{C}_u = F_{\mathrm{VLM}}\left(\mathcal{O},\,L_{global},\,l_{pre},\,f_{pre}\right)$",
 'cam_seg':  r"$l_e,\,h_{\langle SEG\rangle} = F_{\mathrm{VLM}}(c,o),\qquad M = F_{dec}\left(F_{MLP}(h_{\langle SEG\rangle}),\,F_{enc}(o)\right)$",
}
for k,s in eqs.items():
    fig=plt.figure(figsize=(0.1,0.1))
    t=fig.text(0,0,s,fontsize=22)
    fig.canvas.draw()
    bb=t.get_window_extent()
    w,h=bb.width/fig.dpi, bb.height/fig.dpi
    plt.close(fig)
    fig=plt.figure(figsize=(w+0.3,h+0.3))
    fig.text(0.5,0.5,s,fontsize=22,ha='center',va='center')
    fig.savefig(f'eq/{k}.png',dpi=300,transparent=True)
    plt.close(fig)
    print(k, round(w,2), round(h,2))
