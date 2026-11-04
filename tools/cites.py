# -*- coding: utf-8 -*-
"""Render [Author+ year] citations one step smaller than the surrounding text."""
import copy, re
from pptx.util import Pt
from pptx.text.text import _Run

CITE = re.compile(r'\[[^\[\]]*?(?:19|20)\d{2}\]')


def iter_frames(slide):
    for sh in slide.shapes:
        if sh.has_text_frame:
            yield sh.text_frame
        elif sh.shape_type == 19:
            for r in sh.table.rows:
                for c in r.cells:
                    yield c.text_frame


def para_size(para, default=18.0):
    for r in para.runs:
        if r.font.size is not None:
            return r.font.size.pt
    return default


def shrink_cites(prs, step=2):
    n = 0
    for slide in prs.slides:
        for tf in iter_frames(slide):
            for para in tf.paragraphs:
                base = para_size(para)
                for run in list(para.runs):
                    txt = run.text
                    if not CITE.search(txt):
                        continue
                    # already shrunk? (run is exactly a citation and smaller than base)
                    sz = run.font.size.pt if run.font.size is not None else base
                    parts = []
                    pos = 0
                    for m in CITE.finditer(txt):
                        if m.start() > pos:
                            parts.append((txt[pos:m.start()], False))
                        parts.append((m.group(0), True))
                        pos = m.end()
                    if pos < len(txt):
                        parts.append((txt[pos:], False))
                    r = run._r; parent = r.getparent(); idx = parent.index(r)
                    parent.remove(r)
                    for i, (t, is_cite) in enumerate(parts):
                        nr = copy.deepcopy(r)
                        parent.insert(idx + i, nr)
                        nrun = _Run(nr, para)
                        nrun.text = t
                        if is_cite:
                            nrun.font.size = Pt(max(sz - step, 6))
                            n += 1
    return n
