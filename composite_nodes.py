import bpy

## IMportant - CHANGE object's pass index and set render engine to cycles

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
math_node.inputs[1].default_value = 255
math_node.location = 300, -200

# link nodes
links = tree.links
link = links.new(render_node.outputs[0], comp_node.inputs[0])
link = links.new(render_node.outputs[0], file_node.inputs[0])
link = links.new(render_node.outputs[3], math_node.inputs[0])
link = links.new(math_node.outputs[0], file_node.inputs[0]) # Change between math_node and render_node