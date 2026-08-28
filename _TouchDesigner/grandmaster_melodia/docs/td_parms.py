o=op("/project1/starfield/resonance_rings")
lines=[]
lines.append("type(pars): "+str(type(o.pars)))
for nm in ["value0name","value0","const0name","const0value","const1name","vec0name","ac0name","ac0chopvalue","resolutionw","resolutionh","nval","glslversion"]:
    try:
        p=o.par[nm]
        lines.append("%s EXISTS eval=%s"%(nm, str(p.eval())[:30]))
    except Exception as e:
        lines.append("%s NO (%s)"%(nm, str(e)[:40]))
# list page names
try:
    lines.append("pages: "+",".join(o.pars.pageNames()))
except Exception as e:
    lines.append("pages ERR "+str(e)[:60])
op("/project1/audio/_probe2").text="\n".join(lines)
