import bpy

subdivide_count = 100
img = "/Users/vishesh/Downloads/stone_wall_4k.blend/textures/stone_wall_diff_4k.jpg"
img2 = "/Users/vishesh/Downloads/stone_wall_4k.blend/textures/stone_wall_rough_4k.exr"
img3 = "/Users/vishesh/Downloads/stone_wall_4k.blend/textures/stone_wall_nor_gl_4k.exr"
img4 = "/Users/vishesh/Downloads/stone_wall_4k.blend/textures/stone_wall_disp_4k.png"




bpy.ops.mesh.primitive_plane_add(size=100, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.subdivide(number_cuts=subdivide_count)   
objects = bpy.data.objects
plane = objects["Plane"]
bpy.ops.object.editmode_toggle()


material_basic = bpy.data.materials.new(name="Basic")
material_basic.use_nodes = True
bpy.context.object.active_material = material_basic
nodes = material_basic.node_tree.nodes


principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
node_out = material_basic.node_tree.nodes.get("Material Output")

node_tex = material_basic.node_tree.nodes.new('ShaderNodeTexImage')
node_tex.image = bpy.data.images.load(img)
node_tex.location = (-700, 800)

node_rough = material_basic.node_tree.nodes.new('ShaderNodeTexImage')
node_rough.image = bpy.data.images.load(img2)
node_rough.location = (-700, 500)

node_norm = material_basic.node_tree.nodes.new('ShaderNodeTexImage')
node_norm.image = bpy.data.images.load(img3)
node_norm.location = (-700, 200)

node_dis = material_basic.node_tree.nodes.new('ShaderNodeTexImage')
node_dis.image = bpy.data.images.load(img4)
node_dis.location = (-700, -100)

norm_map = material_basic.node_tree.nodes.new('ShaderNodeNormalMap')
norm_map.location = (-250, 0)

node_disp = material_basic.node_tree.nodes.new('ShaderNodeDisplacement')
node_disp.location = (0, -450)

node_tex_coor = material_basic.node_tree.nodes.new('ShaderNodeTexCoord')
node_tex_coor.location = (-1400, 500)

node_map = material_basic.node_tree.nodes.new('ShaderNodeMapping')
node_map.location = (-1200, 500)

link = material_basic.node_tree.links.new
link(node_tex.outputs["Color"], principled_node.inputs["Base Color"])
link(node_rough.outputs["Color"], principled_node.inputs["Roughness"])
link(node_norm.outputs["Color"], norm_map.inputs["Color"])
link(node_dis.outputs["Color"], node_disp.inputs["Height"])

link(node_tex_coor.outputs["UV"], node_map.inputs["Vector"])
link(node_map.outputs["Vector"], node_tex.inputs["Vector"])
link(node_map.outputs["Vector"], node_rough.inputs["Vector"])
link(node_map.outputs["Vector"], node_norm.inputs["Vector"])
link(node_map.outputs["Vector"], node_dis.inputs["Vector"])

link(norm_map.outputs["Normal"], principled_node.inputs["Normal"])
link(node_disp.outputs["Displacement"], node_out.inputs["Displacement"])

