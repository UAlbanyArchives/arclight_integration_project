import os
import sys
import yaml
import requests
import urllib.parse
from get_media_info import get_media_info
from iiif_prezi3 import Manifest, Canvas, Annotation, AnnotationPage, config

config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"


def create_iiif_canvas(manifest, id_root, label, resource_type, resource_path, page_count, **kwargs):
    """Create a IIIF Canvas for images, videos, or audio."""
    
    # Default to not setting height and width
    height = kwargs.get("height", None)
    width = kwargs.get("width", None)
    
    if resource_type == "Image":
        # Handle image resources
        canvas = manifest.make_canvas(id=f"{id_root}/canvas/{page_count}", label=label, height=height, width=width)
        canvas.add_image(image_url=kwargs["image_url"],
                         anno_page_id=f"{id_root}/page/{page_count}",
                         anno_id=f"{id_root}/annotation/{kwargs['filename']}",
                         format="image/jpeg",
                         height=height,
                         width=width)
    else:
        # Use ffprobe to get duration and format for audio/video
        duration, format_type = get_media_info(resource_path)
        
        # Create canvas for audio or video (height/width for video only)
        canvas = manifest.make_canvas(id=f"{id_root}/canvas/{page_count}", label=label)
        canvas.duration = duration

        # Create the AnnotationPage
        anno_page_id = f"{id_root}/canvas/{page_count}/page"
        annotation_page = AnnotationPage(id=anno_page_id)

        # Create media annotation with painting motivation
        annotation = Annotation(id=f"{id_root}/canvas/{page_count}/page/annotation",
                                motivation="painting",
                                body={
                                    "id": kwargs["media_url"],
                                    "type": "Video" if resource_type == "Video" else "Sound",
                                    "format": format_type,
                                    "duration": duration
                                },
                                target=f"{id_root}/canvas/{page_count}")  # Target the canvas ID

        # Add the annotation to the annotation page
        annotation_page.items.append(annotation)
        
        # Add the annotation page to the canvas
        canvas.items.append(annotation_page)

    return canvas



def create_iiif_manifest(file_dir, id_root, label, colID, objID, resource_type):
    # Create a new IIIF Manifest
    manifest = Manifest(id=f"{id_root}/manifest.json", label=label, behavior=["paged"])
    page_count = 0

    # Loop through the resources in the directory
    for resource_file in os.listdir(file_dir):
        resource_path = os.path.join(file_dir, resource_file)
        filename = urllib.parse.quote(os.path.splitext(resource_file)[0])
        quoted_file = urllib.parse.quote(resource_file.strip())
        page_count += 1

        if resource_type in ["Audio", "Video"]:
            # Use the media URL (modify this to suit your media hosting environment)
            media_url = f"http://lib-arcimg-p101.lib.albany.edu/meta/{colID}/{objID}/v1/{os.path.basename(file_dir)}/{quoted_file}"
            create_iiif_canvas(manifest, id_root, resource_file, resource_type, resource_path, page_count,
                               media_url=media_url, filename=filename)
        elif resource_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_info = f"http://lib-arcimg-p101.lib.albany.edu/iiif/3/%2F{colID}%2F{objID}%2Fv1%2Fjpg%2F{resource_file}/info.json"
            #print (resource_file)
            #print (image_info)
            r = requests.get(image_info)
            #print (r.status_code)
            response = r.json()

            image_url = f"http://lib-arcimg-p101.lib.albany.edu/iiif/3/%2F{colID}%2F{objID}%2Fv1%2Fjpg%2F{quoted_file}/full/max/0/default.jpg"
            create_iiif_canvas(manifest, id_root, resource_file, "Image", resource_path, page_count,
                               height=response["height"], width=response["width"], image_url=image_url, filename=filename)

    return manifest

def read_objects(collection_id=None):
    for collection in os.listdir(root):
        col_path = os.path.join(root, collection)

        # Check if collection_id is provided and matches the current collection
        if collection_id and collection_id not in collection:
            continue  # Skip this collection if it doesn't match

        if os.path.isdir(col_path):
            for obj in os.listdir(col_path):
                objPath = os.path.join(col_path, obj, "v1")
                metadataPath = os.path.join(objPath, "metadata.yml")
                manifestPath = os.path.join(objPath, "manifest.json")
                with open(metadataPath, 'r') as yml_file:
                    metadata = yaml.safe_load(yml_file)
                resource_type = metadata["resource_type"]
                if resource_type == "Audio":
                    filesPath = os.path.join(objPath, "ogg")
                elif resource_type == "Video":
                    filesPath = os.path.join(objPath, "webm")
                else:
                    filesPath = os.path.join(objPath, "jpg")

                if os.path.exists(filesPath):
                    print(f"{collection}/{obj}")

                    id_root = f"http://lib-arcimg-p101.lib.albany.edu/meta/{collection}/{obj}/v1"
                    manifest_label = f"{metadata['title'].strip()}, {metadata['date_created'].strip()}"

                    # Create the manifest
                    iiif_manifest = create_iiif_manifest(filesPath, id_root, manifest_label, collection, obj, resource_type)

                    # Save the manifest to a JSON file
                    with open(manifestPath, 'w') as f:
                        f.write(iiif_manifest.json(indent=2))

                    print("\t --> IIIF manifest created successfully!")
                else:
                    print(f"\tERROR: no path found {filesPath}")


if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        collection_id_arg = sys.argv[1]
        read_objects(collection_id=collection_id_arg)
    else:
        read_objects()
