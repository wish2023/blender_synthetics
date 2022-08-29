import bpy
import random

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

size = 500
subdivide_count = 100
bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.subdivide(number_cuts=subdivide_count)
    
objects = bpy.data.objects
plane = objects["Plane"]

bpy.ops.object.editmode_toggle()

tex = bpy.data.textures.new("Voronoi", 'VORONOI')
tex.distance_metric = 'DISTANCE_SQUARED'
modifier = plane.modifiers.new(name="Displace", type='DISPLACE')
modifier.texture = bpy.data.textures['Voronoi']
modifier.strength = random.randint(2, 20)
bpy.ops.object.modifier_apply(modifier='Displace')

material_basic = bpy.data.materials.new(name="Basic")
material_basic.use_nodes = True

bpy.context.object.active_material = material_basic

principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
colorramp_node = material_basic.node_tree.nodes.new("ShaderNodeValToRGB")
voronoi_node = material_basic.node_tree.nodes.new("ShaderNodeTexVoronoi")

voronoi_node.location = (-500, 0)
colorramp_node.location = (-280,0)

dimensions = ['2D', '3D']
features = ['F1', 'F2', 'SMOOTH_F1']
distances = ['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']

voronoi_node.voronoi_dimensions = random.choice(dimensions)
voronoi_node.distance = random.choice(distances)
voronoi_node.feature = random.choice(features)
voronoi_node.inputs[2].default_value = random.uniform(2, 30) # scale
#voronoi_node.inputs[-1].default_value = random.random() # randomness


link = material_basic.node_tree.links.new
link(colorramp_node.outputs[0], principled_node.inputs[0])
voronoi_output = random.randint(0,2)
link(voronoi_node.outputs[voronoi_output], colorramp_node.inputs[0])


num_elements = random.randint(10, 20)

for i in range(num_elements - 2):
    colorramp_node.color_ramp.elements.new(0.1 * (i+1))

for i in range(num_elements):     
    colorramp_node.color_ramp.elements[i].position = i * (1 / (num_elements-1))
    colorramp_node.color_ramp.elements[i].color = (random.random(), random.random(), random.random(),1)
    



"""
Things to randomise

1. Distance or colour can be output from voronoi texture
2. Randomness (0-1) and scale (3-20) in voronoi texture. Smoothness is possible too.
3. Randomise distance metric.

Add colour ramp node if distance is output from voronoi texture
1. Randomise position and RGB values of each section in coloramp. Randomly add 2-3 extra nodes
2. Can be used for other metrics too


1. Plug colour into other inputs like roughness sometimes


Future
1. Try changing displacement too.
2. Add texture mapping
"""