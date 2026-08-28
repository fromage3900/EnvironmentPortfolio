lines=[]
for n in ["band1_analyze","band2_analyze","band3_analyze","band4_analyze","band5_analyze","bands_merge","rename_hsv","analyze"]:
    try:
        c=op("/project1/audio/"+n)
        names=[ch.name for ch in c.chans()]
        lines.append(n+" => "+",".join(names))
    except Exception as e:
        lines.append(n+" => ERR "+str(e))
op("/project1/audio/_probe2").text="\n".join(lines)
