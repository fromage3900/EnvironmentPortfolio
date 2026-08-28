#!/usr/bin/env python3
"""Apply E01: set ring radius/opacity EXPRESSIONS via par.expr."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_call import call

rings = [
    (1, 0.08), (2, 0.18), (3, 0.30), (4, 0.44), (5, 0.60),
]

stmts = []
for (i, base) in rings:
    ex = "%0.3f + op('/project1/audio/band%d_lag')['band%d']*1.0" % (base, i, i)
    ba = "0.2 + op('/project1/audio/band%d_lag')['band%d']*0.8" % (i, i)
    path = "/project1/melusina_rings/ring%d" % i
    stmts.append('op(\"%s\").par.radiusx.expr = \"%s\"' % (path, ex))
    stmts.append('op(\"%s\").par.radiusy.expr = \"%s\"' % (path, ex))
    stmts.append('op(\"%s\").par.borderalpha.expr = \"%s\"' % (path, ba))

code = "\n".join(stmts)
code += "\nprint('set ok, count=' + str(%d))" % (len(stmts))
r = call("execute_python", {"code": code})
print(r)
