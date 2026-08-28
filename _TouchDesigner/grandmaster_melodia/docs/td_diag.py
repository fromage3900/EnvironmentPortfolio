lines=[]
try:
    lines.append("root=/project1 exists: "+str(op("/project1") is not None))
except Exception as e:
    lines.append("proj err "+str(e))
try:
    p2 = op("/project1/audio/_probe2")
    lines.append("_probe2 exists: "+str(p2 is not None))
except Exception as e:
    lines.append("p2 err "+str(e))
try:
    audio = op("/project1/audio")
    lines.append("audio child count: "+str(len(audio.children)))
except Exception as e:
    lines.append("audio err "+str(e))
op("/project1/audio/_probe2").text="\n".join(lines)
