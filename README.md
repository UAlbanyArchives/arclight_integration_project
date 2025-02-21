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
discovery_storage_root: /path/to/digital_object_root
manifest_url_root: https://my.server.org
error_log_file: /path/to/errors.log
audio_thumbnail_file: ./fixtures/thumbnail.jpg
```

Optionally, you can pass the path to any `.yml` file as the last arg of any iiiflow function.

For audio thumbnails and test to work, set audio_thumbnail_file to either a local path or accessible url to an image file.

```
create_ptif("collection1", "object1", "path/to/config.yml")
```

### Create thumbnails

Creates a 300x300 thumbnail.jpg

```
from iiiflow import make_thumbnail

make_thumbnail("collection1", "object1")
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

### Validate metadata.yml

Validates metadata.yml using rules defined in the [Digital Object Discovery Storage Specification](https://github.com/UAlbanyArchives/arclight_integration_project/blob/main/discovery_storage_spec.md).

```
from iiiflow import validate_metadata

validate_metadata("collection1", "object1")
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

### Tests

This runs the tests with all dependancies

`docker-compose run test`
