# -*- coding: utf-8 -*-
"""Build the survey deck from draft_<lang>.md on top of the reference deck's master/layouts.

usage: python3 build2.py ja/draft_ja.md
"""
import re
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
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
DRAFT = sys.argv[1] if len(sys.argv) > 1 else S + '/ja/draft_ja.md'
LANG = 'en' if DRAFT.endswith('draft_en.md') else 'ja'
NOTE_TAG = '[E] ' if LANG == 'en' else '[J] '
OUT = ROOT + ('/20261105_KaneyoshiHiratsuka_SurveySlide_EN.pptx' if LANG == 'en' else '/20261105_KaneyoshiHiratsuka_SurveySlide.pptx')


def t(ja, en):
    return en if LANG == 'en' else ja


# ------------------------------------------------------------------ draft parsing
def parse_draft(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    deck = dict(title=None, subtitle=None, notes='', slides={})
    cur = None
    for ln in lines:
        if ln.startswith('# ') and deck['title'] is None:
            deck['title'] = ln[2:].strip(); continue
        m = re.match(r'^## スライド(\d+)\s+(.*)$', ln) or re.match(r'^## Slide (\d+)\s+(.*)$', ln)
        if m:
            cur = dict(bullets=[], notes='', head=m.group(2).strip())
            deck['slides'][int(m.group(1))] = cur; continue
        if ln.startswith('ノート:') or ln.startswith('Notes:'):
            txt = ln.split(':', 1)[1].strip()
            if cur is None: deck['notes'] = txt
            else: cur['notes'] = txt
            continue
        if ln.startswith('- '):
            if cur is not None: cur['bullets'].append(ln[2:].strip())
            continue
        if cur is None and ln.strip() and deck['title'] and deck['subtitle'] is None:
            deck['subtitle'] = ln.strip()
    return deck


deck = parse_draft(DRAFT)
DECK_TITLE = deck['title']


def slide_title(n):
    head = deck['slides'][n]['head']
    m = re.match(r'^(\S+?)[:：]?\s+(.*)$', head)
    return m.group(2).strip() if m else head


prs = Presentation(REF)
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)
LAYOUT_TITLE = prs.slide_layouts[0]
LAYOUT_CONTENT = prs.slide_layouts[1]

BLUE_F, BLUE_L = 'DAE8FC', '6C8EBF'
GREEN_F, GREEN_L = 'D5E8D4', '82B366'
ORANGE_F, ORANGE_L = 'FFE6CC', 'D79B00'
GRAY_F, GRAY_L = 'EDEDED', '7F7F7F'
PINK_F, PINK_L = 'F8CECC', 'B85450'
YELLOW_F, YELLOW_L = 'FFF2CC', 'D6B656'
PURPLE_F, PURPLE_L = 'E1D5E7', '9673A6'
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


def inch(v):
    return int(round(v * 914400))


def has_jp(t):
    return any(ord(ch) > 0x2E7F for ch in t)


def _style_run(run, size=24, bold=False, color=None, italic=False, lang=None, font='Arial', underline=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if font:
        run.font.name = font
    if underline is not None:
        run.font.underline = underline
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if lang is None:
        lang = 'ja-JP' if has_jp(run.text) else 'en-US'
    rPr = run._r.get_or_add_rPr()
    rPr.set('lang', lang)
    rPr.set('altLang', 'en-US' if lang == 'ja-JP' else 'ja-JP')


def add_runs(p, segments, size=24, color=None, bold=False, lang=None):
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


def set_bullet(p, level=0, spacing=150, char=None):
    pPr = p._p.get_or_add_pPr()
    if level == 0:
        pPr.set('marL', '342900'); pPr.set('indent', '-342900')
    else:
        pPr.set('marL', '800100'); pPr.set('indent', '-285750'); pPr.set('lvl', '1')
    lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
    etree.SubElement(lnSpc, qn('a:spcPct')).set('val', str(int(spacing * 1000)))
    buFont = etree.SubElement(pPr, qn('a:buFont'))
    buFont.set('typeface', 'Wingdings'); buFont.set('pitchFamily', '2'); buFont.set('charset', '2')
    etree.SubElement(pPr, qn('a:buChar')).set('char', char or ('n' if level == 0 else 'l'))


def set_line_spacing(p, spacing):
    pPr = p._p.get_or_add_pPr()
    lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
    etree.SubElement(lnSpc, qn('a:spcPct')).set('val', str(int(spacing * 1000)))


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


def add_text(slide, x, y, w, h, lines, size=18, color=None, bold=False, align=None, autofit=True,
             anchor=None, spacing=None, margin=None):
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
        add_runs(p, ln, size=size, color=color, bold=bold)
    return tb


# highlights: substrings rendered bold red, per slide number
HIGHLIGHT = {
    2: ['99%'],
    12: ['+17 / +21 / +40%'],
    21: ['76.7% → 88.3%'],
    23: [t('本手法 90%', 'CaM 90%')],
    30: ['23.7% → 36.8%'],
    32: ['50% → 69%'],
}


def rich_bullet(text, n):
    """Split a bullet into runs: bold leading label (before the first '：'), red highlights."""
    segs = []
    rest = text
    m = re.match(r'^([^：。]{1,22})：', text) or (LANG == 'en' and re.match(r'^([A-Za-z0-9①②③ ./+\-()]{1,28}):', text))
    if m and not has_jp(m.group(1)[:1]) or (m and m.group(1) in ('多様化は RBF の斥力、精緻化は報酬の勾配を MCMC 風に複数回注入',)):
        pass
    if m and (LANG == 'en' or not has_jp(m.group(1)) or m.group(1) in ('私見', '切り出し', '生成', '物体の変種', '配置の変種', 'タスクの変種', '制約', '事後検知（Reactive）', '事前予防（Proactive）', '① キーポイント抽出', '② 報酬生成', '③ 誘導付き生成')):
        segs.append((m.group(1), dict(bold=True)))
        rest = text[len(m.group(1)):]
    for h in HIGHLIGHT.get(n, []):
        if h in rest:
            a, b = rest.split(h, 1)
            segs.append(a); segs.append((h, dict(bold=True, color=RED))); rest = b
    segs.append(rest)
    return segs


def add_bullets(slide, n, size=24, spacing=150, items=None, x=0.886, y=1.269, w=12.313):
    items = items if items is not None else deck['slides'][n]['bullets']
    tb = textbox(slide, inch(x), inch(y), inch(w), inch(1.0))
    tf = tb.text_frame
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        set_bullet(p, level=0, spacing=spacing)
        add_runs(p, rich_bullet(it, n), size=size)
        units = sum(1.0 if ord(ch) > 0x2E7F else 0.52 for ch in it)
        limit = (w - 0.6) / (size / 72.0)
        if units > limit:
            print(f'  [wrap warning] slide {n}: {units:.0f} > {limit:.0f}: {it[:50]}')
    return tb


def add_picture(slide, name, x, y, w=None, h=None, folder=FIG):
    path = folder + name + ('' if name.endswith(('.png', '.jpg')) else '.png')
    kw = {}
    if w is not None: kw['width'] = inch(w)
    if h is not None: kw['height'] = inch(h)
    return slide.shapes.add_picture(path, inch(x), inch(y), **kw)


def add_eq(slide, name, x, y, w):
    return add_picture(slide, name, x, y, w=w, folder=EQ)


VID = S + '/videos/ready/'


def add_video(slide, name, x, y, w, caption_text=None, border=True):
    from PIL import Image
    poster = VID + name + '.jpg'
    iw, ih = Image.open(poster).size
    h = w * ih / iw
    mv = slide.shapes.add_movie(VID + name + '.mp4', inch(x), inch(y), inch(w), inch(h),
                                poster_frame_image=poster, mime_type='video/mp4')
    if border:
        mv.line.color.rgb = RGBColor.from_string('7F7F7F'); mv.line.width = Pt(0.75)
    if caption_text:
        add_text(slide, x, y + h + 0.05, w, 0.4, [caption_text], size=13, align=PP_ALIGN.CENTER, color=NAVY)
    return mv


def video_row(slide, items, y, total_w=12.3, x0=0.5, gap=0.3, max_h=None):
    """items: list of (name, caption). Lay videos in a row with equal height."""
    from PIL import Image
    ars = []
    for name, _ in items:
        iw, ih = Image.open(VID + name + '.jpg').size
        ars.append(iw / ih)
    h = (total_w - gap * (len(items) - 1)) / sum(ars)
    if max_h and h > max_h:
        h = max_h
    ws = [a * h for a in ars]
    x = x0 + (total_w - sum(ws) - gap * (len(items) - 1)) / 2
    for (name, cap), w in zip(items, ws):
        add_video(slide, name, x, y, w, caption_text=cap)
        x += w + gap
    return h


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


def add_arrow(slide, x, y, w, h, shape=MSO_SHAPE.RIGHT_ARROW, fill='FFC000', line='BF9000'):
    shp = slide.shapes.add_shape(shape, inch(x), inch(y), inch(w), inch(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = RGBColor.from_string(fill)
    shp.line.color.rgb = RGBColor.from_string(line)
    shp.shadow.inherit = False
    return shp


def caption(slide, x, y, w, text, size=11, color=MUTED, align=PP_ALIGN.LEFT):
    return add_text(slide, x, y, w, 0.3, [text], size=size, color=color, align=align)


def new_slide(category, title, title_size=36):
    slide_counter[0] += 1
    n = slide_counter[0]
    slide = prs.slides.add_slide(LAYOUT_CONTENT)
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    slide.shapes.add_picture(HEADER_IMG, 0, 0, Emu(12192000), Emu(635000))
    slide.shapes._spTree.append(etree.fromstring(SLDNUM_XML % (900, n)))
    tb = textbox(slide, 0, 0, 10048875, 400110)
    add_runs(tb.text_frame.paragraphs[0], category, size=20)
    tb = textbox(slide, 218047, 457201, 11543317, 646290)
    add_runs(tb.text_frame.paragraphs[0], title, size=title_size, bold=True)
    tu = sum(1.0 if ord(ch) > 0x2E7F else 0.58 for ch in title)
    if tu > 12.6 / (title_size / 72.0):
        print(f'  [title warning] slide {n}: {title}')
    notes = deck['slides'].get(n, {}).get('notes', '')
    if notes:
        slide.notes_slide.notes_text_frame.text = NOTE_TAG + notes
    return slide


def content_slide(category, n, size=24):
    s = new_slide(category, slide_title(n))
    add_bullets(s, n, size=size, spacing=150 if size >= 24 else 130)
    return s


# ------------------------------------------------------------------ papers
PAPERS = [
    dict(title='SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation',
         cite='N. Ranawaka, J. Wong et al., “SimFoundry: Modular and automated scene generation for policy learning and evaluation,” 2026. [Online]. Available: https://arxiv.org/abs/2606.28276',
         url='https://arxiv.org/abs/2606.28276'),
    dict(title='Code-as-Monitor: Constraint-aware Visual Programming for Reactive and Proactive Robotic Failure Detection',
         cite='E. Zhou, Q. Su, C. Chi et al., “Code-as-Monitor: Constraint-aware visual programming for reactive and proactive robotic failure detection,” 2024. [Online]. Available: https://arxiv.org/abs/2412.04455',
         url='https://arxiv.org/abs/2412.04455'),
    dict(title='VLS: Steering Pretrained Robot Policies via Vision–Language Models',
         cite='S. Liu et al., “VLS: Steering pretrained robot policies via vision–language models,” 2026. [Online]. Available: https://arxiv.org/abs/2602.03973',
         url='https://arxiv.org/abs/2602.03973'),
]
CAT1 = [('1. ', {}), ('SimFoundry', dict(bold=True, link=PAPERS[0]['url']))]
CAT2 = [('2. ', {}), ('Code-as-Monitor', dict(bold=True, link=PAPERS[1]['url']))]
CAT3 = [('3. ', {}), ('VLS', dict(bold=True, link=PAPERS[2]['url']))]


def papers_slide(active):
    slide = new_slide('Papers', DECK_TITLE)
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
        etree.SubElement(pPr, qn('a:buFont')).set('typeface', '+mj-lt')
        etree.SubElement(pPr, qn('a:buAutoNum')).set('type', 'arabicPeriod')
        on = (active is None) or (i == active)
        col = None if on else 'A6A6A6'
        r = p.add_run(); r.text = pp['title']
        _style_run(r, size=22, bold=True, color=col, lang='en-US')
        r.hyperlink.address = pp['url']
        br = etree.SubElement(p._p, qn('a:br'))
        r2 = p.add_run(); r2.text = pp['cite']
        _style_run(r2, size=14, color=col or '404040', lang='en-US')
        p._p.remove(br); r2._r.addprevious(br)
        sp = etree.SubElement(p._p, qn('a:endParaRPr')); sp.set('sz', '800'); sp.set('lang', 'en-US')
    return slide


# ================================================================== 1 title
slide_counter[0] += 1
s = prs.slides.add_slide(LAYOUT_TITLE)
for ph in list(s.placeholders):
    ph._element.getparent().remove(ph._element)
s.shapes.add_picture(HEADER_IMG, 0, 0, Emu(12192000), Emu(635000))
tb = textbox(s, 125835, 2950000, 11940330, 646331)
p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
add_runs(p, DECK_TITLE, size=36, bold=True)
p2 = tb.text_frame.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
add_runs(p2, deck['subtitle'], size=24, color=NAVY)
tb = textbox(s, 6015872, 4300000 if LANG == 'ja' else 4500000, 5392132, 707886)
p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
add_runs(p, 'Research Seminar 2026/11/05', size=20)
p = tb.text_frame.add_paragraph(); p.alignment = PP_ALIGN.RIGHT
add_runs(p, 'Kaneyoshi Hiratsuka', size=20)
s.notes_slide.notes_text_frame.text = NOTE_TAG + deck['notes']

# ================================================================== 2 background: VLM progress
s = content_slide('Background', 2, size=20)
add_picture(s, 'astra_case34.jpg', 0.7, 3.85, w=5.2)
add_picture(s, 'aspire_cost.png', 6.6, 3.75, w=5.5)
caption(s, 0.7, 6.78, 5.3, 'GPT-6 Astra plans Dual-ALOHA spatial-constraint puzzles (Awesome-Astra-Embodied-AI, case 34, Q. Wang)')
caption(s, 6.6, 6.82, 5.9, 'ASPIRE success vs. API cost on 10 LIBERO-Pro tasks (NVlabs/ASPIRE README, Oct. 2026)')

# ================================================================== 3 background: three areas
s = content_slide('Background', 3, size=20)
add_box(s, 0.6, 3.55, 12.1, 0.55, '', fill=PURPLE_F, line=PURPLE_L,
        lines=[('opt', [t('VLM（空間理解 ・ 推論 ・ コード生成）', 'VLM (spatial understanding, reasoning, code generation)')], dict(size=18, bold=True))])
areas = [
    (0.6, BLUE_F, BLUE_L, '① Real2Sim', 'SimFoundry', t('動画から Sim を作り、評価と学習データに使う', 'Build a sim from a video; use it for evaluation and training data')),
    (4.85, ORANGE_F, ORANGE_L, t('② 失敗検出', '② Failure detection'), 'Code-as-Monitor', t('監視コードで実行中の失敗を検知し予防する', 'Detect and prevent failures during execution with monitor code')),
    (9.1, GREEN_F, GREEN_L, t('③ 推論時の誘導', '③ Inference-time steering'), 'VLS', t('報酬関数でポリシーの行動生成を誘導する', 'Steer the policy\'s action generation with reward functions')),
]
for x, f, l, head, name, sub in areas:
    add_arrow(s, x + 1.6, 4.13, 0.4, 0.3, shape=MSO_SHAPE.DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
    add_box(s, x, 4.47, 3.6, 1.45, '', fill=f, line=l,
            lines=[('opt', [head], dict(size=18, bold=True)),
                   ('opt', [name], dict(size=16, bold=True, color=NAVY)),
                   ('opt', [sub], dict(size=13, bold=False))])
    add_arrow(s, x + 1.6, 5.95, 0.4, 0.3, shape=MSO_SHAPE.UP_DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
add_box(s, 0.6, 6.3, 12.1, 0.58, '', fill=GRAY_F, line=GRAY_L,
        lines=[('opt', [t('学習済みポリシー（π0.5 / Diffusion Policy / GR00T …）', 'Pretrained policy (π0.5 / Diffusion Policy / GR00T …)')], dict(size=16, bold=True))])

# ================================================================== 4, 5 papers
papers_slide(None)
papers_slide(0)

# ================================================================== SimFoundry 6-12
s = content_slide(CAT1, 6)
add_picture(s, 'sf_tab1', 0.45, 3.1, w=8.6)
caption(s, 0.45, 6.78, 8.6, 'Table 1 in Ranawaka et al., 2026')
add_box(s, 9.4, 3.3, 3.6, 3.2, '', fill=YELLOW_F, line=YELLOW_L,
        lines=[('opt', [t('SimFoundry の狙い', 'Goal of SimFoundry')], dict(size=18, bold=True)),
               ('opt', [t('動画1本から', 'From a single video,')], dict(size=16, bold=False)),
               ('opt', [t('評価にも学習にも使える', 'build a sim usable for both')], dict(size=16, bold=True, color=RED)),
               ('opt', [t('Sim 環境を自動で作り、', 'evaluation and training,')], dict(size=16, bold=False)),
               ('opt', [t('物体・シーン・タスクの', 'and diversify it along')], dict(size=16, bold=False)),
               ('opt', [t('3軸で多様化する', 'objects, scenes and tasks')], dict(size=16, bold=False))])

s = content_slide(CAT1, 7)
add_picture(s, 'sf_fig1', 1.65, 3.1, w=10.0)
caption(s, 1.65, 6.95, 8, 'Fig. 1 in Ranawaka et al., 2026')

s = content_slide(CAT1, 8, size=22)
video_row(s, [('sf_dining', t('家のダイニング：実世界 → 複製シーン', 'Dining room: real → reconstructed')), ('sf_toys', t('おもちゃの机：実世界 → 複製シーン', 'Toy table: real → reconstructed'))], 3.4, total_w=11.0, x0=1.15, gap=0.6)
caption(s, 0.5, 7.0, 12, 'Videos from github.com/NVlabs/SimFoundry (docs/gallery)')

s = content_slide(CAT1, 9)
add_picture(s, 'sf_fig2_top', 0.5, 3.45, w=12.3)
caption(s, 0.5, 6.85, 8, 'Fig. 2 (top) in Ranawaka et al., 2026')

s = content_slide(CAT1, 10)
add_picture(s, 'sf_fig2_bot', 0.5, 3.45, w=12.3)
caption(s, 0.5, 6.85, 8, 'Fig. 2 (bottom) in Ranawaka et al., 2026')

s = content_slide(CAT1, 11)
add_picture(s, 'sf_tasks', 1.4, 3.3, h=3.5)
add_picture(s, 'sf_scatter', 5.3, 3.3, h=3.5)
add_box(s, 9.2, 3.5, 3.7, 1.5, '', fill=BLUE_F, line=BLUE_L,
        lines=[('opt', [t('サブタスク単位の評価', 'Sub-task evaluation')], dict(size=16, bold=True)),
               ('opt', [('r', dict(italic=True)), ' 0.90 → 0.95'], dict(size=20, bold=True, color=RED)),
               ('opt', [t('長期タスクの弱い段階も分かる', 'Shows the weak stage of long tasks')], dict(size=14, bold=False))])
add_box(s, 9.2, 5.2, 3.7, 1.5, '', fill=BLUE_F, line=BLUE_L,
        lines=[('opt', [t('モデルの得意・不得意も見える', 'Reveals model strengths')], dict(size=16, bold=True)),
               ('opt', [t('GR00T N1.7 は精密な把持に強い', 'GR00T N1.7: precise grasping')], dict(size=14, bold=False)),
               ('opt', [t('π0.5 は言語の追従に強い', 'π0.5: language following')], dict(size=14, bold=False))])
caption(s, 1.4, 6.85, 8, 'Fig. 4 in Ranawaka et al., 2026')

s = content_slide(CAT1, 12)
add_picture(s, 'sf_fig5', 0.5, 3.55, w=12.3)
caption(s, 0.5, 6.5, 12, t('Fig. 5 in Ranawaka et al., 2026   A: 物体の変種は未知の物体に効く   B: 配置の変種は新しい配置に効く   C: 関連タスクのデモが目標タスクを押し上げる', 'Fig. 5 in Ranawaka et al., 2026   A: object cousins help on unseen objects   B: scene cousins help on new layouts   C: related-task demos lift the target task'), size=12)

s = content_slide(CAT1, 13, size=22)
video_row(s, [('sf_yam_sim', t('Sim で学習（YAM、両腕）', 'Trained in sim (YAM, bimanual)')), ('sf_yam_real', t('同じポリシーを実機で実行', 'Same policy on the real robot')), ('sf_yam_cousin', t('未知の物体で実行', 'Unseen objects'))], 3.5, gap=0.35)
caption(s, 0.5, 6.9, 12, 'Videos from github.com/NVlabs/SimFoundry (docs/gallery): YAM simulated / real / unseen-object evaluation')

s = content_slide(CAT1, 14)
add_picture(s, 'sf_fig3', 0.5, 3.4, w=12.3)
caption(s, 0.5, 6.78, 12, t('Fig. 3 in Ranawaka et al., 2026   上：実世界   中：Digital Twin   下：Digital Cousin', 'Fig. 3 in Ranawaka et al., 2026   top: real   middle: digital twin   bottom: digital cousin'), size=12)

# ================================================================== 13 papers (#2) + CaM 14-19
papers_slide(1)

s = content_slide(CAT2, 16)
add_picture(s, 'cam_fig1', 1.5, 3.3, w=10.3)
caption(s, 1.5, 7.05, 8, 'Fig. 1 in Zhou et al., 2025')

s = content_slide(CAT2, 17)
add_picture(s, 'cam_fig2', 0.5, 3.45, w=8.3)
add_eq(s, 'cam_gen', 9.0, 3.6, 4.0)
add_box(s, 9.0, 4.3, 4.0, 1.2, '', fill=ORANGE_F, line=ORANGE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('事前予防 = 実行中に保つ制約 ', 'Proactive = constraints during execution '), ('C', dict(italic=True)), ('d', dict(size=12))], dict(size=14, bold=True)),
               ('opt', [t('鍋の把持を保つ、パンは鍋の中、鍋は水平', 'keep grasping the pan, bread stays in the pan, pan stays level')], dict(size=13, bold=False))])
add_box(s, 9.0, 5.6, 4.0, 1.2, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('事後検知 = 完了時に満たす制約 ', 'Reactive = constraints upon completion '), ('C', dict(italic=True)), ('u', dict(size=12))], dict(size=14, bold=True)),
               ('opt', [t('鍋がコンロの真上にある', 'the pan is directly above the stove')], dict(size=13, bold=False))])
caption(s, 0.5, 7.0, 8, 'Fig. 2, Eq. (1) in Zhou et al., 2025')

s = content_slide(CAT2, 18)
add_picture(s, 'cam_fig3', 0.5, 3.45, w=12.3)
add_text(s, 0.6, 6.15, 1.4, 0.4, [[('ConSeg:', dict(bold=True))]], size=16, color=NAVY)
add_eq(s, 'cam_seg', 2.0, 6.17, 7.4)
caption(s, 9.6, 6.25, 3.5, 'Fig. 3, Eq. (2) in Zhou et al., 2025')

s = content_slide(CAT2, 19)
add_picture(s, 'cam_code', 0.5, 3.5, w=8.3)
flow = [(t('サブゴールの開始時に VLM を1回呼ぶ', 'Call the VLM once at the start of a subgoal'), ORANGE_F, ORANGE_L), (t('要素を追跡する（CoTracker）', 'Track the elements (CoTracker)'), BLUE_F, BLUE_L),
        (t('コードを毎フレーム評価する', 'Evaluate the code every frame'), GREEN_F, GREEN_L), (t('False なら停止し、理由を付けて再計画', 'On False: stop, return the reason, re-plan'), PINK_F, PINK_L)]
for i, (txt_, f, l) in enumerate(flow):
    add_box(s, 9.2, 3.5 + i * 0.85, 3.8, 0.6, txt_, fill=f, line=l, size=14)
    if i < len(flow) - 1:
        add_arrow(s, 10.95, 3.5 + i * 0.85 + 0.6, 0.3, 0.25, shape=MSO_SHAPE.DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
caption(s, 0.5, 6.75, 8, 'Monitor code example from Fig. 2 in Zhou et al., 2025')

s = content_slide(CAT2, 20, size=22)
video_row(s, [('cam_stack_ours', t('積み木積み：本手法', 'Stack in order: CaM')), ('cam_stack_doremi', t('積み木積み：DoReMi', 'Stack in order: DoReMi')), ('cam_sweep', t('ブロックの半分だけ掃く', 'Sweep half the blocks')), ('cam_pour', t('お茶注ぎ（面の傾き）', 'Pour tea (surface tilt)'))], 3.5, gap=0.25)
caption(s, 0.5, 6.95, 12, 'Videos from zhoues.github.io/Code-as-Monitor (CLIPort / OmniGibson demos)')

s = content_slide(CAT2, 21)
add_picture(s, 'cam_tab2', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab1', 0.5, 5.0, w=5.4)
add_picture(s, 'cam_tab9', 6.3, 5.3, w=6.5)
caption(s, 0.5, 6.85, 12, 'Table 1, 2, 9 in Zhou et al., 2025 (DRM: DoReMi, IM: Inner Monologue)')

s = content_slide(CAT2, 22, size=22)
video_row(s, [('cam_real_clear', t('動物以外を片付ける（2倍速）', 'Clear all objects except animals (2x)')), ('cam_real_grasp', t('果物に近い順に動物を掴む', 'Grasp animals nearest to fruits first'))], 3.3, total_w=6.0, x0=3.65, gap=0.6, max_h=3.1)
caption(s, 0.5, 7.0, 12, 'Videos from zhoues.github.io/Code-as-Monitor (real-world demos, UR5 + Leap Hand)')

s = content_slide(CAT2, 23)
add_picture(s, 'cam_fig5', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab4', 0.5, 5.75, w=5.2)
add_picture(s, 'cam_tab6', 6.3, 5.75, w=5.0)
add_text(s, 11.45, 5.8, 1.7, 1.0, [[(t('限界', 'Limits'), dict(bold=True))], [t('VLM の幻覚', 'VLM hallucination')], [t('力に関する失敗は捉えにくい', 'force-related failures are hard to catch')]], size=11, color=MUTED, spacing=100)
caption(s, 0.5, 7.05, 12, 'Fig. 5, Table 4, Table 6 in Zhou et al., 2025')

# ================================================================== 20 papers (#3) + VLS 21-26
papers_slide(2)

s = content_slide(CAT3, 25)
add_picture(s, 'vls_fig1', 2.0, 3.35, w=9.3)
caption(s, 2.0, 7.0, 8, 'Fig. 1 in Liu et al., 2026')

s = content_slide(CAT3, 26)
add_eq(s, 'vls_guid', 0.9, 3.4, 7.6)
add_eq(s, 'vls_surr', 0.9, 4.0, 5.6)
rows = [
    (t('既存の誘導の手法', 'Existing steering methods'), t('誘導の信号', 'Guidance signal'), t('課題', 'Issue')),
    ('V-GPS / VGD', t('学習済みの価値関数・Q', 'learned value / Q function'), t('批評家の好みにポリシーが引きずられる', 'policy is pulled toward the critic\'s preferences')),
    ('DynaGuide / Latent Policy Barrier', t('学習済みのダイナミクスモデル', 'learned dynamics model'), t('モデルの誤差とロールアウトの計算コスト', 'model error and rollout cost')),
    ('ITPS / FOREWARN / Do-What-You-Say', t('人間や VLM による候補の選択', 'selection of candidates by humans / VLMs'), t('信号が離散で疎なのでサンプル効率が悪い', 'discrete, sparse signal; sample-inefficient')),
    (t('VLS（本論文）', 'VLS (this paper)'), t('VLM が書いた微分可能な報酬関数', 'differentiable reward written by a VLM'), t('訓練が要らず、勾配が密。推論コストが課題', 'training-free, dense gradients; inference cost is the issue')),
]
tbl = s.shapes.add_table(len(rows), 3, inch(0.9), inch(4.7), inch(11.6), inch(2.1)).table
tbl.columns[0].width = inch(3.9); tbl.columns[1].width = inch(3.4); tbl.columns[2].width = inch(4.3)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        c = tbl.cell(i, j)
        c.text = ''
        add_runs(c.text_frame.paragraphs[0], val, size=14, bold=(i == 0 or i == len(rows) - 1), color=('FFFFFF' if i == 0 else None))
        c.margin_top = c.margin_bottom = inch(0.03)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor.from_string(NAVY if i == 0 else (GREEN_F if i == len(rows) - 1 else ('F2F2F2' if i % 2 else 'FFFFFF')))
caption(s, 8.7, 3.45, 4.5, 'Eq. (5), (6), (7) in Liu et al., 2026', size=11)

s = content_slide(CAT3, 27)
add_picture(s, 'vls_fig2', 0.5, 3.45, w=7.6)
add_box(s, 8.5, 3.5, 4.4, 1.55, '', fill=YELLOW_F, line=YELLOW_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('報酬関数の例（VLM の出力）', 'Example reward (VLM output)')], dict(size=15, bold=True)),
               ('opt', [t('目標のキーポイントと行動系列の距離の二乗和にマイナスを付ける。近づくほど高い報酬', 'Negative squared distance between the action sequence and the target keypoint: closer is better')], dict(size=13, bold=False)),
               ('opt', [t('距離、内積、ソフト制約の組み合わせだけを許し、微分できる形に保つ', 'Only distances, dot products and soft constraints are allowed, keeping it differentiable')], dict(size=13, bold=False))])
add_box(s, 8.5, 5.2, 4.4, 1.55, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('VLM は計算グラフの外', 'The VLM stays off the graph')], dict(size=15, bold=True)),
               ('opt', [t('VLM を呼ぶのは報酬の生成と段階切り替えの判断だけ。勾配は生成された関数を通して行動へ逆伝播する', 'The VLM is called only to write rewards and to judge stage switches; gradients flow through the generated function to the actions')], dict(size=13, bold=False))])
caption(s, 0.5, 7.0, 8, 'Fig. 2 in Liu et al., 2026')

s = content_slide(CAT3, 28)
add_picture(s, 'vls_loop', 0.5, 3.4, w=12.3)
for lab, eqn, x, w in [(t('候補を引き離す斥力（RBF）', 'Repulsion between candidates (RBF)'), 'vls_rbf', 0.5, 3.9), (t('報酬で重み付けした選別（FK）', 'Reward-weighted resampling (FK)'), 'vls_fk', 4.7, 4.2), (t('誘導の強さの調整', 'Adaptive guidance strength'), 'vls_lam', 9.2, 3.5)]:
    add_text(s, x, 5.45, w, 0.35, [lab], size=14, bold=True, color=NAVY)
    add_eq(s, eqn, x, 5.85, w)
caption(s, 0.5, 7.0, 12, 'Fig. 2 (bottom), Eq. (8)–(10) in Liu et al., 2026')

s = content_slide(CAT3, 29, size=22)
video_row(s, [('vls_libero_base', t('LIBERO-PRO：π0.5（失敗）', 'LIBERO-PRO: π0.5 (fail)')), ('vls_libero_vls', t('LIBERO-PRO：+VLS（成功）', 'LIBERO-PRO: +VLS (success)')), ('vls_coll_base', t('壁を避ける：ベース（失敗）', 'Avoid the wall: base (fail)')), ('vls_coll_vls', t('壁を避ける：+VLS（成功）', 'Avoid the wall: +VLS (success)'))], 3.5, gap=0.25)
caption(s, 0.5, 6.95, 12, 'Videos from vision-language-steering.github.io (LIBERO-PRO position perturbation, collision avoidance)')

s = content_slide(CAT3, 30)
add_picture(s, 'vls_tab1', 0.5, 3.5, w=7.4)
add_picture(s, 'vls_fig3', 0.5, 5.1, w=7.4)
add_picture(s, 'vls_abl', 8.2, 3.5, w=4.8)
add_picture(s, 'vls_scale', 8.2, 5.1, w=4.8)
caption(s, 0.5, 6.95, 7, 'Table I, Fig. 3 in Liu et al., 2026')
caption(s, 8.2, 6.5, 4.8, t('Fig. 4 in Liu et al., 2026（左：Ablation、右：サンプル数のスケーリング）', 'Fig. 4 in Liu et al., 2026 (left: ablation, right: scaling with the number of samples)'))

s = content_slide(CAT3, 31, size=22)
video_row(s, [('vls_real_banana', t('同じ条件：バナナを緑の皿に', 'In-distribution: banana on green plate')), ('vls_real_mug', t('未知の物体：マグを皿に', 'Unseen object: mug on plate')), ('vls_real_pos', t('皿の位置を入れ替え', 'Plates swapped'))], 3.5, gap=0.3)
caption(s, 0.5, 6.9, 12, 'Videos from vision-language-steering.github.io (real-world Franka rollouts)')

s = content_slide(CAT3, 32)
add_picture(s, 'vls_fig5', 0.5, 3.45, w=12.3)
caption(s, 0.5, 7.0, 8, 'Fig. 5 in Liu et al., 2026')

# ================================================================== 27 insights
s = new_slide('Insights', slide_title(33))
add_bullets(s, 33, size=20, spacing=130)
boxes2 = [(0.9, BLUE_F, BLUE_L, '① Real2Sim', 'SimFoundry', t('VLM の空間理解で Sim を作る', 'Build sims with VLM spatial understanding')),
          (5.0, ORANGE_F, ORANGE_L, t('② 失敗検出', '② Failure detection'), 'Code-as-Monitor', t('VLM が書いたコードで監視する', 'Monitor with VLM-written code')),
          (9.1, GREEN_F, GREEN_L, t('③ 推論時の誘導', '③ Steering'), 'VLS', t('VLM が書いた報酬で誘導する', 'Steer with VLM-written rewards'))]
for x, f, l, head, name, sub in boxes2:
    add_box(s, x, 5.55, 3.4, 1.0, '', fill=f, line=l,
            lines=[('opt', [head + '  ', (name, dict(color=NAVY))], dict(size=16, bold=True)), ('opt', [sub], dict(size=13, bold=False))])
add_text(s, 0.9, 6.6, 11.6, 0.4, [[t('VLM が書く「幾何要素とコード」を、Sim の構築、実行の監視、生成の誘導に使う', 'Use VLM-written geometry and code for building sims, monitoring execution, and steering generation')]], size=14, color=NAVY, align=PP_ALIGN.CENTER)

# ================================================================== 34 own work
s = content_slide('Insights', 34, size=22)
video_row(s, [('own_demo1', t('LIBERO-Goal：誘導 + 監視', 'LIBERO-Goal: steering + monitoring')), ('own_demo2', t('LIBERO-Object：誘導 + 監視', 'LIBERO-Object: steering + monitoring'))], 3.5, total_w=12.3, gap=0.4)
caption(s, 0.5, 7.0, 12, 'Own preliminary experiments (LIBERO), 2026')

prs.save(OUT)
print('saved', OUT, 'slides:', len(prs.slides))
