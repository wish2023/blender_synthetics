import bpy
from bpy import context

import math
import random

import os
import glob
import yaml



def create_plane(plane_size=500, texture_path=None):
    subdivide_count = 100
    bpy.ops.mesh.primitive_plane_add(size=plane_size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.subdivide(number_cuts=subdivide_count)
        
    objects = bpy.data.objects
    plane = objects["Plane"]

    bpy.ops.object.editmode_toggle()

    if texture_path:
        generate_texture(texture_path)
    else:
        generate_random_background()
        
def generate_texture(texture_path):

    img_tex = glob.glob(os.path.join(texture_path, "*_diff_*"))[0]
    img_rough = glob.glob(os.path.join(texture_path, "*_rough_*"))[0]
    img_norm = glob.glob(os.path.join(texture_path, "*_nor_gl_*"))[0]
    img_dis = glob.glob(os.path.join(texture_path, "*_disp_*"))[0]


    material_basic = bpy.data.materials.new(name="Basic")
    material_basic.use_nodes = True
    bpy.context.object.active_material = material_basic
    nodes = material_basic.node_tree.nodes


    principled_node = nodes.get("Principled BSDF")
    node_out = nodes.get("Material Output")

    node_tex = nodes.new('ShaderNodeTexImage')
    node_tex.image = bpy.data.images.load(img_tex)
    node_tex.location = (-700, 800)

    node_rough = nodes.new('ShaderNodeTexImage')
    node_rough.image = bpy.data.images.load(img_rough)
    node_rough.location = (-700, 500)

    node_norm = nodes.new('ShaderNodeTexImage')
    node_norm.image = bpy.data.images.load(img_norm)
    node_norm.location = (-700, 200)

    node_dis = nodes.new('ShaderNodeTexImage')
    node_dis.image = bpy.data.images.load(img_dis)
    node_dis.location = (-700, -100)

    norm_map = nodes.new('ShaderNodeNormalMap')
    norm_map.location = (-250, 0)

    node_disp = nodes.new('ShaderNodeDisplacement')
    node_disp.location = (0, -450)

    node_tex_coor = nodes.new('ShaderNodeTexCoord')
    node_tex_coor.location = (-1400, 500)

    node_map = nodes.new('ShaderNodeMapping')
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




def generate_random_background():

    material_basic = bpy.data.materials.new(name="Basic")
    material_basic.use_nodes = True
    bpy.context.object.active_material = material_basic
    nodes = material_basic.node_tree.nodes

    principled_node = nodes.get("Principled BSDF")
    colorramp_node = nodes.new("ShaderNodeValToRGB")
    voronoi_node = nodes.new("ShaderNodeTexVoronoi")

    voronoi_node.location = (-500, 0)
    colorramp_node.location = (-280,0)

    dimensions = ['2D', '3D']
    features = ['F1', 'F2', 'SMOOTH_F1']
    distances = ['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']

    voronoi_node.voronoi_dimensions = random.choice(dimensions)
    voronoi_node.distance = random.choice(distances)
    voronoi_node.feature = random.choice(features)
    voronoi_node.inputs[2].default_value = random.uniform(2, 10) # scale


    link = material_basic.node_tree.links.new
    link(colorramp_node.outputs[0], principled_node.inputs[0])
    voronoi_output = random.randint(0,2)
    link(voronoi_node.outputs[voronoi_output], colorramp_node.inputs[0])


    num_elements = random.randint(5, 15)

    for i in range(num_elements - 2):
        colorramp_node.color_ramp.elements.new(0.1 * (i+1))

    for i in range(num_elements):     
        colorramp_node.color_ramp.elements[i].position = i * (1 / (num_elements-1))
        colorramp_node.color_ramp.elements[i].color = (random.random(), random.random(), random.random(),1)

def add_sun(min_sun_energy, max_sun_energy, min_sun_tilt):

    bpy.ops.object.light_add(type='SUN', radius=10, align='WORLD', location=(0,0,0), scale=(10, 10, 1))
    bpy.context.scene.objects["Sun"].data.energy = random.randrange(min_sun_energy, max_sun_energy)
    bpy.context.scene.objects["Sun"].rotation_euler[0] = random.uniform(0, math.radians(max_sun_tilt))
    bpy.context.scene.objects["Sun"].rotation_euler[1] = random.uniform(0, math.radians(max_sun_tilt))
    bpy.context.scene.objects["Sun"].rotation_euler[2] = random.uniform(0, 2*math.pi)
    
    
def add_camera(min_camera_height, max_camera_height, max_camera_tilt):

    z = random.randrange(min_camera_height, max_camera_height)
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0,0,z), rotation=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.scene.camera = context.object

    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects["Camera"].select_set(True)
    bpy.context.scene.objects["Empty"].select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.scene.objects["Empty"].rotation_euler[0] = random.uniform(0, math.radians(max_camera_tilt))
    bpy.context.scene.objects["Empty"].rotation_euler[2] = random.uniform(0, 2*math.pi)
    

    

def get_object_names(class_path, class_name=None):
    object_names = []
    filenames = os.listdir(class_path)
    
    for filename in filenames:
        filepath = os.path.join(class_path, filename)
        obj_name = os.path.splitext(filepath)[0].split("/")[-1]
        ext = os.path.splitext(filepath)[1]

        if ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=filepath)
        elif ext == ".obj":
            bpy.ops.import_scene.obj(filepath=filepath)
        elif ext == ".blend":
            blender_path = os.path.join("Object", obj_name)
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, blender_path),
                directory=os.path.join(filepath, "Object"),
                filename=obj_name
                )
        else:
            continue
        
        object_names.append(obj_name)
        if class_name:
            parent_class[obj_name] = class_name

        bpy.ops.object.select_all(action='DESELECT') # May be redundant
        
        object = bpy.data.objects[obj_name]
        object.hide_render = True
        object.rotation_euler.y += math.radians(90)
        
        for coll in object.users_collection:
            coll.objects.unlink(object)
        context.scene.collection.children.get("Models").objects.link(object)

    return object_names


def get_cat_id(obj):
    return class_ids[parent_class[obj.name.split('.')[0]]]

def is_target(obj):
    return obj.name.split('.')[0] in parent_class

def is_obstacle(obj):
    return obj.name.split('.')[0] in obstacles_list

def hair_emission(count, scale):
            objects = bpy.data.objects
            plane = objects["Plane"] 

            bpy.context.view_layer.objects.active = plane
            bpy.ops.object.particle_system_add()
            
            particle_count = count
            particle_scale = scale

            ps = plane.modifiers.new("part", 'PARTICLE_SYSTEM')
            psys = plane.particle_systems[ps.name]

            psys.settings.type = "HAIR"
            psys.settings.use_advanced_hair = True

            # EMISSION
            seed = random.randrange(10000)
            psys.settings.count = particle_count # param
            psys.settings.hair_length = particle_scale # param
            psys.seed = seed

            # #RENDER
            psys.settings.render_type = "COLLECTION"
            plane.show_instancer_for_render = True
            psys.settings.instance_collection = bpy.data.collections["Models"]
            psys.settings.particle_size = particle_scale
            
            psys.settings.use_scale_instance = True
            psys.settings.use_rotation_instance = True
            psys.settings.use_global_instance = True
            
            # # ROTATION
            psys.settings.use_rotations = True
            psys.settings.rotation_mode = "NOR" # "GLOB_Z"
            psys.settings.phase_factor_random = 2.0 # change to random num (0 to 2.0)
            psys.settings.child_type = "NONE"
                
            plane.select_set(True)
            bpy.ops.object.duplicates_make_real()
            plane.modifiers.remove(ps)
            
            objs = bpy.context.selected_objects
            coll_target = bpy.context.scene.collection.children.get("Instances")
            coll_obstacles = bpy.context.scene.collection.children.get("Obstacles")
            for i, obj in enumerate(objs):
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                
                obj_copy = obj
                obj_copy.data = obj.data.copy()
                obj_copy.hide_render = False

                if is_target(obj_copy):
                    coll_target.objects.link(obj_copy)
                    inst_id = get_cat_id(obj_copy) * 1000 + i + 1 # cannot have inst_id = 0
                    obj_copy["inst_id"] = inst_id # for bpycv
                    obj_copy.pass_index = inst_id # for inbuilt segmaps
                elif is_obstacle(obj_copy):
                    coll_obstacles.objects.link(obj_copy)
                else:
                    raise Exception(obj_copy.name, "is neither an obstacle nor a target")


def blender_setup():

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    collection = bpy.data.collections.new("Models")
    bpy.context.scene.collection.children.link(collection)
    collection2 = bpy.data.collections.new("Instances")
    bpy.context.scene.collection.children.link(collection2)
    collection3 = bpy.data.collections.new("Obstacles")
    bpy.context.scene.collection.children.link(collection3)
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = True
    bpy.context.scene.use_nodes = True

    tree = bpy.context.scene.node_tree

    for node in tree.nodes:
        tree.nodes.remove(node)

    render_node = tree.nodes.new(type='CompositorNodeRLayers')
    render_node.layer = 'ViewLayer'
    render_node.location = 0,0

    comp_node = tree.nodes.new('CompositorNodeComposite')   
    comp_node.location = 600,0

    file_node = tree.nodes.new('CompositorNodeOutputFile')
    file_node.location = 600, -200

    math_node = tree.nodes.new('CompositorNodeMath')
    math_node.inputs[1].default_value = 65535
    math_node.operation = 'DIVIDE'

    math_node.location = 300, -200

    links = tree.links
    link = links.new(render_node.outputs["IndexOB"], math_node.inputs[0])
    link = links.new(render_node.outputs[0], comp_node.inputs[0])


def render(render_path, render_name="synthetics.png", occlusion_aware=True):
    img_path = os.path.join(render_path, "img")
    occ_aware_seg_path = os.path.join(render_path, "seg_maps")
    occ_ignore_seg_path = os.path.join(render_path, "other_seg_maps")
    
    if not os.path.isdir(render_path):
        os.mkdir(render_path)
    if not os.path.isdir(img_path):
        os.mkdir(img_path)
    if not os.path.isdir(occ_aware_seg_path):
        os.mkdir(occ_aware_seg_path)
    if not os.path.isdir(occ_ignore_seg_path):
        os.mkdir(occ_ignore_seg_path)


    tree = bpy.context.scene.node_tree
    links = tree.links

    render_node = tree.nodes["Render Layers"] 
    file_node = tree.nodes["File Output"]
    math_node = tree.nodes["Math"]


    link = links.new(render_node.outputs[0], file_node.inputs[0])
    file_node.format.color_depth = '8'
    file_node.format.color_mode = 'RGBA'
    file_node.format.file_format = 'PNG'
    file_node.base_path = img_path
    file_node.file_slots[0].path = render_name
    bpy.ops.render.render(write_still=True)

    link = links.new(math_node.outputs[0], file_node.inputs[0])
    file_node.format.color_depth = '16'
    file_node.format.color_mode = 'BW'
    file_node.format.file_format = 'PNG'
    file_node.base_path = occ_aware_seg_path
    file_node.file_slots[0].path = render_name
    bpy.ops.render.render(write_still=True)

    hide_obstacles()

    file_node.base_path = occ_ignore_seg_path
    file_node.file_slots[0].path = render_name
    bpy.ops.render.render(write_still=True)


def hide_obstacles():
    for obj in bpy.data.collections['Obstacles'].all_objects:
        obj.hide_render = True


if __name__ == "__main__":

    with open("/home/vishesh/Desktop/synthetics/blender-synthetics/data/models.yaml") as file:
        models_info = yaml.load(file, Loader=yaml.FullLoader)
    with open("/home/vishesh/Desktop/synthetics/blender-synthetics/data/config.yaml") as file:
        config_info = yaml.load(file, Loader=yaml.FullLoader)

    classes_list = models_info["classes"]
    scenes_list = [os.path.join(models_info["scenes"], s) for s in os.listdir(models_info["scenes"])] if "scenes" in models_info else None
    obstacles_path = models_info["obstacles_path"] if "obstacles_path" in models_info else None
    render_path = models_info["render_to"]
    occlusion_aware = config_info["occlusion_aware"]
    min_camera_height = config_info["min_camera_height"]
    max_camera_height = config_info["max_camera_height"]
    max_camera_tilt = config_info["max_camera_tilt"]
    min_sun_energy = config_info["min_sun_energy"]
    max_sun_energy = config_info["max_sun_energy"]
    max_sun_tilt = config_info["max_sun_tilt"]
    num_img = config_info["num_img"]
    plane_size = config_info["plane_size"]
    min_obj_count = config_info["min_obj_count"]
    max_obj_count = config_info["max_obj_count"]

    
    objects_dict = {} # objects_dict[class_name] = objects_names_list
    class_ids = {} # class_ids[class_name] = i
    parent_class = {} # parent_class[obj_name] = class_name

    blender_setup()

    # refactor
    obstacles_list = get_object_names(obstacles_path) if obstacles_path else []
    for i, class_path in enumerate(classes_list):
        class_name = os.path.basename(os.path.normpath(class_path))
        objects_dict[class_name] = get_object_names(class_path, class_name)
        class_ids[class_name] = i
    #refactor


    
    for i in range(num_img):
        render_name = f"synthetics{i}"
        
        # refactor
        bpy.ops.object.select_all(action='SELECT')
        for obstacle_name in obstacles_list:
            bpy.data.objects[obstacle_name].select_set(False)
        for class_name in class_ids:
            for obj_name in objects_dict[class_name]:
                bpy.data.objects[obj_name].select_set(False)
        bpy.ops.object.delete()
        # refactor
        
        scene = random.choice(scenes_list) if scenes_list else None
        create_plane(plane_size, texture_path=scene)
        add_sun(min_sun_energy, max_sun_energy, max_sun_tilt)
        add_camera(min_camera_height, max_camera_height, max_camera_tilt)

        object_count = random.randrange(min_obj_count, max_obj_count)
        hair_emission(count=object_count, scale=1)

        render(render_path, render_name, occlusion_aware)

        print("-------------")
        print(f"Image {i+1} of {num_img} complete")
        print("-------------")
    