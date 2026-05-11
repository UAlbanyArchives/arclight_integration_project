import os

# Function to retrieve the root directory where collections are stored
def storage_root(config_path="~/.iiiflow.yml"):
    from .utils import validate_config_and_paths

    # `validate_config_and_paths` returns three values: discovery_storage_root, log_file_path, and object_path
    # Here, without sending it a collection_id and object_id, object_path will be None
    discovery_storage_root, log_file_path, object_path = validate_config_and_paths(config_path)
    
    # Return the path where collections can be found (discovery storage root)
    return discovery_storage_root

# Class for a single collection of objects
class Collection:
    def __init__(self, id, collection_path):
        """
        Initialize a Collection object with an ID and the path to the collection directory.
        
        Args:
            id (str): The unique identifier for the collection (e.g., "apap101").
            collection_path (str): The file system path to the collection directory.
        """
        self.id = id
        self.path = collection_path

    @property
    def objects(self):
        """
        Lazily load the objects (subdirectories) within the collection directory.
        
        This property will only be called when accessed, and it will list all subdirectories
        within the collection's directory. These subdirectories are assumed to represent objects
        in the collection.

        Returns:
            list: A list of subdirectory names (objects) within the collection's directory.
        """
        # List all subdirectories (objects) inside the collection's directory
        return [f for f in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, f))]

# Collections class that holds multiple Collection objects
class Collections:
    def __init__(self, storage_root):
        """
        Initialize the Collections object, which will hold multiple Collection objects.
        
        Args:
            storage_root (str): The root directory path where all collections are stored.
        """
        self.collections = []  # Initialize an empty list to store the Collection objects
        # Iterate through all items in the storage_root directory
        for collection_id in os.listdir(storage_root):
            collection_path = os.path.join(storage_root, collection_id)  # Get the full path for each collection
            if os.path.isdir(collection_path):  # Check if the item is a directory (indicating a collection)
                # If it is a directory, create a new Collection object and add it to the collections list
                self.collections.append(Collection(id=collection_id, collection_path=collection_path))
    
    def __len__(self):
        """Return the number of collections."""
        return len(self.collections)
    
    def __iter__(self):
        """
        Make the Collections object iterable. This allows us to loop through all collections.

        Returns:
            iterator: An iterator over the list of Collection objects.
        """
        return iter(self.collections)

def get_collections(config_path="~/.iiiflow.yml"):
    """Create and return a Collections instance on demand."""
    return Collections(storage_root(config_path))


def __getattr__(name):
    """Lazily initialise `collections` on first access so import-time side effects
    (reading ~/.iiiflow.yml, scanning the filesystem) are deferred until needed."""
    if name == "collections":
        import sys
        value = get_collections()
        setattr(sys.modules[__name__], "collections", value)
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def create_ptif(*args, **kwargs):
    from .ptif import create_ptif as _create_ptif
    return _create_ptif(*args, **kwargs)


def create_pdf(*args, **kwargs):
    from .pdf import create_pdf as _create_pdf
    return _create_pdf(*args, **kwargs)


def create_hocr(*args, **kwargs):
    from .tesseract import create_hocr as _create_hocr
    return _create_hocr(*args, **kwargs)


def make_thumbnail(*args, **kwargs):
    from .thumbnail import make_thumbnail as _make_thumbnail
    return _make_thumbnail(*args, **kwargs)


def validate_metadata(*args, **kwargs):
    from .metadata import validate_metadata as _validate_metadata
    return _validate_metadata(*args, **kwargs)


def update_metadata(*args, **kwargs):
    from .metadata import update_metadata as _update_metadata
    return _update_metadata(*args, **kwargs)


def create_manifest(*args, **kwargs):
    from .manifest import create_manifest as _create_manifest
    return _create_manifest(*args, **kwargs)


def create_transcription(*args, **kwargs):
    from .transcribe import create_transcription as _create_transcription
    return _create_transcription(*args, **kwargs)


def pdf_to_jpgs(*args, **kwargs):
    from .conversions import pdf_to_jpgs as _pdf_to_jpgs
    return _pdf_to_jpgs(*args, **kwargs)


def index_hocr_to_solr(*args, **kwargs):
    from .hocr_indexer import index_hocr_to_solr as _index_hocr_to_solr
    return _index_hocr_to_solr(*args, **kwargs)
