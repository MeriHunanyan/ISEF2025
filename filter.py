import os
import shutil

# Change this to your main folder path
MAIN_FOLDER ="/home/meri/SharedFolder"

# Define partial download extensions
PARTIAL_EXTENSIONS = (".partial")

def is_partially_downloaded(folder_path):
    """Check if a folder contains a partially downloaded file."""
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(PARTIAL_EXTENSIONS):
                return True  # Found a partial file, mark for deletion
    return False

def clean_folders(main_folder):
    """Delete folders containing partially downloaded files."""
    for subfolder in os.listdir(main_folder):
        subfolder_path = os.path.join(main_folder, subfolder)
        
        if os.path.isdir(subfolder_path):  # Ensure it's a folder
            if is_partially_downloaded(subfolder_path):
                print(f"Deleting: {subfolder_path}")
                shutil.rmtree(subfolder_path)  # Remove folder
            else:
                print(f"Keeping: {subfolder_path}")

if __name__ == "__main__":
    clean_folders(MAIN_FOLDER)
