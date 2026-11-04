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
    13: ['+17 / +21 / +40%'],
    23: ['76.7% → 88.3%'],
    25: [t('本手法 90%', 'CaM 90%')],
    34: ['23.7% → 36.8%'],
    36: ['50% → 69%'],
}


def rich_bullet(text, n):
    """Bold a short leading label (before the first colon), red highlights."""
    segs = []
    rest = text
    m = re.match(r'^([^：。]{1,24})：', text) or (LANG == 'en' and re.match(r'^([^:.]{1,30}):', text))
    if m:
        segs.append((m.group(1), dict(bold=True)))
        rest = text[len(m.group(1)):]
    for hl in HIGHLIGHT.get(n, []):
        if hl in rest:
            a, b = rest.split(hl, 1)
            segs.append(a); segs.append((hl, dict(bold=True, color=RED))); rest = b
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
    pos = []
    for (name, cap), w in zip(items, ws):
        add_video(slide, name, x, y, w, caption_text=cap)
        pos.append((x, w))
        x += w + gap
    return h, pos


def callouts(slide, pos, y, texts, size=12):
    """One short '見どころ' note under each video. texts: list of str (may contain newline)."""
    for (x, w), txt in zip(pos, texts):
        lines = txt.split('\n')
        tb = add_text(slide, x, y, w, 0.5, [[('▶ ', dict(color=RED, bold=True)), lines[0]]] + [[l] for l in lines[1:]],
                      size=size, spacing=105)
        tb.text_frame.margin_left = tb.text_frame.margin_right = 0


def step_row(slide, steps, y, h, x0=0.5, total_w=12.3, gap=0.35, head_size=15, body_size=12, head_fill=None):
    """steps: list of dict(img=..., head=..., body=..., w=relative width). Images sit under a numbered heading."""
    from PIL import Image
    rel = [st.get('w', 1.0) for st in steps]
    arrow_w = 0.3
    usable = total_w - gap * (len(steps) - 1)
    ws = [usable * r / sum(rel) for r in rel]
    x = x0
    out = []
    for i, (st, w) in enumerate(zip(steps, ws)):
        fill, line = head_fill[i] if head_fill else (BLUE_F, BLUE_L)
        add_box(slide, x, y, w, 0.42, st['head'], fill=fill, line=line, size=head_size, bold=True)
        img_y = y + 0.52
        img_h = h - 0.52 - (0.75 if st.get('body') else 0)
        if st.get('img'):
            iw, ih = Image.open(FIG + st['img'] + '.png').size
            ar = iw / ih
            pw, ph = w, w / ar
            if ph > img_h:
                ph, pw = img_h, img_h * ar
            pic = add_picture(slide, st['img'], x + (w - pw) / 2, img_y + (img_h - ph) / 2, w=pw)
            pic.line.color.rgb = RGBColor.from_string('BFBFBF'); pic.line.width = Pt(0.5)
        if st.get('body'):
            add_text(slide, x, y + h - 0.72, w, 0.7, [st['body']], size=body_size, spacing=105)
        if i < len(steps) - 1:
            add_arrow(slide, x + w + 0.03, y + 0.6 + img_h / 2 - 0.15, gap - 0.06, 0.3, fill='BFBFBF', line='7F7F7F')
        out.append((x, w))
        x += w + gap
    return out


def positioning(slide, active, rows, y=3.55):
    """Framework diagram (left, active area highlighted) + 4-row fact table (right)."""
    L = 0.5; W = 6.4
    add_box(slide, L, y, W, 0.5, t('VLM（空間理解 ・ 推論 ・ コード生成）', 'VLM (spatial understanding, reasoning, code generation)'),
            fill=PURPLE_F, line=PURPLE_L, size=14)
    areas = [(BLUE_F, BLUE_L, '① Real2Sim', 'SimFoundry'), (ORANGE_F, ORANGE_L, t('② 失敗検出', '② Failure detection'), 'Code-as-Monitor'),
             (GREEN_F, GREEN_L, t('③ 推論時の誘導', '③ Steering'), 'VLS')]
    bw = (W - 0.4) / 3
    for i, (f, l, head, name) in enumerate(areas):
        x = L + i * (bw + 0.2)
        on = (i == active)
        col = '7F7F7F' if on else 'BFBFBF'
        add_arrow(slide, x + bw / 2 - 0.15, y + 0.52, 0.3, 0.38, shape=MSO_SHAPE.DOWN_ARROW, fill=col, line='7F7F7F')
        box = add_box(slide, x, y + 0.95, bw, 1.0, '', fill=f if on else 'F2F2F2', line=l if on else 'BFBFBF',
                      lines=[('opt', [head], dict(size=14, bold=True, color='000000' if on else 'A6A6A6')),
                             ('opt', [name], dict(size=13, bold=True, color=NAVY if on else 'A6A6A6'))])
        if on:
            box.line.width = Pt(2.5)
        add_arrow(slide, x + bw / 2 - 0.15, y + 2.0, 0.3, 0.5, shape=MSO_SHAPE.UP_DOWN_ARROW, fill=col, line='7F7F7F')
    add_box(slide, L, y + 2.55, W, 0.5, t('学習済みポリシー', 'Pretrained policy'), fill=GRAY_F, line=GRAY_L, size=14)
    RX = 7.3; RW = 5.7; rh = 0.68
    for i, (k, v) in enumerate(rows):
        yy = y + i * (rh + 0.1)
        add_box(slide, RX, yy, 1.7, rh, k, fill=[BLUE_F, ORANGE_F, GREEN_F][active], line=[BLUE_L, ORANGE_L, GREEN_L][active], size=13)
        add_box(slide, RX + 1.8, yy, RW - 1.8, rh, '', fill='FFFFFF', line='BFBFBF', align=PP_ALIGN.LEFT,
                lines=[('opt', [v], dict(size=12, bold=False))], margin=0.08)

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
add_box(s, 0.6, 3.5, 12.1, 0.55, t('VLM（空間理解 ・ 推論 ・ コード生成）', 'VLM (spatial understanding, reasoning, code generation)'),
        fill=PURPLE_F, line=PURPLE_L, size=18)
areas = [
    (0.6, BLUE_F, BLUE_L, '① Real2Sim', 'SimFoundry', t('動画から Sim を作り、評価と学習データに使う', 'Build a sim from a video; use it for evaluation and training data')),
    (4.85, ORANGE_F, ORANGE_L, t('② 失敗検出', '② Failure detection'), 'Code-as-Monitor', t('監視コードで実行中の失敗を検知し予防する', 'Detect and prevent failures during execution with monitor code')),
    (9.1, GREEN_F, GREEN_L, t('③ 推論時の誘導', '③ Inference-time steering'), 'VLS', t('報酬関数でポリシーの行動生成を誘導する', 'Steer the policy\'s action generation with reward functions')),
]
for x, f, l, head, name, sub in areas:
    add_arrow(s, x + 1.65, 4.08, 0.3, 0.38, shape=MSO_SHAPE.DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
    add_box(s, x, 4.5, 3.6, 1.4, '', fill=f, line=l,
            lines=[('opt', [head], dict(size=18, bold=True)),
                   ('opt', [name], dict(size=16, bold=True, color=NAVY)),
                   ('opt', [sub], dict(size=13, bold=False))])
    add_arrow(s, x + 1.65, 5.93, 0.3, 0.5, shape=MSO_SHAPE.UP_DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
add_box(s, 0.6, 6.47, 12.1, 0.55, t('学習済みポリシー（π0.5 / Diffusion Policy / GR00T …）', 'Pretrained policy (π0.5 / Diffusion Policy / GR00T …)'),
        fill=GRAY_F, line=GRAY_L, size=16)

# ================================================================== 4, 5 papers
papers_slide(None)
papers_slide(0)

# ================================================================== SimFoundry 6-15
s = content_slide(CAT1, 6, size=22)
positioning(s, 0, [
    (t('入力', 'Input'), t('実世界の動画1本と、評価または学習したいポリシー', 'One real-world video, plus the policy to evaluate or train')),
    (t('VLM の役割', 'Role of the VLM'), t('物体の検出、質量・摩擦の推定、別の配置やタスクの提案', 'Detect objects, estimate mass and friction, propose layouts and tasks')),
    (t('出力の使い道', 'Where the output goes'), t('シミュレータ。シーンの構築とデモの自動生成に使う', 'The simulator: scene construction and automatic demo generation')),
    (t('ポリシーの扱い', 'What happens to the policy'), t('Sim の中で評価される、または Sim のデータで学習される', 'Evaluated inside the sim, or trained on sim data')),
])

s = content_slide(CAT1, 7, size=22)
add_picture(s, 'sf_fig1', 1.65, 3.3, w=10.0)
caption(s, 1.65, 7.0, 8, 'Fig. 1 in Ranawaka et al., 2026')

s = content_slide(CAT1, 8, size=20)
add_picture(s, 'sf_tab1', 0.45, 3.45, w=7.4)
caption(s, 0.45, 6.65, 7.4, 'Table 1 in Ranawaka et al., 2026')
rows3 = [(t('構築', 'Construction'), t('手作業・半自動', 'manual / semi-automatic'), t('動画1本から全自動', 'fully automatic from one video')),
         (t('出力', 'Output'), t('複製シーン1つ', 'one twin scene'), t('複製 ＋ 物体・配置・タスクの変種', 'twin + object / layout / task variants')),
         (t('用途', 'Use'), t('評価か学習のどちらか', 'evaluation or training'), t('評価と学習の両方', 'both evaluation and training'))]
add_box(s, 9.0, 3.45, 2.0, 0.45, t('既存の Real2Sim', 'Prior real-to-sim'), fill=GRAY_F, line=GRAY_L, size=13)
add_box(s, 11.05, 3.45, 2.0, 0.45, 'SimFoundry', fill=BLUE_F, line=BLUE_L, size=13)
for i, (k, a, b) in enumerate(rows3):
    yy = 4.0 + i * 1.0
    add_box(s, 8.0, yy, 0.95, 0.9, k, fill=GRAY_F, line=GRAY_L, size=13)
    add_box(s, 9.0, yy, 2.0, 0.9, '', fill='FFFFFF', line='BFBFBF', lines=[('opt', [a], dict(size=12, bold=False, color='595959'))], margin=0.06)
    add_box(s, 11.05, yy, 2.0, 0.9, '', fill='FFFFFF', line=BLUE_L, lines=[('opt', [b], dict(size=12, bold=True, color=NAVY))], margin=0.06)

s = content_slide(CAT1, 9, size=20)
step_row(s, [
    dict(img='sf_s2_depth', head=t('① 深度 → 点群', '① Depth → point cloud'), body='Depth Anything 3, SAM 3'),
    dict(img='sf_s2_masks', head=t('② 物体の切り抜き', '② Cut out each object'), body=t('Gemini 3 Pro で列挙、SAM 3 でマスク', 'Gemini 3 Pro lists, SAM 3 masks')),
    dict(img='sf_s3_mesh', head=t('③ メッシュ化と姿勢合わせ', '③ Mesh + pose'), body='Hunyuan3D 2.1 / TRELLIS.2, FoundationPose'),
    dict(img='sf_s4_scene', head=t('④ 物性と安定化', '④ Properties + stabilization'), body=t('CoACD, Gemini（質量・摩擦）, PyBullet → IsaacLab', 'CoACD, Gemini (mass, friction), PyBullet → IsaacLab')),
], y=3.75, h=3.0)
caption(s, 0.5, 6.95, 12, 'Images from Fig. 2 in Ranawaka et al., 2026')

s = content_slide(CAT1, 10, size=20)
add_picture(s, 'sf_fig2_bot', 0.5, 3.7, w=12.3)
caption(s, 0.5, 7.1, 8, 'Fig. 2 (bottom) in Ranawaka et al., 2026')

s = content_slide(CAT1, 11, size=20)
add_picture(s, 'sf_tasks', 0.6, 3.7, h=3.2)
add_box(s, 4.2, 3.7, 4.2, 1.5, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('実機ポリシーの Sim 評価', 'Evaluating real policies in sim')], dict(size=15, bold=True)),
               ('opt', [t('タスクごとに 25 ロールアウト。初期位置は 5×5 格子からサンプル。成功は 0 / 1', '25 rollouts per task; start positions from a 5×5 grid; success is 0 / 1')], dict(size=12, bold=False))])
add_box(s, 8.7, 3.7, 4.3, 1.5, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('指標', 'Metrics')], dict(size=15, bold=True)),
               ('opt', [t('Pearson r：Sim と実機の成功率の相関。MMRV：Sim での順位が実機と食い違う度合い（0 が理想）', 'Pearson r: correlation of success rates. MMRV: how far sim rankings violate real rankings (0 is ideal)')], dict(size=12, bold=False))])
add_box(s, 4.2, 5.4, 8.8, 1.5, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('Sim で学習して実機へ', 'Training in sim for the real robot')], dict(size=15, bold=True)),
               ('opt', [t('人のテレオペで 10〜15 デモ → MimicGen で軌道を増やし、材質とカメラ位置をランダム化 → DROID では π0 / π0.5 を微調整、YAM では Flow Matching ポリシーをゼロから学習 → Sim で最良のチェックポイントを選び実機へ', '10-15 teleoperated demos → MimicGen augmentation with material and camera randomization → fine-tune π0 / π0.5 on DROID, train a flow-matching policy from scratch on YAM → pick the best checkpoint in sim and deploy')], dict(size=12, bold=False))])
caption(s, 0.6, 6.95, 4, 'Tasks: Fig. 4 in Ranawaka et al., 2026')

s = content_slide(CAT1, 12)
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

s = content_slide(CAT1, 13)
add_picture(s, 'sf_fig5', 0.5, 3.55, w=12.3)
caption(s, 0.5, 6.5, 12, t('Fig. 5 in Ranawaka et al., 2026   A: 物体の変種は未知の物体に効く   B: 配置の変種は新しい配置に効く   C: 関連タスクのデモが目標タスクを押し上げる', 'Fig. 5 in Ranawaka et al., 2026   A: object cousins help on unseen objects   B: scene cousins help on new layouts   C: related-task demos lift the target task'), size=12)

s = content_slide(CAT1, 14, size=22)
h_, pos = video_row(s, [('sf_yam_sim_cut', t('Sim で学習（YAM、両腕）', 'Trained in sim (YAM, bimanual)')), ('sf_yam_real', t('同じポリシーを実機で実行', 'Same policy on the real robot')), ('sf_yam_cousin', t('未知の物体で実行', 'Unseen objects'))], 3.45, gap=0.35)
callouts(s, pos, 3.45 + h_ + 0.5, [t('複製シーンの中で鍋をコンロへ運ぶ', 'Carrying the pot to the stove inside the twin'),
                                    t('微調整なしで実機でも同じ動き', 'The same motion on the real robot, no fine-tuning'),
                                    t('学習にない黄色いボウルでも掴める', 'Grasps a yellow bowl never seen in training')])
caption(s, 0.5, 7.05, 12, 'Videos from github.com/NVlabs/SimFoundry (docs/gallery): YAM simulated / real / unseen-object evaluation')

s = content_slide(CAT1, 15, size=22)
h_, pos = video_row(s, [('sf_dining', t('家のダイニング：実世界 → 複製シーン', 'Dining room: real → reconstructed')), ('sf_toys', t('おもちゃの机：実世界 → 複製シーン', 'Toy table: real → reconstructed'))], 3.5, total_w=10.0, x0=1.65, gap=0.6)
callouts(s, pos, 3.5 + h_ + 0.5, [t('前半が実世界、後半が Sim。瓶の形やへらの向きまで一致する', 'First half real, second half sim. Bottle shape and spatula pose match'),
                                   t('小さな物（クッキー、にんじん）も個別のメッシュになる', 'Small items (cookie, carrot) become individual meshes')])
caption(s, 0.5, 7.05, 12, 'Videos from github.com/NVlabs/SimFoundry (docs/gallery)')

# ================================================================== 16 papers (#2) + CaM 17-26
papers_slide(1)

s = content_slide(CAT2, 17, size=22)
positioning(s, 1, [
    (t('入力', 'Input'), t('タスクの指示、多視点のカメラ画像、実行中のポリシー（開ループ可）', 'Task instruction, multi-view images, the running policy (open-loop is fine)')),
    (t('VLM の役割', 'Role of the VLM'), t('守るべき条件を文章で書き、それを判定するコードを書く', 'Write the conditions to keep, and the code that checks them')),
    (t('出力の使い道', 'Where the output goes'), t('実行中の監視プロセス。点を追跡し、コードを毎フレーム実行する', 'A monitor running alongside: tracks points, runs the code every frame')),
    (t('ポリシーの扱い', 'What happens to the policy'), t('そのまま動く。条件を破ったら止められ、再計画を受ける', 'Runs unchanged; stopped and re-planned when a condition breaks')),
])

s = content_slide(CAT2, 18, size=22)
add_picture(s, 'cam_fig1', 1.5, 3.45, w=10.3)
caption(s, 1.5, 7.1, 8, 'Fig. 1 in Zhou et al., 2025')

s = content_slide(CAT2, 19, size=22)
add_picture(s, f'cam_compare_{LANG}.png', 0.9, 3.6, w=11.5, folder=S + '/diag/')
caption(s, 0.9, 6.9, 11, t('Inner Monologue と DoReMi は論文の比較手法', 'Inner Monologue and DoReMi are the baselines in the paper'))

s = content_slide(CAT2, 20, size=20)
add_picture(s, 'cam_fig2', 0.5, 3.4, w=8.4)
caption(s, 0.5, 7.2, 8, 'Fig. 2 in Zhou et al., 2025')
add_box(s, 9.2, 3.5, 3.8, 1.1, '', fill=ORANGE_F, line=ORANGE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('実行中に守る制約（事前予防）', 'During execution (proactive)')], dict(size=13, bold=True)),
               ('opt', [t('取っ手を持ち続ける。パンは鍋の中。鍋は水平', 'keep the handle, bread in pan, pan level')], dict(size=12, bold=False))])
add_box(s, 9.2, 4.7, 3.8, 1.1, '', fill=BLUE_F, line=BLUE_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('完了時に満たす制約（事後検知）', 'Upon completion (reactive)')], dict(size=13, bold=True)),
               ('opt', [t('鍋がコンロの真上にある', 'the pan is directly above the stove')], dict(size=12, bold=False))])
add_box(s, 9.2, 5.9, 3.8, 1.1, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('違反したら', 'On a violation')], dict(size=13, bold=True)),
               ('opt', [t('ポリシーを止め、理由（鍋が 25° 傾いた）を Generator に返して再計画', 'stop the policy, return the reason (pan tilted 25°) to the Generator, re-plan')], dict(size=12, bold=False))])

s = content_slide(CAT2, 21, size=20)
add_picture(s, 'cam_fig3', 0.5, 3.6, w=12.3)
add_text(s, 0.6, 6.3, 1.4, 0.4, [[('ConSeg:', dict(bold=True))]], size=16, color=NAVY)
add_eq(s, 'cam_seg', 2.0, 6.32, 7.4)
caption(s, 9.6, 6.4, 3.5, 'Fig. 3, Eq. (2) in Zhou et al., 2025')

s = content_slide(CAT2, 22, size=20)
add_picture(s, 'cam_code', 0.5, 3.7, w=8.3)
flow = [(t('サブゴールの開始時に VLM を1回呼ぶ', 'Call the VLM once at the start of a subgoal'), ORANGE_F, ORANGE_L), (t('要素を追跡する（CoTracker）', 'Track the elements (CoTracker)'), BLUE_F, BLUE_L),
        (t('コードを毎フレーム評価する', 'Evaluate the code every frame'), GREEN_F, GREEN_L), (t('False なら停止し、理由を付けて再計画', 'On False: stop, return the reason, re-plan'), PINK_F, PINK_L)]
for i, (txt_, f, l) in enumerate(flow):
    add_box(s, 9.2, 3.7 + i * 0.8, 3.8, 0.58, txt_, fill=f, line=l, size=14)
    if i < len(flow) - 1:
        add_arrow(s, 10.95, 3.7 + i * 0.8 + 0.58, 0.3, 0.22, shape=MSO_SHAPE.DOWN_ARROW, fill='BFBFBF', line='7F7F7F')
caption(s, 0.5, 6.95, 8, 'Monitor code example from Fig. 2 in Zhou et al., 2025')

s = content_slide(CAT2, 23)
add_picture(s, 'cam_tab2', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab1', 0.5, 5.0, w=5.4)
add_picture(s, 'cam_tab9', 6.3, 5.3, w=6.5)
caption(s, 0.5, 6.85, 12, 'Table 1, 2, 9 in Zhou et al., 2025 (DRM: DoReMi, IM: Inner Monologue)')

s = content_slide(CAT2, 24, size=22)
h_, pos = video_row(s, [('cam_stack_ours', t('積み木積み：本手法', 'Stack in order: CaM')), ('cam_stack_doremi_cut', t('積み木積み：DoReMi', 'Stack in order: DoReMi')), ('cam_sweep', t('ブロックの半分だけ掃く', 'Sweep half the blocks')), ('cam_pour', t('お茶注ぎ（面の傾き）', 'Pour tea (surface tilt)'))], 3.4, gap=0.25)
callouts(s, pos, 3.4 + h_ + 0.5, [t('積み木の位置を点で追跡。ずれたら積み直してから次へ', 'Block positions tracked as points; restacks after a shift'),
                                   t('VLM に毎回問うため、積めているのに失敗と誤判定してやり直す', 'Asks the VLM each time; misjudges a good stack and redoes it'),
                                   t('領域内の点を数え、半分になったところで止まる', 'Counts points inside the region; stops at half'),
                                   t('ポットの面の傾きを監視し、傾けすぎを止める', 'Watches the teapot surface; stops over-tilting')])
caption(s, 0.5, 7.05, 12, 'Videos from zhoues.github.io/Code-as-Monitor (CLIPort / OmniGibson demos)')

s = content_slide(CAT2, 25)
add_picture(s, 'cam_fig5', 0.5, 3.45, w=12.3)
add_picture(s, 'cam_tab4', 0.5, 5.75, w=5.2)
add_picture(s, 'cam_tab6', 6.3, 5.75, w=5.0)
add_text(s, 11.45, 5.8, 1.7, 1.0, [[(t('限界', 'Limits'), dict(bold=True))], [t('VLM の幻覚', 'VLM hallucination')], [t('力に関する失敗は捉えにくい', 'force-related failures are hard to catch')]], size=11, color=MUTED, spacing=100)
caption(s, 0.5, 7.05, 12, 'Fig. 5, Table 4, Table 6 in Zhou et al., 2025')

s = content_slide(CAT2, 26, size=22)
h_, pos = video_row(s, [('cam_real_clear_cut', t('動物以外を片付ける（2倍速）', 'Clear all objects except animals (2x)')), ('cam_real_grasp_cut', t('果物に近い順に動物を掴む', 'Grasp animals nearest to fruits first'))], 3.3, total_w=8.0, x0=2.65, gap=2.2, max_h=2.55)
callouts(s, [(0.6, 5.9), (6.9, 5.9)], 3.3 + h_ + 0.5, [t('0:01 人がぬいぐるみとカップを動かす → 追跡点で目標を更新\n0:18 掴んだぬいぐるみを人が抜き取る → 検知して掴み直す', '0:01 a person moves the toy and cup → target updated from tracked points\n0:18 the toy is pulled from the hand → detected, re-grasped'),
                                                      t('0:03 人が馬を動かす → 牛が最も近くなり、目標が牛に変わる\n0:14 人が梨を動かす → 距離を再計算し、再び馬へ', '0:03 a person moves the horse → the cow is now nearest, target switches\n0:14 the pear is moved → distances recomputed, back to the horse')])
caption(s, 0.5, 7.05, 12, 'Videos from zhoues.github.io/Code-as-Monitor (real-world demos, UR5 + Leap Hand), trimmed')

# ================================================================== 27 papers (#3) + VLS 28-37
papers_slide(2)

s = content_slide(CAT3, 28, size=22)
positioning(s, 2, [
    (t('入力', 'Input'), t('RGB-D 画像と指示、凍結した拡散／フローマッチングのポリシー', 'RGB-D images and the instruction, plus a frozen diffusion / flow policy')),
    (t('VLM の役割', 'Role of the VLM'), t('段階ごとの報酬関数を、微分可能な PyTorch のコードとして書く', 'Write a reward per stage as differentiable PyTorch code')),
    (t('出力の使い道', 'Where the output goes'), t('ポリシーのノイズ除去ループ。各ステップで報酬の勾配を足す', 'The policy\'s denoising loop: the reward gradient is added every step')),
    (t('ポリシーの扱い', 'What happens to the policy'), t('重みは変えない。生成の途中で行動が少しずつ曲げられる', 'Weights unchanged; the action is bent gradually during generation')),
])

s = content_slide(CAT3, 29, size=22)
add_picture(s, 'vls_fig1', 2.55, 3.35, w=8.2)
caption(s, 2.55, 7.15, 8, 'Fig. 1 in Liu et al., 2026')

s = content_slide(CAT3, 30, size=22)
add_picture(s, f'vls_compare_{LANG}.png', 0.8, 3.65, w=11.7, folder=S + '/diag/')

s = content_slide(CAT3, 31, size=20)
add_picture(s, 'vls_fig2', 0.5, 3.45, w=7.6)
caption(s, 0.5, 7.2, 8, 'Fig. 2 in Liu et al., 2026')
add_box(s, 8.5, 3.5, 4.5, 1.1, '', fill=GREEN_F, line=GREEN_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('使うモデル', 'Models used')], dict(size=13, bold=True)),
               ('opt', [t('キーポイント：SAM, DINOv2　報酬：GPT-4o 系の VLM　ベース：π0.5（LIBERO-PRO, 実機）, Diffusion Policy（CALVIN）', 'Keypoints: SAM, DINOv2.  Reward: GPT-4o-class VLM.  Base: π0.5 (LIBERO-PRO, real), Diffusion Policy (CALVIN)')], dict(size=12, bold=False))])
add_box(s, 8.5, 4.7, 4.5, 1.1, '', fill=YELLOW_F, line=YELLOW_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('報酬関数の制約', 'Constraints on the reward')], dict(size=13, bold=True)),
               ('opt', [t('距離・内積・ソフト制約など微分可能な torch 演算のみ。VLM 自体は計算グラフの外', 'Only differentiable torch ops (distances, dot products, soft constraints); the VLM stays off the graph')], dict(size=12, bold=False))])
add_box(s, 8.5, 5.9, 4.5, 1.1, '', fill=GRAY_F, line=GRAY_L, align=PP_ALIGN.LEFT,
        lines=[('opt', [t('段階の切り替え', 'Stage switching')], dict(size=13, bold=True)),
               ('opt', [t('報酬が閾値を超えたら VLM が実行結果を見て次の段階の報酬を選ぶ', 'When the reward crosses a threshold, the VLM inspects the outcome and picks the next stage reward')], dict(size=12, bold=False))])

s = content_slide(CAT3, 32, size=20)
add_eq(s, 'vls_guid', 0.7, 3.55, 7.0)
caption(s, 7.9, 3.6, 4.5, 'Eq. (5), (6), (7) in Liu et al., 2026', size=11)
add_picture(s, 'vls_loop', 0.7, 4.15, w=11.9)
for lab, eqn, x, w in [(t('候補を引き離す斥力（RBF）', 'Repulsion between candidates (RBF)'), 'vls_rbf', 0.7, 3.7), (t('報酬で重み付けした選別（FK）', 'Reward-weighted resampling (FK)'), 'vls_fk', 4.8, 4.0), (t('誘導の強さ λ の調整', 'Adaptive guidance strength λ'), 'vls_lam', 9.2, 3.4)]:
    add_text(s, x, 5.95, w, 0.35, [lab], size=13, bold=True, color=NAVY)
    add_eq(s, eqn, x, 6.3, w)
caption(s, 0.7, 7.1, 12, 'Fig. 2 (bottom), Eq. (8)–(10) in Liu et al., 2026')

s = content_slide(CAT3, 33, size=20)
step_row(s, [
    dict(img='vls_s1_kpset', head=t('① 3D の点を取り出す', '① Extract 3D keypoints'), body=t('かご = 点 2', 'basket = point 2'), w=0.9),
    dict(img='vls_s2_code', head=t('② VLM が報酬をコードで書く', '② VLM writes the reward as code'), body=t('軌道と点 2 の距離の二乗にマイナス', 'negative squared distance to point 2'), w=1.3),
    dict(img='vls_s3_loop_only', head=t('③ 各ステップで勾配を足す', '③ Add the gradient every step'), body=t('初期候補 → 斥力 → 補正 → 選別', 'init → repulsion → refine → resample'), w=1.5),
], y=3.75, h=3.0, head_fill=[(GREEN_F, GREEN_L), (GREEN_F, GREEN_L), (GREEN_F, GREEN_L)])
caption(s, 0.5, 7.05, 12, 'Images from Fig. 2 in Liu et al., 2026')

s = content_slide(CAT3, 34)
add_picture(s, 'vls_tab1', 0.5, 3.5, w=7.4)
add_picture(s, 'vls_fig3', 0.5, 5.1, w=7.4)
add_picture(s, 'vls_abl', 8.2, 3.5, w=4.8)
add_picture(s, 'vls_scale', 8.2, 5.1, w=4.8)
caption(s, 0.5, 6.95, 7, 'Table I, Fig. 3 in Liu et al., 2026')
caption(s, 8.2, 6.5, 4.8, t('Fig. 4 in Liu et al., 2026（左：Ablation、右：サンプル数のスケーリング）', 'Fig. 4 in Liu et al., 2026 (left: ablation, right: scaling with the number of samples)'))

s = content_slide(CAT3, 35, size=22)
h_, pos = video_row(s, [('vls_libero_base_cut', t('LIBERO-PRO：π0.5（失敗）', 'LIBERO-PRO: π0.5 (fail)')), ('vls_libero_vls', t('LIBERO-PRO：+VLS（成功）', 'LIBERO-PRO: +VLS (success)')), ('vls_coll_base_cut', t('壁を避ける：ベース（失敗）', 'Avoid the wall: base (fail)')), ('vls_coll_vls', t('壁を避ける：+VLS（成功）', 'Avoid the wall: +VLS (success)'))], 3.35, total_w=11.0, x0=1.15, gap=0.3)
callouts(s, pos, 3.35 + h_ + 0.5, [t('学習時の位置へ向かい、空振りする', 'Reaches for the training-time spot and misses'),
                                    t('数字付きの点が目標。報酬で補正される', 'Numbered points are the targets; corrected by reward'),
                                    t('「壁を避けて」を知らず、壁にぶつかる', 'Does not know "avoid the wall"; hits it'),
                                    t('壁から遠いほど高報酬 → 迂回する', 'Reward grows away from the wall → detours')])
caption(s, 0.5, 7.05, 12, 'Videos from vision-language-steering.github.io (LIBERO-PRO position perturbation, collision avoidance), trimmed')

s = content_slide(CAT3, 36)
add_picture(s, 'vls_fig5', 0.5, 3.45, w=12.3)
caption(s, 0.5, 7.0, 8, 'Fig. 5 in Liu et al., 2026')

s = content_slide(CAT3, 37, size=22)
h_, pos = video_row(s, [('vls_real_banana', t('同じ条件：バナナを緑の皿に', 'In-distribution: banana on green plate')), ('vls_real_mug', t('未知の物体：マグを皿に', 'Unseen object: mug on plate')), ('vls_real_pos', t('皿の位置を入れ替え', 'Plates swapped'))], 3.4, gap=0.3)
callouts(s, pos, 3.4 + h_ + 0.5, [t('左上の Guide が誘導の有無、Sig_Str が強さ。仕上げで弱まる', 'Top-left: Guide on/off, Sig_Str = strength; it weakens near the end'),
                                   t('学習にないマグでも、点との距離で報酬が書けるので掴める', 'A mug never seen in training; distance-to-point rewards still work'),
                                   t('指示は同じ。皿の位置を点で取り直すだけで追従する', 'Same instruction; re-extracted plate points are enough to follow')])
caption(s, 0.5, 7.05, 12, 'Videos from vision-language-steering.github.io (real-world Franka rollouts)')

# ================================================================== 38 summary (bullets + table)
s = new_slide('Insights', slide_title(38))
add_bullets(s, 38, size=18, spacing=120)
hdr = ['', 'SimFoundry', 'Code-as-Monitor', 'VLS']
rows = [
    (t('VLM の出力', 'VLM output'), t('物体の 3D モデルと物性、配置・タスクの提案', '3D objects with properties; layout / task proposals'), t('制約文と判定コード', 'Constraint sentences + checking code'), t('報酬関数のコード', 'Reward-function code')),
    (t('入れ先', 'Enters at'), t('学習データ（配備前）', 'Training data (before deployment)'), t('実行を止める条件（実行中）', 'A stop condition (during execution)'), t('行動生成の目的関数（生成中）', 'The objective of generation (during generation)')),
    (t('ポリシーへの影響', 'Effect on the policy'), t('学習データが増える。重みは学習で変わる', 'More training data; weights change by training'), t('重みは不変。失敗時に止めて再計画', 'Weights unchanged; stop and re-plan on failure'), t('重みは不変。生成される行動がその場で変わる', 'Weights unchanged; the generated action changes on the spot')),
    (t('主な効果', 'Main effect'), t('Sim 評価 r = 0.91、変種で実機 +17〜40%', 'Sim eval r = 0.91; variants +17-40% real'), t('外乱下 +12 pt、長期タスク 0 → 90%', '+12 pt under disturbance; 0 → 90% long-horizon'), t('LIBERO-PRO +13 pt、実機 +19〜27 pt', 'LIBERO-PRO +13 pt; real +19-27 pt')),
    (t('コスト', 'Cost'), t('再構成 約5分/物体。実行時は VLM 不要', '~5 min per object; no VLM at run time'), t('VLM はサブゴールごとに1回', 'One VLM call per subgoal'), t('約1秒/チャンク。VLM の誤りが行動に直結', '~1 s per chunk; VLM errors hit the action directly')),
]
tbl = s.shapes.add_table(len(rows) + 1, 4, inch(0.6), inch(4.2), inch(12.1), inch(2.8)).table
tbl.columns[0].width = inch(1.9); tbl.columns[1].width = inch(3.4); tbl.columns[2].width = inch(3.4); tbl.columns[3].width = inch(3.4)
colf = [GRAY_F, BLUE_F, ORANGE_F, GREEN_F]
for j, val in enumerate(hdr):
    c = tbl.cell(0, j); c.text = ''
    add_runs(c.text_frame.paragraphs[0], val, size=14, bold=True, color=NAVY)
    c.margin_top = c.margin_bottom = inch(0.03)
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(colf[j])
for i, row in enumerate(rows, start=1):
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.text = ''
        add_runs(c.text_frame.paragraphs[0], val, size=12, bold=(j == 0))
        c.margin_top = c.margin_bottom = inch(0.04)
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string('F2F2F2' if j == 0 else ('FFFFFF' if i % 2 else 'FAFAFA'))

# ================================================================== 39 own work
s = content_slide('Insights', 39, size=22)
h_, pos = video_row(s, [('own_demo1', t('LIBERO-Goal：誘導 + 監視', 'LIBERO-Goal: steering + monitoring')), ('own_demo2', t('LIBERO-Object：誘導 + 監視', 'LIBERO-Object: steering + monitoring'))], 3.45, total_w=12.3, gap=0.4)
caption(s, 0.5, 7.0, 12, 'Own preliminary experiments (LIBERO), 2026')

prs.save(OUT)
print('saved', OUT, 'slides:', len(prs.slides))
