import os
import yaml
import requests
import urllib.parse
from iiif_prezi3 import Manifest, Canvas, Annotation, config

config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"

def create_iiif_manifest(image_dir, id_root, label, colID, objID):
    # Create a new IIIF Manifest
    manifest = Manifest(id=f"{id_root}/manifest.json", label=label, behavior=["paged"])
    page_count = 0

    # Loop through the images in the specified directory
    for image_file in os.listdir(image_dir):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_path = os.path.join(image_dir, image_file)
            filename = urllib.parse.quote(os.path.splitext(image_file)[0])
            page_count += 1
            quoted_file = urllib.parse.quote(image_file.strip())
            #print (quoted_file)

            image_info = f"http://lib-arcimg-p101.lib.albany.edu/iiif/3/%2F{colID}%2F{objID}%2Fv1%2Fjpg%2F{image_file}/info.json"
            #print (image_info)
            url_root = f"http://lib-arcimg-p101.lib.albany.edu/iiif/3/"

            image_url = f"{url_root}%2F{colID}%2F{objID}%2Fv1%2Fjpg%2F{quoted_file}/full/max/0/default.jpg"
            thumbnail_url = f"http://lib-arcimg-p101.lib.albany.edu/meta/{colID}/{objID}/v1/thumbnail.jpg"
            response = requests.get(image_info).json()

            # Create a new Canvas for each image with a sanitized ID
            canvas = manifest.make_canvas(id=f"{id_root}/canvas/p{page_count}", label=image_file, height=response["height"], width=response["width"])
            
            anno_page = canvas.add_image(image_url=image_url,
                             anno_page_id=f"{id_root}/page/p{page_count}/{page_count}",
                             anno_id=f"{id_root}/annotation/{filename}",
                             format="image/jpeg",
                             height=response["height"],
                             width=response["width"]
                             )

            # Add the annotation to the canvas
            #canvas.add_annotation(annotation)

    return manifest

# Your existing code for handling directories and generating manifests
if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

for colID in os.listdir(root):
    colPath = os.path.join(root, colID)
    if os.path.isdir(colPath):
        for objID in os.listdir(colPath):
            objPath = os.path.join(colPath, objID, "v1")
            metadataPath = os.path.join(objPath, "metadata.yml")
            manifestPath = os.path.join(objPath, "manifest.json")
            jpgPath = os.path.join(objPath, "jpg")
            if os.path.exists(jpgPath):
                with open(metadataPath, 'r') as yml_file:
                    data = yaml.safe_load(yml_file)

                id_root = f"http://lib-arcimg-p101.lib.albany.edu/meta/{colID}/{objID}/v1"
                manifest_label = f"{data['title'].strip()}, {data['date_created'].strip()}"

                # Create the manifest
                iiif_manifest = create_iiif_manifest(jpgPath, id_root, manifest_label, colID, objID)

                # Save the manifest to a JSON file
                with open(manifestPath, 'w') as f:
                    f.write(iiif_manifest.json(indent=2))  # Changed to json()

                print("IIIF manifest created successfully!")
