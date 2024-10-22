# Hyrax export process

1. Inital export from Hyrax
2. Export thumbnails
3. Export derivatives
4. Extract images
5. Extract text
6. Create manifest

Export scripts are in \scripts

## 1. Inital file export

There is [rake task](https://github.com/UAlbanyArchives/hyrax-UAlbany/blob/main/lib/tasks/export_files.rake) in our Hyrax instance to initally export objects from Hyrax. This includes `metadata.yml` and content files in subdirectories by file extension:
```
SPE_DAO/
	└── u531/
		└── 9019sk86q/
			└── v1/
				├── csv/
				├── pdf/
				├── xslx/
				└── metadata.yml
```

You can export individual objects by ID:
```
rake export:export_files ID=8336hn42n
```

Or export all objects in a collection with a collection ID:
```
rake export:export_files COLLECTION=ua531
```

Both of these options will not export files where the object folder already exists in `SPE_DAO`, such as if this is present:
```
\\Lincoln\Library\SPE_DAO\ua531\8910kc626
```

You can override this with `FORCE=true`. This will overwrite the `metadata.yml` and content files for object(s):
```
rake export:export_files ID=8336hn42n FORCE=true
rake export:export_files COLLECTION=ua531 FORCE=true
```

## 2. Export thumbnails

There's not a good way to get the thumbnails out of Hyrax via the DB. Yet, we can get them over http based on an identifier in `metadata.yml`:
```
python getThumbnails.py ua200
```
Running this with a collection ID will re-download and overwrite all thumbnails for each exported object in a collection.

Running it without an arg will download thumbnails for every object in `SPE_DAO`
```
python getThumbnails.py
```

## 3. Export derivatives

Hyrax also creates useful derivative files, such as webm for videos, pdfs for office docs, etc.

```
python getDerivatives.py ua200
```

This will also run for everything in `SPE_DAO` if you don't give it a collection ID.

This also updates `metadata.yml` to list the original file and format.

## 4. Extract images from PDFs

`extractImages.py` has some Linux dependancies so we should run it in docker.

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python extractImages.py
python extractImages.py apap214
```

## 5. Extract Text

### Option 1: Extract text from PDFs (fastest)

```
python extractText.py apap015
```

This will also run for everything in `SPE_DAO` if you don't give it a collection ID.

### Option 2: Recognize text with tesseract

This creates better structured text, but will take much longer.

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python tesseract.py apap042
```

### Option 3: Generate Transcript with Whisper

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python create_transcription.py apap138
```

## 6. Create manifest

IIIF Presentation API v3 manifests

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python manifest.py apa042
```

This will also run for everything in `SPE_DAO` if you don't give it a collection ID.

This still needs work.

## Useful links

* [HTRflow](https://huggingface.co/blog/Gabriel/htrflow)
* [Whisper normalization](https://github.com/IUBLibTech/fantastic_futures_2024_whisper/blob/main/normalize_content_media.py)

