import bpy
import time

## IMportant - CHANGE object's pass index and set render engine to cycles


bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = True
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

# clear default nodes
for node in tree.nodes:
    tree.nodes.remove(node)

render_node = tree.nodes.new(type='CompositorNodeRLayers')
render_node.layer = 'ViewLayer'
render_node.location = 0,0

comp_node = tree.nodes.new('CompositorNodeComposite')   
comp_node.location = 400,0

file_node = tree.nodes.new('CompositorNodeOutputFile')
file_node.location = 500, -300

math_node = tree.nodes.new('CompositorNodeMath')
math_node.operation = 'DIVIDE'
math_node.location = 300, -200

# link nodes
links = tree.links
link = links.new(render_node.outputs[0], comp_node.inputs[0])
link = links.new(render_node.outputs[0], file_node.inputs[0])
link = links.new(render_node.outputs["IndexOB"], math_node.inputs[0])

render_segmentation = True
render_path = "/Users/vishesh/Desktop/DSTA/blender/blender-synthetics/"

if render_segmentation:
    math_node.inputs[1].default_value = 65535 # Change for 8 bit png
    link = links.new(math_node.outputs[0], file_node.inputs[0])
    file_node.format.color_mode = 'BW'
    file_node.format.color_depth = '16'
    file_node.format.file_format = 'PNG'
    file_node.base_path = render_path
    file_node.file_slots[0].path = "test"
else:
    math_node.inputs[1].default_value = 65535 # Change for 8 bit png
    link = links.new(math_node.outputs[0], file_node.inputs[0])
    file_node.format.color_mode = 'BW'
    file_node.format.color_depth = '16'
    file_node.format.file_format = 'PNG'
    file_node.base_path = render_path
    file_node.file_slots[0].path = "test"


for i in range(3):
    file_node.file_slots[0].path = f"test{i}"
    bpy.ops.render.render(write_still=True)


for i in range(4,6):
    file_node.file_slots[0].path = f"test{i}"
    bpy.ops.render.render(write_still=True)
