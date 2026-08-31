import hou

hou.setFps(24)
geo = hou.node("/obj").createNode("geo", node_name="t_tank5", run_init_scripts=False)
tank = geo.createNode("particlefluidtank", "fluid_tank")
tank.parm("sizex").set(8.0); tank.parm("sizey").set(4.0); tank.parm("sizez").set(6.0)
tank.parm("waterlevel").set(0.5)
sep = tank.parm("particlesep").eval()

water = geo.createNode("box", "water_box")
water.parm("sizex").set(7.6); water.parm("sizey").set(1.8); water.parm("sizez").set(5.6)
water.parm("ty").set(0.9)
surf = geo.createNode("vdbfrompolygons", "water_sdf"); surf.setInput(0, water)
surf.parm("distancename").set("surface"); surf.parm("voxelsize").set(0.1)
nsurf = geo.createNode("name", "name_surface"); nsurf.setInput(0, surf); nsurf.parm("name1").set("surface")

# zero velocity volume
vdb_vel = geo.createNode("vdb", "zero_vel"); vdb_vel.parm("volume_name").set("vel") if vdb_vel.parm("volume_name") else None
nvel = geo.createNode("name", "name_vel"); nvel.setInput(0, vdb_vel); nvel.parm("name1").set("vel")

ramp = geo.createNode("box", "climbing_ramp")
ramp.parm("sizex").set(8.0); ramp.parm("sizey").set(0.6); ramp.parm("sizez").set(3.0)
ramp.parm("ty").set(1.0); ramp.parm("rz").set(-28.0)
xf = geo.createNode("xform", "ramp_world"); xf.setInput(0, ramp); xf.parm("ty").set(1.5)
coll = geo.createNode("vdbfrompolygons", "collision_vdb"); coll.setInput(0, xf)
coll.parm("distancename").set("collision"); coll.parm("voxelsize").set(0.1)
ncoll = geo.createNode("name", "name_collision"); ncoll.setInput(0, coll); ncoll.parm("name1").set("collision")

domain = geo.createNode("box", "domain_box")
domain.parm("sizex").set(8.0); domain.parm("sizey").set(4.0); domain.parm("sizez").set(6.0)

def add_detail(node, name, val):
    ac = geo.createNode("attribcreate::2.0", f"d_{name}")
    ac.setInput(0, node)
    ac.parm("class1").set(0)
    ac.parm("name1").set(name)
    ac.parm("value1v1").set(val)
    return ac

dom_g = add_detail(domain, "gridscale", 1.0)
dom_g = add_detail(dom_g, "particlesep", sep)

py = geo.createNode("python", "domain_volumenames")
py.setInput(0, dom_g)
py.parm("python").set(
    'node = hou.pwd()\n'
    'g = node.geometry()\n'
    'attr = g.addArrayAttrib(hou.attribType.Global, "volumenames", hou.attribData.String, 1)\n'
    'g.setGlobalAttribValue(attr, ["surface", "vel", "collision"])\n'
)
dom_g = py

merge_in = geo.createNode("merge", "merge_in0")
merge_in.setInput(0, tank); merge_in.setInput(1, nsurf); merge_in.setInput(2, nvel)

solver = geo.createNode("flipsolver", "flip")
solver.setInput(0, merge_in)
solver.setInput(1, dom_g)
solver.setInput(2, ncoll)

hou.setFrame(1)
try:
    solver.cook(force=True)
except hou.OperationFailed:
    print("FLIPSOLVER ERRORS:", solver.errors()); raise
g = solver.geometry()
print(f"frame 1: points={len(g.points())}")

hou.setFrame(24)
try:
    solver.cook(force=True)
except hou.OperationFailed:
    print("FLIPSOLVER ERRORS f24:", solver.errors()); raise
g = solver.geometry()
print(f"frame 24: points={len(g.points())}")
if len(g.points()):
    print("  sample f24:", [tuple(round(v, 2) for v in p.position()) for p in g.points()[:5]])
    print("  pointattrs:", [a.name() for a in g.pointAttribs()])




