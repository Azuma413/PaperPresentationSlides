import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np, sys
font_manager.fontManager.addfont('/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf')
matplotlib.rcParams['font.family'] = 'IPAPGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ja'
def t(ja, en): return en if LANG == 'en' else ja

GRAY, ORANGE, PURPLE, GREEN = '#9E9E9E', '#D79B00', '#9673A6', '#2E7D32'

def style(ax):
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=9)

def label_bars(ax, bars, fmt='{:.0f}', size=8):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 1.5, fmt.format(h), ha='center', va='bottom', fontsize=size)

# ---------------------------------------------------------------- CaM: Table 1 + Table 2
def cam_results():
    fig, axes = plt.subplots(1, 3, figsize=(12.3, 3.4), dpi=200, gridspec_kw=dict(width_ratios=[1.15, 1.15, 0.8]))
    # (a) CLIPort stack in order vs drop probability
    ax = axes[0]
    p = [t('なし', 'none'), 'p = 0.15', 'p = 0.3']
    data = {t('監視なし (CLIPort)', 'no monitor (CLIPort)'): [100, 56.67, 21.67],
            'Inner Monologue': [100, 81.67, 75.0],
            'DoReMi': [100, 83.33, 76.67],
            'Code-as-Monitor': [100, 95.0, 88.33]}
    cols = [GRAY, '#BFBFBF', PURPLE, GREEN]
    x = np.arange(3); w = 0.2
    for i, (k, v) in enumerate(data.items()):
        b = ax.bar(x + (i - 1.5) * w, v, w, color=cols[i], label=k)
        if i in (0, 3): label_bars(ax, b)
    ax.set_xticks(x); ax.set_xticklabels(p)
    ax.set_ylim(0, 115); ax.set_ylabel(t('成功率 (%)', 'success rate (%)'), fontsize=9)
    ax.set_title(t('(a) 積み木積み：落下の外乱を強くする', '(a) Stack in order: stronger drop disturbance'), fontsize=10)
    ax.legend(fontsize=7.5, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2)
    style(ax)
    # (b) OmniGibson avg SR under disturbance
    ax = axes[1]
    tasks = [t('ペン挿入\n(点)', 'Slot pen\n(point)'), t('本を立てる\n(線)', 'Stow book\n(line)'), t('お茶注ぎ\n(面)', 'Pour tea\n(surface)')]
    rekep = [np.mean([20, 10, 10]), np.mean([30, 30, 20]), np.mean([20, 20, 10])]
    drm = [np.mean([10, 20, 20]), np.mean([40, 20, 40]), 0.0]
    ours = [np.mean([50, 40, 40]), np.mean([60, 70, 60]), np.mean([40, 40, 30])]
    x = np.arange(3); w = 0.26
    b1 = ax.bar(x - w, rekep, w, color=GRAY, label=t('監視なし (ReKep)', 'no monitor (ReKep)'))
    b2 = ax.bar(x, drm, w, color=PURPLE, label='DoReMi')
    b3 = ax.bar(x + w, ours, w, color=GREEN, label='Code-as-Monitor')
    label_bars(ax, b1); label_bars(ax, b2); label_bars(ax, b3)
    ax.set_xticks(x); ax.set_xticklabels(tasks, fontsize=9)
    ax.set_ylim(0, 80); ax.set_ylabel(t('外乱下の成功率 (%)', 'success under disturbance (%)'), fontsize=9)
    ax.set_title(t('(b) OmniGibson：3種類の外乱（3条件の平均）', '(b) OmniGibson: three disturbance types (mean of 3)'), fontsize=10)
    ax.legend(fontsize=7.5, frameon=False, loc='upper left')
    style(ax)
    # (c) efficiency: DoReMi vs CaM (mean over slot pen, stow book)
    ax = axes[2]
    time_d, time_o = np.mean([177.84, 127.17]), np.mean([101.85, 93.08])
    tok_d, tok_o = np.mean([54.54, 38.67]), np.mean([25.82, 18.67])
    x = np.arange(2); w = 0.32
    vals_d = [100, 100]; vals_o = [100 * time_o / time_d, 100 * tok_o / tok_d]
    b1 = ax.bar(x - w / 2, vals_d, w, color=PURPLE, label='DoReMi')
    b2 = ax.bar(x + w / 2, vals_o, w, color=GREEN, label='Code-as-Monitor')
    for b, v in zip(b2, vals_o):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f'−{100 - v:.0f}%', ha='center', fontsize=9, color=GREEN, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels([t('実行時間', 'execution time'), t('VLM の token 数', 'VLM tokens')], fontsize=9)
    ax.set_ylim(0, 120); ax.set_ylabel(t('DoReMi = 100 としたとき', 'relative to DoReMi = 100'), fontsize=9)
    ax.set_title(t('(c) 効率（OmniGibson）', '(c) Efficiency (OmniGibson)'), fontsize=10)
    ax.legend(fontsize=7.5, frameon=False, loc='upper right')
    style(ax)
    fig.tight_layout(w_pad=1.5)
    fig.savefig(f'diag/cam_results_{LANG}.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

# ---------------------------------------------------------------- VLS: Table I (LIBERO-PRO)
def vls_results():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3), dpi=200, sharey=True)
    suites = ['Goal', 'Spatial', '10', 'Object']
    base = {'task': [12.0, 48.5, 21.5, 10.5], 'pos': [29.0, 41.0, 11.0, 16.0]}
    vls = {'task': [33.5, 54.0, 25.5, 41.0], 'pos': [38.0, 42.0, 15.5, 45.0]}
    titles = {'task': t('タスクの指示を変える', 'task perturbation'), 'pos': t('物体の配置を変える', 'position perturbation')}
    for ax, k in zip(axes, ['task', 'pos']):
        x = np.arange(4); w = 0.36
        b1 = ax.bar(x - w / 2, base[k], w, color=GRAY, label=t('凍結 π0.5', 'frozen π0.5'))
        b2 = ax.bar(x + w / 2, vls[k], w, color=ORANGE, label='+ VLS')
        label_bars(ax, b1); label_bars(ax, b2)
        ax.set_xticks(x); ax.set_xticklabels(suites, fontsize=9); ax.set_xlabel(t('LIBERO のタスク群', 'LIBERO suite'), fontsize=9)
        ax.set_ylim(0, 70)
        ax.set_title(titles[k] + f"  ({t('平均', 'avg')} {np.mean(base[k]):.1f} → {np.mean(vls[k]):.1f}%)", fontsize=10)
        ax.axhline(np.mean(base[k]), color=GRAY, ls='--', lw=1)
        ax.axhline(np.mean(vls[k]), color=ORANGE, ls='--', lw=1)
        style(ax)
    axes[0].set_ylabel(t('成功率 (%)', 'success rate (%)'), fontsize=9)
    axes[0].legend(fontsize=8, frameon=False, loc='upper left')
    fig.suptitle(t('LIBERO-PRO：学習時と条件を変えたときの成功率', 'LIBERO-PRO: success when test conditions differ from training'), fontsize=11)
    fig.tight_layout()
    fig.savefig(f'diag/vls_results_{LANG}.png', bbox_inches='tight', facecolor='white'); plt.close(fig)

cam_results(); vls_results(); print('ok', LANG)
