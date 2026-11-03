# -*- coding: utf-8 -*-
"""Build the Japanese survey slide deck on top of the reference deck's master/layouts."""
import copy
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = '/home/user/PaperPresentationSlides'
REF = ROOT + '/参考用/20260514_KaneyoshiHiratsuka_SurveySlide_A_Survey_of_Recent_Advances_in_Vision-Language-Action_Models_v2.pptx'
OUT = ROOT + '/20261105_KaneyoshiHiratsuka_SurveySlide.pptx'
S = '/tmp/claude-0/-home-user-PaperPresentationSlides/b16a4cd5-a6b6-52ff-a060-bdd5dfede159/scratchpad'
FIG = S + '/figs/'
EQ = S + '/eq/'
HEADER_IMG = S + '/unpacked/ppt/media/image1.jpg'

prs = Presentation(REF)
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)

LAYOUT_TITLE = prs.slide_layouts[0]
LAYOUT_CONTENT = prs.slide_layouts[1]

# colours (match the reference's pastel boxes)
BLUE_F, BLUE_L = 'DAE8FC', '6C8EBF'
GREEN_F, GREEN_L = 'D5E8D4', '82B366'
ORANGE_F, ORANGE_L = 'FFE6CC', 'D79B00'
GRAY_F, GRAY_L = 'EDEDED', '7F7F7F'
PINK_F, PINK_L = 'F8CECC', 'B85450'
YELLOW_F, YELLOW_L = 'FFF2CC', 'D6B656'
RED = 'C00000'
NAVY = '1F3864'
MUTED = '7F7F7F'

SLDNUM_XML = (
    '<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    '<p:nvSpPr><p:cNvPr id="%d" name="スライド番号プレースホルダー"/>'
    '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    '<p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr>'
    '<p:spPr><a:xfrm><a:off x="8610600" y="6356350"/><a:ext cx="2743200" cy="365125"/></a:xfrm></p:spPr>'
    '<p:txBody><a:bodyPr/><a:lstStyle/><a:p>'
    '<a:fld id="{F250D92A-AB23-4586-B03B-20FC810DD95B}" type="slidenum">'
    '<a:rPr lang="ja-JP" altLang="en-US"/><a:t>%d</a:t></a:fld>'
    '<a:endParaRPr lang="ja-JP" altLang="en-US"/></a:p></p:txBody></p:sp>'
)

slide_counter = [0]


def _style_run(run, size=24, bold=False, color=None, italic=False, lang='ja-JP', font='Arial', underline=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if font:
        run.font.name = font
    if underline is not None:
        run.font.underline = underline
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    rPr = run._r.get_or_add_rPr()
    rPr.set('lang', lang)
    rPr.set('altLang', 'en-US' if lang == 'ja-JP' else 'ja-JP')


def add_runs(p, segments, size=24, color=None, bold=False, lang='ja-JP'):
    """segments: str or list of str/(str, dict)"""
    if isinstance(segments, str):
        segments = [segments]
    for seg in segments:
        if isinstance(seg, tuple) and len(seg) == 2 and isinstance(seg[1], dict):
            text, opt = seg
        elif isinstance(seg, (tuple, list)):
            add_runs(p, list(seg), size=size, color=color, bold=bold, lang=lang)
            continue
        else:
            text, opt = seg, {}
        r = p.add_run()
        r.text = text
        o = dict(size=size, bold=bold, color=color, lang=lang)
        o.update(opt)
        link = o.pop('link', None)
        _style_run(r, **o)
        if link:
            r.hyperlink.address = link


def set_bullet(p, level=0, spacing=150, char=None, size_pct=None):
    pPr = p._p.get_or_add_pPr()
    if level == 0:
        pPr.set('marL', '342900'); pPr.set('indent', '-342900')
    else:
        pPr.set('marL', '800100'); pPr.set('indent', '-285750')
        pPr.set('lvl', '1')
    lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
    spcPct = etree.SubElement(lnSpc, qn('a:spcPct')); spcPct.set('val', str(int(spacing * 1000)))
    if size_pct:
        bu = etree.SubElement(pPr, qn('a:buSzPct')); bu.set('val', str(int(size_pct * 1000)))
    buFont = etree.SubElement(pPr, qn('a:buFont'))
    buFont.set('typeface', 'Wingdings'); buFont.set('pitchFamily', '2'); buFont.set('charset', '2')
    buChar = etree.SubElement(pPr, qn('a:buChar'))
    buChar.set('char', char or ('n' if level == 0 else 'l'))


def set_line_spacing(p, spacing):
    pPr = p._p.get_or_add_pPr()
    lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
    spcPct = etree.SubElement(lnSpc, qn('a:spcPct')); spcPct.set('val', str(int(spacing * 1000)))


def textbox(slide, x, y, w, h, autofit=True, anchor=None, margin=None):
    tb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    if autofit:
        tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    if anchor:
        tf.vertical_anchor = anchor
    if margin is not None:
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(margin)
    return tb


def inch(v):
    return int(round(v * 914400))


def add_text(slide, x, y, w, h, lines, size=18, color=None, bold=False, align=None, autofit=True,
             anchor=None, spacing=None, margin=None, lang='ja-JP'):
    """lines: list of segments (each a str or list of runs)."""
    tb = textbox(slide, inch(x), inch(y), inch(w), inch(h), autofit=autofit, anchor=anchor, margin=margin)
    tf = tb.text_frame
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        if align:
            p.alignment = align
        if spacing:
            set_line_spacing(p, spacing)
        add_runs(p, ln, size=size, color=color, bold=bold, lang=lang)
    return tb


def add_bullets(slide, items, x=0.886, y=1.269, w=12.313, size=24, spacing=150, sub_size=None):
    """items: list of segments or ('sub', segments)."""
    tb = textbox(slide, inch(x), inch(y), inch(w), inch(1.0))
    tf = tb.text_frame
    first = True
    for it in items:
        level = 0
        if isinstance(it, tuple) and it and it[0] == 'sub':
            level = 1
            it = it[1]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        set_bullet(p, level=level, spacing=spacing)
        add_runs(p, it, size=(sub_size or size - 4) if level else size)
        # rough width check: full-width char = 1, ascii = 0.55
        def _flat(x):
            if isinstance(x, str): return x
            if isinstance(x, tuple) and len(x) == 2 and isinstance(x[1], dict): return x[0]
            return ''.join(_flat(y) for y in x)
        txt = _flat(it)
        units = sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in txt)
        limit = (w - 0.6) / (size / 72.0)
        if units > limit:
            print(f'  [wrap warning] slide {slide_counter[0]}: {units:.0f} > {limit:.0f}: {txt[:50]}')
    return tb


def add_picture(slide, name, x, y, w=None, h=None, folder=FIG):
    path = folder + name + '.png' if not name.endswith(('.png', '.jpg')) else folder + name
    kw = {}
    if w is not None:
        kw['width'] = inch(w)
    if h is not None:
        kw['height'] = inch(h)
    return slide.shapes.add_picture(path, inch(x), inch(y), **kw)


def add_eq(slide, name, x, y, w):
    return add_picture(slide, name, x, y, w=w, folder=EQ)


def add_box(slide, x, y, w, h, text, fill=BLUE_F, line=BLUE_L, size=16, bold=True, color='000000',
            shape=MSO_SHAPE.ROUNDED_RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, lines=None,
            margin=0.05):
    shp = slide.shapes.add_shape(shape, inch(x), inch(y), inch(w), inch(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = RGBColor.from_string(fill)
    shp.line.color.rgb = RGBColor.from_string(line)
    shp.line.width = Pt(1)
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = inch(margin)
    tf.margin_top = tf.margin_bottom = inch(0.03)
    lines = lines if lines is not None else [text]
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if isinstance(ln, tuple) and ln and ln[0] == 'opt':
            _, segs, opt = ln
            o = dict(size=size, bold=bold, color=color); o.update(opt)
            add_runs(p, segs, **o)
        else:
            add_runs(p, ln, size=size, bold=bold, color=color)
    return shp


def add_arrow(slide, x, y, w, h, shape=MSO_SHAPE.RIGHT_ARROW, fill='FFC000', line='BF9000', rot=0):
    shp = slide.shapes.add_shape(shape, inch(x), inch(y), inch(w), inch(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = RGBColor.from_string(fill)
    shp.line.color.rgb = RGBColor.from_string(line)
    shp.shadow.inherit = False
    if rot:
        shp.rotation = rot
    return shp


def caption(slide, x, y, w, text, size=11, color=MUTED, align=PP_ALIGN.LEFT):
    return add_text(slide, x, y, w, 0.3, [text], size=size, color=color, align=align, lang='en-US')


def new_slide(category, title, notes=None, title_size=36):
    slide_counter[0] += 1
    slide = prs.slides.add_slide(LAYOUT_CONTENT)
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    slide.shapes.add_picture(HEADER_IMG, 0, 0, Emu(12192000), Emu(635000))
    # slide number placeholder
    sp = etree.fromstring(SLDNUM_XML % (900, slide_counter[0]))
    slide.shapes._spTree.append(sp)
    # category label
    tb = textbox(slide, 0, 0, 10048875, 400110)
    p = tb.text_frame.paragraphs[0]
    if isinstance(category, str):
        add_runs(p, category, size=20, lang='en-US')
    else:
        add_runs(p, category, size=20, lang='en-US')
    # title
    tb = textbox(slide, 218047, 457201, 11543317, 646290)
    p = tb.text_frame.paragraphs[0]
    add_runs(p, title, size=title_size, bold=True, lang='ja-JP')
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide


# ------------------------------------------------------------------ papers list
PAPERS = [
    dict(short='SimFoundry',
         title='SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation',
         cite='N. Ranawaka, J. Wong et al., “SimFoundry: Modular and automated scene generation for policy learning and evaluation,” 2026. [Online]. Available: https://arxiv.org/abs/2606.28276',
         url='https://arxiv.org/abs/2606.28276'),
    dict(short='VLS',
         title='VLS: Steering Pretrained Robot Policies via Vision–Language Models',
         cite='S. Liu et al., “VLS: Steering pretrained robot policies via vision–language models,” 2026. [Online]. Available: https://arxiv.org/abs/2602.03973',
         url='https://arxiv.org/abs/2602.03973'),
    dict(short='Code-as-Monitor',
         title='Code-as-Monitor: Constraint-aware Visual Programming for Reactive and Proactive Robotic Failure Detection',
         cite='E. Zhou, Q. Su, C. Chi et al., “Code-as-Monitor: Constraint-aware visual programming for reactive and proactive robotic failure detection,” in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR), 2025. [Online]. Available: https://arxiv.org/abs/2412.04455',
         url='https://arxiv.org/abs/2412.04455'),
]
DECK_TITLE = '学習済みポリシーを頑健に運用する3つの層'


def papers_slide(active, notes):
    slide = new_slide('Papers', DECK_TITLE)
    # centred big title replaced by reference-like heading: keep title centred
    tb = textbox(slide, inch(0.52), inch(1.55), inch(12.57), inch(5.0))
    tf = tb.text_frame
    first = True
    for i, pp in enumerate(PAPERS):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', '457200'); pPr.set('indent', '-457200')
        lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
        etree.SubElement(lnSpc, qn('a:spcPct')).set('val', '150000')
        buFont = etree.SubElement(pPr, qn('a:buFont')); buFont.set('typeface', '+mj-lt')
        etree.SubElement(pPr, qn('a:buAutoNum')).set('type', 'arabicPeriod')
        on = (active is None) or (i == active)
        col = None if on else 'A6A6A6'
        r = p.add_run(); r.text = pp['title']
        _style_run(r, size=22, bold=True, color=col, lang='en-US')
        r.hyperlink.address = pp['url']
        br = etree.SubElement(p._p, qn('a:br'))
        r2 = p.add_run(); r2.text = pp['cite']
        _style_run(r2, size=14, color=col or '404040', lang='en-US')
        # move br before r2 (SubElement appended it after r2's creation? ensure order)
        p._p.remove(br); r2._r.addprevious(br)
        sp = etree.SubElement(p._p, qn('a:endParaRPr')); sp.set('sz', '800'); sp.set('lang', 'en-US')
    slide.notes_slide.notes_text_frame.text = notes
    return slide


# ================================================================== SLIDE 1: title
slide_counter[0] += 1
s = prs.slides.add_slide(LAYOUT_TITLE)
for ph in list(s.placeholders):
    ph._element.getparent().remove(ph._element)
s.shapes.add_picture(HEADER_IMG, 0, 0, Emu(12192000), Emu(635000))
tb = textbox(s, 125835, 2950000, 11940330, 646331)
p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
add_runs(p, DECK_TITLE, size=36, bold=True)
p2 = tb.text_frame.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
add_runs(p2, 'Sim 評価 ・ 推論時ステアリング ・ 実行監視', size=24, color=NAVY)
tb = textbox(s, 6015872, 4300000, 5392132, 707886)
p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
add_runs(p, 'Research Seminar 2026/11/05', size=20, lang='en-US')
p = tb.text_frame.add_paragraph(); p.alignment = PP_ALIGN.RIGHT
add_runs(p, 'Kaneyoshi Hiratsuka', size=20, lang='en-US')
s.notes_slide.notes_text_frame.text = (
    '[J] 皆さん、こんにちは。本日は「学習済みロボットポリシーを頑健に運用する」という観点で3本の論文を紹介します。'
    '最近のVLAや拡散ポリシーは分布内では高い性能を出しますが、実際に配備すると評価コスト、分布外への脆さ、実行中の失敗という3つの壁にぶつかります。'
    '今日の3本は、ポリシー本体を再学習せずに、その「外側」でこれらの壁に対処するという共通点を持っています。'
    '配備前のSim評価・学習（SimFoundry）、推論時のステアリング（VLS）、実行中の監視（Code-as-Monitor）という3つの層として整理して紹介します。'
)

# ================================================================== SLIDE 2: background 1
s = new_slide('Background', '学習済みポリシーは配備時に何につまずくか', notes=(
    '[J] まず背景です。π0.5やDiffusion Policyのような学習済みポリシーを実機に配備すると、3種類の問題に直面します。'
    '1つ目は評価と学習のコストです。実機での厳密な比較には数千試行が必要で、学習データの収集も数か月規模になります。'
    '2つ目は分布外、OODへの脆さです。物体や配置、指示が少し変わるだけで失敗しますが、これは動作スキルが無いのではなく、学習時の空間配置と結び付きすぎているためです。'
    '3つ目は実行中の失敗です。外乱や長期タスクでは失敗は避けられず、検知と予防が必要になります。'
    'そして共通の前提として、ポリシー本体は再学習せず凍結したまま扱いたい、という点があります。再学習は高コストで、既にある能力を選択的に引き出せないからです。'
))
cols = [
    (0.45, '① 評価・学習のコスト', BLUE_F, BLUE_L, '実機評価は数千試行規模。学習データ収集も数か月かかる', 'sf_tasks', 2.6),
    (4.70, '② 分布外 (OOD) への脆さ', GREEN_F, GREEN_L, '物体・配置・指示が少し変わるだけで失敗。スキルは「ある」のに使えない', 'vls_fig1_left', 2.6),
    (8.95, '③ 実行中の失敗', ORANGE_F, ORANGE_L, '外乱・長期タスクでは失敗は不可避。検知と予防が必要', 'cam_fig1a', 2.6),
]
for x, head, f, l, desc, img, imh in cols:
    add_box(s, x, 1.35, 3.95, 0.55, head, fill=f, line=l, size=18)
    add_text(s, x, 1.98, 3.95, 0.9, [desc], size=15, spacing=110)
    pic = add_picture(s, img, x, 3.0, h=imh)
    # centre image in column
    pic.left = inch(x + (3.95 - pic.width / 914400) / 2)
caption(s, 0.45, 5.62, 4.0, 'Ranawaka et al., 2026 (SimFoundry) Fig. 4')
caption(s, 4.70, 5.62, 4.0, 'Liu et al., 2026 (VLS) Fig. 1')
caption(s, 8.95, 5.62, 4.0, 'Zhou et al., 2025 (Code-as-Monitor) Fig. 1')
add_arrow(s, 0.9, 6.15, 1.0, 0.5)
add_text(s, 2.0, 6.08, 11.0, 0.6,
         [['共通の前提：ポリシー本体（', ('π0.5, Diffusion Policy, GR00T …', dict(lang='en-US')), '）は再学習せず ',
           ('凍結したまま', dict(bold=True, color=RED)), ' 頑健に使いたい']], size=22)

# ================================================================== SLIDE 3: background 2 (three layers)
s = new_slide('Background', '3本の論文 = ポリシーを囲む3つの層', notes=(
    '[J] 本日の3本は、ポリシーのライフサイクルに沿って3つの層として整理できます。'
    '配備前の層がSimFoundryで、1本の動画から物理シミュレータ上のDigital Twinを自動構築し、その変種であるDigital Cousinsを生成して、Sim上で評価と学習データ生成を行います。'
    '推論時の層がVLSで、VLMが書いた微分可能な報酬関数の勾配を、凍結した拡散／フローポリシーのdenoisingに注入して、分布外の条件に行動を適応させます。'
    '実行中の層がCode-as-Monitorで、VLMが生成した監視コードで幾何的な制約を常時検査し、失敗を事後検知するだけでなく事前に予防して再計画に繋げます。'
    '共通点は、VLMや基盤モデルをポリシーの外側に置き、本体には手を入れないことです。'
))
add_bullets(s, [
    [('SimFoundry', dict(bold=True, lang='en-US')), '：配備前に Real→Sim で評価・学習データ生成'],
    [('VLS', dict(bold=True, lang='en-US')), '：推論時に行動分布を補正して分布外に適応'],
    [('Code-as-Monitor', dict(bold=True, lang='en-US')), '：実行中に失敗を検知・予防して再計画'],
])
# timeline
phases = [(0.6, '配備前', 'Before deployment'), (4.85, '推論時', 'Inference time'), (9.1, '実行中', 'During execution')]
for x, jp, en in phases:
    add_text(s, x, 3.05, 3.6, 0.4, [[(jp, dict(bold=True)), ('  ' + en, dict(size=14, color=MUTED, lang='en-US'))]], size=18, align=PP_ALIGN.CENTER)
boxes = [
    (0.6, BLUE_F, BLUE_L, 'SimFoundry', ['1本の動画 → Digital Twin', 'Cousins で多様化', 'Sim 評価 / Sim→Real 学習']),
    (4.85, GREEN_F, GREEN_L, 'VLS', ['VLM が微分可能な報酬を生成', '報酬勾配で denoising を操舵', '訓練不要・パラメータ不変']),
    (9.1, ORANGE_F, ORANGE_L, 'Code-as-Monitor', ['VLM が監視コードを生成', '幾何要素を追跡し制約を検査', 'Reactive + Proactive 検知']),
]
for x, f, l, name, sub in boxes:
    add_box(s, x, 3.5, 3.6, 1.75, '', fill=f, line=l,
            lines=[('opt', [(name, dict(lang='en-US'))], dict(size=22, bold=True))] +
                  [('opt', [t], dict(size=14, bold=False)) for t in sub])
add_arrow(s, 4.3, 4.15, 0.45, 0.45)
add_arrow(s, 8.55, 4.15, 0.45, 0.45)
# frozen policy bar
add_box(s, 0.6, 5.85, 12.1, 0.8, '', fill=GRAY_F, line=GRAY_L,
        lines=[('opt', ['凍結された学習済みポリシー（', ('π0.5 / Diffusion Policy / GR00T / OpenVLA …', dict(lang='en-US')), '）本体は変更しない'], dict(size=18, bold=True))])
for x in (2.4, 6.65, 10.9):
    add_arrow(s, x - 0.2, 5.3, 0.4, 0.5, shape=MSO_SHAPE.UP_DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
caption(s, 0.6, 6.75, 12, '層を分ける利点：モジュール性、基盤モデルの差し替え、再学習なしでの改善', size=14, color=NAVY)

# ================================================================== SLIDE 4: papers (all)
papers_slide(None, (
    '[J] 紹介する3本です。1本目はNVIDIA・Stanford・Georgia TechらによるSimFoundry。実世界の動画1本からシミュレーション環境を自動生成し、ポリシーの評価と学習に使います。'
    '2本目はワシントン大学・AI2らによるVLS。訓練なしで、凍結した生成ポリシーを推論時にVLM生成の報酬で操舵します。'
    '3本目は北航大・北京大・BAAI・GalbotらによるCode-as-Monitor（CVPR 2025）。VLMが生成したコードでロボットの失敗をリアルタイムに検知・予防します。'
    'それぞれ「配備前」「推論時」「実行中」の順で紹介します。'
))

# ================================================================== SLIDE 5: papers (#1)
papers_slide(0, (
    '[J] では1本目、SimFoundryです。一言で言えば「1本の実世界動画から、評価にも学習にも使えるシミュレーション環境を全自動で作るモジュール型システム」です。'
    'キーワードは3つ、Digital Twin、Digital Cousins、そしてReal-to-Sim評価とSim-to-Real学習の両立です。'
))

# ================================================================== SimFoundry slides
CAT1 = [('1. ', {}), ('SimFoundry', dict(bold=True, link=PAPERS[0]['url']))]

s = new_slide(CAT1, '背景：実機での評価・学習はスケールしない', notes=(
    '[J] 背景です。ロボット基盤モデルの学習には大規模なテレオペデータが必要で、評価も実機で数千試行を要します。'
    'そこでシミュレーションが代替として注目され、自動デモ生成やSim評価と実機性能の相関が示されてきました。'
    'しかし実世界に合ったSimシーンを手作業で構築することがボトルネックです。'
    'Real-to-Simの既存システムを表で比較すると、Sim-to-Real学習ができるもの、Real-to-Sim評価ができるもの、自動構築ができるもの、はそれぞれ存在しますが、'
    'これらを全て備え、さらに物体・シーン・タスクの3軸で多様化まで行えるものはありませんでした。SimFoundryはこの全てを1つのパイプラインで満たすことを狙います。'
))
add_bullets(s, [
    '✅ Sim は安価にスケールし、実機性能との相関も報告されている',
    '❌ 実世界に合った Sim シーンの手作業構築がボトルネック',
    '❌ 既存手法は「評価」「学習」「多様化」のどれかが欠ける',
])
add_picture(s, 'sf_tab1', 0.45, 3.1, w=8.6)
caption(s, 0.45, 6.78, 8.6, 'Table 1 in Ranawaka et al., 2026')
add_box(s, 9.4, 3.3, 3.6, 3.2, '', fill=YELLOW_F, line=YELLOW_L, anchor=MSO_ANCHOR.MIDDLE,
        lines=[('opt', ['SimFoundry の狙い'], dict(size=18, bold=True)),
               ('opt', ['動画1本から'], dict(size=16, bold=False)),
               ('opt', ['「評価も学習もできる」'], dict(size=16, bold=True, color=RED)),
               ('opt', ['Sim 環境を全自動で構築し、'], dict(size=16, bold=False)),
               ('opt', ['物体・シーン・タスクの'], dict(size=16, bold=False)),
               ('opt', ['3軸で多様化する'], dict(size=16, bold=False))])

s = new_slide(CAT1, '概要：Digital Twin から Digital Cousins へ', notes=(
    '[J] 全体像です。入力は実世界シーンを撮った動画1本、出力は物理シミュレータ上で操作可能なsim-readyなDigital Twinです。'
    'さらにTwinを基点に、アフォーダンス、つまりタスク上の意味を保ったままの変種、Digital Cousinsを無限に生成できます。'
    '変化の軸は物体、シーン配置、タスクの3つです。'
    '生成した環境は、右回りの矢印のように実機ポリシーをSimで評価するReal-to-Sim評価と、Simで学習して実機に転移するSim-to-Real学習の両方に使えます。'
))
add_bullets(s, [
    '入力：実世界の動画1本 → 出力：物理 Sim 上の Digital Twin',
    'Twin を基点に、機能を保った変種 = Digital Cousins を無限に生成',
    '用途：Real→Sim 評価と Sim→Real 学習の両方',
])
add_picture(s, 'sf_fig1', 1.65, 3.1, w=10.0)
caption(s, 1.65, 6.95, 8, 'Fig. 1 in Ranawaka et al., 2026')

s = new_slide(CAT1, '手法：Extraction → Generation の自動パイプライン', notes=(
    '[J] 再構成パイプラインです。Extractionでは動画から代表フレームを選び、深度推定で点群を作り、VLMで物体を検出、SAM 3で1物体ずつ切り出してはinpaintingで消す、という処理を前景が無くなるまで繰り返します。'
    'Generationでは物体ごとの画像を高解像度化して2D-to-3Dメッシュ生成を行い、FoundationPoseなどで位置合わせ、引き出しや戸棚は別モジュールで関節を推定します。'
    'CoACDで衝突形状を作り、質量や摩擦といった物理パラメータはVLMに問い合わせて付与、最後にPyBulletで貫通を解消して安定化させ、IsaacLabなどへ書き出します。'
    '重要なのは全モジュールが差し替え可能な設計で、より良い基盤モデルが出ればそのまま組み込めることです。背景は3D Gaussian Splattingでも再構成できます。'
))
add_bullets(s, [
    [('Extraction', dict(bold=True, lang='en-US')), '：深度推定 → VLM 検出 → SAM 3 で1物体ずつ切り出し'],
    [('Generation', dict(bold=True, lang='en-US')), '：2D→3D メッシュ、位置合わせ、関節推定、物性付与'],
    '全モジュールが差し替え可能。背景は 3DGS で再構成',
])
add_picture(s, 'sf_fig2_top', 0.5, 3.45, w=12.3)
caption(s, 0.5, 6.85, 8, 'Fig. 2 (top) in Ranawaka et al., 2026')

s = new_slide(CAT1, '手法：3種類の Digital Cousins', notes=(
    '[J] Augmentation、つまりDigital Cousinsの生成です。'
    'Object cousinsは、物体画像を画像空間で摂動してから2D-to-3D生成をやり直すことで、形状やテクスチャは違うが同じ機能を持つ物体を作ります。'
    'Scene cousinsは、OnTopやRightOfのような空間述語をVLMに操作させて、単なる位置ノイズではなく意味のある別配置を生成します。distractor物体も追加できます。'
    'Task cousinsは、シーン内の物体とアフォーダンスから実行可能な別タスクをVLMに提案させ、BDDL形式の目標記述に変換して、MimicGen系の手法でデモを自動生成します。'
    'これにより1つの実シーンから、物体・配置・タスクの多様性を持つ大量の学習データが得られます。'
))
add_bullets(s, [
    [('Object', dict(bold=True, lang='en-US')), '：物体画像を摂動 → 2D→3D 再生成（同機能・別形状）'],
    [('Scene', dict(bold=True, lang='en-US')), '：空間述語（OnTop / RightOf）を VLM が操作し別配置を生成'],
    [('Task', dict(bold=True, lang='en-US')), '：実行可能な別タスクを VLM が提案 → BDDL 化しデモを自動生成'],
])
add_picture(s, 'sf_fig2_bot', 0.5, 3.45, w=12.3)
caption(s, 0.5, 6.85, 8, 'Fig. 2 (bottom) in Ranawaka et al., 2026')

s = new_slide(CAT1, '結果①：Real→Sim 評価は実機性能を予測できる', notes=(
    '[J] 1つ目の結果、Real-to-Sim評価です。DROIDのFranka単腕と、YAMの双腕という2つの実機セットアップで7タスク、π0、π0.5、GR00T N1.6、N1.7、DreamZeroの5種類のポリシーをSimと実機の両方で評価しました。'
    '右の散布図で、SimFoundryの青い点は対角線近くに乗っており、平均Pearson相関0.911、順位逆転の指標MMRVは0.018です。'
    '比較対象の最先端手法PolaRiSのオレンジはばらついており、相関で0.59以上の差があります。しかもPolaRiSがSimデータで軽くfine-tuningしているのに対し、SimFoundryはポリシーを一切Simに適応させないゼロショット評価です。'
    'さらにサブタスク単位で評価すると相関は0.90から0.95に上がり、どの段階が弱いかという改善の指針も得られます。'
))
add_bullets(s, [
    '7タスク × 5ポリシーを Sim と実機の両方で評価',
    ['平均 Pearson ', ('r', dict(italic=True, lang='en-US')), (' = 0.911、MMRV = 0.018', dict(bold=True)), '（順位逆転ほぼ無し）'],
    ['PolaRiS より ', ('r', dict(italic=True, lang='en-US')), ' が 0.59 高い。Sim への fine-tuning なし'],
])
add_picture(s, 'sf_tasks', 1.4, 3.3, h=3.5)
add_picture(s, 'sf_scatter', 5.3, 3.3, h=3.5)
add_box(s, 9.2, 3.5, 3.7, 1.5, '', fill=BLUE_F, line=BLUE_L,
        lines=[('opt', ['サブタスク単位の評価'], dict(size=16, bold=True)),
               ('opt', [('r', dict(italic=True, lang='en-US')), ' 0.90 → 0.95'], dict(size=20, bold=True, color=RED)),
               ('opt', ['長期タスクの弱点段階も特定'], dict(size=14, bold=False))])
add_box(s, 9.2, 5.2, 3.7, 1.5, '', fill=BLUE_F, line=BLUE_L,
        lines=[('opt', ['モデルの得手不得手も可視化'], dict(size=16, bold=True)),
               ('opt', ['GR00T N1.7：精密把持に強い'], dict(size=14, bold=False)),
               ('opt', ['π0.5：言語追従に強い'], dict(size=14, bold=False))])
caption(s, 1.4, 6.85, 8, 'Fig. 4 in Ranawaka et al., 2026')

s = new_slide(CAT1, '結果②：Sim→Real 学習と Cousins の効果', notes=(
    '[J] 2つ目の結果、Sim-to-Real学習です。SimFoundryのデータのみで学習したポリシーが実機にゼロショットで転移し、YAMのPot on Stoveで99%、DROIDのStack Dishwareで100%に達しています。'
    'YAMではスクラッチ学習のフローマッチングポリシー、DROIDではπ0.5のDROIDチェックポイントをSimデモでfine-tuningしています。'
    '図はCousinsの効果です。Aのobject cousinsは未知物体への頑健性を上げ、Pot on Stoveの未知物体で50ポイント改善します。Bのscene cousinsは配置汎化で、Twinのみでは0%だったcousin配置で16%、Twin配置でも最大28ポイント改善。'
    'Cのtask cousinsは、総デモ数を固定して一部を関連タスクに置き換えると、むしろ目標タスクの成功率が上がり、Throw Away Trashで60ポイント改善しています。'
    '13タスクのマルチタスクデータでπ0.5を微調整すると、未学習タスクでも29%の成功率を示し、実機で最大18%改善しました。'
))
add_bullets(s, [
    'Sim データのみで学習 → 実機ゼロショットで成功率 99–100%',
    [('Object / Scene / Task cousins', dict(lang='en-US')), ' で実機成功率が平均 ', ('+17 / +21 / +40%', dict(bold=True, color=RED))],
    '13タスクの Sim データで π0.5 を微調整 → 未学習タスクでも 29%',
])
add_picture(s, 'sf_fig5', 0.5, 3.55, w=12.3)
caption(s, 0.5, 6.5, 12, 'Fig. 5 in Ranawaka et al., 2026   A: 物体の変種で未知物体に頑健   B: 配置の変種で新配置に転移   C: 関連タスクのデモが目標タスクを押し上げる', size=12)

s = new_slide(CAT1, '結果③：再構成の品質とコスト', notes=(
    '[J] システム自体の分析です。12シーンでの幾何評価では、全自動のゼロショットでF1スコア0.81から0.92で、SAM3Dの0.66から0.71を上回ります。'
    '再構成は1物体あたり約5分で、さらに1物体3分の手作業調整を加えるとF1は0.93から0.99まで上がります。忠実度と手間をオンデマンドで交換できるわけです。'
    '図は上段が実世界、中段がDigital Twin、下段がDigital Cousinで、物体の形や配置が変わりつつ、タスク上の意味は保たれていることが分かります。'
    '制約としては、卓上シーン前提であること、各基盤モデルの失敗モードをそのまま継承することが挙げられています。'
))
add_bullets(s, [
    ['12シーンでゼロショット F1 ', ('0.81–0.92', dict(bold=True)), '（SAM3D：0.66–0.71）'],
    '1物体あたり約5分。+3分の手作業調整で F1 0.93–0.99',
    '制約：卓上シーン前提。基盤モデルの失敗モードを継承',
])
add_picture(s, 'sf_fig3', 0.5, 3.4, w=12.3)
caption(s, 0.5, 6.78, 12, 'Fig. 3 in Ranawaka et al., 2026   上：実世界   中：Digital Twin   下：Digital Cousin', size=12)

# ================================================================== SLIDE: papers (#2)
papers_slide(1, (
    '[J] 2本目、VLS、Vision-Language Steeringです。一言で言うと「凍結した拡散／フローポリシーのサンプリング過程を、VLMが書いた微分可能な報酬で推論時に操舵する、訓練不要の枠組み」です。'
    'キーワードは3つ、Classifier guidance、VLMによるプログラム的報酬生成、そして勾配ベースの精緻化と勾配不要の再サンプリングの組み合わせです。'
))

# ================================================================== VLS slides
CAT2 = [('2. ', {}), ('VLS', dict(bold=True, link=PAPERS[1]['url']))]

s = new_slide(CAT2, '背景：生成ポリシーはなぜ分布外で失敗するか', notes=(
    '[J] 背景です。拡散モデルやフローマッチングに基づく模倣学習ポリシーは、分布内では高い性能を示します。'
    'しかし、同じタスクを障害物の近くで行う、支持面がずれる、少し散らかっている、といった軽微な変化で失敗します。'
    '著者らの主張は、これは動作スキルが欠けているのではなく、行動生成が学習時の空間配置やタスク指定と強く結び付いているからだ、というものです。'
    '図の左のように学習済みポリシーは分布内では固定の振る舞いをし、中央のように新しい物体・シーン・指示に対しては対応できません。'
    '再学習や微調整はコストが高いだけでなく、既にある能力を学び直すことになり概念的にもずれています。そこで「推論時の制御問題」として捉え直す、というのがVLSの立場です。'
))
add_bullets(s, [
    'Diffusion / Flow-matching ポリシーは分布内では高性能',
    '❌ スキルはあるのに、学習時の配置・指示と結び付いて使えない',
    '❌ 再学習は高コスト → 本質は「推論時の制御問題」',
])
add_picture(s, 'vls_fig1', 2.0, 3.35, w=9.3)
caption(s, 2.0, 7.0, 8, 'Fig. 1 in Liu et al., 2026')

s = new_slide(CAT2, '問題設定：Classifier Guidance による操舵', notes=(
    '[J] 問題設定です。凍結したベースポリシーπ*のdenoising過程に、分布外条件の対数尤度の勾配gを注入するClassifier guidanceの形で操舵します。'
    '拡散ならノイズ予測、フローなら速度場に、誘導強度λを掛けた勾配を足すだけです。'
    '難しいのはgのモデル化です。実世界の条件は単なるクラスラベルではなく、空間的・意味的な制約の構造を持ち、しかも行動軌道に対して密で情報量のある勾配を返す必要があります。'
    '既存の操舵手法を整理すると、学習済みの価値関数を使うもの、ダイナミクスモデルを使うもの、人間やVLMに候補を選ばせるものがありますが、それぞれ批評家の嗜好への偏り、モデル誤差とコスト、離散で疎な信号という課題があります。'
    'VLSは、VLMに微分可能な代理スコアRを「プログラムとして書かせる」ことで、訓練不要で密な勾配を得ます。'
))
add_bullets(s, [
    ['凍結ポリシー ', ('π*', dict(lang='en-US')), ' の denoising に勾配 ', ('g', dict(italic=True, lang='en-US')), ' を注入（classifier guidance）'],
    ['課題：条件 ', ('(o, l)', dict(italic=True, lang='en-US')), ('OOD', dict(size=14, lang='en-US')), ' は空間的・意味的な制約の構造を持つ'],
    ['→ 微分可能な代理スコア ', ('R', dict(italic=True, lang='en-US')), ' を VLM に', ('「プログラムとして書かせる」', dict(bold=True, color=RED))],
])
add_eq(s, 'vls_guid', 0.9, 3.4, 7.6)
add_eq(s, 'vls_surr', 0.9, 4.0, 5.6)
rows = [
    ('既存の操舵手法', '誘導信号', '課題'),
    ('V-GPS / VGD', '学習済み価値関数・Q', '批評家の嗜好にポリシーが引きずられる'),
    ('DynaGuide / Latent Policy Barrier', '学習済みダイナミクスモデル', 'モデル誤差・ロールアウトの計算コスト'),
    ('ITPS / FOREWARN / Do-What-You-Say', '人間・VLM による候補の選択', '信号が離散・疎でサンプル効率が悪い'),
    ('VLS（本論文）', 'VLM が書いた微分可能な報酬関数', '訓練不要・密な勾配。推論コストが課題'),
]
tbl = s.shapes.add_table(len(rows), 3, inch(0.9), inch(4.7), inch(11.6), inch(2.1)).table
tbl.columns[0].width = inch(3.9); tbl.columns[1].width = inch(3.4); tbl.columns[2].width = inch(4.3)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        c = tbl.cell(i, j)
        c.text = ''
        p = c.text_frame.paragraphs[0]
        add_runs(p, val, size=14, bold=(i == 0 or i == len(rows) - 1), color=('FFFFFF' if i == 0 else None))
        c.margin_top = c.margin_bottom = inch(0.03)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor.from_string(NAVY if i == 0 else (GREEN_F if i == len(rows) - 1 else ('F2F2F2' if i % 2 else 'FFFFFF')))
caption(s, 8.7, 3.45, 4.5, 'Eq. (5), (6), (7) in Liu et al., 2026', size=11)

s = new_slide(CAT2, '手法：VLS パイプライン', notes=(
    '[J] VLSのパイプラインは3つの要素からなります。'
    '1つ目はGroundingで、RGB-D観測と指示からVLMがタスク関連物体を特定し、SAMでマスク、DINOv2で密な特徴を取り、深度で3D点群に戻してクラスタリングし、タスク関連の3Dキーポイント集合Pを作ります。分布外の入力が、こうして幾何的な足場に圧縮されます。'
    '2つ目は報酬生成で、VLMにタスクをS個の段階に分解させ、各段階についてキーポイントと行動系列を引数にとる報酬関数をPyTorchの微分可能なテンソル演算で書かせます。例えば目標キーポイントまでの距離の二乗和にマイナスを付けたものです。VLM自体は計算グラフの外にあり、勾配は生成された関数を通して逆伝播します。'
    '3つ目が報酬誘導denoisingループと閉ループの段階切替で、次のスライドで説明します。'
))
add_bullets(s, [
    [('① Grounding', dict(bold=True, lang='en-US')), '：SAM + DINOv2 + 深度 → タスク関連 3D キーポイント ', ('P', dict(italic=True, lang='en-US'))],
    [('② Reward', dict(bold=True, lang='en-US')), '：VLM が段階ごとの報酬を PyTorch 関数として出力'],
    [('③ Denoising', dict(bold=True, lang='en-US')), '：報酬勾配で生成を補正し、報酬の推移で段階を切替'],
])
add_picture(s, 'vls_fig2', 0.5, 3.45, w=7.6)
add_box(s, 8.5, 3.5, 4.4, 1.55, '', fill=YELLOW_F, line=YELLOW_L, align=PP_ALIGN.LEFT,
        lines=[('opt', ['報酬関数の例（VLM 出力）'], dict(size=15, bold=True)),
               ('opt', ['目標キーポイントと行動系列の距離の二乗和にマイナス → 近づくほど高報酬'], dict(size=13, bold=False)),
               ('opt', ['距離・内積・ソフト制約の組合せのみ許可し微分可能性を保証'], dict(size=13, bold=False))])
add_box(s, 8.5, 5.2, 4.4, 1.55, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', ['VLM は計算グラフの外'], dict(size=15, bold=True)),
               ('opt', ['VLM の呼び出しは報酬生成と段階切替の判断のみ。勾配は生成された関数を通して行動へ逆伝播'], dict(size=13, bold=False))])
caption(s, 0.5, 7.0, 8, 'Fig. 2 in Liu et al., 2026')

s = new_slide(CAT2, '手法：Reward-Guided Denoising と閉ループ制御', notes=(
    '[J] denoisingループの中身です。まずバッチでB個の行動候補を初期化し、初期段階ではRBF斥力を勾配として注入して候補同士を引き離し、ベースポリシーの狭いモードへの早期崩壊を防ぎます。'
    '次に段階sの報酬勾配を注入して精緻化します。拡散ポリシーでは1ステップあたり4回の内部更新を行い、MCMC風に安定化させます。'
    'さらに勾配不要の再サンプリングとして、Feynman-Kac steeringの考え方で報酬の指数を粒子の重みとし、多項再サンプリングで高報酬の粒子を複製、制約違反の候補を間引きます。'
    '閉ループ制御では、各段階の最初のチャンクの報酬を基準にした相対値で誘導強度λを適応させ、ずれが大きいときは強く、仕上げに近づくとベースポリシーに任せます。'
    '段階遷移はSchmitt triggerのヒステリシスで、2つの閾値を使って前進・維持・強化を判定し、境界付近の振動や早すぎる遷移を防ぎます。遷移時にはVLMが実行結果を解釈して次の報酬関数を選びます。'
))
add_bullets(s, [
    [('多様化', dict(bold=True)), '：RBF 斥力　', ('精緻化', dict(bold=True)), '：報酬勾配を MCMC 風に複数回注入'],
    [('再サンプリング', dict(bold=True)), '：Feynman–Kac 重みで高報酬の粒子を複製'],
    [('閉ループ', dict(bold=True)), '：誘導強度 λ を適応、Schmitt trigger で段階を遷移'],
])
add_picture(s, 'vls_loop', 0.5, 3.4, w=12.3)
labels = [('多様化（RBF 斥力）', 'vls_rbf', 0.5, 3.9), ('再サンプリング（FK 重み）', 'vls_fk', 4.7, 4.2), ('適応的誘導強度', 'vls_lam', 9.2, 3.5)]
for lab, eqn, x, w in labels:
    add_text(s, x, 5.45, w, 0.35, [lab], size=14, bold=True, color=NAVY)
    add_eq(s, eqn, x, 5.85, w)
caption(s, 0.5, 7.0, 12, 'Fig. 2 (bottom), Eq. (8)–(10) in Liu et al., 2026')

s = new_slide(CAT2, '結果①：Sim（LIBERO-PRO / CALVIN）', notes=(
    '[J] シミュレーション結果です。LIBERO-PROはLIBEROに物体配置とタスク指定の摂動を加えた分布外ベンチマークで、OpenVLAやπ0はほぼ0%、π0.5のLeRobot版でも23.7%です。'
    'この凍結π0.5にVLSを付けるだけで36.8%、13ポイント改善します。VLMバックボーンを持つVLAでも、ロボットデータでの後学習が空間推論を学習文脈に絡めてしまう、というのが著者らの解釈です。'
    'CALVINではDiffusion Policyをベースに、可動物体で94%、ベースの7.4倍、関節物体で87%、9.6倍を達成し、DynaGuideやITPSを15から25ポイント上回ります。'
    'Ablationでは勾配誘導を外すと17%に崩壊し、密で軌道微分可能な誘導が主因だと分かります。FK再サンプリングとRBFは成功率への影響は小さいものの、エピソード長や安定性を改善します。'
    '右下はサンプル数のスケーリングで、サンプルを増やすと性能は上がる一方で推論時間が1.2秒を超え、計算と性能のトレードオフになります。'
))
add_bullets(s, [
    [('LIBERO-PRO', dict(bold=True, lang='en-US')), '：凍結 π0.5 + VLS で ', ('23.7% → 36.8%', dict(bold=True, color=RED)), '（+13 pt）'],
    [('CALVIN', dict(bold=True, lang='en-US')), '：可動物体 94%（7.4倍）、関節物体 87%（9.6倍）'],
    [('Ablation', dict(bold=True, lang='en-US')), '：勾配誘導を外すと 17% に崩壊。FK / RBF は効率に寄与'],
])
add_picture(s, 'vls_tab1', 0.5, 3.5, w=7.4)
add_picture(s, 'vls_fig3', 0.5, 5.1, w=7.4)
add_picture(s, 'vls_abl', 8.2, 3.5, w=4.8)
add_picture(s, 'vls_scale', 8.2, 5.1, w=4.8)
caption(s, 0.5, 6.95, 7, 'Table I, Fig. 3 in Liu et al., 2026')
caption(s, 8.2, 6.5, 4.8, 'Fig. 4 in Liu et al., 2026（左：Ablation、右：サンプル数のスケーリング）')

s = new_slide(CAT2, '結果②：実機（Franka）と限界', notes=(
    '[J] 実機はFranka Emikaで、凍結したπ0.5をベースにしています。'
    '分布内タスクは指示された皿にオレンジを置く、バナナも加えて物体と皿の両方を選ぶ、というもので、平均成功率は50%から69%、19ポイント改善しました。'
    '分布外では、皿を未知の黄色い皿に変える見た目の変化、皿の位置を入れ替える位置の変化、バナナを未知のマグに置き換える物体の変化を試しています。ベースラインは大きく落ち、特にマグでは0%ですが、VLSは40%で、平均は42%から69%です。'
    '限界として、バッチサンプリング、MCMC、再サンプリングによる推論オーバーヘッドが大きく、図4ではチャンクあたり約1秒でした。進捗を考慮した報酬生成と効率化が今後の課題とされています。'
))
add_bullets(s, [
    [('分布内', dict(bold=True)), '：物体選択 + 配置タスクで ', ('50% → 69%', dict(bold=True, color=RED)), '（+19 pt）'],
    [('分布外', dict(bold=True)), '：色変更・位置交換・未知物体でも安定（マグ 0% → 40%）'],
    [('限界', dict(bold=True)), '：バッチ + MCMC + 再サンプリングで推論 約1 秒/チャンク'],
])
add_picture(s, 'vls_fig5', 0.5, 3.45, w=12.3)
caption(s, 0.5, 7.0, 8, 'Fig. 5 in Liu et al., 2026')

# ================================================================== SLIDE: papers (#3)
papers_slide(2, (
    '[J] 3本目、Code-as-Monitor、略してCaMです。CVPR 2025の論文です。一言で言うと「失敗の事後検知と事前予防を時空間制約充足問題として統一し、VLMが生成したコードでリアルタイムに監視する枠組み」です。'
    'キーワードは3つ、ReactiveとProactiveの統一、制約要素という幾何抽象化、そして1サブゴールにつき1回だけのVLM呼び出しです。'
))

# ================================================================== CaM slides
CAT3 = [('3. ', {}), ('Code-as-Monitor', dict(bold=True, link=PAPERS[2]['url']))]

s = new_slide(CAT3, '背景：Reactive と Proactive の失敗検知', notes=(
    '[J] 背景です。ロボットの失敗検知には2つのモードがあります。Reactiveは失敗が起きた後に検知するもので、図の(a)ではロブスターが鍋から飛び出して落ちたことを検知します。'
    'Proactiveは予見できる失敗を事前に防ぐもので、(b)では鍋が傾いたことを検知して落ちる前に修正します。これにはリアルタイムで高精度な監視が必要です。'
    '既存研究はLLMやVLMにVQAとして失敗を問う形が主流ですが、計算コストが高くて遅く、単一画像からの3D時空間理解が粗いという問題があります。Proactiveな検知はほとんど未開拓で、事前に定義した失敗に限られていました。'
    'CaMは両方を1つの枠組みで、開集合の失敗に対して、リアルタイムに行うことを目指します。(c)のように開ループのポリシーと組み合わせて閉ループ化できます。'
))
add_bullets(s, [
    [('Reactive', dict(bold=True, lang='en-US')), '：失敗が起きた「後」に検知（例：ロブスターが落ちた）'],
    [('Proactive', dict(bold=True, lang='en-US')), '：予見できる失敗を「前」に防ぐ（例：鍋の傾きを修正）'],
    '❌ VLM-VQA 型の検知は遅く 3D 理解が粗い。Proactive は未開拓',
])
add_picture(s, 'cam_fig1', 1.5, 3.3, w=10.3)
caption(s, 1.5, 7.05, 8, 'Fig. 1 in Zhou et al., 2025')

s = new_slide(CAT3, '手法：Code-as-Monitor の全体像', notes=(
    '[J] CaMの全体像です。鍵となる定式化は、ReactiveとProactiveの両方を時空間制約充足問題として統一することです。'
    'Constraint GeneratorであるGPT-4oが、タスク指示、前のサブゴール、失敗フィードバック、多視点観測から、次のサブゴールと2種類の制約を生成します。'
    '実行中に保つべき制約C_d、例えば「パンは鍋の中に留まる」「鍋は水平を保つ」と、完了時に満たすべき制約C_u、例えば「鍋はコンロの真上にある」です。前者がProactive、後者がReactiveに対応します。'
    'Constraint Painterは各制約に対応する制約要素を画像に描画し、Constraint Monitorがそれを視覚プロンプトとしてGPT-4oに監視コードを書かせます。'
    '重要なのは、VLMの呼び出しはサブゴール開始時の1回だけで、実行中はCoTrackerで要素を追跡しながらコードを評価するだけなので、リアルタイムに動くことです。違反が出れば即座にポリシーを止め、理由を返して再計画します。'
))
add_bullets(s, [
    'Reactive / Proactive を「時空間制約充足問題」として統一',
    [('Generator', dict(bold=True, lang='en-US')), '（GPT-4o）→ ', ('Painter', dict(bold=True, lang='en-US')), '（描画）→ ', ('Monitor', dict(bold=True, lang='en-US')), '（コード）'],
    'VLM 呼び出しはサブゴール開始時の1回。以後はコードで常時監視',
])
add_picture(s, 'cam_fig2', 0.5, 3.45, w=8.3)
add_eq(s, 'cam_gen', 9.0, 3.6, 4.0)
add_box(s, 9.0, 4.3, 4.0, 1.2, '', fill=ORANGE_F, line=ORANGE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', ['Proactive = 実行中の制約 ', ('C', dict(italic=True, lang='en-US')), ('d', dict(size=12, lang='en-US'))], dict(size=14, bold=True)),
               ('opt', ['鍋の把持を維持、パンは鍋の中、鍋は水平'], dict(size=13, bold=False))])
add_box(s, 9.0, 5.6, 4.0, 1.2, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', ['Reactive = 完了時の制約 ', ('C', dict(italic=True, lang='en-US')), ('u', dict(size=12, lang='en-US'))], dict(size=14, bold=True)),
               ('opt', ['鍋がコンロの真上にある'], dict(size=13, bold=False))])
caption(s, 0.5, 7.0, 8, 'Fig. 2, Eq. (1) in Zhou et al., 2025')

s = new_slide(CAT3, '手法：制約要素（Constraint Element）と ConSeg', notes=(
    '[J] CaMのもう1つの中核が制約要素です。制約に関係する物体や部位を、点・線・面といったコンパクトな幾何要素に抽象化します。'
    '例えば「鍋は水平を保つ」なら鍋の面を3点で表し、法線とz軸の角度を計算すれば良い。見た目やテクスチャといった無関係な情報を捨てるので追跡が容易で、未知の物体やシーンにも汎化します。'
    'パイプラインは、制約文からConSegでインスタンスと部位のマスクを得て、深度で3D点群に投影し、要素タイプに応じてボクセル化・クラスタリングして代表点を選び、点を連結して要素にします。それを多視点画像に番号付きで描き込みます。'
    'ConSegはLISAをベースに、LLaVAとSAMのエンコーダ・デコーダを凍結したままLoRAで学習し、制約文から直接マスクと要素タイプを出力します。'
    '学習データはBridgeData V2からGPT-4oでサブゴール・制約・物体部位の対応を自動生成し、Grounded SAMとSemantic SAMでマスクを作って人手で確認した、1万軌道・22万枚のデータセットです。'
))
add_bullets(s, [
    '物体 / 部位を「点・線・面」に抽象化 → 追跡が容易、見た目に依存しない',
    [('ConSeg', dict(bold=True, lang='en-US')), '：LISA ベース（LLaVA + SAM + LoRA）。制約文 → マスク'],
    '学習データ：BridgeData V2 を GPT-4o で自動注釈（10,181 軌道）',
])
add_picture(s, 'cam_fig3', 0.5, 3.45, w=12.3)
add_text(s, 0.6, 6.15, 1.4, 0.4, [[('ConSeg:', dict(bold=True, lang='en-US'))]], size=16, color=NAVY)
add_eq(s, 'cam_seg', 2.0, 6.17, 7.4)
caption(s, 9.6, 6.25, 3.5, 'Fig. 3, Eq. (2) in Zhou et al., 2025')

s = new_slide(CAT3, '手法：Monitor Code の生成と実行', notes=(
    '[J] 監視コードの実際です。制約要素を描き込んだ多視点画像と、次のサブゴール、制約文をGPT-4oに与えて、要素の3D位置を引数に取る関数を書かせます。'
    'コードはNumPyで角度や距離を計算し、閾値を超えたら失敗を示すブール値と、理由を説明する文字列を返します。例では鍋の面の法線とz軸の角度が15度を超えたら「鍋が水平でない」と返しています。'
    '現在位置だけでなく履歴も入力に含めるので、「2cm動かす」「180度回す」のような精度が要る条件も監視できます。これはVLMに画像を直接問うReactive手法では不可能でした。'
    '閾値はよくあるタスクは知識ベースから、未知のタスクはVLMの知識で設定します。生成直後に現在の状態を入力としてif-else分岐を全て通す白箱テストを行い、エラーがあれば再生成します。'
    '実行中は要素を追跡しつつコードを評価し、Falseが返れば即座にポリシーを停止し、理由をフィードバックとしてConstraint Generatorに渡して再計画します。'
))
add_bullets(s, [
    '入力：要素の 3D 位置（現在 + 履歴）→ 角度・距離を計算 → (bool, 理由)',
    '閾値は知識ベース or VLM。生成直後に全分岐をテスト、失敗なら再生成',
    '違反を検知 → ポリシーを即停止、理由を返して再計画',
])
add_picture(s, 'cam_code', 0.5, 3.5, w=8.3)
flow = [('サブゴール開始：VLM 呼び出しは1回', ORANGE_F, ORANGE_L), ('要素を追跡（CoTracker）', BLUE_F, BLUE_L),
        ('コードを毎フレーム評価', GREEN_F, GREEN_L), ('False → 停止・理由付きで再計画', PINK_F, PINK_L)]
y0 = 3.5
for i, (t, f, l) in enumerate(flow):
    add_box(s, 9.2, y0 + i * 0.85, 3.8, 0.6, t, fill=f, line=l, size=14)
    if i < len(flow) - 1:
        add_arrow(s, 10.95, y0 + i * 0.85 + 0.6, 0.3, 0.25, shape=MSO_SHAPE.DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
caption(s, 0.5, 6.75, 8, 'Monitor code example from Fig. 2 in Zhou et al., 2025')

s = new_slide(CAT3, '結果①：Sim（CLIPort / OmniGibson / RLBench）', notes=(
    '[J] シミュレーション結果です。3つのシミュレータで、それぞれ異なるロボット・エンドエフェクタ・ポリシーを使い、外乱を加えて失敗を誘発しています。'
    'CLIPortの積み木積みでは、吸着が外れる確率0.3や配置ノイズ3cmといった強い外乱下で、DoReMiの76.7%に対しCaMは88.3%、VQAを繰り返すDoReMiは単一画像の3D理解が粗く誤判定が増えます。'
    'ブロックの半分だけを掃くタスクでは、要素の点を数えることで16.7%から75%に跳ね上がりました。'
    'OmniGibsonでは、点・線・面レベルの外乱を用意し、面レベルの外乱であるお茶注ぎはCaMだけが検知できました。コード生成はサブゴールごとに1回なので、実行時間は34.8%、トークンは52.2%削減されています。'
    'RLBenchでは学習データに無い関節物体や工具使用のタスクでも、ARPの91.3%から97.1%に改善し、汎化性を示しています。'
))
add_bullets(s, [
    [('CLIPort', dict(bold=True, lang='en-US')), '：強い外乱下で ', ('76.7% → 88.3%', dict(bold=True, color=RED)), '、Sweep Half 16.7 → 75.0%'],
    [('OmniGibson', dict(bold=True, lang='en-US')), '：面レベル外乱は CaM のみ検知。時間 −35%、token −52%'],
    [('RLBench', dict(bold=True, lang='en-US')), '：未学習の関節物体・工具使用でも 91.3% → 97.1%'],
])
add_picture(s, 'cam_tab2', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab1', 0.5, 5.0, w=5.4)
add_picture(s, 'cam_tab9', 6.3, 5.3, w=6.5)
caption(s, 0.5, 6.85, 12, 'Table 1, 2, 9 in Zhou et al., 2025（DRM: DoReMi, IM: Inner Monologue）')

s = new_slide(CAT3, '結果②：実機（UR5 + Leap Hand）と Ablation', notes=(
    '[J] 実機はUR5とLeap Hand、ポリシーは開ループの把持生成モデルDexGraspNet 2.0です。ConSegはSimで微調整していないベースモデルをそのまま使っています。'
    '把持中に物体を動かす、移動中に手から取り除く、という外乱下で、変形物体や透明物体を含む4種類の物体でCaMは90%以上、DoReMiより約20ポイント高く、実行時間も短い。'
    '雑然としたシーンで「果物に近い順に動物を掴む」という推論を要する長期タスクでは、人が馬や梨を動かすと把持順が変わりますが、CaMは距離を監視して目標を切り替え、DoReMiが0%のところ90%を達成しました。開ループポリシーが実質的に閉ループ化されています。'
    'Ablationでは、多視点を外すと65%から40%、制約認識セグメンテーションをDINOv2の意味点に置き換えると42.5%、点の連結を外すと55%に落ち、各要素が重要だと分かります。実機でも要素化しないと60%から20%に落ちます。'
    '限界としては、VLMの幻覚、変位を伴わない力関連の失敗を捉えにくいこと、音や流体のような他のモダリティを扱えないことが挙げられています。'
))
add_bullets(s, [
    '開ループ把持ポリシーに CaM を付けて閉ループ化：外乱下で 90% 超',
    ['推論を要する長期タスク：DoReMi 0% → ', ('CaM 90%', dict(bold=True, color=RED))],
    'Ablation：多視点・制約認識 Seg・点の連結が重要（65% → 40–55%）',
])
add_picture(s, 'cam_fig5', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab4', 0.5, 5.75, w=5.2)
add_picture(s, 'cam_tab6', 6.3, 5.75, w=5.0)
add_text(s, 11.45, 5.8, 1.7, 1.0, [[('限界：', dict(bold=True))], ['VLM の幻覚'], ['力の失敗は捉えにくい']], size=11, color=MUTED, spacing=100)
caption(s, 0.5, 7.05, 12, 'Fig. 5, Table 4, Table 6 in Zhou et al., 2025')

# ================================================================== Insights
s = new_slide('Insights', 'まとめ：凍結ポリシーを「外側」から賢くする', notes=(
    '[J] まとめです。3本に共通するのは、VLMや基盤モデルをポリシーの外側に置き、本体は再学習しないことです。これにより、より良いモデルが出たときに差し替えられるモジュール性が得られます。'
    '特にVLSとCaMは同じ型をしていると感じました。どちらもVLMが「幾何要素とそれを使うコード」を書きます。VLSではそれを報酬として行動生成を誘導し、CaMでは監視条件として実行を検査する。つまり同じコードを、生成時のガイドと実行時のモニタの両方に使える可能性があります。'
    'SimFoundryのDigital Cousinsは、こうした推論時の機構を安全に、大量に、分布外条件で検証する土台になります。'
    '一方で共通の課題はレイテンシとVLMの幻覚です。VLSはチャンクあたり約1秒、CaMもサブゴールごとにVLMを呼びます。'
    '私自身の研究の観点からは、Simで検証済みの報酬・監視コードを資産として蓄積し、実機では再利用するだけにすることで、推論時のVLM依存とレイテンシを下げられるのではないかと考えています。'
    'ご清聴ありがとうございました。質問をお受けします。'
))
add_bullets(s, [
    '3本とも VLM / 基盤モデルをポリシーの外側に置き、本体は再学習しない → モジュール性と差し替え可能性',
    [('VLS と CaM は同じ型：VLM が「幾何要素 + コード」を書く。', dict()), ('報酬として生成を誘導 / 監視条件として実行を検査', dict(bold=True)), ' → 統一できる可能性'],
    'SimFoundry の Digital Cousins は、こうした推論時機構を分布外条件で安全・大量に検証する土台になる',
    [('私見：共通課題はレイテンシ（VLS 約1 s/チャンク、CaM の VLM 呼び出し）と VLM の幻覚。', dict()), ('Sim で検証済みの「コード資産」を蓄積・再利用する', dict(bold=True, color=RED)), '方向が有望'],
], size=20, spacing=130)
# bottom diagram (same as slide 3, compact)
boxes2 = [(0.9, BLUE_F, BLUE_L, 'SimFoundry', '配備前：Sim で評価・学習'),
          (5.0, GREEN_F, GREEN_L, 'VLS', '推論時：報酬で生成を操舵'),
          (9.1, ORANGE_F, ORANGE_L, 'Code-as-Monitor', '実行中：コードで監視・予防')]
for x, f, l, name, sub in boxes2:
    add_box(s, x, 5.5, 3.4, 0.95, '', fill=f, line=l,
            lines=[('opt', [(name, dict(lang='en-US'))], dict(size=18, bold=True)), ('opt', [sub], dict(size=13, bold=False))])
add_arrow(s, 4.4, 5.75, 0.5, 0.45)
add_arrow(s, 8.5, 5.75, 0.5, 0.45)
add_text(s, 0.9, 6.55, 11.6, 0.4, [['VLM が書く「幾何要素 + コード」を、生成のガイドにも実行のモニタにも使う、という統一的な見方']], size=14, color=NAVY, align=PP_ALIGN.CENTER)

prs.save(OUT)
print('saved', OUT, 'slides:', len(prs.slides))
