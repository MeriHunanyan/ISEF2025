import openslide
import json
import os
import numpy as np
import sys
from PIL import Image, ImageDraw
from pathlib import Path

svs_dir = "/home/meri/SharedFolder/PKG-HER2tumorROIs_v3/Yale_HER2_cohort/SVS/"
output_dir = "/home/meri/SharedFolder/outnp"

class slide_path_manager:
    def __init__(self, annotation_file_path):
        self.annotation_file_path_ = annotation_file_path
        file_name_without_extension = Path(annotation_file_path).name
        self.file_name_ = Path(file_name_without_extension).stem

    def get_annotation_file_path(self):
        return self.annotation_file_path_

    def get_slide_file_path(self):
        return os.path.join(svs_dir, self.file_name_ + ".svs")

    def get_tumor_file_path(self, feauture_idx, conture_idx, ext = "np"):
        return os.path.join(output_dir, self.file_name_ + "_" + str(feauture_idx) + "_" + str(conture_idx) + "_tum." + ext)

    def get_clean_file_path(self, feauture_idx, conture_idx, ext = "np"):
        return os.path.join(output_dir, self.file_name_ + "_" + str(feauture_idx) + "_" + str(conture_idx) + "_clean." + ext)

def process_slide(path_manager):
    slide = openslide.OpenSlide(path_manager.get_slide_file_path())
    print(path_manager.get_annotation_file_path())
    with open(path_manager.get_annotation_file_path(), "r") as f:
        annotations = json.load(f)

    for feature in annotations["features"]:
        geom = feature["geometry"]
        props = feature["properties"]
        fidx = props["annotation_id"]
        coords = geom["coordinates"]
        coords_NL = []
        cidx = 1
        for conture in coords:
            process_conture(slide, conture, path_manager, fidx, cidx)
            cidx += 1
    slide.close()

def create_mask(patch_size, coords_NL, offset_x, offset_y):
    mask = Image.new("L", patch_size, 0)  # Black background
    draw = ImageDraw.Draw(mask)
    # Adjust coordinates relative to patch (since we extracted a bounding box)
    relative_coords = [(x - offset_x, y - offset_y) for x, y in coords_NL]
    # Draw polygon on mask (white for cancerous area)
    draw.polygon(relative_coords, outline=255, fill=255)
    ret = np.array(mask)
    return ret;

def dbg_nparray_to_png(pixels, path):
    image = Image.fromarray(pixels)
    image.save(path + ".png")


def process_conture(slide, conture, path_manager, feauture_idx, contur_idx):
    xmin = int(min([point[0] for point in conture]))
    xmax = int(max([point[0] for point in conture]))
    ymin = int(min([point[1] for point in conture]))
    ymax = int(max([point[1] for point in conture]))
    width, height = xmax - xmin, ymax - ymin
    LEVEL = 0
    patch = slide.read_region((xmin, ymin), LEVEL, (width, height)).convert("RGB")
    patch_array = np.array(patch)
    del patch
    mask = create_mask((width, height), conture, xmin, ymin)
    masked_patch = np.where(mask[..., None] == 255, patch_array, 0)
    np.save(path_manager.get_tumor_file_path(feauture_idx, contur_idx, ".npy"), masked_patch)
#    np.save(mask_file_path, masked_patch)
    #dbg_nparray_to_png(masked_patch, path_manager.get_tumor_file_path(feauture_idx, contur_idx, "png"))
    
    del masked_patch
    neg_masked_patch = np.where(mask[..., None] != 255, patch_array, 0)
    np.save(path_manager.get_clean_file_path(feauture_idx, contur_idx, ".npy"), neg_masked_patch)
    #dbg_nparray_to_png(neg_masked_patch, path_manager.get_clean_file_path(feauture_idx, contur_idx, "png"))
#    np.save(neg_file_path, neg_masked_patch)

count = 1
for f in os.listdir("/home/meri/SharedFolder/Outputgeojson"):
    if count > 47 and f.lower().endswith('.geojson'):
        json_path ="/home/meri/SharedFolder/Outputgeojson/" + str(f)
        path_manager = slide_path_manager(json_path)
        slide_path = path_manager.get_slide_file_path()
        process_slide(path_manager)
    count = count + 1
sys.exit(0)

