import openslide
import json
import os
import numpy as np
from PIL import Image, ImageDraw

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
    def create_mask(patch_size, coords_NL, offset_x, offset_y):
        """ Create a binary mask for the cancer region inside the patch. """
        print("patch size = ", patch_size)
        mask = Image.new("L", patch_size, 0)  # Black background
        draw = ImageDraw.Draw(mask)
        print("after draw")        
        # Adjust coordinates relative to patch (since we extracted a bounding box)
        relative_coords = [(x - offset_x, y - offset_y) for x, y in coords_NL]
        print("reletive cords find")
        # Draw polygon on mask (white for cancerous area)
        draw.polygon(relative_coords, outline=255, fill=255)
        print("draw polygon")
        ret = np.array(mask)
        print("after np.array(mask)")
        return ret;

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

