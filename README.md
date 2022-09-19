# Blender Synthetcis

Create your own synthetic dataset for object detection.

## Description

This repo creates random scenes on blender, imports custom 3D models with randomised configurations, and renders numerous images with annotations to train an object detection model.

## Getting Started

### Install blender 3.2

- Follow installation instructions [here](https://www.blender.org/download/releases/3-2/) 
- Ensure your GPU is supported on blender. Refer [here](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html)

### Clone repo

```
git clone https://github.com/wish2023/blender-synthetics.git
```

### Install packages

```
sh install_requirements.sh your/blender/dir/location
```
## Generate synthetics

- Update `data/models.yaml` and `data/config.yaml` as required. Refer to [models](#models) and  [configurations](#configurations) for details.
- Generate images. `blender --background --python src/render_blender.py`
- Generate annotations `python3 src/create_labels.py`

## Models

### Classes

Your targets of interest. Bounding boxes will be drawn around these objects.

### Obstacles (Optional)

Other objects which will be present in the scene. These won't be annotated.

### Scenes (Optional)

Textures that your scene may have. Explore possible textures from [texture haven](https://polyhaven.com/textures) and store all texture subfolders in a main folder.

## Configurations

### Occlusion aware

Plane texture

### Models

Description

### Camera Height and Angle

Description

### Lighting and Shadow

Descriptions

### Data Format

YOLO, COCO

