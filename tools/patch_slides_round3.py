# -*- coding: utf-8 -*-
"""Round 3 on the Japanese deck: shorten the ablation bullet (p.22) and shrink citations.
usage: python3 patch7.py <in.pptx> <out_noshrink.pptx> <out_final.pptx>
"""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-PaperPresentationSlides/b16a4cd5-a6b6-52ff-a060-bdd5dfede159/scratchpad')
from pptx import Presentation
from cites import shrink_cites, iter_frames

IN, OUT_NOSHRINK, OUT_FINAL = sys.argv[1:4]
P = Presentation(IN)

REPS = [
    ('：多視点、部位の切り出し、点群の連結が重要（65% → 40〜55%）', '：多視点・部位分割・点の連結を外すと 65% → 40〜55%'),
]
hits = 0
for slide in P.slides:
    for tf in iter_frames(slide):
        for para in tf.paragraphs:
            for run in para.runs:
                for a, b in REPS:
                    if a in run.text:
                        run.text = run.text.replace(a, b); hits += 1
print('replacements', hits)
P.save(OUT_NOSHRINK)
n = shrink_cites(P)
print('citations shrunk', n)
P.save(OUT_FINAL)
