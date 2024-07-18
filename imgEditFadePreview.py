import os
from imgDefaultEdit import supperpose_image_preview
from imgEdit import supperpose_image
from config import dbValorant


def preview(type):
    dossier = f"crosshairs/{type}"

    # Iterate over all folders in the specified directory
    for root, dirs, files in os.walk(dossier):
        crosshair_id = root.split("\\")[-1]
        blank_path = os.path.join(root, "blank.png")
        preview_path = "backgrounds/defaultPreview.png"

        print(f"Blank Path: {blank_path}")
        print(f"Crosshair ID: {crosshair_id}")

        # Check if files exist
        if not os.path.exists(blank_path):
            print(f"File not found: {blank_path}")
            continue


        previewDef = supperpose_image_preview(blank_path, preview_path)

        print(f"Preview: {previewDef}")


def fade(type):
    
    dossier = f"crosshairs/{type}"
    e = 0
    for root, dirs, files in os.walk(dossier):
        e += 1
        print(e)
        crosshair_id = root.split("\\")[-1]
        fade_path = os.path.join(root, "fade.png")
        bg_fade_path = "backgrounds/png/blaugelb.png"
            
        if not os.path.exists(fade_path):
            print(f"File not found: {fade_path}")
            continue
        if not os.path.exists(bg_fade_path):
            print(f"File not found: {bg_fade_path}")
            pass
        
        fadeDef = supperpose_image(fade_path, bg_fade_path, "fadebg")
        
        print(f"Fade: {fadeDef}")
    
    
# preview("user")
# fade("user")