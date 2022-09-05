from unittest import case
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
        bpy.data.objects[obj_name].hide_render = True
        
    return object_names


def createCopies2(namelist, num, tank_particle_scale):
    objects = bpy.data.objects
    obj_num = 0
    for obj_name in namelist:
        plane = objects["Plane"]
        bpy.context.view_layer.objects.active = plane
        bpy.ops.object.particle_system_add()
        
#        if objects[i].name.startswith('Leo2A4') or objects[i].name.startswith('M142'): # to use list of strings instead
        particle_count = num
        particle_scale = tank_particle_scale
        if obj_num==0:
            particle_sys_name = "ParticleSystem" 
            particle_settings_name = "ParticleSettings"
            ps_name = bpy.data.particles[particle_settings_name].name = "ps" 
        else:
            particle_sys_name = "ParticleSystem." + str(obj_num).zfill(3)
            ps_name = bpy.data.particles[particle_settings_name].name = "ps" + str(obj_num) 
        ob = objects[obj_name] ## #FIX
        #ps_name = "ps1"
        bpy.data.particles[ps_name].type = "HAIR"
        bpy.data.particles[ps_name].use_advanced_hair = True
        # EMISSION
        bpy.data.particles[ps_name].count = particle_count # param
        bpy.data.objects["Plane"].particle_systems[particle_sys_name].seed = obj_num # param(?) # seed to change random locations of particles

        #RENDER
        bpy.data.particles[ps_name].render_type = "OBJECT"
        bpy.data.objects["Plane"].show_instancer_for_render = False # don't show emitter
        bpy.data.particles[ps_name].instance_object = ob #"tree1.001" #obj name will be the foilage object
        bpy.data.particles[ps_name].particle_size = particle_scale # param (0.1 to 0.5?)

        
        bpy.data.particles[ps_name].use_scale_instance = True
        bpy.data.particles[ps_name].use_rotation_instance = True
        bpy.data.particles[ps_name].use_global_instance = True

        
        # ROTATION
        bpy.data.particles[ps_name].use_rotations = True # param
        bpy.data.particles[ps_name].rotation_mode = "GLOB_Z"
        bpy.data.particles[ps_name].phase_factor_random = 2.0 # param (0 to 2.0)
        #bpy.data.particles["ParticleSettings.022"].phase_factor # param  phase (-1 to 1)
        # Do this for very dense forest
        bpy.data.particles[ps_name].child_type = "NONE" # param default = "NONE", or "SIMPLE" or "INTERPOLATED"
        obj_num +=1
        
        plane = bpy.data.objects["Plane"] 
        bpy.context.view_layer.objects.active = plane
        plane.select_set(True)
        ## IMPT STEP: to convert particles to individual meshes! 
        bpy.ops.object.duplicates_make_real()


def createCopies(namelist, num, bvhtree, is_target=False, cat_id=None): # namelist - All fbx models in same class
    C = bpy.context
    objects = bpy.data.objects


    def is_overlapping(obj1, obj2):

        bm1 = bmesh.new()
        bm2 = bmesh.new()

        #fill bmesh data from objects
        bm1.from_mesh(objects[obj1].data)
        bm2.from_mesh(objects[obj2].data)            

        #fixed it here:
        bm1.transform(objects[obj1].matrix_world)
        bm2.transform(objects[obj2].matrix_world) 

        #make BVH tree from BMesh of objects
        obj_now_BVHtree = BVHTree.FromBMesh(bm1)
        obj_next_BVHtree = BVHTree.FromBMesh(bm2)           

        #get intersecting pairs
        inter = obj_now_BVHtree.overlap(obj_next_BVHtree)

        #if list is empty, no objects are touching
        if inter != []:
            return True
        else:
            return False


    def reposition_z(object, bvhtree):

        # create a direction vector, which points downwards and
        # a origin for the raycast
        dir = mathutils.Vector((0, 0, -1))
        origin = mathutils.Vector((*object.location[:2], MAXIMUM_Z - EPSILON))

        # if there is a hit, move the cube to that location
        loc, no, i, d = bvhtree.ray_cast(origin, dir)
        if d is not None:
            object.location = loc
    
    start_ind = 0
    for object in namelist:
        end_ind = start_ind+num

        src_obj = objects[object]
        for i in range (start_ind, end_ind):
            new_obj = src_obj.copy()
            new_obj.data = src_obj.data.copy()
            new_obj.animation_data_clear()
            new_obj.name = src_obj.name + str(i)
            new_obj.hide_render = False
            new_obj["inst_id"] = cat_id * 1000 + i
            new_obj.rotation_euler[2] = random.uniform(0, 2*math.pi)
            new_obj.location[0] = random.randrange(-plane_size/2, plane_size/2)
            new_obj.location[1] = random.randrange(-plane_size/2, plane_size/2)
#            reposition_z(new_obj, bvhtree)
            C.collection.objects.link(new_obj)
            obj_list.append(new_obj.name)

#            for obj in obj_list[:-1]:
#                if is_overlapping(obj, new_obj.name):
#                    bpy.ops.object.select_all(action='DESELECT')
#                    bpy.data.objects[new_obj.name].select_set(True)
#                    bpy.ops.object.delete()
#                    obj_list.pop()
#                    break
                
#            print(object, start_ind, i, end_ind)



        start_ind = end_ind
        


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
    
    tank_objects_namelist = get_object_names(tank_folder_path)
    #plant_objects_namelist = get_object_names(plant_folder_path)
    
    for i in range(1):
        render_name = "synthetics" + str(i) + ".png"
        
        bpy.ops.object.select_all(action='SELECT')
        for obj_name in tank_objects_namelist:
            bpy.data.objects[obj_name].select_set(False)
        bpy.ops.object.delete()
        
        plane_size = 120
        create_plane(plane_size)
        add_sun()
        add_camera()

        tank_count = random.randrange(5, 10) 
#        createCopies2(tank_objects_namelist, tank_count, 1.3)

        EPSILON = 0.0000001 # the epsilon value for the BVHTree calculations
        MAXIMUM_Z = 1000 # maximum ray distance XY plane
        landscape = bpy.data.objects["Plane"]

         # create the BVHTrees from a bmesh of the "sticky" object
         # the bmesh conversion makes it easy to apply the individual objects transformation matrices
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(landscape, depsgraph)
        bmesh.ops.transform(bm, matrix=landscape.matrix_world, verts=bm.verts)
        bvhtree = BVHTree.FromBMesh(bm, epsilon=EPSILON)

        obj_list = []
        createCopies(tank_objects_namelist, tank_count, bvhtree, is_target=True, cat_id=1)
        
        print(i)
#        render(render_name)
    
