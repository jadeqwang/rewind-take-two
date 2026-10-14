#!/usr/bin/env python
"""Book titles on the two C_coop books (v8, Jade's idea after v7): 2:09.2-2:14.9 (C1_hold, C2a_swap, C2b_letgo).

The plate's two leaning books have blank covers. Each cover gets an engraved-style title page drawn flat (IM Fell
English, a double-rule frame, author in italic at the foot) and warped onto the cover quad by a perspective
transform, then laid in as ink (alpha 0.92, a 0.4 px blur so it sits in the hatching). Pixel pass only.

  left (orange side):  NONLINEAR DYNAMICS and CHAOS, Steven H. Strogatz  (real title, no "Theory")
  right (blue side):   THE ELEGANT UNIVERSE, Brian Greene

Writes media/shots/C_coop/plate_titled.png, which tools/sections/D/build_timeline.py uses as the plate.
Note: the engine caches images by path, so a redraw needs a new filename or a cleared media/engine_cache.

  ~/Documents/moongazing/.venv/bin/python tools/book_titles.py [OUT]
"""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='render/fonts/'
W,H=500,1400   # flat cover canvas (cover is ~165x470 px on plate, so ~3x)
INK=(28,24,22)

def coeffs(dst, src):
    # PIL PERSPECTIVE wants output(dst)->input(src) mapping
    A=[];B=[]
    for (x,y),(u,v) in zip(dst,src):
        A+= [[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]; B+=[u,v]
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()

def centered(d, y, text, font, tracking=0):
    w=d.textlength(text,font=font)+tracking*(len(text)-1)
    while w>W-150:   # keep inside the inner rule with a margin
        font=font.font_variant(size=font.size-2)
        w=d.textlength(text,font=font)+tracking*(len(text)-1)
    x=(W-w)/2
    for ch in text:
        d.text((x,y),ch,font=font,fill=255); x+=d.textlength(ch,font=font)+tracking

def cover(lines):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    # engraved double-rule frame
    d.rectangle([34,40,W-34,H-40],outline=255,width=7)
    d.rectangle([52,58,W-52,H-58],outline=255,width=3)
    for y,text,font,tr in lines: centered(d,y,text,font,tr)
    return m

fell=lambda s: ImageFont.truetype(F+'IMFeENrm28P.ttf',s)
felli=lambda s: ImageFont.truetype(F+'IMFeENit28P.ttf',s)

strogatz=cover([
  (150,'NONLINEAR',fell(78),4),(245,'DYNAMICS',fell(78),4),
  (345,'and',felli(64),0),(425,'CHAOS',fell(104),6),
  (1210,'Steven H. Strogatz',felli(50),0)])
greene=cover([
  (150,'THE',fell(66),6),(230,'ELEGANT',fell(92),4),(345,'UNIVERSE',fell(84),3),
  (1210,'Brian Greene',felli(56),0)])

plate=Image.open('media/shots/C_coop/plate.png').convert('RGB')
# cover corners on the 1920x1080 plate (TL, TR, BR, BL of the title page)
quads={'L':[(150,75),(315,135),(415,540),(275,600)],
       'R':[(1615,132),(1790,75),(1660,605),(1510,545)]}
out=plate.copy()
for key,mask in [('L',strogatz),('R',greene)]:
    q=quads[key]
    warped=mask.transform(plate.size,Image.PERSPECTIVE,
        coeffs([(x,y) for x,y in q],[(0,0),(W,0),(W,H),(0,H)]),Image.BICUBIC)
    warped=warped.filter(ImageFilter.GaussianBlur(0.4))
    ink=Image.new('RGB',plate.size,INK)
    out=Image.composite(ink,out,warped.point(lambda v:int(v*0.92)))
out.save(sys.argv[1] if len(sys.argv) > 1 else 'media/shots/C_coop/plate_titled.png')
