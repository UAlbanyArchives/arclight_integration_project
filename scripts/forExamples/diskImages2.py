import os
import mimetypes
import requests
import urllib.parse
from iiif_prezi3 import Collection, Manifest, Canvas, Annotation, Service, AnnotationPage

# Define the URL root and root path
url_root = "https://media.archives.albany.edu"
root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "apap362", "kjo56png0e")

def fetch_image_dimensions(info_json_url):
    try:
        response = requests.get(info_json_url)
        response.raise_for_status()
        data = response.json()
        return data.get("width", 1000), data.get("height", 1000)  # Default to 1000x1000
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching dimensions for {info_json_url}: {e}")
        return None, None

def url_encode_path(path):
    """Encodes a path to make it URL-safe."""
    return urllib.parse.quote(path, safe="/:")

def create_manifest_for_pdf(path, pdf_filename, obj_id, base_url):
    encoded_obj_id = urllib.parse.quote(obj_id).replace("/", "%2F")
    escaped_obj_id = obj_id.replace(" ", "%20")
    manifest = Manifest(id=f"{base_url}/{escaped_obj_id}/manifest.json", 
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

def create_collection(path, obj_id, nested_items, base_url):
    """Create a IIIF Collection with references to manifests or collections."""
    # URL encode the obj_id for safe use in URLs
    encoded_obj_id = urllib.parse.quote(obj_id)
    collection = Collection(id=f"{base_url}/{encoded_obj_id}/collection.json", 
                            label={"en": [os.path.basename(obj_id)]})
    
    # Add references to nested items
    for item in nested_items:
        collection.items.append({
            "id": item.id.replace(" ", "%20"),
            "type": "Collection" if isinstance(item, Collection) else "Manifest",
            "label": {
                "en": [item.label["en"][0]]  # Use the same label as the item
            }
        })
    
    return collection

def create_manifest(path, obj_id, base_url):
    """
    Create a IIIF Manifest for a directory of files.

    Args:
        path (str): Path to the directory containing files.
        obj_id (str): Unique identifier for the object.
        base_url (str): Base URL for constructing IIIF resource URLs.

    Returns:
        Manifest: The generated IIIF Manifest object.
    """
    iiif_base_url = f"{base_url}/iiif/3"  # Base URL for IIIF services

    # Encode base_url and obj_id
    encoded_base_url = url_encode_path(base_url)
    encoded_obj_id = url_encode_path(obj_id).replace("/", "%2F")
    escaped_obj_id = obj_id.replace(" ", "%20")

    # Define manifest ID and label
    manifest_id = f"{base_url}/{escaped_obj_id}/manifest.json"
    manifest_label = obj_id

    # Initialize the manifest
    manifest = Manifest(id=manifest_id, label={"en": [manifest_label]})

    # Add manifest-level rendering for the "content.txt" file
    content_txt_path = os.path.join(path, "content.txt")
    if os.path.exists(content_txt_path):
        manifest.rendering = [
            {
                "id": f"{base_url}/{escaped_obj_id}/content.txt",
                "type": "Text",
                "label": {"en": ["Download Text"]},
                "format": "text/plain",
            }
        ]
    pdf_root = os.path.dirname(path)
    pdf_name = os.path.basename(path)
    if pdf_name.startswith("alt-"):
        pdf_name = pdf_name[4:]
    pdf_path = os.path.join(pdf_root, pdf_name + ".pdf")
    if os.path.exists(pdf_path):
        manifest.rendering.append(
            {
                "id": f"{base_url}/{os.path.dirname(escaped_obj_id)}/{pdf_name}.pdf",
                "type": "Text",
                "label": {"en": ["Download Original PDF"]},
                "format": "application/pdf",
            }
        )

    # Process .tiff and corresponding .hocr files
    manifest.items = []
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".tiff"):
            encoded_filename = url_encode_path(filename)
            tiff_path = os.path.join(path, filename)
            tiff_id = f"{iiif_base_url}/{encoded_obj_id}%2F{encoded_filename}/full/max/0/default.jpg"
            tiff_label = filename
            

            # Correct path for the IIIF image URL
            iiif_url_path = f"{encoded_obj_id}%2F{encoded_filename}"
            img_id = f"{iiif_base_url}/{iiif_url_path}"
            info_json_url = f"{img_id}/info.json"

            width, height = fetch_image_dimensions(info_json_url)

            # Create the Canvas
            canvas_id = f"{encoded_base_url}/{encoded_obj_id}/canvas/{url_encode_path(filename.split('.')[0])}"
            canvas = Canvas(
                id=canvas_id,
                label={"en": [tiff_label]},
                height=height,
                width=width,
            )

            # Create the AnnotationPage
            anno_page_id = f"{canvas_id}/page"
            annotation_page = AnnotationPage(id=anno_page_id, items=[])

            # Create the Annotation
            annotation = Annotation(
                id=f"{canvas_id}/annotation",
                motivation="painting",
                body={
                    "id": tiff_id,
                    "type": "Image",
                    "format": "image/tiff",
                    "height": height,
                    "width": width,
                    "service": [
                        {
                            "id": f"{encoded_base_url}/iiif/3/{encoded_obj_id}%2F{encoded_filename}",
                            "type": "ImageService3",
                            "profile": "level1",
                        }
                    ],
                },
                target=canvas_id,
            )

            # Add the Annotation to the AnnotationPage
            annotation_page.items.append(annotation)

            # Add the AnnotationPage to the Canvas
            canvas.items.append(annotation_page)


            # Check for corresponding HOCR file
            hocr_filename = f"{os.path.splitext(filename)[0]}.hocr"
            hocr_path = os.path.join(path, hocr_filename)
            if os.path.exists(hocr_path):
                encoded_hocr_filename = url_encode_path(hocr_filename)
                canvas.rendering = [
                    {
                        "id": f"{base_url}/{escaped_obj_id}/{encoded_hocr_filename}",
                        "type": "Text",
                        "label": {"en": ["HOCR data (OCR)"]},
                        "format": "text/vnd.hocr+html",
                        "profile": "http://kba.cloud/hocr-spec/1.2/",
                    }
                ]

            # Add canvas to manifest
            manifest.items.append(canvas)

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

            # Save the manifest as a JSON file directly in this directory
            manifest_json_path = os.path.join(path, 'manifest.json')
            with open(manifest_json_path, 'w') as f:
                f.write(manifest.json(indent=2))

    elif contains_dirs:
        obj_id = os.path.relpath(path, root_path).replace(os.sep, "/")
        for entry in entries:
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                nested_items = process_directory(entry_path, entry, base_url)
                items.extend(nested_items)
        
        if items:
            collection = create_collection(path, obj_id, items, base_url)

            collection_json_path = os.path.join(path, 'collection.json')
            with open(collection_json_path, 'w') as f:
                f.write(collection.json(indent=2))

            items = [collection]

    return items

def main():
    process_directory(obj_path, os.path.basename(obj_path), url_root)

if __name__ == "__main__":
    main()
