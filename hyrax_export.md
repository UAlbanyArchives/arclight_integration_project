# Hyrax export process

1. Inital export from Hyrax
2. Export thumbnails
3. Export derivatives
4. Extract images
5. Convert to Pyramidal Tiffs
6. Extract text
7. Create manifest

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
python extractImages.py apap214 pk02cv45j
```

Add Collection and object ids to limit to those collections/objects.

### Alternatively, look for originals in preservation packages

Needs to be run either on Windows or railsdev for access.
```
python findOriginals.py
```

## 5. Convert to Pyramidal Tiffs

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python makeTiffs.py
python makeTiffs.py ua807
python makeTiffs.py ua807 pk02cv4fj
```

Add Collection and object ids to limit to those collections/objects.

## 6. Extract Text

### Option 1: Recognize text with tesseract

This creates structured text, which we eventially need but will take awhile.

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python tesseract.py apap042
```

### Option 2: Extract text from PDFs (fastest)

```
python extractText.py apap015
```

This will either extract existing OCR text within scanned PDFs as a temporary measure, or will extract better text from born-digital PDFs.

For born-digital PDFs, if this is run after tesseract, it will not override the structured HOCR, but will produce better `content.txt` files for indexing.

### Option 3: Generate Transcript with Whisper

`docker compose up`

In new terminal:
```
docker exec -it python1 bash
python create_transcription.py apap138
```

## 7. Create manifest

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

