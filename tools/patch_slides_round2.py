# -*- coding: utf-8 -*-
"""Second review round: slide 10 figure, slide 27 bullets/table, slide 31 layout,
citations [Author+ year] on prior work, 変種 -> Digital Cousins.
usage: python3 patch6.py <in.pptx> <out.pptx> [ja|en]
"""
import sys
IN, OUT_PATH = sys.argv[1], sys.argv[2]
LANG_ARG = sys.argv[3] if len(sys.argv) > 3 else 'ja'
S = '/tmp/claude-0/-home-user-PaperPresentationSlides/b16a4cd5-a6b6-52ff-a060-bdd5dfede159/scratchpad'
sys.argv = ['build2.py', S + ('/en/draft_en.md' if LANG_ARG == 'en' else '/ja/draft_ja.md')]
exec(open(S + '/build_head.py').read())

P = Presentation(IN)
KEEP = ('Picture 1', 'スライド番号プレースホルダー', 'TextBox 900', 'TextBox 901', 'TextBox 902')


def shape_text(sh):
    return sh.text_frame.text.strip() if sh.has_text_frame else ''


def remove(sh):
    el = sh._element; el.getparent().remove(el)


def clear_body(slide):
    for sh in list(slide.shapes):
        if sh.name not in KEEP and not (sh.is_placeholder):
            remove(sh)


def set_bullets(slide, n, items, size=20, spacing=150):
    for sh in list(slide.shapes):
        if sh.name == 'TextBox 902':
            remove(sh)
    add_bullets(slide, n, size=size, spacing=spacing, items=items)


def sl(n):
    return P.slides[n - 1]


def make_table(slide, x, y, w, h, hdr, rows, widths, hdr_size, cell_size, hdr_fills, row_fill=None, bold_col0=True):
    tbl = slide.shapes.add_table(len(rows) + 1, len(hdr), inch(x), inch(y), inch(w), inch(h)).table
    for j, wd in enumerate(widths):
        tbl.columns[j].width = inch(wd)
    for j, val in enumerate(hdr):
        c = tbl.cell(0, j); c.text = ''
        add_runs(c.text_frame.paragraphs[0], val, size=hdr_size, bold=True, color=NAVY)
        c.margin_top = c.margin_bottom = inch(0.04)
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(hdr_fills[j])
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = tbl.cell(i, j); c.text = ''
            for k, ln in enumerate(val.split('\n')):
                p = c.text_frame.paragraphs[0] if k == 0 else c.text_frame.add_paragraph()
                add_runs(p, ln, size=cell_size, bold=(j == 0 and bold_col0))
            c.margin_top = c.margin_bottom = inch(0.05)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            f = row_fill(i, j) if row_fill else ('F2F2F2' if j == 0 else ('FFFFFF' if i % 2 else 'FAFAFA'))
            c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(f)
    return tbl


# ------------------------------------------------------------------ slide 10: 実験設定
s = sl(10)
clear_body(s)
add_picture(s, 'sf_evalgrid', 0.5, 3.35, w=6.6)
caption(s, 0.5, 6.4, 6.6, t('Fig. J.1 in Ranawaka et al., 2026：Stack Dishware の初期位置グリッド。各物体 25 点から毎回サンプル', 'Fig. J.1 in Ranawaka et al., 2026: start-position grid for Stack Dishware; each object is sampled from 25 points'))
hdr = ['', t('評価（実機ポリシーを Sim で）', 'Evaluation (real policies in sim)'), t('学習（Sim のデータで実機へ）', 'Training (sim data, real robot)')]
rows = [
    (t('ロボット', 'Robots'), t('DROID（Franka 1本腕）、YAM（両腕）', 'DROID (one Franka arm), YAM (two arms)'), t('同じ 2 種', 'The same two')),
    (t('ポリシー', 'Policies'), t('ゼロショット：π0, π0.5, GR00T N1.6 / N1.7, DreamZero\n微調整：π0, π0.5, GR00T N1.6（実機デモ 50 本）', 'Zero-shot: π0, π0.5, GR00T N1.6 / N1.7, DreamZero\nFine-tuned: π0, π0.5, GR00T N1.6 (50 real demos)'), t('DROID：π0 / π0.5 を微調整\nYAM：Flow Matching をゼロから学習', 'DROID: fine-tune π0 / π0.5\nYAM: flow matching from scratch')),
    (t('タスク', 'Tasks'), t('ゼロショット 4 + 微調整 3 の計 7', '4 zero-shot + 3 fine-tuned = 7'), t('Pot on Stove など 3 + 13 タスク', 'Pot on Stove etc.: 3 + 13 tasks')),
    (t('データ', 'Data'), t('タスクごとに 25 試行（右図の位置から）', '25 trials per task (positions as in the grid)'), t('テレオペ 10〜15 本 → MimicGen → 材質・カメラをランダム化', '10-15 teleop demos → MimicGen → material / camera randomization')),
]
make_table(s, 7.35, 3.35, 5.65, 3.2, hdr, rows, [1.0, 2.45, 2.2], 12, 11, ['EDEDED', BLUE_F, GREEN_F])

# ------------------------------------------------------------------ slide 27: VLS vs prior steering
s = sl(27)
for sh in list(s.shapes):
    if sh.shape_type == 19:
        remove(sh)
set_bullets(s, 27, [
    t('既存の推論時誘導は，「候補から選ぶ」か「学習済みモデルの勾配で誘導する」の 2 系統', 'Prior inference-time steering either picks among candidates or follows a learned model\'s gradient'),
    t('VLS は追加の学習なしに候補そのものを動かせる点が異なる（下表）', 'VLS differs in moving the candidates themselves with no extra training (table)'),
], size=20)
hdr = ['', t('代表例', 'Examples'), t('どう誘導するか', 'How it steers'), t('弱点', 'Weakness')]
rows = [
    (t('候補から選ぶ\n（Test-Time Compute 系）', 'Pick among candidates\n(test-time compute)'), 'ITPS [Wang+ 2024]\nFOREWARN [Wu+ 2025]\nDo What You Say [Wu+ 2025]',
     t('ポリシーが出した候補を VLM・人・検証器が選ぶ', 'A VLM, a person or a verifier picks one of the policy\'s candidates'),
     t('候補に良い行動がなければ選べない', 'If no candidate is good, nothing can be picked')),
    (t('学習済みモデルの勾配で誘導', 'Steer with a learned model'), 'V-GPS [Nakamoto+ 2024]\nVGD [Ye 2025]\nDynaGuide [Du+ 2025]',
     t('価値関数やダイナミクスモデルの勾配でノイズ除去を誘導', 'Gradients from a value or dynamics model guide the denoising'),
     t('補助モデルの学習が要り、その誤差や好みに引きずられる', 'Needs an extra model; its errors and preferences leak in')),
    ('VLS', t('本論文 [Liu+ 2026]', 'This paper [Liu+ 2026]'),
     t('VLM が書いた報酬の勾配で候補そのものを動かし、報酬で選別', 'The gradient of a VLM-written reward moves the candidates; reward-based resampling'),
     t('追加学習は不要。VLM の誤りは報酬に直結', 'No extra training; VLM mistakes go straight into the reward')),
]
make_table(s, 0.6, 3.0, 12.1, 3.7, hdr, rows, [2.7, 2.7, 3.5, 3.2], 15, 14, ['EDEDED'] * 4,
           row_fill=lambda i, j: GREEN_F if i == 3 else ('FFFFFF' if i % 2 else 'FAFAFA'))

# ------------------------------------------------------------------ slide 31: VLS sim results layout
s = sl(31)
clear_body(s)
add_picture(s, f'vls_results_{LANG}.png', 0.4, 3.4, w=7.5, folder=S + '/diag/')
caption(s, 0.4, 6.95, 7.4, 'Data from Table I in Liu et al., 2026')
add_picture(s, 'vls_fig3_bars', 8.1, 3.45, w=4.9)
caption(s, 8.1, 5.38, 4.9, t('Fig. 3 in Liu et al., 2026：CALVIN で既存の誘導手法と比較', 'Fig. 3 in Liu et al., 2026: CALVIN, vs. prior steering methods'))
add_picture(s, 'vls_abl', 8.1, 5.7, w=4.9)
caption(s, 8.1, 7.0, 4.0, t('Fig. 4 (left) in Liu et al., 2026（勾配なしで 17%）', 'Fig. 4 (left) in Liu et al., 2026: ablation (no gradient: 17% mean)'))

# ------------------------------------------------------------------ citations + Digital Cousins (run-level replacements)
CITES = [
    ('LIBERO-Pro 80', 'LIBERO-Pro [Zhou+ 2025] 80'),
    ('RoboDojo 22.5%', 'RoboDojo [2026] 22.5%'),
    ('Depth Anything 3 で', 'Depth Anything 3 [Lin+ 2025] で'),
    ('SAM 3 で1つずつ', 'SAM 3 [Carion+ 2025] で1つずつ'),
    ('③ Hunyuan3D で切り抜きからメッシュを作り、FoundationPose で姿勢を合わせる', '③ Hunyuan3D [2025] でメッシュ化し、FoundationPose [Wen+ 2024] で姿勢合わせ'),
    ('CoACD で', 'CoACD [Wei+ 2022] で'),
    ('10〜15 デモを収集 → MimicGen で増やす → π0.5かFlow Policyを学習', 'デモ 10〜15 本 → MimicGen [Mandlekar+ 2023] で拡張 → π0.5 / Flow Policy'),
    ('SAM3D は', 'SAM3D [SAM 3D Team 2025] は'),
    ('BridgeData V2 の', 'BridgeData V2 [Walke+ 2023] の'),
    ('（CoTracker）', '（CoTracker [Karaev+ 2024]）'),
    ('DoReMi より', 'DoReMi [Guo+ 2023] より'),
    ('token −52.2%（OmniGibson）', 'token −52.2%'),
    ('Data from Table 1, 2 in Zhou et al., 2025.', 'Data from Table 1, 2 in Zhou et al., 2025 (OmniGibson [Li+ 2022]).'),
    ('ReKep：監視なし', 'ReKep [Huang+ 2024]：監視なし'),
    ('DoReMi：VLM に画像で問い続ける比較手法', 'DoReMi [Guo+ 2023]：VLM に画像で問い続ける比較手法。Inner Monologue [Huang+ 2022]：サブゴール完了時だけ問う比較手法'),
    ('DoReMi (先行研究)', 'DoReMi [Guo+ 2023]'),
    ('DoReMi 0%', 'DoReMi [Guo+ 2023] 0%'),
    ('LIBERO-PRO は指示・配置を学習時から変更。CALVIN は物体の位置が毎回変わる', 'LIBERO-PRO [Zhou+ 2025] と CALVIN [Mees+ 2022]。学習時と条件を変えて評価'),
    ('CALVIN：可動物体 94%、関節物体 87%。DynaGuide や ITPS より 15〜25 pt 高い', 'CALVIN：可動物体 94%、関節物体 87%（DynaGuide [Du+ 2025] などより +15〜25 pt）'),
    ('動画は LIBERO での例', '動画は LIBERO [Liu+ 2023] での例'),
    # Digital Cousins
    ('複製 ＋ 物体・配置・タスクの変種', 'Twin ＋ 物体・配置・タスクの Cousins'),
    ('実機への転移と変種の効果', '実機への転移と Digital Cousins の効果'),
    ('A: 物体の変種は未知の物体に効く   B: 配置の変種は新しい配置に効く', 'A: 物体の Cousins は未知の物体に効く   B: 配置の Cousins は新しい配置に効く'),
    ('右は学習に含めなかった未知の物体での実行。物体の変種を学習に混ぜた効果', '右は未知の物体での実行。物体の Digital Cousins を学習に混ぜた効果'),
    ('物体の 3D モデルと変種', 'Digital Twin と Digital Cousins'),
]


def iter_frames(slide):
    for sh in slide.shapes:
        if sh.has_text_frame:
            yield sh.text_frame
        elif sh.shape_type == 19:
            for r in sh.table.rows:
                for c in r.cells:
                    yield c.text_frame


applied = {}
for si, slide in enumerate(P.slides, 1):
    for tf in iter_frames(slide):
        for para in tf.paragraphs:
            runs = para.runs
            full = ''.join(r.text for r in runs)
            for a, b in CITES:
                if a not in full:
                    continue
                # try single-run replacement first
                done = False
                for r in runs:
                    if a in r.text:
                        r.text = r.text.replace(a, b, 1); done = True; break
                if not done:
                    # match spans runs: splice into the run holding the match start, keep its format
                    start = full.index(a); end = start + len(a); pos = 0
                    first = last = None
                    for r in runs:
                        rs, re_ = pos, pos + len(r.text)
                        if first is None and rs <= start < re_:
                            first = (r, start - rs)
                        if rs < end <= re_:
                            last = (r, end - rs)
                        pos = re_
                    fr, fo = first; lr, lo = last
                    tail = lr.text[lo:]
                    seen = False
                    for r in runs:
                        if r is fr:
                            seen = True; r.text = r.text[:fo] + b + (tail if lr is not fr else lr.text[lo:])
                        elif seen:
                            r.text = ''
                            if r is lr: seen = False
                applied.setdefault(a, []).append(si)
                full = ''.join(r.text for r in runs)

for a, b in CITES:
    print(('OK  ' if a in applied else 'MISS'), a[:40], applied.get(a, ''))

for sh in sl(21).shapes:
    if shape_text(sh).startswith('Data from Table 1, 2'):
        sh.width = inch(10.8)

# any 変種 left?
for si, slide in enumerate(P.slides, 1):
    for tf in iter_frames(slide):
        if '変種' in tf.text:
            print('REMAINING 変種 on slide', si, ':', tf.text[:60])

P.save(OUT_PATH)
print('saved', OUT_PATH, len(P.slides))
