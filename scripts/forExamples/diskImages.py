import os
import requests
import urllib.parse
from iiif_prezi3 import Collection, Manifest, Service

# Define the URL root
url_root = "https://media.archives.albany.edu"
root_path = "\\\\Lincoln\\Library\\SPE_DAO" if os.name == "nt" else "/media/Library/SPE_DAO"
obj_path = os.path.join(root_path, "apap362", "5uvc0cb36g")

def fetch_image_dimensions(info_json_url):
    """Fetch the dimensions of an image from its IIIF info.json URL."""
    try:
        response = requests.get(info_json_url)
        response.raise_for_status()
        data = response.json()
        return data["width"], data["height"]
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching dimensions for {info_json_url}: {e}")
        return None, None  # Default to None if there's an error

def create_manifest(path, obj_id, base_url):
    """Create a IIIF Manifest for a given directory."""
    encoded_obj_id = urllib.parse.quote(obj_id).replace("/", "%2F")
    manifest = Manifest(id=f"{base_url}/{encoded_obj_id.replace('%2F', '/')}/manifest.json", 
                        label={"en": [os.path.basename(obj_id)]})

    iiif_base_url = f"{base_url}/iiif/3"  # Base URL for IIIF services

    for filename in os.listdir(path):
        if filename.startswith('.'):  # Skip dotfiles
            continue
        if filename.startswith('alt-'):  # Skip alternative formats
            continue
        if not filename.lower().endswith('.tiff'):  # Skip non-tiffs
            continue
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            # Construct the relative path from the `examples/{obj_id}` directory
            relative_path = os.path.relpath(file_path, start=path)
            # Encode the entire path including slashes
            encoded_full_path = urllib.parse.quote(relative_path, safe='')

            # Correct path for the IIIF image URL
            iiif_url_path = f"{encoded_obj_id}%2F{encoded_full_path}"
            img_id = f"{iiif_base_url}/{iiif_url_path}"
            info_json_url = f"{img_id}/info.json"

            # Fetch image dimensions from info.json
            width, height = fetch_image_dimensions(info_json_url)
            canvas_id = f"{base_url}/{encoded_obj_id}/canvas/{encoded_full_path}"
            canvas = manifest.make_canvas(id=canvas_id)
            canvas.width = width
            canvas.height = height
            
            # Define the service dictionary for the image service
            service = {
                "id": img_id,
                "profile": "level1",
                "type": "ImageService3"
            }

            # Add image to canvas with the service definition
            canvas.add_image(
                image_url=f"{img_id}/full/max/0/default.jpg",
                anno_page_id=f"{iiif_base_url}/{encoded_obj_id}/page/{encoded_full_path}",
                anno_id=f"{iiif_base_url}/{encoded_obj_id}/annotation/{encoded_full_path}",
                format="image/tiff",
                height=height,
                width=width,
                service=[service]
            )
    
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
            "id": item.id,
            "type": "Collection" if isinstance(item, Collection) else "Manifest",
            "label": {
                "en": [item.label["en"][0]]  # Use the same label as the item
            }
        })
    
    return collection

def process_directory(path, parent_id, base_url):
    """Recursively process directories to generate manifests and collections."""
    items = []
    entries = [entry for entry in os.listdir(path) if not entry.startswith('.')]
    contains_files = any(os.path.isfile(os.path.join(path, f)) for f in entries)
    contains_dirs = any(os.path.isdir(os.path.join(path, d)) for d in entries)

    if contains_files and not contains_dirs:
        # Create a manifest if this folder only has files
        obj_id = os.path.relpath(path, root_path).replace(os.sep, "/")
        manifest = create_manifest(path, obj_id, base_url)
        items.append(manifest)

        # Save the manifest as a JSON file directly in this directory
        manifest_json_path = os.path.join(path, 'manifest.json')
        with open(manifest_json_path, 'w') as f:
            f.write(manifest.json(indent=2))

    elif contains_dirs:
        # Create a collection if this folder contains other folders
        obj_id = os.path.relpath(path, root_path).replace(os.sep, "/")
        for entry in entries:
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                nested_items = process_directory(entry_path, entry, base_url)
                items.extend(nested_items)
        
        if items:
            collection = create_collection(path, obj_id, items, base_url)

            # Save the collection as a JSON file directly in this directory
            collection_json_path = os.path.join(path, 'collection.json')
            with open(collection_json_path, 'w') as f:
                f.write(collection.json(indent=2))

            # Add the collection to the list of items
            items = [collection]  # Wrap in a collection

    return items

def main():
    # Generate the IIIF collection or manifest structure based on obj_path
    process_directory(obj_path, os.path.basename(obj_path), url_root)

if __name__ == "__main__":
    main()
