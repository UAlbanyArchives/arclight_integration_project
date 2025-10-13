import time
import argparse
from iiiflow import collections, index_hocr_to_solr

def format_elapsed(seconds):
    """Return a human-readable string for elapsed seconds."""
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours}h {mins}m {secs}s"
    elif mins:
        return f"{mins}m {secs}s"
    else:
        return f"{secs}s"

def main():
    parser = argparse.ArgumentParser(description="Update IIIF manifests.")
    parser.add_argument(
        "--collection-id",
        help="Limit to a specific collection ID (e.g., apap101)",
        default=None,
    )

    args = parser.parse_args()

    start_time = time.time()

    for collection in collections:
        if args.collection_id and collection.id != args.collection_id:
            continue

        print(f"Indexing collection: {collection.id}")
        for object_id in collection.objects:
            index_hocr_to_solr(collection.id, object_id)

    elapsed = time.time() - start_time
    print(f"\Time elapsed: {format_elapsed(elapsed)}")
    