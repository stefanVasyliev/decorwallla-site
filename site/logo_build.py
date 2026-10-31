# Rebuilds assets/logo-white.svg and logo-black.svg: the slat mark, measured from the supplied logo, plus the
# wordmark set in Outfit (SemiBold / Regular) converted to outlines. Needs fonttools and the Outfit TTF files.
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
def text_path(fontfile, text, x, baseline, cap_px, tracking=0):
    f=TTFont(fontfile); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
    cap=f['OS/2'].sCapHeight or upm*0.7
    sc=cap_px/cap; d=[]
    for ch in text:
        g=cmap[ord(ch)]; pen=SVGPathPen(gs)
        gs[g].draw(TransformPen(pen,(sc,0,0,-sc,x,baseline)))
        d.append(pen.getCommands()); x+=gs[g].width*sc+tracking
    return " ".join(d), x
# mark, measured from the supplied logo (2000 x 1125 canvas)
def mark():
    top=lambda x: 380+(x-212)*80/230
    bot=lambda x: 713-(x-212)*58/230
    bars=[(212,275),(292,320),(336,362),(377,402),(417,442)]
    return " ".join(f"M{a} {top(a):.1f}L{b} {top(b):.1f}L{b} {bot(b):.1f}L{a} {bot(a):.1f}Z" for a,b in bars)
def build(bold, reg, fill, out, cap=147):
    d1,x=text_path(bold,"DecorWall",520,620,cap,-2)
    d2,x2=text_path(reg,"LA",x+60,620,cap,4)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="200 370 {x2-200+10:.0f} 355" fill="{fill}"><path d="{mark()}"/><path d="{d1}"/><path d="{d2}"/></svg>'
    open(out,'w').write(svg); return x2
if __name__=="__main__":
    for name,b,r in [("outfit","QGYyz_MVcBeNP4NjuGObqx1XmO1I4e6yC4E.ttf","QGYyz_MVcBeNP4NjuGObqx1XmO1I4TC1C4E.ttf"),
                     ("lexend","wlptgwvFAVdoq2_F94zlCfv0bz1WC-UR_LA.ttf","wlptgwvFAVdoq2_F94zlCfv0bz1WCzsW_LA.ttf"),
                     ("urbanist","L0xjDF02iFML4hGCyOCpRdycFsGxSrqDLBkfFg.ttf","L0xjDF02iFML4hGCyOCpRdycFsGxSrqDyx4fFg.ttf")]:
        print(name, build(b,r,"#000",f"{name}.svg"))
