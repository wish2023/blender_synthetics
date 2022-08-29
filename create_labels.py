import os

import numpy as np
import pandas as pd

import cv2
from PIL import Image

view_annotations = True

seg_maps_path = "/home/vishesh/Desktop/synthetics/results/seg_maps"
yolo_annotated_path = "/home/vishesh/Desktop/synthetics/results/yolo_annotated"
obb_annotated_path = "/home/vishesh/Desktop/synthetics/results/obb_annotated"
img_path = "/home/vishesh/Desktop/synthetics/results/img"
yolo_labels_path = "/home/vishesh/Desktop/synthetics/results/yolo_labels"
obb_labels_path = "/home/vishesh/Desktop/synthetics/results/obb_labels"


for img_name in os.listdir(seg_maps_path):

    ann = {"cat_id": [], "xc": [], "yc": [], "w": [], "h": [], 
        "obb1x": [], "obb1y": [], "obb2x": [], "obb2y": [], "obb3x": [], "obb3y": [], "obb4x": [], "obb4y": []}

    seg_map = Image.open(os.path.join(seg_maps_path, img_name))
    seg_map = np.array(np.asarray(seg_map))
    img_h, img_w = seg_map.shape[:2]

    instances = np.unique(seg_map)
    instances = instances[instances != 0]

    if view_annotations:
        img = cv2.imread(os.path.join(img_path, img_name))
        img_bb, img_obb = img.copy(), img.copy()

    for inst in instances:
        cat_id = inst // 1000
        
        points = cv2.findNonZero((seg_map == inst).astype(int))
        x, y, w, h = cv2.boundingRect(points)
        obb = cv2.minAreaRect(points)
        obb_points = cv2.boxPoints(obb).astype(int)

        if view_annotations:
            img_bb = cv2.rectangle(img_bb, (x, y), (x+w, y+h), color=(0,0,255), thickness=2)
            img_obb = cv2.polylines(img_obb, [obb_points], isClosed=True, color=(0, 0, 255), thickness=2)

        ann["cat_id"].append(cat_id) 
        ann["xc"].append((x + w/2) / img_w)
        ann["yc"].append((y + h/2) / img_h)
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
    yolo_col = ["cat_id", "xc", "yc", "w", "h"]
    np.savetxt(os.path.join(yolo_labels_path, img_name[:-4] + ".txt"), df[yolo_col], delimiter=' ', fmt=['%d', '%.4f', '%.4f', '%.4f', '%.4f'])

    obb_col = ["cat_id", "obb1x", "obb1y", "obb2x", "obb2y", "obb3x", "obb3y", "obb4x", "obb4y"]
    np.savetxt(os.path.join(obb_labels_path, img_name[:-4] + ".txt"), df[obb_col], delimiter=' ', fmt=['%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d'])
    
    if view_annotations:
        cv2.imwrite(os.path.join(yolo_annotated_path, img_name), img_bb)
        cv2.imwrite(os.path.join(obb_annotated_path, img_name), img_obb)

