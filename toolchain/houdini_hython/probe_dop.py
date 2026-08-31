import hou

hou.setFps(24)
obj = hou.node("/obj")
geo = obj.createNode("geo", node_name="t_shelf2", run_init_scripts=False)
tank = geo.createNode("particlefluidtank", "tank")
tank.parm("sizex").set(8.0); tank.parm("sizey").set(4.0); tank.parm("sizez").set(6.0)
tank.parm("waterlevel").set(0.5)

py = geo.createNode("python", "tag_attrs")
py.setInput(0, tank)
py.parm("python").set(
    'g = hou.pwd().geometry()\n'
    'a1 = g.addAttrib(hou.attribType.Global, "gridscale", 1.0)\n'
    'a2 = g.addAttrib(hou.attribType.Global, "particlesep", 0.25)\n'
    'a3 = g.addArrayAttrib(hou.attribType.Global, "volumenames", hou.attribData.String, 1)\n'
    'g.setGlobalAttribValue(a3, ["surface"])\n'
)

solver = geo.createNode("flipsolver", "flip")
solver.setInput(0, py)

hou.setFrame(1)
try:
    solver.cook(force=True)
    print("f1 ok points:", len(solver.geometry().points()))
except hou.OperationFailed:
    print("ERR f1:", solver.errors()); raise

hou.setFrame(24)
try:
    solver.cook(force=True)
    g = solver.geometry()
    print("f24 points:", len(g.points()))
    if len(g.points()):
        print("sample:", [tuple(round(v,2) for v in p.position()) for p in g.points()[:4]])
except hou.OperationFailed:
    print("ERR f24:", solver.errors()); raise
