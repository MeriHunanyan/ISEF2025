import openslide
import json
import os
import numpy as np
from PIL import Image, ImageDraw

# Load GeoJSON annotation file
geojson_path = "annotations.geojson"
with open(geojson_path, "r") as f:
    annotations = json.load(f)

# Define extraction level
LEVEL = 0  # High resolution

# Output directories
patches_dir = "patches/cancerous/"
os.makedirs(patches_dir, exist_ok=True)

# Process each annotation
for Annotations in annotations["Annotations"]:
    slide_name = geojson_path
    coordinates = feature["regions"]  # Outer boundary of the polygon

    # Convert coordinates to integer (WSI space)
    x_coords, y_coords = zip(*coordinates)
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))

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

    # Convert to NumPy array
    patch_array = np.array(patch)

    # Save patch
    patch.save(os.path.join(patches_dir, f"{slide_name}_cancer_{x_min}_{y_min}.png"))

    slide.close()

print("Patch extraction complete.")
def create_mask(patch_size, coordinates, offset_x, offset_y):
    """ Create a binary mask for the cancer region inside the patch. """
    mask = Image.new("L", patch_size, 0)  # Black background
    draw = ImageDraw.Draw(mask)
    
    # Adjust coordinates relative to patch (since we extracted a bounding box)
    relative_coords = [(x - offset_x, y - offset_y) for x, y in coordinates]

    # Draw polygon on mask (white for cancerous area)
    draw.polygon(relative_coords, outline=255, fill=255)

    return np.array(mask)

# Generate mask
mask = create_mask((width, height), coordinates, x_min, y_min)

# Apply mask to patch
masked_patch = np.where(mask[..., None] == 255, patch_array, 0)  # Keep cancerous area, zero out background

# Save masked patch
np.save(os.path.join(patches_dir, f"{slide_name}_masked.npy"), masked_patch)

