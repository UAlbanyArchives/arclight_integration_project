# Arclight Integration Project
Integrating Arclight with Digital Content, IIIF, and ArchivesSpace

## IIIFlow

This is a python package that uses the directory structure defined in the [Digital Object Discovery Storage Specification](https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md) for a IIIF pipeline.

iiiflow functions create pyramidal tiffs, thumbnails, HOCR and text transcriptions, and combines them all into a IIIF v3 manifest.

### Setup

#### Prereqisites

In addition to python dependancies in `requirements.txt`, there are some OS dependancies.

* Pyramidal tiffs requires [vips](https://github.com/libvips/libvips)
* Thumbnail generation requires [ImageMagick](https://imagemagick.org/index.php) (should probably be changed to vips)
* HOCR requires [tesseract](https://github.com/tesseract-ocr/tesseract)
* A/V transcriptions requires [whisper](https://github.com/openai/whisper)

#### Config

iiiflow expects a `.iiiflow.yml` config file in your home directory (`~`) that defines paths to the root of your Digital Object Discovery Storage, error log, and a base url for where your images are hosted.

```
---
provider: My provider
discovery_storage_root: /path/to/digital_object_root
manifest_url_root: https://my.server.org
image_api_root: https://my.server.org/iiif/3
error_log_file: /path/to/errors.log
audio_thumbnail_file: ./fixtures/thumbnail.jpg
lang_code: en
solr_url: http://localhost:8983
solr_core: iiif_content_search
content_search_url: https://my.server.org/search/1
```

Optionally, you can pass the path to any `.yml` file as the last arg of any iiiflow function.

For audio thumbnails and test to work, set audio_thumbnail_file to either a local path or accessible url to an image file.

For Solr indexing and content search functionality:
- `solr_url`: URL to your Solr instance (e.g., http://localhost:8983)
- `solr_core`: Name of the Solr core for content search (default: iiif_content_search)
- `content_search_url`: The URL for your IIIF Content Search 1.0 endpoint

```
create_ptif("collection1", "object1", "path/to/config.yml")
```

### Create thumbnails

Creates a 300x300 thumbnail.jpg

```
from iiiflow import make_thumbnail

make_thumbnail("collection1", "object1")
```

### Create a PDF

Creates a PDF alternative rendering

```
from iiiflow import create_pdf

create_pdf("collection1", "object1")
```

### Create pyramidal Tiffs

Uses the .ptif extension to distinguish from traditional tiffs.

```
from iiiflow import create_ptif

create_ptif("collection1", "object1")
```

### Recognize text and create .hocr

```
from iiiflow import create_hocr

create_hocr("collection1", "object1")
```

### Create A/V transcription

```
from iiiflow import create_transcription

create_transcription("collection1", "object1")
```

### Index HOCR content to Solr

Indexes HOCR content to Solr for IIIF Content Search 2.0 support. This enables text search functionality in IIIF viewers.

```
from iiiflow import index_hocr_to_solr

index_hocr_to_solr("collection1", "object1")
```

### Manage metadata.yml

#### Validation

Validates metadata.yml using rules defined in the [Digital Object Discovery Storage Specification](https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md).

```
from iiiflow import validate_metadata

validate_metadata("collection1", "object1")
```

#### Updating metadata

It is much faster to directly update metadata in `manifest.json` from `metadata.yml` rather then re-building the whole manifest from scratch. This also updates the manifest `behavior` field.

```
from iiiflow import update_metadata

update_metadata("collection1", "object1")
```

### Create manifest

```
from iiiflow import create_manifest

create_manifest("collection1", "object1")
```

### Iterate over collections and objects

```
import os
from iiiflow import collections, create_manifest

for collection in collections:
	print (collection.id)
	if collection.id == "ua807":
		for object_id in collection.objects:
			print (object_id)
			object_path = os.path.join(collection.path, object_id)
			print (os.path.isdir(object_path))
			create_manifest(collection.id, object_id)
```

### Rebuild manifests

There is also a built-in command to rebuild manifests

#### Default: Regenerate manifests older than 25 hours
```
rebuild-manifests
```

#### Regenerate if older than 12 hours
```
rebuild-manifests --hours 12
```

#### Only for one collection, with a 6-hour threshold
```
rebuild-manifests --collection-id apap101 --hours 6
```

### Tests

This runs the tests with all dependancies

`docker-compose run test`

### Pushing a release

After running tests.
```
python -m build
twine upload dist/*
```
