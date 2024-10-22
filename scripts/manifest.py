import os
import sys
import yaml
import requests
import urllib.parse
from PIL import Image
from get_media_info import get_media_info
from iiif_prezi3 import Manifest, Canvas, Annotation, AnnotationPage, config

config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"


def create_iiif_canvas(manifest, url_root, label, resource_type, resource_path, page_count, thumbnail_data, **kwargs):
    """Create a IIIF Canvas for images, videos, or audio, with optional thumbnail."""
    
    # Default to not setting height and width
    height = kwargs.get("height", None)
    width = kwargs.get("width", None)
    
    if resource_type == "Image":
        # Handle image resources
        canvas = manifest.make_canvas(id=f"{url_root}/canvas/p{page_count}", label=label, height=height, width=width)
        service = [
                  {
                    "id": kwargs["image_url"],
                    "profile": "level1",
                    "type": "ImageService3"
                  }
                ]
        canvas.add_image(image_url=kwargs["image_url"] + "/full/max/0/default.jpg",
                         anno_page_id=f"{url_root}/page/p{page_count}/{page_count}",
                         anno_id=f"{url_root}/annotation/{kwargs['filename']}",
                         format="image/jpeg",
                         height=height,
                         width=width,
                         service=service)
    else:
        # Use ffprobe to get duration and format for audio/video
        duration, mimetype, video_width, video_height = get_media_info(resource_path)

        
        # Create canvas for audio or video (height/width for video only)
        canvas = manifest.make_canvas(id=f"{url_root}/canvas/p{page_count}", label=label)
        canvas.duration = duration

        # Create the AnnotationPage
        anno_page_id = f"{url_root}/canvas/page/p{page_count}{page_count}"
        annotation_page = AnnotationPage(id=anno_page_id)

        # Create media annotation with painting motivation
        annotation = Annotation(id=f"{url_root}/canvas/{page_count}/page/annotation",
                                motivation="painting",
                                body={
                                    "id": kwargs["media_url"],
                                    "type": "Video" if resource_type == "Video" else "Sound",
                                    "format": mimetype,
                                    "duration": duration,
                                    "width": video_width,
                                    "height": video_height 
                                },
                                target=f"{url_root}/canvas/p{page_count}")  # Target the canvas ID

        # Add the annotation to the annotation page
        annotation_page.items.append(annotation)
        
        # Add the annotation page to the canvas
        canvas.items.append(annotation_page)

    # Add thumbnail if thumbnail_url is provided
    if page_count == 1 and "url" in thumbnail_data:
        thumbnail_width = thumbnail_data.get("width", None)
        thumbnail_height = thumbnail_data.get("height", None)

        thumbnail = {
            "id": thumbnail_data["url"],
            "type": "Image",
            "format": "image/jpeg",
        }

        # Add optional width and height if provided
        if thumbnail_width and thumbnail_height:
            thumbnail["width"] = thumbnail_width
            thumbnail["height"] = thumbnail_height

        canvas.thumbnail = [thumbnail]

    return canvas



def create_iiif_manifest(file_dir, url_root, obj_url_root, iiif_url_root, label, behavior, thumbnail_data, resource_type):
    # Create a new IIIF Manifest
    manifest = Manifest(id=f"{obj_url_root}/manifest.json", label=label, behavior=[behavior])
    page_count = 0

    # Loop through the resources in the directory
    for resource_file in os.listdir(file_dir):
        resource_path = os.path.join(file_dir, resource_file)
        filename = urllib.parse.quote(os.path.splitext(resource_file)[0])
        quoted_file = urllib.parse.quote(resource_file.strip())
        page_count += 1

        if resource_type in ["Audio", "Video"]:
            # Use the media URL (modify this to suit your media hosting environment)
            media_url = f"{obj_url_root}/{os.path.basename(file_dir)}/{quoted_file}"
            create_iiif_canvas(manifest, url_root, resource_file, resource_type, resource_path, page_count, thumbnail_data,
                               media_url=media_url, filename=filename)
        elif resource_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_info = f"{iiif_url_root}%2F{quoted_file}/info.json"
            r = requests.get(image_info)
            #print (r.status_code)
            response = r.json()

            image_url = f"{iiif_url_root}%2F{quoted_file}"#/full/max/0/default.jpg"
            create_iiif_canvas(manifest, url_root, resource_file, "Image", resource_path, page_count, thumbnail_data,
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

                if os.path.isdir(filesPath):
                    print(f"{collection}/{obj}")

                    # set IIIF manifest behavior
                    behavior = "individuals"
                    if "original_format" in metadata.keys():
                        if metadata["original_format"] == "pdf":
                            behavior = "paged"

                    #url_root = f"https://media.archives.albany.edu"
                    url_root = f"http://lib-arcimg-p101.lib.albany.edu"
                    obj_url_root = f"{url_root}/meta/{collection}/{obj}/v1"
                    iiif_url_root = f"{url_root}/iiif/3/%2F{collection}%2F{obj}%2Fv1%2Fjpg"
                    manifest_label = f"{metadata['title'].strip()}, {metadata['date_created'].strip()}"

                    thumbnail_path = os.path.join(objPath, "thumbnail.jpg")
                    thumbnail_url = f"{obj_url_root}/thumbnail.jpg"
                    # Get the width and height of the thumbnail image
                    try:
                        with Image.open(thumbnail_path) as img:
                            thumbnail_width, thumbnail_height = img.size
                    except Exception as e:
                        print(f"Error reading thumbnail image: {e}")
                        thumbnail_width = None
                        thumbnail_height = None
                    thumbnail_data = {"url": thumbnail_url, "width": thumbnail_width, "height": thumbnail_height}
                    
                    # Create the manifest
                    iiif_manifest = create_iiif_manifest(filesPath, url_root, obj_url_root, iiif_url_root, manifest_label, behavior, thumbnail_data, resource_type)

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
