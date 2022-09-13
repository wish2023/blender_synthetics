import bpy
import bpycv
from bpy import context

import cv2
import numpy as np
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
    # img_tex = "/home/vishesh/Downloads/terrain/aerial_rocks_04_diff_4k.jpg"
    # img_rough = "/home/vishesh/Downloads/terrain/aerial_rocks_04_rough_4k.jpg"
    # img_norm = "/home/vishesh/Downloads/terrain/aerial_rocks_04_nor_gl_4k.exr"
    # img_dis = "/home/vishesh/Downloads/terrain/aerial_rocks_04_disp_4k.png"

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
    # tex = bpy.data.textures.new("Voronoi", 'VORONOI')
    # tex.distance_metric = 'DISTANCE_SQUARED'
    # modifier = plane.modifiers.new(name="Displace", type='DISPLACE')
    # modifier.texture = bpy.data.textures['Voronoi']
    # modifier.strength = random.randint(1,4)
    # bpy.ops.object.modifier_apply(modifier='Displace')

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
    #voronoi_node.inputs[-1].default_value = random.random() # randomness

    ##########################################
#    print(voronoi_node.voronoi_dimensions)
#    print(voronoi_node.distance)
#    print(voronoi_node.feature)
#    print(voronoi_node.inputs[2].default_value)
    ##########################################


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
        parent_class[obj_name] = class_name
        bpy.ops.object.select_all(action='DESELECT') # May be redundant
        

        object = bpy.data.objects[obj_name]
        object.hide_render = True
        object.rotation_euler.y += math.radians(90)
        
        for coll in object.users_collection:
            coll.objects.unlink(object)
        context.scene.collection.children.get("Models").objects.link(object)

    return object_names


def get_cat_id(obj_name):
    return class_ids[parent_class[obj_name.split('.')[0]]]

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
            print("Seed", seed)
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
            for i, obj in enumerate(objs):
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                coll_target.objects.link(obj)
                obj_copy = obj
                obj_copy.data = obj.data.copy()
                obj_copy["inst_id"] = get_cat_id(obj.name) * 1000 + i + 1 # cannot have inst_id = 0
                obj_copy.hide_render = False

def hide_obstacles():
    pass

def render(render_path, render_name="synthetics.png", occlusion_aware=True):
    img_path = os.path.join(render_path, "img")
    seg_path = os.path.join(render_path, "seg_maps")
    
    if not os.path.isdir(render_path):
        os.mkdir(render_path)
    if not os.path.isdir(img_path):
        os.mkdir(img_path)
    if not os.path.isdir(seg_path):
        os.mkdir(seg_path)
    
    result = bpycv.render_data()

    if occlusion_aware:
        cv2.imwrite(os.path.join(seg_path, render_name), np.uint16(result["inst"]))
    else:
        hide_obstacles()
        hidden_obstacles_result = bpycv.render_data()
        cv2.imwrite(os.path.join(seg_path, render_name), np.uint16(hidden_obstacles_result["inst"]))

    cv2.imwrite(os.path.join(img_path, render_name), result["image"][..., ::-1])


if __name__ == "__main__":

    with open("/home/vishesh/Desktop/synthetics/blender-synthetics/models.yaml") as file:
        models_info = yaml.load(file, Loader=yaml.FullLoader)
    with open("/home/vishesh/Desktop/synthetics/blender-synthetics/config.yaml") as file:
        config_info = yaml.load(file, Loader=yaml.FullLoader)

    classes_list = models_info["classes"]
    scenes_list = [os.path.join(models_info["scenes"], s) for s in os.listdir(models_info["scenes"])]
    render_path = models_info["render_to"]
    occlusion_aware = config_info["occlusion_aware"]
    min_camera_height = config_info["min_camera_height"]
    max_camera_height = config_info["max_camera_height"]
    max_camera_tilt = config_info["max_camera_tilt"]
    min_sun_energy = config_info["min_sun_energy"]
    max_sun_energy = config_info["max_sun_energy"]
    max_sun_tilt = config_info["max_sun_tilt"]

    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    collection = bpy.data.collections.new("Models")
    bpy.context.scene.collection.children.link(collection)
    collection2 = bpy.data.collections.new("Instances")
    bpy.context.scene.collection.children.link(collection2)
    collection3 = bpy.data.collections.new("Obstacles")
    bpy.context.scene.collection.children.link(collection3)
    
    objects_dict = {} # objects_dict[class_name] = objects_names_list
    class_ids = {} # class_ids[class_name] = i
    parent_class = {} # parent_class[obj_name] = class_name

    obstacles_list = get_object_names(obstacles_path)

    for i, class_path in enumerate(classes_list): # do the same for obstacles
        class_name = os.path.basename(os.path.normpath(class_path))
        objects_dict[class_name] = get_object_names(class_path, class_name)
        class_ids[class_name] = i

    

    
    for i in range(num_img):
        render_name = "synthetics" + str(i) + ".png"
        
        bpy.ops.object.select_all(action='SELECT')
        for class_name in class_ids:
            for obj_name in objects_dict[class_name]:
                bpy.data.objects[obj_name].select_set(False)
        bpy.ops.object.delete()
        
        plane_size = 120
        create_plane(plane_size, texture_path=random.choice(scenes_list))
        add_sun(min_sun_energy, max_sun_energy, max_sun_tilt)
        add_camera(min_camera_height, max_camera_height, max_camera_tilt)

        object_count = 12 #random.randrange(3, 5)
        hair_emission(count=object_count, scale=1)

        # print(i)
        # render(render_path, render_name, occlusion_aware)
    