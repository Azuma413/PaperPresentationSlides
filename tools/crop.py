from PIL import Image
import os
S=1.5  # 200dpi -> 300dpi
crops = {
 # name: (page image, (x0,y0,x1,y1) in 200dpi px)
 'cam_fig1':   ('cam-01', (160, 668, 1548, 1170)),
 'cam_fig1a':  ('cam-01', (163, 726, 748, 1138)),
 'cam_fig2':   ('cam-03', (150, 198, 1545, 825)),
 'cam_code':   ('cam-03', (950, 203, 1540, 418)),
 'cam_fig3':   ('cam-04', (160, 196, 1548, 502)),
 'cam_fig4':   ('cam-05', (160, 200, 840, 552)),
 'cam_tab1':   ('cam-06', (880, 297, 1535, 517)),
 'cam_tab2':   ('cam-07', (160, 228, 1540, 372)),
 'cam_fig5':   ('cam-07', (160, 409, 1540, 650)),
 'cam_tab3':   ('cam-07', (160, 808, 820, 1046)),
 'cam_tab4':   ('cam-07', (160, 1276, 820, 1432)),
 'cam_tab5':   ('cam-07', (880, 814, 1540, 1068)),
 'cam_fig6':   ('cam-08', (160, 203, 1540, 690)),
 'cam_tab6':   ('cam-08', (160, 858, 820, 1012)),
 'cam_tab9':   ('cam-20', (160, 847, 1540, 1046)),
 'cam_fig11':  ('cam-20', (160, 210, 1540, 693)),
 'vls_fig1':   ('vls-01', (137, 533, 1562, 1128)),
 'vls_ood':    ('vls-01', (368, 616, 600, 1100)),
 'vls_fig2':   ('vls-05', (137, 143, 1562, 842)),
 'vls_loop':   ('vls-05', (205, 652, 1562, 842)),
 'vls_stage':  ('vls-05', (1160, 412, 1562, 610)),
 'vls_reward': ('vls-05', (572, 412, 1155, 610)),
 'vls_ground': ('vls-05', (572, 143, 1562, 390)),
 'vls_tab1':   ('vls-07', (247, 126, 1452, 363)),
 'vls_fig3':   ('vls-07', (137, 495, 1562, 858)),
 'vls_abl':    ('vls-08', (137, 132, 847, 325)),
 'vls_scale':  ('vls-08', (863, 132, 1562, 325)),
 'vls_fig5':   ('vls-08', (137, 462, 1562, 891)),
 'sf_fig1':    ('sf-01', (193, 632, 1474, 1123)),
 'sf_tab1':    ('sf-03', (150, 328, 1480, 883)),
 'sf_fig2':    ('sf-04', (173, 234, 1480, 954)),
 'sf_fig2_top':('sf-04', (173, 234, 1480, 571)),
 'sf_fig2_bot':('sf-04', (173, 605, 1480, 954)),
 'sf_fig3':    ('sf-06', (173, 234, 1480, 591)),
 'sf_tasks':   ('sf-07', (173, 234, 796, 848)),
 'sf_scatter': ('sf-07', (854, 234, 1480, 848)),
 'sf_fig5':    ('sf-08', (173, 234, 1480, 538)),
}
for name,(pg,(x0,y0,x1,y1)) in crops.items():
    im=Image.open(f'hi300/{pg}.png')
    box=tuple(int(round(v*S)) for v in (x0,y0,x1,y1))
    c=im.crop(box)
    c.save(f'figs/{name}.png')
    print(name, c.size)
# contact sheet
import math
names=list(crops)
thumbs=[]
for n in names:
    im=Image.open(f'figs/{n}.png'); im.thumbnail((500,300)); thumbs.append((n,im))
cols=4; rows=math.ceil(len(thumbs)/cols)
sheet=Image.new('RGB',(cols*520,rows*330),'white')
from PIL import ImageDraw
d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(thumbs):
    x=(i%cols)*520+10; y=(i//cols)*330+10
    sheet.paste(im,(x,y+20)); d.text((x,y),n,fill='red')
sheet.save('figs_sheet.jpg',quality=75)
