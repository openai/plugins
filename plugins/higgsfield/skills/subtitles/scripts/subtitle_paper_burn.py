#!/usr/bin/env python3
"""subtitle_paper_burn.py — burn subtitles as handwritten text on real-looking
TORN PAPER labels. Each caption is rendered (PIL) as a cream paper scrap with
deckled edges, fiber grain and a soft shadow, plus the caption text in a chosen
font, then overlaid on the video timed to its window, low in the frame.

Readability:
  - each caption is HELD until the next one appears (so it never vanishes early)
    while speech is continuous (gap <= --bridge, default 1.0s); across a real
    PAUSE the caption dies --tail seconds after its own speech ends instead of
    lingering into the silence. Minimum on-screen time still applies.
  - text auto-fits the paper: it word-wraps to the label width (--maxw-frac) and,
    if a single word is still too wide, the font shrinks — so bold/wide fonts
    (marker, anton) and narrow 9:16 frames never spill past the scrap.

Styles (--style):
  paper  torn cream paper label, dark handwritten text (default)
  bold   UGC caption look — ALL-CAPS, white fill with a thick black stroke,
         no plate, bottom-anchored in platform safe zones (portrait uses the
         IG Reels spec: bottom 16.7% H, sides 11% W; landscape 17% / 7.5%),
         ONE fitted font size for the whole video, max 2 balanced lines.
         No animation, no emoji — static overlays like paper. Paper's bottom
         margin is also raised to 17% on portrait for the same reason.

Fonts (pick per video style with --font-key, or pass --font <path>):
  patrick     Patrick Hand      — legible handwritten (paper default)
  caveat      Caveat            — flowing cursive script
  marker      Permanent Marker  — bold marker / punchy
  anton       Anton             — heavy condensed display / impact
  montserrat  Montserrat XBold  — clean geometric caps (bold default)
  metropolis  Metropolis XBold  — drop-in alternative (add the .ttf yourself)
The script checks scripts/fonts/ first and then uses fontconfig to find a
compatible system font. Pass --font for an exact face.

Usage:
  subtitle_paper_burn.py --in v.mp4 --srt subs.srt --out out.mp4
     [--style paper|bold] [--font-key patrick|caveat|marker|anton|montserrat|metropolis]
     [--font PATH] [--fontsize-frac 0.055] [--bottom-frac 0.06] [--maxw-frac 0.8]
     [--min-dur 1.2] [--gap 0.06] [--tail 0.6]
"""
import sys, os, re, argparse, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

FONT_FILES = {
    "patrick":    "PatrickHand-Regular.ttf",
    "caveat":     "Caveat-Regular.ttf",
    "marker":     "PermanentMarker-Regular.ttf",
    "anton":      "Anton-Regular.ttf",
    "montserrat": "Montserrat-ExtraBold.ttf",   # bold style default (UGC caps)
    "metropolis": "Metropolis-ExtraBold.ttf",   # drop-in if the file is added
}

# Per-style defaults (used when the flag is not passed explicitly).
# Two margin profiles: landscape keeps the classic low placement; portrait
# follows the Instagram Reels/Stories safe zones (1080x1920 basis: bottom
# 320px = 16.7% H, sides 120px = 11.1% W -> usable width 78%).
STYLE_DEFAULTS = {
    #          font-key      size-frac  bottom-frac(land, port)  maxw-frac(land, port)
    "paper": ("patrick",     0.032,     (0.10, 0.17),            (0.72, 0.72)),
    "bold":  ("montserrat",  0.046,     (0.17, 0.17),            (0.85, 0.77)),
}


def parse_srt(p):
    out=[]
    for b in re.split(r"\n\s*\n", open(p,encoding="utf-8").read().strip()):
        m=re.search(r"(\d\d:\d\d:\d\d[,.]\d+)\s*-->\s*(\d\d:\d\d:\d\d[,.]\d+)", b)
        if not m: continue
        def sec(t):
            t=t.replace(",","."); h,mm,s=t.split(":"); return int(h)*3600+int(mm)*60+float(s)
        lines=[l for l in b.splitlines() if "-->" not in l and not l.strip().isdigit()]
        text=" ".join(lines).strip()
        if text: out.append((sec(m.group(1)),sec(m.group(2)),text))
    return out


def hold_captions(caps, min_dur, max_dur, gap, tail, bridge=1.0):
    """Hold each caption until the next appears ONLY across a short gap
    (<= bridge seconds, i.e. continuous speech — no flicker between chunks).
    Across a real pause (block tails: measured 2-3.3s of silence) the caption
    must NOT linger: it dies tail seconds after its own speech ends. Without
    the bridge condition the last chunk of every block sat on screen up to
    max_dur into the silence ('sticky last word', dev matrix 2026-07-21)."""
    caps=sorted(caps,key=lambda c:c[0]); ext=[]
    for i,(s,e,t) in enumerate(caps):
        if i+1 < len(caps) and (caps[i+1][0]-e) <= bridge:
            ne = min(caps[i+1][0]-gap, s+max_dur)     # up to next, capped by max_dur
            if ne < s+0.1: ne = caps[i+1][0]-gap
        else:
            ne = min(max(e+tail, s+min_dur), s+max_dur)
        ext.append((s,ne,t))
    return ext


def probe_wh(v):
    r=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
        "stream=width,height","-of","csv=p=0",v],capture_output=True,text=True).stdout.strip()
    w,h=r.split(","); return int(w),int(h)


def _torn_profile(n, amp, rng):
    x=rng.normal(0,1,n).cumsum(); x=x-x.min(); x=x/(x.max()+1e-6)
    k=max(5,n//12); x=np.convolve(x,np.ones(k)/k,mode="same")
    x=x-x.min(); x=x/(x.max()+1e-6)
    return (x*amp).astype(int)


def _geo(font):
    """padding + torn-edge amplitude, all scaled to the font size."""
    return int(font.size*0.85), int(font.size*0.5), max(4,int(font.size*0.16))


def _ink_w(draw, s, font):
    """Real inked width of a string (textbbox), not the advance width — bold /
    marker fonts overshoot their advance, so advance-based sizing spills."""
    l,_,r,_=draw.textbbox((0,0),s,font=font); return r-l


def _fit_font(draw, text, font, max_w, min_size=12):
    """Shrink the font until the single widest WORD fits in max_w, so no word
    can ever overflow the label (wrapping then handles the rest)."""
    words=text.split() or [text]
    while font.size>min_size:
        widest=max(_ink_w(draw,w,font) for w in words)
        if widest<=max_w: break
        font=ImageFont.truetype(font.path,max(min_size,int(font.size*0.9)))
    return font


def _wrap_lines(draw, text, font, max_w):
    """Greedy word-wrap so every line's inked width fits in max_w (a lone
    over-wide word, already shrunk by _fit_font, keeps its own line)."""
    lines=[]; cur=""
    for w in text.split():
        trial=w if not cur else cur+" "+w
        if _ink_w(draw,trial,font)<=max_w or not cur:
            cur=trial
        else:
            lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines or [text]


def paper_label(text, font, W, H, bottom_frac, maxw_frac):
    tmp=ImageDraw.Draw(Image.new("RGBA",(10,10)))
    box_max=int(W*maxw_frac)
    # Fit the font so the widest word fits, then wrap the caption to that width.
    # This is what keeps bold/wide fonts (marker, anton) and narrow 9:16 frames
    # inside the paper scrap instead of spilling past its edges.
    padx,pady,amp=_geo(font)
    font=_fit_font(tmp,text,font,max(1,box_max-2*padx-2*amp))
    padx,pady,amp=_geo(font)
    max_text_w=max(1,box_max-2*padx-2*amp)
    lines=_wrap_lines(tmp,text,font,max_text_w)
    bbs=[tmp.textbbox((0,0),ln,font=font) for ln in lines]
    line_ws=[b[2]-b[0] for b in bbs]
    asc,desc=font.getmetrics(); line_h=asc+desc; line_gap=int(line_h*0.14)
    text_w=int(max(line_ws)); text_h=len(lines)*line_h+(len(lines)-1)*line_gap
    lw=text_w+2*padx+2*amp; lh=text_h+2*pady+2*amp
    rng=np.random.default_rng(abs(hash(text))%99999)
    mask=np.ones((lh,lw),bool)
    top=_torn_profile(lw,amp,rng); bot=_torn_profile(lw,amp,rng)
    left=_torn_profile(lh,amp,rng); right=_torn_profile(lh,amp,rng)
    for x in range(lw):
        mask[:top[x],x]=False
        if bot[x]: mask[lh-bot[x]:,x]=False
    for y in range(lh):
        mask[y,:left[y]]=False
        if right[y]: mask[y,lw-right[y]:]=False
    alpha=(mask*255).astype(np.uint8)
    base=np.zeros((lh,lw,3),float)+np.array([245,241,231])
    base+=rng.normal(0,9,(lh,lw,1)); base+=rng.normal(0,5,(lh,1,1))
    base=np.clip(base,0,255)
    lab=Image.fromarray(np.dstack([base.astype(np.uint8),alpha]),"RGBA").filter(ImageFilter.GaussianBlur(0.4))
    d=ImageDraw.Draw(lab)
    y0=pady+amp
    for k,(ln,b) in enumerate(zip(lines,bbs)):
        tw=b[2]-b[0]; th=b[3]-b[1]
        x=(lw-tw)//2-b[0]                                   # center ink, correct side bearing
        y=y0+k*(line_h+line_gap)+(line_h-th)//2-b[1]        # center ink in its line slot
        d.text((x,y),ln,font=font,fill=(38,32,28,255))
    lx=(W-lw)//2; ly=H-int(H*bottom_frac)-lh
    canvas=Image.new("RGBA",(W,H),(0,0,0,0)); sh=Image.new("RGBA",(W,H),(0,0,0,0))
    shp=Image.fromarray(np.dstack([np.zeros((lh,lw,3),np.uint8),(mask*140).astype(np.uint8)]),"RGBA")
    sh.paste(shp,(lx+int(amp*0.7),ly+int(amp*1.1)),shp)
    sh=sh.filter(ImageFilter.GaussianBlur(max(3,int(lh*0.06))))
    canvas.alpha_composite(sh); canvas.alpha_composite(lab,(lx,ly))
    return canvas


def _balanced_two_lines(draw, text, font, max_w):
    """One line if it fits; otherwise the 2-line split that minimizes the longer
    line (the scrollbait/capsmith look). Returns None if even the best 2-line
    split overflows max_w (caller shrinks the font and retries)."""
    if _ink_w(draw, text, font) <= max_w: return [text]
    words = text.split()
    if len(words) < 2: return None
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wid = max(_ink_w(draw, a, font), _ink_w(draw, b, font))
        if best is None or wid < best[0]: best = (wid, [a, b])
    return best[1] if best[0] <= max_w else None


def bold_fit_size(draw, texts, path, size, max_w, min_size=14):
    """ONE font size for the whole video (captions must not jump between
    phrases): the largest size at which EVERY caption fits max_w in <=2
    balanced lines."""
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if all(_balanced_two_lines(draw, t, f, max_w) for t in texts): break
        size = int(size * 0.94)
    return max(size, min_size)


def bold_label(text, font, W, H, bottom_frac, maxw_frac):
    """UGC caption style (no plate): ALL-CAPS, white fill, thick black stroke,
    bottom-anchored inside platform safe zones. No animation, no emoji."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    max_w = int(W * maxw_frac)
    lines = _balanced_two_lines(tmp, text, font, max_w) or _wrap_lines(tmp, text, font, max_w)[:2]
    stroke = max(3, round(font.size * 0.07))
    asc, desc = font.getmetrics(); line_h = asc + desc + 2 * stroke
    line_gap = int(line_h * 0.06)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    total_h = len(lines) * line_h + (len(lines) - 1) * line_gap
    y0 = H - int(H * bottom_frac) - total_h
    for k, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=font, stroke_width=stroke)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        y = y0 + k * (line_h + line_gap) - bb[1]
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 235))
    return canvas


def resolve_font(font_arg, font_key):
    if font_arg: return font_arg
    d=os.path.join(os.path.dirname(os.path.abspath(__file__)),"fonts")
    fn=FONT_FILES.get(font_key, FONT_FILES["patrick"])
    p=os.path.join(d,fn)
    if not os.path.exists(p):
        for alt_key in ("montserrat","caveat"):
            alt=os.path.join(d,FONT_FILES[alt_key])
            if os.path.exists(alt):
                print(f"(font {fn} missing -> falling back to {alt_key})",file=sys.stderr); return alt
        families = {
            "patrick": "DejaVu Sans",
            "caveat": "DejaVu Sans",
            "marker": "DejaVu Sans:style=Bold",
            "anton": "DejaVu Sans Condensed:style=Bold",
            "montserrat": "DejaVu Sans:style=Bold",
            "metropolis": "DejaVu Sans:style=Bold",
        }
        try:
            system_font=subprocess.check_output(
                ["fc-match","-f","%{file}",families.get(font_key,"DejaVu Sans")],
                text=True,
            ).strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            system_font=""
        if system_font and os.path.exists(system_font):
            print(f"(font {fn} missing -> using system font {system_font})",file=sys.stderr)
            return system_font
        raise SystemExit(
            f"font not found: {p}; pass --font /path/to/a/covering-font.ttf"
        )
    return p


def _covers(font_path, text, size=48):
    """True when the font can draw EVERY letter of `text`.
    Checked per character: a Latin-only face draws punctuation fine but renders
    nothing for e.g. Cyrillic letters, which used to ship as an EMPTY paper
    label. So one blank letter = no coverage."""
    letters=[ch for ch in dict.fromkeys(text) if ch.isalpha()][:60]
    if not letters: return True
    try: f=ImageFont.truetype(font_path,size)
    except Exception: return False
    for ch in letters:
        img=Image.new("L",(size*3,size*3),0)
        ImageDraw.Draw(img).text((size//2,size//2),ch,font=f,fill=255)
        if img.getbbox() is None:
            return False
    return True


def font_for_text(font_arg, font_key, texts):
    """Resolve the font, then GUARANTEE it can draw the captions: fall back through
    bundled broad faces and system fonts, and warn about the swap."""
    path=resolve_font(font_arg,font_key)
    joined="".join(texts)
    if _covers(path,joined): return path
    d=os.path.join(os.path.dirname(os.path.abspath(__file__)),"fonts")
    for alt_key in ("montserrat","anton","caveat"):
        alt=os.path.join(d,FONT_FILES[alt_key])
        if os.path.exists(alt) and _covers(alt,joined):
            print(f"WARN: {os.path.basename(path)} has no glyphs for this text "
                  f"(script/language mismatch) -> using {alt_key} instead",file=sys.stderr)
            return alt
    for family in ("Noto Sans","DejaVu Sans","Liberation Sans"):
        try:
            alt=subprocess.check_output(
                ["fc-match","-f","%{file}",family],text=True
            ).strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
        if alt and os.path.exists(alt) and _covers(alt,joined):
            print(f"WARN: {os.path.basename(path)} has no glyphs for this text "
                  f"-> using system font {alt}",file=sys.stderr)
            return alt
    print(f"WARN: no available font covers this text; captions may render empty "
          f"({os.path.basename(path)})",file=sys.stderr)
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--in",dest="inp",required=True); ap.add_argument("--srt",required=True)
    ap.add_argument("--out",default="paper_subbed.mp4")
    ap.add_argument("--style",default="paper",choices=list(STYLE_DEFAULTS),
                    help="paper = torn cream label; bold = UGC ALL-CAPS white with black stroke (no plate)")
    ap.add_argument("--font-key",default=None,choices=list(FONT_FILES))
    ap.add_argument("--font",default="")
    ap.add_argument("--fontsize-frac",type=float,default=None)
    ap.add_argument("--bottom-frac",type=float,default=None)
    ap.add_argument("--maxw-frac",type=float,default=None)
    ap.add_argument("--min-dur",type=float,default=1.2)
    ap.add_argument("--max-dur",type=float,default=3.5)
    ap.add_argument("--gap",type=float,default=0.06)
    ap.add_argument("--tail",type=float,default=0.6)
    ap.add_argument("--bridge",type=float,default=1.0,
                    help="hold a caption up to the next one only if the silence between them is <= this (s)")
    a=ap.parse_args()
    W,H=probe_wh(a.inp)
    portrait = 1 if H > W else 0
    dk,dsize,dbottom,dmaxw=STYLE_DEFAULTS[a.style]
    font_key=a.font_key or dk
    size_frac=a.fontsize_frac if a.fontsize_frac is not None else dsize
    bottom_frac=a.bottom_frac if a.bottom_frac is not None else dbottom[portrait]
    maxw_frac=a.maxw_frac if a.maxw_frac is not None else dmaxw[portrait]
    caps=hold_captions(parse_srt(a.srt),a.min_dur,a.max_dur,a.gap,a.tail,a.bridge)
    if not caps: print("no captions"); sys.exit(1)
    # Resolve the font AGAINST THE ACTUAL CAPTION TEXT so a Latin-only face can
    # never ship empty labels for Cyrillic/other scripts.
    font_path=font_for_text(a.font,font_key,[t for _,_,t in caps])
    font=ImageFont.truetype(font_path,int(H*size_frac))
    if a.style=="bold":
        # ALL-CAPS + ONE size across the whole video (captions must not jump).
        caps=[(s,e,t.upper()) for s,e,t in caps]
        tmp=ImageDraw.Draw(Image.new("RGBA",(10,10)))
        size=bold_fit_size(tmp,[t for _,_,t in caps],font_path,int(H*size_frac),int(W*maxw_frac))
        font=ImageFont.truetype(font_path,size)
    render=bold_label if a.style=="bold" else paper_label
    td=tempfile.mkdtemp(); pngs=[]
    for i,(s,e,t) in enumerate(caps):
        p=os.path.join(td,f"c{i:03d}.png"); render(t,font,W,H,bottom_frac,maxw_frac).save(p)
        pngs.append((p,s,e))
    inputs=["-i",a.inp]
    for p,_,_ in pngs: inputs+=["-i",p]
    fc=""; cur="[0:v]"
    for idx,(p,s,e) in enumerate(pngs):
        nxt=f"[v{idx}]"; fc+=f"{cur}[{idx+1}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'{nxt};"; cur=nxt
    fc=fc.rstrip(";")
    cmd=["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",fc,"-map",cur,"-map","0:a?",
         "-c:a","copy","-c:v","libx264","-preset","veryfast","-crf","20","-movflags","+faststart",a.out]
    print(f"[{a.style}-burn] {len(caps)} captions ({font_key}) -> {a.out}",file=sys.stderr)
    subprocess.run(cmd,check=True); print("DONE",a.out,file=sys.stderr)


if __name__=="__main__": main()
