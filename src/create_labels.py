import os
import yaml

import numpy as np
import pandas as pd
import random

import cv2


with open("/home/vishesh/Desktop/synthetics/blender-synthetics/data/config.yaml") as file:
    config_info = yaml.load(file, Loader=yaml.FullLoader)

with open("/home/vishesh/Desktop/synthetics/blender-synthetics/data/models.yaml") as file:
    models_info = yaml.load(file, Loader=yaml.FullLoader)

view_annotations = config_info["view_annotations"]
occlusion_aware = config_info["occlusion_aware"]
visibility_thresh = config_info["visibility_thresh"]
component_visibility_thresh = config_info["component_visibility_thresh"]
results_dir = models_info["render_to"]
num_classes = len(models_info["classes"])

occ_aware_seg_path = os.path.join(results_dir, "seg_maps")
occ_ignore_seg_path = os.path.join(results_dir, "other_seg_maps")
yolo_annotated_path = os.path.join(results_dir, "yolo_annotated")
obb_annotated_path = os.path.join(results_dir, "obb_annotated")
img_path = os.path.join(results_dir, "img")
yolo_labels_path = os.path.join(results_dir, "yolo_labels")
obb_labels_path = os.path.join(results_dir, "obb_labels")


if not os.path.isdir(yolo_annotated_path):
    os.mkdir(yolo_annotated_path)
if not os.path.isdir(obb_annotated_path):
    os.mkdir(obb_annotated_path)
if not os.path.isdir(yolo_labels_path):
    os.mkdir(yolo_labels_path)
if not os.path.isdir(obb_labels_path):
    os.mkdir(obb_labels_path)


colors = {}

for i in range(num_classes):
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    colors[i] = random_color


def is_inst_visible(inst, occ_aware_seg_map, occ_ignore_seg_map, thresh):
    visibility = np.count_nonzero(occ_aware_seg_map == inst) / np.count_nonzero(occ_ignore_seg_map == inst)
    if visibility >= thresh:
        return True
    else:
        return False


def remove_small_components(inst, occ_aware_seg_map, occ_ignore_seg_map, thresh):
    inst_size = np.count_nonzero(occ_ignore_seg_map == inst)
    seg_map_copy = np.copy(occ_aware_seg_map)
    seg_map_copy[occ_aware_seg_map != inst] = 0
    seg_map_copy[occ_aware_seg_map == inst] = 1
    seg_map_copy = seg_map_copy.astype('uint8')

    num_components, components = cv2.connectedComponents(seg_map_copy)

    for i in range(1, num_components):
        component_size = np.count_nonzero(components == i)
        if component_size / inst_size < thresh:
            occ_aware_seg_map[components == i] = 0 # delete component

def ccw(x1, y1, x2, y2, x3, y3):
    return (y3-y1) * (x2-x1) > (y2-y1) * (x3-x1)


# Return true if line segments intersect
def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    return ccw(x1, y1 ,x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and \
        ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)


for img_name in os.listdir(img_path):

    overlapping = set() # instances indices which overlap

    ann = {"cat_id": [], "xc": [], "yc": [], "w": [], "h": [], 
        "obb1x": [], "obb1y": [], "obb2x": [], "obb2y": [], 
        "obb3x": [], "obb3y": [], "obb4x": [], "obb4y": []}

    occ_aware_seg_map = cv2.imread(os.path.join(occ_aware_seg_path, img_name), -1)
    occ_ignore_seg_map = cv2.imread(os.path.join(occ_ignore_seg_path, img_name), -1)
    img = cv2.imread(os.path.join(img_path, img_name))


    img_h, img_w = occ_aware_seg_map.shape[:2]

    instances = np.unique(occ_aware_seg_map)
    instances = instances[instances != 0]

    if view_annotations:
        img_bb, img_obb = img.copy(), img.copy()

    for inst in instances:
        cat_id = inst // 1000

        if not is_inst_visible(inst, occ_aware_seg_map, occ_ignore_seg_map, visibility_thresh): # is it being occluded too much
            continue

        if occlusion_aware:
            remove_small_components(inst, occ_aware_seg_map, occ_ignore_seg_map, component_visibility_thresh) # remove components with too few pixels
            seg_map = occ_aware_seg_map
        else:
            seg_map = occ_ignore_seg_map
        
        points = cv2.findNonZero((seg_map == inst).astype(int))
        if points is None:
            continue
        x_bb, y_bb, w, h = cv2.boundingRect(points)

        if occlusion_aware == False and (x_bb == 0 or y_bb == 0 or x_bb+w == img.shape[1] or y_bb+h == img.shape[0]): # bounding box on edge, object partially not in frame
            continue # re-adjust bb if occlusion_aware, so that OBBs don't extend image

        obb = cv2.minAreaRect(points)
        obb_points = cv2.boxPoints(obb).astype(int)

        for i in range(obb_points.shape[0]): # check every segment
            x1, y1, x2, y2 = obb_points[i][0], obb_points[i][1], \
                                obb_points[(i+1) % obb_points.shape[0]][0], obb_points[(i+1) % obb_points.shape[0]][1]
            
            for j in range(len(ann["xc"])): # number of boxes in img so far
                obb_points2 = np.array([[ann["obb1x"][j], ann["obb1y"][j]], 
                                        [ann["obb2x"][j], ann["obb2y"][j]], 
                                        [ann["obb3x"][j], ann["obb3y"][j]], 
                                        [ann["obb4x"][j], ann["obb4y"][j]]])

                
                w2, h2 = round(ann["w"][j]*img_w), round(ann["h"][j]*img_h)
                x_bb2, y_bb2 = round((ann["xc"][j] * img_w) - w2/2), round((ann["yc"][j] * img_h) - h2/2)


                for k in range(obb_points2.shape[0]):
                    x3, y3, x4, y4 = obb_points2[k][0], obb_points2[k][1], \
                                obb_points2[(k+1) % obb_points2.shape[0]][0], obb_points2[(k+1) % obb_points2.shape[0]][1]

                    
                    if intersect(x1, y1, x2, y2, x3, y3, x4, y4):
                        overlapping.add(j)
                        overlapping.add(len(ann["xc"]))

                        img_obb = cv2.polylines(img_obb, [obb_points], isClosed=True, color=(0,0,255), thickness=3)
                        img_obb = cv2.polylines(img_obb, [obb_points2], isClosed=True, color=(0,0,255), thickness=3)
                        img_bb = cv2.rectangle(img_bb, (x_bb, y_bb), (x_bb+w, y_bb+h), color=(0,0,255), thickness=3)
                        img_bb = cv2.rectangle(img_bb, (x_bb2, y_bb2), (x_bb2+w2, y_bb2+h2), color=(0,0,255), thickness=3)
                        img = cv2.fillPoly(img, [obb_points], color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                        img = cv2.fillPoly(img, [obb_points2], color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

                        continue


        if view_annotations and len(ann["xc"]) not in overlapping: # if current instance isn't overlapping
            img_bb = cv2.rectangle(img_bb, (x_bb, y_bb), (x_bb+w, y_bb+h), color=colors[cat_id], thickness=2)
            img_obb = cv2.polylines(img_obb, [obb_points], isClosed=True, color=colors[cat_id], thickness=2)

        ann["cat_id"].append(cat_id) 
        ann["xc"].append((x_bb + w/2) / img_w)
        ann["yc"].append((y_bb + h/2) / img_h)
        ann["w"].append(w / img_w)
        ann["h"].append(h / img_h)

        ann["obb1x"].append(obb_points[0][0])
        ann["obb1y"].append(obb_points[0][1])
        ann["obb2x"].append(obb_points[1][0])
        ann["obb2y"].append(obb_points[1][1])
        ann["obb3x"].append(obb_points[2][0])
        ann["obb3y"].append(obb_points[2][1])
        ann["obb4x"].append(obb_points[3][0])
        ann["obb4y"].append(obb_points[3][1])



    df = pd.DataFrame.from_dict(ann)
    df = df.drop(list(overlapping))
    yolo_col = ["cat_id", "xc", "yc", "w", "h"]
    np.savetxt(os.path.join(yolo_labels_path, img_name[:-4] + ".txt"), df[yolo_col], delimiter=' ', fmt=['%d', '%.4f', '%.4f', '%.4f', '%.4f'])

    obb_col = ["cat_id", "obb1x", "obb1y", "obb2x", "obb2y", "obb3x", "obb3y", "obb4x", "obb4y"]
    np.savetxt(os.path.join(obb_labels_path, img_name[:-4] + ".txt"), df[obb_col], delimiter=' ', fmt=['%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d'])
    
    cv2.imwrite(os.path.join(img_path, img_name), img)
    if view_annotations:
        cv2.imwrite(os.path.join(yolo_annotated_path, img_name), img_bb)
        cv2.imwrite(os.path.join(obb_annotated_path, img_name), img_obb)


