import os
import sys
import yaml
import json
import traceback
import urllib.parse
from PIL import Image
from iiif_prezi3 import Manifest, Canvas, Annotation, AnnotationPage, KeyValueString, config
from .utils import validate_config_and_paths, remove_nulls
from .utils import get_image_dimensions, get_media_info


def create_iiif_canvas(manifest, url_root, obj_url_root, label, resource_type, resource_path, page_count, thumbnail_data, **kwargs):
    """Create a IIIF Canvas for images, videos, or audio, with optional thumbnail."""
    supplementing_annotations = []
    renderings = []
    
    # Default to not setting height and width
    height = kwargs.get("height", None)
    width = kwargs.get("width", None)
    
    if resource_type == "Image":
        # Handle image resources
        canvas = manifest.make_canvas(id=f"{obj_url_root}/canvas/p{page_count}", label=label, height=height, width=width)
        service = [
                  {
                    "id": kwargs["image_url"],
                    "profile": "level1",
                    "type": "ImageService3"
                  }
                ]
        if kwargs.get("resource_format", None) == "ptif":
            image_mime = "image/tiff"
        else:
            image_mime = "image/jpeg"
        canvas.add_image(image_url=kwargs["image_url"] + "/full/max/0/default.jpg",
                         anno_page_id=f"{obj_url_root}/page/p{page_count}/{page_count}",
                         anno_id=f"{obj_url_root}/annotation/{kwargs['filename']}",
                         format=image_mime,
                         height=height,
                         width=width,
                         service=service)

        # Check for HOCR file for the image
        hocr_file = os.path.join(os.path.dirname(os.path.dirname(resource_path)), "hocr", f"{os.path.splitext(os.path.basename(resource_path))[0]}.hocr")
        if os.path.exists(hocr_file):
            canvas_rendering = {
                "id": f"{obj_url_root}/hocr/{urllib.parse.quote(os.path.basename(hocr_file))}",
                "label": "HOCR data (OCR)",
                "type": "Text",
                "format": "text/vnd.hocr+html",
                "profile": "http://kba.cloud/hocr-spec/1.2/"
            }
            canvas.rendering = [canvas_rendering]

    else:
        # Use ffprobe to get duration and format for audio/video
        duration, mimetype, video_width, video_height = get_media_info(resource_path)
    
        # Create canvas for audio or video (height/width for video only)
        canvas = manifest.make_canvas(id=f"{obj_url_root}/canvas/p{page_count}", label=label)
        canvas.duration = duration

        # Create the AnnotationPage
        anno_page_id = f"{obj_url_root}/canvas/page/p{page_count}{page_count}"
        annotation_page = AnnotationPage(id=anno_page_id)

        # Create media annotation with painting motivation
        annotation = Annotation(id=f"{obj_url_root}/canvas/{page_count}/page/annotation",
                                motivation="painting",
                                body={
                                    "id": kwargs["media_url"],
                                    "type": "Video" if resource_type == "Video" else "Sound",
                                    "format": mimetype,
                                    "duration": duration,
                                    "width": video_width,
                                    "height": video_height 
                                },
                                target=f"{obj_url_root}/canvas/p{page_count}")  # Target the canvas ID

        # Add the annotation to the annotation page
        annotation_page.items.append(annotation)

        if resource_type == "Audio":
            # include both ogg and mp3 audio for broader compatability
            obj_path = os.path.dirname(os.path.dirname(resource_path))
            audio_filename, audio_ext = os.path.splitext(os.path.basename(resource_path))
            ogg_path = os.path.join(obj_path, "ogg")
            mp3_path = os.path.join(obj_path, "mp3")
            if audio_ext == ".ogg" and os.path.isdir(mp3_path):
                audio_url = f"{obj_url_root}/mp3/{urllib.parse.quote(audio_filename)}.mp3"
                annotation_ogg = Annotation(
                    id=f"{obj_url_root}/canvas/{page_count}/page/annotation/mp3",
                    motivation="painting",
                    body={
                        "id": audio_url,
                        "type": "Sound",
                        "format": "audio/mpeg",
                        "duration": duration
                    },
                    target=f"{url_root}/canvas/p{page_count}"
                )
                annotation_page.items.append(annotation_ogg)
            elif audio_ext == ".mp3" and os.path.isdir(ogg_path):
                audio_url = f"{obj_url_root}/ogg/{urllib.parse.quote(audio_filename)}.ogg"
                annotation_mp3 = Annotation(
                    id=f"{obj_url_root}/canvas/{page_count}/page/annotation/ogg",
                    motivation="painting",
                    body={
                        "id": audio_url,
                        "type": "Sound",
                        "format": "audio/ogg",
                        "duration": duration
                    },
                    target=f"{obj_url_root}/canvas/p{page_count}"
                )
                annotation_page.items.append(annotation_mp3)

        
        # Add the annotation page to the canvas
        canvas.items.append(annotation_page)

        # Check for VTT file for the video/audio
        vtt_file = os.path.join(os.path.dirname(os.path.dirname(resource_path)), "vtt", f"{os.path.splitext(os.path.basename(resource_path))[0]}.vtt")
        if os.path.exists(vtt_file):
            supplementing_annotations.append({
                "id": f"{obj_url_root}/vtt/{os.path.basename(vtt_file)}",
                "type": "Text",
                "format": "text/vtt",
                "label": { "en": [ "WebVTT (captions)" ] }
            })
        
        # Check for TXT transcription file
        """ This isn't valid I don't think
        txt_file = os.path.join(os.path.dirname(os.path.dirname(resource_path)), "txt", f"{os.path.splitext(os.path.basename(resource_path))[0]}.txt")
        if os.path.exists(txt_file):
            renderings.append({
                "id": f"{obj_url_root}/txt/{os.path.basename(txt_file)}",
                "type": "Text",
                "format": "text/plain",
                "label": { "en": [ "Text transcription" ] }
            })
        """

    # Add supplementing annotations for VTT files
    if supplementing_annotations:
        canvas.annotations = [{
            "id": f"{obj_url_root}/canvas/{page_count}/supplementing",
            "type": "AnnotationPage",
            "items": [
                {
                    "id": f"{obj_url_root}/canvas/{page_count}/annotation",
                    "type": "Annotation",
                    "motivation": "supplementing",
                    "body": supplementing_annotations,
                    "target": f"{url_root}/canvas/p{page_count}"
                }
            ]
        }]

    # Add any alternative renderings
    if renderings:
        canvas.rendering = renderings

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




def create_iiif_manifest(file_dir, url_root, obj_url_root, iiif_url_root, resource_format, label, metadata, thumbnail_data, resource_type):
    orgText = "M.E. Grenander Department of Special Collections and Archives, University Libraries, University at Albany, State University of New York"

    # Set IIIF manifest behavior
    behavior = ["individuals"]
    if "behavior" in metadata.keys():
        behavior = [metadata["behavior"]]

    # Set rights and metadata
    attributionStatement = orgText
    rights = None  # Initialize rights
    if "license" in metadata and metadata['license'] and metadata['license'].lower().strip() != "unknown":
        rights = metadata["license"]
        if "publicdomain" in rights:
            attributionStatement = f"<span>This object is in the public domain, but you are encouraged to attribute: <br/> {orgText} <br/> <a href=\"{rights}\" title=\"Public Domain\"><img src=\"https://licensebuttons.net/p/88x31.png\"/></a></span>"
        elif "by-nc-nd" in rights:
            attributionStatement = f"<span>{orgText} <br/> <a href=\"{rights}\" title=\"CC BY-NC-ND 4.0\"><img src=\"https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png\"/></a></span>"
    elif "rights_statement" in metadata and metadata['rights_statement']:
        rights = metadata["rights_statement"]
        if "InC-EDU" in rights:
            rights = "https://rightsstatements.org/page/InC-EDU/1.0/"
            stmt = "In Copyright - Educational Use Permitted"
            attributionStatement = f"<span>{orgText} <br/> <a href=\"{rights}\" title=\"{stmt}\"><img src=\"https://rightsstatements.org/files/buttons/InC-EDU.dark.svg\"/></a></span>"
    else:
        rights = "https://rightsstatements.org/page/InC-EDU/1.0/"
        stmt = "In Copyright - Educational Use Permitted"
        attributionStatement = f"<span>{orgText} <br/> <a href=\"{rights}\" title=\"{stmt}\"><img src=\"https://rightsstatements.org/files/buttons/InC-EDU.dark.svg\"/></a></span>"

    # Correct structure for requiredStatement using KeyValueString
    requiredStatement = KeyValueString(label="Attribution", value=attributionStatement)

    # Create a new IIIF Manifest
    manifest = Manifest(
        id=f"{obj_url_root}/manifest.json",
        label=label,
        behavior=behavior,
        rights=rights,
        requiredStatement=requiredStatement,
    )

    # Add metadata fields to the manifest
    fields = [
        "title", 
        "date_display", 
        "resource_type", 
        "coverage", 
        "extent", 
        "collection", 
        "collecting_area", 
        "description", 
        "subject",
        "processing_activity",
        "creator",
        "contributor",
        "identifier",
        "source",
        "master_format",
        "date_digitized",
        "date_published"
    ]
    manifest.metadata = []
    for key, value in metadata.items():
        if key in fields:
            if value:  # Only add metadata if the value is not empty
                if isinstance(value, list):  # Handle list of values
                    manifest.metadata.append({
                        "label": {"en": [key]},
                        "value": {"en": value}  # Directly use the list
                    })
                else:  # Handle single value
                    manifest.metadata.append({
                        "label": {"en": [key]},
                        "value": {"en": [value]}
                    })

    # Loop through the resources in the directory
    page_count = 0
    sorted_files = []
    for resource_file in os.listdir(file_dir):
        sorted_files.append(resource_file)
    for resource_file in sorted(sorted_files):
        resource_path = os.path.join(file_dir, resource_file)
        filename = urllib.parse.quote(os.path.splitext(resource_file)[0])
        quoted_file = urllib.parse.quote(resource_file.strip())
        page_count += 1

        if resource_type in ["Audio", "Video"]:
            # Use the media URL (modify this to suit your media hosting environment)
            media_url = f"{obj_url_root}/{os.path.basename(file_dir)}/{quoted_file}"
            create_iiif_canvas(manifest, url_root, obj_url_root, resource_file, resource_type, resource_path, page_count, thumbnail_data,
                               media_url=media_url, filename=filename)
        elif resource_file.lower().endswith(resource_format.lower()):
            img_width, img_height = get_image_dimensions(resource_path)

            image_url = f"{iiif_url_root}%2F{quoted_file}"
            create_iiif_canvas(manifest, url_root, obj_url_root, resource_file, "Image", resource_path, page_count, thumbnail_data,
                               resource_format=resource_format, height=img_height, width=img_width, image_url=image_url, filename=filename)
    manifest_renderings = []
    # Check for alternative renderings to add
    alt_rendering_formats = {
        "pdf": {
            "mimetype": "application/pdf",
            "label": "Download PDF"
        },
        "docx": {
            "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "label": "Download DOCX"
        },
        "doc": {
            "mimetype": "application/msword",
            "label": "Download DOC"
        },
        "rtf": {
            "mimetype": "text/rtf",
            "label": "Download RTF"
        },
        "xlsx": {
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "label": "Download XLSX"
        },
        "xls": {
            "mimetype": "application/vnd.ms-excel",
            "label": "Download XLS"
        },
        "pptx": {
            "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "label": "Download PPTX"
        },
        "ppt": {
            "mimetype": "application/vnd.ms-powerpoint",
            "label": "Download PPT"
        },
        "mp3": {
            "mimetype": "audio/mpeg",
            "label": "Download MP3"
        },
        "mp4": {
            "mimetype": "video/mp4",
            "label": "Download MP4"
        },
        "mov": {
            "mimetype": "video/quicktime",
            "label": "Download MOV"
        },
        "zip": {
            "mimetype": "application/zip",
            "label": "Download ZIP package"
        },
        "txt": {
            "mimetype": "text/plain",
            "label": "Download Text transcription"
        },
        "csv": {
            "mimetype": "text/csv",
            "label": "Download CSV transcription"
        }
    }
    original_file = metadata.get("original_file_legacy", None)
    original_format = os.path.splitext(original_file)[1][1:]
    plaintext_switch = False
    contentTxt = os.path.join(os.path.dirname(file_dir), "content.txt")
    if os.path.isfile(contentTxt):
        manifest_renderings.append({
                    "id": f"{obj_url_root}/content.txt",
                    "type": "Text",
                    "format": "text/plain",
                    "label": "Download Text transcription"
                })
    for format_ext in alt_rendering_formats.keys():
        rendering_format = os.path.join(os.path.dirname(file_dir), format_ext)
        # If there is a single file
        #if os.path.isdir(rendering_format) and len(os.listdir(rendering_format)) == 1:
        if os.path.isdir(rendering_format):
            rendering_files = []
            if len(os.listdir(rendering_format)) == 1 or not "file_sets" in metadata.keys():
                rendering_files = [os.listdir(rendering_format)[0]]
            else:
                for file_set in metadata["file_sets"].values():
                    if file_set.lower().endswith(format_ext):
                        rendering_files.append(file_set)

            for rendering_file in rendering_files:
                rendering_filepath = os.path.join(rendering_format, rendering_file)
                if os.path.isfile(rendering_filepath):
                    if rendering_file == original_file:
                        alt_label = f"{rendering_file} (Original)"
                    elif format_ext == "txt":
                        # skip text renderings if content.txt already added
                        if os.path.isfile(contentTxt):
                            continue
                        else:
                            alt_label = alt_rendering_formats[format_ext]['label']
                    else:
                        alt_label = rendering_file
                    manifest_renderings.append({
                        "id": f"{obj_url_root}/{format_ext}/{urllib.parse.quote(os.path.basename(rendering_file))}",
                        "type": "Text",
                        "format": alt_rendering_formats[format_ext]["mimetype"],
                        "label": alt_label
                    })
    if manifest_renderings:
        manifest.rendering = manifest_renderings

    return manifest


def create_manifest(collection_id, object_id, config_path="~/.iiiflow.yml"):
    """
    Creates a manifest.json compliant with the IIIF v3 Presentation API
    Designed to be used with the discovery storage specification.
    https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md

    Args:
        collection_id (str): The collection ID.
        object_id (str): The object ID.
        config_path (str): Path to the configuration YAML file.
    """

    # Read config and validate paths
    discovery_storage_root, log_file_path, object_path, url_root = validate_config_and_paths(
        config_path, collection_id, object_id, True
    )

    metadataPath = os.path.join(object_path, "metadata.yml")
    manifestPath = os.path.join(object_path, "manifest.json")
    with open(metadataPath, 'r', encoding='utf-8') as yml_file:
        metadata = yaml.safe_load(yml_file)

    resource_type = metadata["resource_type"]
    if resource_type == "Audio":
        oggPath = os.path.join(object_path, "ogg")
        mp3Path = os.path.join(object_path, "mp3")
        if os.path.isdir(oggPath) and len(os.listdir(oggPath)) > 0:
            resource_format = "ogg"
            filesPath = oggPath
        elif os.path.isdir(mp3Path) and len(os.listdir(mp3Path)) > 0:
            resource_format = "mp3"
            filesPath = mp3Path
    elif resource_type == "Video":
        resource_format = "webm"
        filesPath = os.path.join(object_path, resource_format)
    else:
        filesPath = os.path.join(object_path, "ptif")
        if not os.path.isdir(filesPath):
            filesPath = os.path.join(object_path, "jpg")
            resource_format = "jpg"
        else:
            resource_format = "ptif"

    if os.path.isdir(filesPath):
        print(f"{collection_id}/{object_id}")

        obj_url_root = f"{url_root}/{collection_id}/{object_id}"
        iiif_url_root = f"{url_root}/iiif/3/%2F{collection_id}%2F{object_id}%2F{resource_format}"
        if "title" in metadata.keys():
            manifest_label = metadata['title'].strip()
            if "date_display" in metadata.keys():
                manifest_label = manifest_label + f", {metadata['date_display'].strip()}"
        elif "manfest_label" in metadata.keys():
            manifest_label = metadata['manfest_label'].strip()

        thumbnail_path = os.path.join(object_path, "thumbnail.jpg")
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
        iiif_manifest = create_iiif_manifest(filesPath, url_root, obj_url_root, iiif_url_root, resource_format, manifest_label, metadata, thumbnail_data, resource_type)
        manifest_dict = iiif_manifest.dict()
        manifest_dict = remove_nulls(manifest_dict)
        manifest_output = {
            '@context': "http://iiif.io/api/presentation/3/context.json",
            'logo': f"{url_root}/logo.png",
            **manifest_dict
        }

        # Save the manifest to a JSON file
        with open(manifestPath, 'w') as f:
            json.dump(manifest_output, f, indent=2)

        print("\t --> IIIF manifest created successfully!")
    else:
        print(f"\tERROR: no path found {filesPath}")

