import bpy
import bpycv
from bpy import context

import cv2
import numpy as np
import math

import os
import random

import bmesh
from mathutils.bvhtree import BVHTree
import mathutils

def create_plane(plane_size=500):
    subdivide_count = 100
    bpy.ops.mesh.primitive_plane_add(size=plane_size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.subdivide(number_cuts=subdivide_count)
        
    objects = bpy.data.objects
    plane = objects["Plane"]

    bpy.ops.object.editmode_toggle()

#    tex = bpy.data.textures.new("Voronoi", 'VORONOI')
#    tex.distance_metric = 'DISTANCE_SQUARED'
#    modifier = plane.modifiers.new(name="Displace", type='DISPLACE')
#    modifier.texture = bpy.data.textures['Voronoi']
#    modifier.strength = random.randint(1,4)
#    bpy.ops.object.modifier_apply(modifier='Displace')

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
        


def add_sun():
    x, y, z = 0, 0, 50
    bpy.ops.object.light_add(type='SUN', radius=10, align='WORLD', location=(x,y,z), scale=(10, 10, 1))
    bpy.context.scene.objects["Sun"].data.energy = random.randrange(1,10,2)
    bpy.context.scene.objects["Sun"].rotation_euler[0] = random.uniform(0, math.radians(70))
    bpy.context.scene.objects["Sun"].rotation_euler[1] = random.uniform(0, math.radians(70))
    bpy.context.scene.objects["Sun"].rotation_euler[2] = random.uniform(0, 2*math.pi)
    
    
def add_camera():
    zmin, zmax = 250, 350
    z = random.randrange(zmin, zmax)
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, z), rotation=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.scene.camera = context.object

    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects["Camera"].select_set(True)
    bpy.context.scene.objects["Empty"].select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.scene.objects["Empty"].rotation_euler[0] = random.uniform(0, math.radians(30))
    bpy.context.scene.objects["Empty"].rotation_euler[2] = random.uniform(0, 2*math.pi)

    

def get_object_names(folder_path):
    object_names = []
    filenames = os.listdir(folder_path)
    
    for filename in filenames:
        filepath = os.path.join(folder_path, filename)
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
        bpy.ops.object.select_all(action='DESELECT') # May be redundant
        
        object = bpy.data.objects[obj_name]
        object.hide_render = True
        object.rotation_euler.y += math.radians(90)
        
        for coll in object.users_collection:
            coll.objects.unlink(object)
        context.scene.collection.children.get("Objects").objects.link(object)
        
        
        
    return object_names


def hair_emission(namelist, count, scale, cat_id=None, is_target=False):
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
            psys.settings.instance_collection = bpy.data.collections["Objects"]
            psys.settings.particle_size = particle_scale
            
            psys.settings.use_scale_instance = True
            psys.settings.use_rotation_instance = True
            psys.settings.use_global_instance = True
            
            # # ROTATION
            psys.settings.use_rotations = True # param
            psys.settings.rotation_mode = "GLOB_Z"
            psys.settings.phase_factor_random = 2.0 # change to random num (0 to 2.0)
            psys.settings.child_type = "NONE" # param default = "NONE", or "SIMPLE" or "INTERPOLATED"
                
            plane.select_set(True)
            bpy.ops.object.duplicates_make_real()
#            plane.modifiers.remove(ps)

#            start_ind = 1
#            for obj_name in namelist:
#                obj = objects[obj_name]
#                end_ind = start_ind + count
#                for i in range(start_ind, end_ind):
#                    obj_inst = obj_name + "." + str(i-start_ind+1).zfill(3)
#                    obj_copy = objects[obj_inst]
#                    obj_copy.data = obj.data.copy()
#                    obj_copy["inst_id"] = cat_id * 1000 + i
#                    obj_copy.hide_render = False
##                    print(obj_inst, cat_id * 1000 + i)
#                start_ind = end_ind

        


def render(render_name="synthetics.png"):
    img_path = os.path.join(render_path, "img")
    seg_path = os.path.join(render_path, "seg_maps")
    
    if not os.path.isdir(img_path):
        os.mkdir(img_path)
    if not os.path.isdir(seg_path):
        os.mkdir(seg_path)
    
    result = bpycv.render_data()
    
    
    cv2.imwrite(os.path.join(img_path, render_name), result["image"][..., ::-1])
    cv2.imwrite(os.path.join(seg_path, render_name), np.uint16(result["inst"]))


if __name__ == "__main__":
    plant_folder_path = "/home/vishesh/Desktop/synthetics/models/plant_imports/"
    tank_folder_path = "/home/vishesh/Desktop/synthetics/models/small_vehicles/"
    render_path = "/home/vishesh/Desktop/synthetics/results"
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    collection = bpy.data.collections.new("Objects")
    bpy.context.scene.collection.children.link(collection)
    
    small_vehicles_namelist = get_object_names(tank_folder_path)
    #plant_objects_namelist = get_object_names(plant_folder_path)
    
    for i in range(1):
        render_name = "synthetics" + str(i) + ".png"
        
        bpy.ops.object.select_all(action='SELECT')
        for obj_name in small_vehicles_namelist:
            bpy.data.objects[obj_name].select_set(False)
        bpy.ops.object.delete()
        
        plane_size = 120
        create_plane(plane_size)
        add_sun()
        add_camera()

        tank_count = 2 #random.randrange(3, 5) 
        hair_emission(small_vehicles_namelist, tank_count, 1, cat_id=2)

        # print(i)
#        render(render_name)
    