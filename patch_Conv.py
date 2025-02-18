import openslide
import json
import os
import numpy as np
import sys
from PIL import Image, ImageDraw
from pathlib import Path

svs_dir = "/home/meri/SharedFolder/PKG-HER2tumorROIs_v3/Yale_HER2_cohort/SVS/"
output_dir = "/home/meri/SharedFolder/out"

def get_slide_path(geojson_path, svs_dir):
    file_name_without_extension = Path(geojson_path).name
    file_name = Path(file_name_without_extension).stem
    return os.path.join(svs_dir, file_name + ".svs")

def get_output_file_paths(geojson_path, output_dir):
    file_name_without_extension = Path(geojson_path).name
    file_name = Path(file_name_without_extension).stem
    return os.path.join(output_dir, file_name + "_mask"),  os.path.join(output_dir, file_name + "_neg")

def processPath(json_path, slide_path, mask_file_path, neg_file_path):
    slide = openslide.OpenSlide(slide_path)
    with open(json_path, "r") as f:
        annotations = json.load(f)

    for feature in annotations["features"]:
        geom = feature["geometry"]
        coords = geom["coordinates"]
        coords_NL = []
        for conture in coords:
            process_conture(slide, conture, mask_file_path, neg_file_path)
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


def process_conture(slide, conture, mask_file_path, neg_file_path):
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
#    np.save(mask_file_path, masked_patch)
    dbg_nparray_to_png(masked_patch, mask_file_path)
    
    del masked_patch
    neg_masked_patch = np.where(mask[..., None] != 255, patch_array, 0)
    dbg_nparray_to_png(neg_masked_patch, neg_file_path)
#    np.save(neg_file_path, neg_masked_patch)

json_path = "/home/meri/SharedFolder/Outputgeojson/Her2Neg_Case_01.geojson"
slide_path = get_slide_path(json_path, svs_dir)
masked_path, negative_path = get_output_file_paths(json_path, output_dir)
processPath(json_path, slide_path, masked_path, negative_path)

sys.exit(0)

# Load GeoJSON annotation file
geojson_path = "/home/meri/SharedFolder/Outputgeojson" 
for i in range(1, 94):
    num = str(i)
    if i < 10:
        num ="0" + num
    geojson_path ="/home/meri/SharedFolder/Outputgeojson/Her2Pos_Case_"+ num + ".geojson"
    with open(geojson_path, "r") as f:
        annotations = json.load(f)
    
    # Define extraction level
    LEVEL = 0  # High resolution

    # Output directories
    patches_dir = "patches/cancerous/"
    os.makedirs(patches_dir, exist_ok=True)

    # x and y coordinates
    x_coords = []
    y_coords = []
    # Process each annotation
    patch_array = None
    for feature in annotations["features"]:
        slide_name = "Her2Pos_Case_" + num + ".svs" 
        geom = feature["geometry"]
        coords = geom["coordinates"]
        coords_NL = []
        for contures in coords:
            for x, y in contures:
                print("x = ", x, "y =", y)
                coords_NL.append([x, y])
                x_coords.append(x)
                y_coords.append(y)
        #sys.exit(0)

        # Convert coordinates to integer (WSI space)
        
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        print("x_min", x_min, "x_max", x_max)

        # Define patch size (bounding box dimensions)
        width, height = x_max - x_min, y_max - y_min

        # Load the corresponding slide
        slide_path = os.path.join("slides/", slide_name)
        if not os.path.exists(slide_path):
            print(f"Slide {slide_name} not found. Skipping...")
            continue

        slide = openslide.OpenSlide(slide_path)

        # Extract patch (bounding box around the cancer region)
        patch = slide.read_region((x_min, y_min), LEVEL, (width, height)).convert("RGB")

        # Convert` to NumPy array
        patch_array = np.array(patch)

        # Save patch
        patch.save(os.path.join(patches_dir, f"{slide_name}_cancer_{x_min}_{y_min}.png"))

        slide.close()

    print("Patch extraction complete.")

    # Generate mask
    print("before create masl")
    mask = create_mask((width, height), coords_NL, x_min, y_min)
    print("after create mask")

    # Apply mask to patch
    print("before np.where")
    masked_patch = np.where(mask[..., None] == 255, patch_array, 0)  # Keep cancerous area, zero out background
    print("masked")
    # Save masked patch
    np.save(os.path.join(patches_dir, f"{slide_name}_masked.npy"), masked_patch)

