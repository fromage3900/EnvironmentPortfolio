lines=[]
cr=op("/project1/comp_rings")
lines.append("comp_rings inputCount: "+str(cr.inputConnectors))
try:
    lines.append("numInputs: "+str(cr.numInputs))
except Exception as e:
    lines.append("numInputs ERR "+str(e))
try:
    ins=[ (i.index, str(i.connectedOp) if i.connectedOp else 'NONE') for i in cr.inputConnectors ]
    lines.append("inputs: "+str(ins))
except Exception as e:
    lines.append("inputs ERR "+str(e))
rr=op("/project1/starfield/resonance_rings")
try:
    outs=[ (i.index, str(i.connectedOp) if i.connectedOp else 'NONE') for i in rr.outputConnectors ]
    lines.append("rr outputs: "+str(outs))
except Exception as e:
    lines.append("rr outs ERR "+str(e))
op("/project1/audio/_probe2").text="\n".join(lines)
