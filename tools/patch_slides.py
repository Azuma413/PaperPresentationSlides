# -*- coding: utf-8 -*-
"""Patch slides 10, 21, 27, 31, 35 (1-based) of the user's edited deck in place.
usage: python3 patch5.py <in.pptx> <out.pptx> [ja|en]
"""
import sys, re
IN, OUT_PATH = sys.argv[1], sys.argv[2]
LANG_ARG = sys.argv[3] if len(sys.argv) > 3 else 'ja'
S = '/tmp/claude-0/-home-user-PaperPresentationSlides/b16a4cd5-a6b6-52ff-a060-bdd5dfede159/scratchpad'
sys.argv = ['build2.py', S + ('/en/draft_en.md' if LANG_ARG == 'en' else '/ja/draft_ja.md')]
exec(open(S + '/build_head.py').read())          # helpers: add_box, add_picture, add_text, caption, add_runs, ...

P = Presentation(IN)
E = 914400


def shape_text(sh):
    return sh.text_frame.text.strip() if sh.has_text_frame else ''


def remove(sh):
    el = sh._element; el.getparent().remove(el)


def body_box(slide):
    """The bullet textbox under the title (TextBox 902)."""
    for sh in slide.shapes:
        if sh.name == 'TextBox 902':
            return sh


def set_bullets(slide, n, items, size=20, spacing=150):
    old = body_box(slide)
    if old is not None:
        remove(old)
    add_bullets(slide, n, size=size, spacing=spacing, items=items)


def sl(n):
    return P.slides[n - 1]


# ------------------------------------------------------------------ slide 10: 実験設定 + figure
s = sl(10)
for sh in list(s.shapes):
    if shape_text(sh) in ('何か入れる．', '何か入れる.'):
        remove(sh)
add_picture(s, 'sf_tasks', 0.6, 3.5, h=3.3)
add_box(s, 4.2, 3.5, 4.2, 1.5, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('実機ポリシーの Sim 評価', 'Evaluating real policies in sim')], dict(size=15, bold=True)),
               ('opt', [t('7 タスク（DROID 6 + YAM 3 のうち）× 5 ポリシー。タスクごとに 25 ロールアウト、成功は 0 / 1', '7 tasks × 5 policies; 25 rollouts per task; success is 0 / 1')], dict(size=12, bold=False))])
add_box(s, 8.7, 3.5, 4.3, 1.5, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('指標', 'Metrics')], dict(size=15, bold=True)),
               ('opt', [t('Pearson r：Sim と実機の成功率の相関。MMRV：Sim での順位が実機と食い違う度合い（0 が理想）', 'Pearson r: correlation of success rates. MMRV: how far sim rankings violate real rankings (0 is ideal)')], dict(size=12, bold=False))])
add_box(s, 4.2, 5.2, 8.8, 1.6, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('Sim で学習して実機へ', 'Training in sim for the real robot')], dict(size=15, bold=True)),
               ('opt', [t('人のテレオペで 10〜15 デモ → MimicGen で軌道を増やし、材質とカメラ位置をランダム化 → DROID では π0 / π0.5 を微調整、YAM では Flow Matching ポリシーをゼロから学習 → Sim で最良のチェックポイントを選んで実機へ', '10-15 teleoperated demos → MimicGen augmentation with material and camera randomization → fine-tune π0 / π0.5 on DROID, train a flow-matching policy from scratch on YAM → pick the best checkpoint in sim and deploy')], dict(size=12, bold=False))])
caption(s, 0.6, 6.85, 4, 'Tasks: Fig. 4 in Ranawaka et al., 2026')

# ------------------------------------------------------------------ slide 21: CaM sim results
s = sl(21)
for sh in list(s.shapes):
    if sh.shape_type == 13 and sh.name != 'Picture 1':
        remove(sh)
    elif sh.name in ('TextBox 906',) or shape_text(sh).startswith('流石に'):
        remove(sh)
set_bullets(s, 21, [
    t('設定：点・線・面の3種類の外乱で失敗を誘発し、成功率・実行時間・token 数を比較', 'Setup: point / line / surface disturbances induce failures; compare success, time and tokens'),
    t('成功率：外乱を強くするほど差が開く。積み木積み（落下 p = 0.3）は 21.7% → 88.3%', 'Success: the gap widens with stronger disturbance; stacking (drop p = 0.3) 21.7% → 88.3%'),
    t('効率：VLM に毎回問う DoReMi より実行時間 −34.8%、token −52.2%（OmniGibson）', 'Efficiency: vs. DoReMi, which queries the VLM every step: time −34.8%, tokens −52.2%'),
], size=20)
add_picture(s, f'cam_results_{LANG}.png', 0.5, 3.45, w=12.3, folder=S + '/diag/')
caption(s, 0.5, 6.95, 12, t('Data from Table 1, 2 in Zhou et al., 2025.  ReKep：監視なしのポリシー、DoReMi：VLM に画像で問い続ける比較手法', 'Data from Table 1, 2 in Zhou et al., 2025.  ReKep: policy without a monitor; DoReMi: baseline that keeps querying the VLM with images'))

# ------------------------------------------------------------------ slide 27: VLS vs prior steering, comparison table
s = sl(27)
for sh in list(s.shapes):
    if shape_text(sh).startswith('既存手法との比較表'):
        remove(sh)
set_bullets(s, 27, [
    t('Test-Time-Compute (TTC) 系は，行動候補に良い行動がなければ VLM や人が選べない', 'Test-time-compute methods cannot pick a good action if none of the candidates is good'),
    t('価値関数やダイナミクスモデルで誘導する手法は，そのモデル化誤差の影響を受けやすい', 'Steering with a value or dynamics model is sensitive to that model\'s errors'),
    t('VLS は報酬の勾配で候補そのものを動かし，報酬で選択する．追加の学習は不要', 'VLS moves the candidates with the reward gradient and selects by reward; no extra training'),
], size=20)
hdr = ['', t('代表例', 'Examples'), t('どう誘導するか', 'How it steers'), t('弱点', 'Weakness')]
rows = [
    (t('候補から選ぶ\n（Test-Time Compute 系）', 'Pick among candidates\n(test-time compute)'), 'ITPS, FOREWARN,\nDo What You Say',
     t('ポリシーが出した候補を VLM・人・検証器が選ぶ', 'A VLM, a person or a verifier picks one of the policy\'s candidates'),
     t('候補に良い行動がなければ選べない', 'If no candidate is good, nothing can be picked')),
    (t('学習済みモデルで誘導', 'Steer with a learned model'), 'V-GPS, VGD,\nDynaGuide',
     t('価値関数やダイナミクスモデルの勾配でノイズ除去を誘導', 'Gradients from a value or dynamics model guide the denoising'),
     t('補助モデルの学習が要り、その誤差や好みに引きずられる', 'Needs an extra model; its errors and preferences leak in')),
    ('VLS', t('（本論文）', '(this paper)'),
     t('VLM が書いた報酬の勾配で候補そのものを動かし、報酬で選別', 'The gradient of a VLM-written reward moves the candidates; reward-based resampling'),
     t('追加学習は不要。VLM の誤りは報酬に直結', 'No extra training; VLM mistakes go straight into the reward')),
]
tbl = s.shapes.add_table(len(rows) + 1, 4, inch(0.6), inch(3.6), inch(12.1), inch(2.9)).table
for j, wdt in enumerate([2.6, 2.2, 3.9, 3.4]):
    tbl.columns[j].width = inch(wdt)
colf = [GRAY_F, GRAY_F, GRAY_F, GRAY_F]
for j, val in enumerate(hdr):
    c = tbl.cell(0, j); c.text = ''
    add_runs(c.text_frame.paragraphs[0], val, size=14, bold=True, color=NAVY)
    c.margin_top = c.margin_bottom = inch(0.03)
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string('EDEDED')
for i, row in enumerate(rows, start=1):
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.text = ''
        lines = val.split('\n')
        for k, ln in enumerate(lines):
            p = c.text_frame.paragraphs[0] if k == 0 else c.text_frame.add_paragraph()
            add_runs(p, ln, size=13, bold=(j == 0), color=(NAVY if i == 3 else None))
        c.margin_top = c.margin_bottom = inch(0.04)
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(GREEN_F if i == 3 else ('FFFFFF' if i % 2 else 'FAFAFA'))

# ------------------------------------------------------------------ slide 31: VLS sim results
s = sl(31)
for sh in list(s.shapes):
    if sh.shape_type == 13 and sh.name != 'Picture 1':
        remove(sh)
    elif sh.name in ('TextBox 907', 'TextBox 908'):
        remove(sh)
set_bullets(s, 31, [
    t('設定：LIBERO-PRO は指示・配置を学習時から変更。CALVIN は物体の位置が毎回変わる', 'Setup: LIBERO-PRO changes instructions / layouts from training; CALVIN re-samples object positions'),
    t('LIBERO-PRO：凍結 π0.5 + VLS で平均 23.7% → 36.8%。物体の変更では 10.5% → 41%', 'LIBERO-PRO: VLS on a frozen π0.5 lifts the mean 23.7% → 36.8%; object perturbation 10.5% → 41%'),
    t('CALVIN：可動物体 94%、関節物体 87%。DynaGuide や ITPS より 15〜25 pt 高い', 'CALVIN: 94% on movable objects, 87% on articulated parts; 15-25 pt above DynaGuide and ITPS'),
], size=20)
add_picture(s, f'vls_results_{LANG}.png', 0.4, 3.4, w=7.6, folder=S + '/diag/')
add_picture(s, 'vls_fig3_bars', 8.1, 3.55, w=4.9)
caption(s, 0.4, 6.95, 7.2, t('Data from Table I in Liu et al., 2026.  Ablation：勾配の誘導を外すと平均 17%（Fig. 4）', 'Data from Table I in Liu et al., 2026.  Ablation: without gradient guidance the mean drops to 17% (Fig. 4)'))
caption(s, 8.1, 5.45, 4.9, t('Fig. 3 in Liu et al., 2026（CALVIN：既存の誘導手法との比較）', 'Fig. 3 in Liu et al., 2026 (CALVIN: comparison with prior steering methods)'))

# ------------------------------------------------------------------ slide 35: summary
s = sl(35)
for sh in list(s.shapes):
    if sh.shape_type == 19:
        remove(sh)
set_bullets(s, 35, [
    t('3本とも VLM が書いたものをポリシーの外側から入れる。違いは入れる場所', 'All three feed something the VLM wrote into the policy from outside; they differ in where'),
    t('CaM と VLS は同じ 3D 点とコードを共有でき、SimFoundry はそれを大量に試す場になる', 'CaM and VLS can share the same 3D points and code; SimFoundry is the place to test them at scale'),
], size=22)
hdr = ['', 'SimFoundry', 'Code-as-Monitor', 'VLS']
rows = [
    (t('VLM が書くもの', 'What the VLM writes'), t('物体の 3D モデルと変種', '3D objects and variants'), t('制約と監視コード', 'Constraints + monitor code'), t('報酬関数', 'Reward function')),
    (t('入れ先', 'Where it goes'), t('学習データ', 'Training data'), t('実行の停止条件', 'Stop condition at run time'), t('行動生成の目的関数', 'Objective of generation')),
    (t('効果', 'Effect'), t('Sim 評価 r = 0.91、実機 +40%', 'Sim eval r = 0.91; real +40%'), t('外乱下 +28.7 pt、時間 −31.8%', '+28.7 pt under disturbance; time −31.8%'), t('LIBERO-PRO +13 pt、実機 +19 pt', 'LIBERO-PRO +13 pt; real +19 pt')),
]
tbl = s.shapes.add_table(len(rows) + 1, 4, inch(0.6), inch(3.5), inch(12.1), inch(2.9)).table
for j, wdt in enumerate([2.3, 3.2, 3.4, 3.2]):
    tbl.columns[j].width = inch(wdt)
colf = [GRAY_F, BLUE_F, ORANGE_F, GREEN_F]
for j, val in enumerate(hdr):
    c = tbl.cell(0, j); c.text = ''
    add_runs(c.text_frame.paragraphs[0], val, size=18, bold=True, color=NAVY)
    c.margin_top = c.margin_bottom = inch(0.05)
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(colf[j])
for i, row in enumerate(rows, start=1):
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.text = ''
        add_runs(c.text_frame.paragraphs[0], val, size=16, bold=(j == 0))
        c.margin_top = c.margin_bottom = inch(0.08)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string('F2F2F2' if j == 0 else ('FFFFFF' if i % 2 else 'FAFAFA'))

P.save(OUT_PATH)
print('saved', OUT_PATH, len(P.slides))
