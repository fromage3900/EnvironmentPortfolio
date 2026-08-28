o=op("/project1/starfield/resonance_rings")
lines=[]
try:
    v = op('/project1/audio/band1_analyze')['band1'][0]
    lines.append("band1_raw="+str(v))
except Exception as e:
    lines.append("band1_raw ERR "+str(e))
try:
    lines.append("const0name="+str(o.par.const0name.eval()))
    lines.append("const0value="+str(o.par.const0value.eval()))
    lines.append("const1value="+str(o.par.const1value.eval()))
    lines.append("const4value="+str(o.par.const4value.eval()))
except Exception as e:
    lines.append("const ERR "+str(e))
lines.append("res="+str(o.par.resolutionw.eval())+"x"+str(o.par.resolutionh.eval()))
op("/project1/audio/_probe2").text="\n".join(lines)
