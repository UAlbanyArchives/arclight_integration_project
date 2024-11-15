import os
import mimetypes
import requests
import urllib.parse
from iiif_prezi3 import Collection, Manifest, Canvas, Annotation, Service

# Define the URL root and root path
url_root = "https://media.archives.albany.edu"
root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "apap362", "kjo56png0e")

def fetch_image_dimensions(info_json_url):
    try:
        response = requests.get(info_json_url)
        response.raise_for_status()
        data = response.json()
        return data.get("width"), data.get("height")
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching dimensions for {info_json_url}: {e}")
        return None, None

def create_manifest_for_pdf(path, pdf_filename, obj_id, base_url):
    encoded_obj_id = urllib.parse.quote(obj_id).replace("/", "%2F")
    manifest = Manifest(id=f"{base_url}/{encoded_obj_id}/manifest.json", 
                        label={"en": [os.path.splitext(pdf_filename)[0]]})
    
    alt_dir = os.path.join(path, f"alt-{os.path.splitext(pdf_filename)[0]}")
    if not os.path.isdir(alt_dir):
        print(f"Alternative directory '{alt_dir}' not found for PDF '{pdf_filename}'")
        return manifest

    tiff_files = sorted([f for f in os.listdir(alt_dir) if f.lower().endswith(".tiff")])
    for page_num, tiff_file in enumerate(tiff_files, start=1):
        page_path = os.path.join(alt_dir, tiff_file)
        width, height = fetch_image_dimensions(f"{base_url}/iiif/3/{encoded_obj_id}/{tiff_file}/info.json")
        canvas = manifest.make_canvas(id=f"{base_url}/{encoded_obj_id}/canvas/p{page_num}", width=width, height=height)
        
        # Add main image (TIFF) and alternative HOCR rendering if available
        canvas.add_image(
            image_url=f"{base_url}/iiif/3/{encoded_obj_id}/{tiff_file}/full/max/0/default.jpg",
            anno_page_id=f"{base_url}/{encoded_obj_id}/page/p{page_num}",
            anno_id=f"{base_url}/{encoded_obj_id}/annotation/p{page_num}",
            format="image/tiff",
            width=width,
            height=height
        )
        
        hocr_file = tiff_file.replace(".tiff", ".hocr")
        hocr_path = os.path.join(alt_dir, hocr_file)
        if os.path.isfile(hocr_path):
            canvas.alternative.extend([{
                "id": f"{base_url}/{encoded_obj_id}/hocr/{hocr_file}",
                "type": "Text",
                "format": "application/vnd.hocr+html"
            }])

    # Add original PDF and content.txt as alternative renderings
    manifest.alternative.extend([
        {"id": f"{base_url}/{encoded_obj_id}/{pdf_filename}", "type": "File", "format": "application/pdf"},
        {"id": f"{base_url}/{encoded_obj_id}/alt-{os.path.splitext(pdf_filename)[0]}/content.txt", "type": "Text", "format": "text/plain"}
    ])
    
    return manifest

def create_manifest(path, obj_id, base_url):
    encoded_obj_id = urllib.parse.quote(obj_id).replace("/", "%2F")
    manifest = Manifest(id=f"{base_url}/{encoded_obj_id.replace('%2F', '/')}/manifest.json", 
                        label={"en": [os.path.basename(obj_id)]})

    iiif_base_url = f"{base_url}/iiif/3"

    for filename in os.listdir(path):
        if filename.startswith('.') or filename.startswith('alt-'):
            continue
        file_path = os.path.join(path, filename)
        mime_type, _ = mimetypes.guess_type(file_path)
        encoded_full_path = urllib.parse.quote(filename, safe='')

        if filename.lower().endswith(".gif"):
            img_id = f"{iiif_base_url}/{encoded_obj_id}%2F{encoded_full_path}"
            width, height = fetch_image_dimensions(f"{img_id}/info.json")
            canvas = manifest.make_canvas(id=f"{base_url}/{encoded_obj_id}/canvas/{encoded_full_path}", width=width, height=height)
            canvas.add_image(
                image_url=f"{img_id}/full/max/0/default.jpg",
                anno_page_id=f"{iiif_base_url}/{encoded_obj_id}/page/{encoded_full_path}",
                anno_id=f"{iiif_base_url}/{encoded_obj_id}/annotation/{encoded_full_path}",
                format="image/gif",
                width=width,
                height=height,
                service=[{"id": img_id, "type": "ImageService3", "profile": "level1"}]
            )
        else:
            # Non-image files (e.g., audio/video) as direct files in the manifest
            canvas_id = f"{base_url}/{encoded_obj_id}/canvas/{encoded_full_path}"
            canvas = manifest.make_canvas(id=canvas_id)
            canvas.items.append({
                "id": f"{base_url}/{encoded_obj_id}/page/{encoded_full_path}",
                "type": "AnnotationPage",
                "items": [{
                    "id": f"{base_url}/{encoded_obj_id}/annotation/{encoded_full_path}",
                    "type": "Annotation",
                    "motivation": "painting",
                    "body": {
                        "id": f"{base_url}/{encoded_obj_id}/{filename}",
                        "type": "File",
                        "format": mime_type,
                    },
                    "target": canvas_id
                }]
            })

    return manifest

def process_directory(path, parent_id, base_url):
    items = []
    entries = [entry for entry in os.listdir(path) if not entry.startswith('.')]
    contains_files = any(os.path.isfile(os.path.join(path, f)) for f in entries)
    contains_dirs = any(os.path.isdir(os.path.join(path, d)) for d in entries)

    if contains_files and not contains_dirs:
        obj_id = os.path.relpath(path, root_path).replace(os.sep, "/")
        if any(entry.lower().endswith(".pdf") for entry in entries):
            for entry in entries:
                if entry.lower().endswith(".pdf"):
                    manifest = create_manifest_for_pdf(path, entry, obj_id, base_url)
                    items.append(manifest)
        else:
            manifest = create_manifest(path, obj_id, base_url)
            items.append(manifest)
    elif contains_dirs:
        obj_id = os.path.relpath(path, root_path).replace(os.sep, "/")
        for entry in entries:
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                nested_items = process_directory(entry_path, entry, base_url)
                items.extend(nested_items)
        
        if items:
            collection = create_collection(path, obj_id, items, base_url)
            items = [collection]

    return items

def main():
    process_directory(obj_path, os.path.basename(obj_path), url_root)

if __name__ == "__main__":
    main()
