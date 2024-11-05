# Digital Object Discovery Storage Specification (0.1)
This is a display version of the specification, which is managed and versioned with markdown in a [Github repository](https://github.com/UAlbanyArchives/arclight_intergration_project).

## Contributors
* Gregory Wiedeman
* Katherine Mules
* Mark Wolfe
* Meghan Slaff

## 1. Introduction

### 1.1 Purpose

The M.E. Grenander Department of Special Collections, Archives, & Preservation at the University at Albany, SUNY Libraries has found that Digital Asset Management Systems (DAMS) or digital repositories do not meet the needs of an archival repository [[Wiedeman, 2023](https://journal.code4lib.org/articles/16963)]. Additionally, UAlbany Libraries have struggled to adapt and maintain an open source digital repository to better meet its needs.

Instead of a traditional digital repository, UAlbany is migrating its digital objects described by archival description to filesystem storage. This "Digital Object Discovery Storage," or "SPE_DAO" for "Special Collections Digital Archival Objects," will be both human-readable and editable via a mounted network filesystem, but also well-structured to enable reliable automated use. This specification governs this storage so we can create software to store and access the digital object stored in SPE_DAO, and also so that this storage can be audited or validated against.

The digital objects stored in SPE_DAO will be made available though a International Image Interoperability Framework (IIIF) image server and indexed in ArcLight. This work is part of the [ArcLight Integration Project](https://archives.albany.edu/web/arclight_integration/), made possible in part by the Institute of Museum and Library Services award [LG-256722-OLS-24](https://www.imls.gov/grants/awarded/lg-256722-ols-24). 

### 1.2 Status of this Document 

Working draft

### 1.3 License

[CC0 - “No Rights Reserved”](https://creativecommons.org/share-your-work/public-domain/cc0/) !["CC0 Public Domain logo"](https://i.creativecommons.org/p/zero/1.0/88x31.png)

### 1.4 Requirements
The key words “MAY”, “MUST”, “MUST NOT” ,“RECOMMENDED”, “REQUIRED”, “OPTIONAL”, “SHOULD”, and “SHOULD NOT” in this document are to be interpreted as described in BCP 14 [RFC2119](https://tools.ietf.org/html/rfc2119) [RFC8174](https://tools.ietf.org/html/rfc8174) when, and only when, they appear in all capitals, as shown here.

### 1.5 Terminology
The following terms have precise definitions as used in this document:

**SPE_DAO:** This is the storage location defined in this specification. It is a shortened name for Digital Object Discovery Storage based on abbrevations for Special Collections Digital Archival Objects which is a term from [EAD](https://www.loc.gov/ead/tglib1998/tlin044.html). 

**archival component:** A unit of archival description, governed by [Describing Archives: A Content Standard](https://saa-ts-dacs.github.io/dacs/06_part_I/02_chapter_01.html) (TS-DACS). In common parlance, this could be an archival collection, series, subseries, file, or item. ArchivesSpace is the system of record for archival components. Each archival component may be described as a Collection or Archival Object in ArchivesSpace. Each archival component is a node in a hierarchical graph structure and may describe any meaningful aggregate of physical or digital objects. An archival component may have no linked digital objects or many linked digital objects.

**archival collection:** The top level "collection" containing many described or undescribed archival components. Each archival collection has a Collection record in ArchivesSpace and a [collection identifier](#2-collection-identifiers) as described below.

**digital object:** A meaningful unit of digital content with accompanying metadata. Digital objects are discrete entities that differ meaningfully in content from another digital object, yet the same digital object can substantially change and have different versions over time and may also be represented in different formats. Digital objects are a useful abstraction and can contain a single digital file, a book, or other object containing multiple files in a simple structure, or the contents of an entire hard drive with a complex hierarchical structure. A single digital object MUST link to a single archival component.

**work:** An intellecual entity in a _common form_ that may or may not have accompanying metadata. Works are typically expressed either as a single file, or as a set of common files such as images. While works can have representations in multiple formats, a work is typically be expressed using a single format, like a set of JPGs, and typically cannot be a set of multiple different formats. A work is essentially a [PCDM Object](https://pcdm.org/2016/04/18/models#Object).

**representation:** an instance of a work. Thus, a work can be represented as a PDF file, a set of JPG files, a TXT file. In the event that there are multiple, different file types for an archival object, a distinction between representation and version needs to be made. This distinction should be made based on the content of the object. If significant content changes exist between the two files, they should be considered two digital objects, linked to the same archival object. But if the only distinction is file type, and the content remains the same, both files should be added to the same digital object, which is linked to one archival object. Transcripts of a video and the video file do not constitute a difference in content and should be linked to the same digital object, as should a video and its thumbnail. If, for instance, a record includes a video package (i.e. branding elements, the video file, the transcript), all elements should be linked to the same digital object as all elements combined create a singular representation.

**version:** The unique individual object that is uploaded to Hyrax is the version. There can be multiple versions of the same object, but there are enough discrepencies in the content to justify creating another digital object with its own unique identifier, instead of uploading multiple objects to the same ID. File format changes do not qualify as a large enough discrepency. For the preexisting digital objects in our current system, there will be at least one version folder with accompanying metadata. The new system will create another version utilizing the metadata and the new IIIF formats. Both will be saved for historical data and review.

**format:** There are various forms that files can appear in. For example, a document can appear as a ".docx" file and/or a ".pdf" file or an image could appear as a ".jpg" file and/or a ".png" file. There is no difference in the content of the object, other than data lossiness between formats (such as when a spreadsheet is converted to a PDF or image compression is applied). 

**thumbnail:** The thumbnail image previews the IIIF file of the digital object. It is a representative image of the file, otherwise referred to as a "smaller version" of the object, but neither of these descriptions should be confused with the definitions of "format" or "version" seen above. Though thumbnails will be included in the metadata files for the migration, they do not serve the same purpose as the format or version files. 

**NOID:** Stands for "Nice Opaque IDentifier" [NOID](https://metacpan.org/dist/Noid/view/noid) creates unique alphanumeric strings for identification.

## 2. Collection identifiers

Each archival collection managed by UAlbany Libraries MUST have a collection identifier that is unique within Special Collections & Archives.

Each collection identifier must start with a two to four character prefix from this set: "apap", "ger", "mss", or "ua".
* Prefixes MUST be lower case.
* This prefix denoting the relevant collecting area. Collections within the Modern Political Archive, as well as the National Death Penalty Archive use the legacy "apap" code.

Each collection identifier MUST have a three digit sequential number directly following the prefix. University Archives collections starting with the `ua` prefix MAY also have a period (`.`) and a second three digit sequential number.

### 2.1 Valid Collection identifier Examples
* apap127
* ger017
* mss005
* ua500
* ua600.001
* ua902.010

### 2.2 Invalid Collection identifier Examples
* APAP808
* ger-117
* Ger044
* apap100.004
* mss_105
* apap 100
* apap50

## 3. Digital object identifiers

All digital object identifiers must be NOIDs, and must be valid directory names in both Unix-based and Windows operating systems. Thus, they cannot contain characters such as `< > : " / \ | ? *` and are RECOMMENDED to be 36 characters or less.

Prior to SPE_DAO, Hyrax generated NOID identifiers with [noid-rails](https://github.com/samvera/noid-rails) which will be maintained during the migtation. Any new objects uploaded after the transition will be given new NOIDs generated using the same minter state.

As an additional measure against potential collisions, legacy Hyrax-generated NOID will continute to have 9 digits, where post-migration NOIDs will have 10 digits.

## 4. Overview of SPE_DAO

SPE_DAO root MUST only contain collection folders named for valid Collection identifiers. Each collection folder must have an associated resource record in ArchivesSpace.

Each Collection folder may contain any number of Digital Object folders named using each object's NOID identifier.

### 4.2 Digital object generic structure example

	└── SPE_DAO/ (root)
		├── collection folder/
		│   ├── NOID/
		│   │	├── representation folder/
		│   │	├── representation folder/
		│   │	├── representation folder/
		│   │	├── representation folder/
		│   │	├── content.txt
		│   │	├── manifest.json
		│   │	├── metadata.yml
		│   │	└── thumbnail.jpg
		│   └── NOID/
		│		├── representation folder/
		│		├── representation folder/
		│		├── representation folder/
		│		├── representation folder/
		│		├── content.txt
		│		├── manifest.json
		│		├── metadata.yml
		│		└── thumbnail.jpg
		└── collection folder/
			└── NOID/
				├── representation folder/
				├── representation folder/
				├── representation folder/
				├── representation folder/
				├── content.txt
				├── manifest.json
				├── metadata.yml
				└── thumbnail.jpg

### 4.2 Example Collection and Digital Object folders

	└── SPE_DAO/ (root)
		├── apap101/
		│   ├── nc580m649/
		│   ├── fx719m44h/
		│   └── tb09j5643/
		├── ger006/
		│   ├── 7urr3r12a3/
		│   ├── ewuel2uscx/
		│   └── ptkk9csngq/
		└── ua902.012/
			└── 4j03cz64w/


## 5. Representation folders

Digital objects often contain many different representations of the same content. This could be different file or image versions, or texual representations of files in HOCR, VTT, CSV, or plain text formats.

Representations folders typically have object-level formats with a single file per digital object, or be split into [canvas-level](https://iiif.io/api/presentation/3.0/#53-canvas) represenations, such as a set of files per page.

*Object-level representation folders*
* pdf
* csv
* office documents
	* docx/doc
	* xlsx/xls
	* pptx/ppt
* A/V formats
	* mp4
	* webm
	* mp3
	* ogg

*Canvas-level representation folders*
* jpg
* tiff
* png
* txt

### 5.1 Representation folder examples

```
	└── SPE_DAO/ (root)
		├── apap101/
		│   ├── nc580m649/
		│   │	├── jpg/
		│   │	├── tiff/
		│   │	├── ocr/
		│   │	├── pdf/
		│   │	├── txt/
		│   │	├── content.txt
		│   │	├── manifest.json
		│   │	├── metadata.yml
		│   │	└── thumbnail.jpg
		│   ├── fx719m44h/
		│   │	├── jpg/
		│   │	├── ocr/
		│   │	├── pdf/
		│   │	├── ppt/
		│   │	├── tiff/
		│   │	├── txt/
		│   │	├── content.txt
		│   │	├── manifest.json
		│   │	├── metadata.yml
		│   │	└── thumbnail.jpg
		│   └── tb09j5643/
		│		├── mp3/
		│		├── ogg/
		│		├── txt/
		│		├── vtt/
		│		├── manifest.json
		│		├── metadata.yml
		│		└── thumbnail.jpg
		└── ua500/
			└── 4j03cz64w/
				├── txt/
				├── vtt/
				├── webm/
				├── content.txt
				├── manifest.json
				├── metadata.yml
				└── thumbnail.jpg
```

### 5.2 Serving priorities

* For objects with a `resource_type` of `Audio`, the `manifest.json` will serve OGG files.
* For objects with a `resource_type` of `Video`, the `manifest.json` will serve WEBM files.
* For objects with all other `resource_type` values, the `manifest.json` will prioritize image formats in this order:
	* tiff (pyramidal)
	* jpg

### 5.3 Object-level Alternative Renderings

These additional formats will be included as [alternative renderings](https://iiif.io/api/cookbook/recipe/0046-rendering/) of the manifest, representing the entire digital object:
* pdf
* office documents
	* docx/doc
	* xlsx/xls
	* pptx/ppt
* mp3
* Video formats
	* mp4
	* mov
	* avi
* vtt (captions)
* `content.txt` (text transcriptions)

### 5.4 Canvas-level Alternative Renderings

For multi-page objects, it is also RECOMMENDED to include canvas level alternative renderings for each page.
* ocr (HOCR XML files)
* txt

#### 5.4.1 Associations between Canvas-level Alternative Renderings

Associated HOCR and TXT file MUST have the same case-sensative filename as the files they represent.

#### 5.4.2 Examples of Associations between Canvas-level Alternative Renderings

```
	└── apap101/
		└── 1n79hq253/
			├── jpg/
			│	├── page1.jpg
			│	├── page2.jpg
			│	└── page3.jpg
			├── pdf/
			│	└── document.pdf
			├── ocr/
			│	├── page1.hocr
			│	├── page2.hocr
			│	└── page3.hocr
			├── tiff/
			│	├── page1.tiff
			│	├── page2.tiff
			│	└── page3.tiff
			├── txt/
			│	├── page1.txt
			│	├── page2.txt
			│	└── page3.txt
			├── manifest.json
			├── metadata.yml
			└── thumbnail.jpg
```

## 6. Metadata files

The most recent version of a digital objects MUST contain the following files directly within the object directory:
* `metadata.yml`
* `manifest.json`

*metadata.yml* is a YAML file containing digital object level metadata.

*manifest.json* is valid [IIIF v3 Presentation API manifest](https://iiif.io/api/presentation/3.0/).

### 6.1 Text encoding and line endings

All text files within a digital object, such as `metadata.yml`, `content.txt`, `content.hocr`, `content.vtt`, and `manifest.json`, MUST use UTF-8 encoding and MUST use a line feed character (LF or \n) for line endings.

### 6.2 `metadata.yml`

* `metadata.yml` must be a valid [YAML file](https://yaml.org/spec/1.2.2/).

Fields contained in `metadata.yml` are defined in [5. `metadata.yml` fields](#5.)

### 6.3 `manifest.json`

* `manifest.json` must be a valid JSON file according to [[rfc7159]](https://tools.ietf.org/html/rfc7159).
* `manifest.json` must be a valid IIIF manifest according to the [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)

### 6.4 `content.txt`

Content files contain text that can be indexed into Solr for discovery. It is RECOMMENDED to use structured formats such as HOCR or VTT to support IIIF annotations and captioning, but an unstructured `content.txt` file is also permitted for legacy digital objects.

## 7. Full-Text Indexing Prioritization

All digital objects will be indexed into ArcLight's Solr core for full-text discovery. This is the order of prioritization:

1. The `context.txt` file if it is present within a digital object folder.
2. A single file within a `txt` representation folder. This will be skipped if there is multiple per-canvas files.
3. All the text from HOCR files within a `ocr` representation folder.

## 8. `metadata.yml` fields

### 8.1 Controlled `metadata.yml` fields

These fields have strict requirements as they support for automated processes.

**archivesspace_record**: (REQUIRED) The identifier number for the archival record that the digital object is linked to.

**collection_number**: (REQUIRED) Collection identifier number of digital object. This value MUST match the collection folder for the digital object.

**coverage**: (REQUIRED) Determines if the digital object is the only file that represents the archival object (the whole) or if it is one component of multiple (a part) that make up the archival object. This value is used in ArcLight to determine if the digital object is fully representative of the archival component.

**date_published**: (REQUIRED) The date the digital object was first made publicly available. Previously, this field was named date_uploaded. This field MUST be an ISO 8601 compliant date with the "T" separator, such as "2018-12-21T15:30:08+00:00".

**identifier**: (REQUIRED) The NOID for the object. This value MUST match the digital object folder name.

**license**: (REQUIRED) Licensing and distribution information governing access to the digital object. This field MUST be the canonical URL for a Creative Commons license or "Unknown". If "Unknown" is used, a valid rights_statement field is REQUIRED. Examples:
* https://creativecommons.org/licenses/by-nc-nd/4.0/
* https://creativecommons.org/publicdomain/zero/1.0/
* Unknown

**preservation_package**: (REQUIRED) Identifier for the preservation package that includes the presevation files used for the digital object. This field was previously named "accession".

**resource_type**: (REQUIRED) The form of the digital object. Value MUST be one of the following set:
* Audio
* Bound Volume
* Dataset
* Document
* Image
* Map
* Mixed Materials (Avoid)
* Pamphlet
* Periodical
* Slides
* Video
* Other (Avoid)
 
**visibility**: (REQUIRED) Denotes whether a digital object will be read and indexed into ArcLight. MUST be one of the following values:
* open
* closed

**behavior**: (OPTIONAL) Sets the [IIIF behavior](https://iiif.io/api/cookbook/recipe/0011-book-3-behavior/) at the object level. Options:
* unordered
* individuals
* continuous
* paged

**original_file**: (OPTIONAL) This field is REQUIRED for born-digital files. Name of original file that was created and used.

**original_file_legacy**: (OPTIONAL) Name of original file for a born-digital file. In legacy use, this field denotes the file that was uploaded to Hyrax for both digitized and born-digital objects. For example, this was often the name of a PDF created after the digitization of a physical object and may not be meaningful. This field is deprecated and will be replaced by original_file and original_format post-Hyrax.

**original_format**: (OPTIONAL) Format (Doc, Png, Jpg, Ppt etc.) of the file before it was uploaded to Hyrax

**rights_statement**: (OPTIONAL) This field is REQUIRED when the value for license is "Unknown." Known copyright status of the digital object. If used this field MUST be the canonical URL for a [RightsStatements.org](https://rightsstatements.org). Examples:
* https://rightsstatements.org/page/InC-EDU/1.0/
  
### 8.2 Uncontrolled `metadata.yml` fields

`metadata.yml` MAY have any number of metadata fields that are not used for automated purposes, but will be included in the `manifest.json` and later indexed into ArcLight. None of these fields are required and many are present due to legacy systems and practices.

**title**: The file name of the digital object.

**date_created**: (If we are going by Hyrax terms) The date of creation determined and added to the archival object by the archivist, not necessarily the date the digital object was created.

**collecting_area**: Archival collecting area of digital object. This is a derivative value of data contained in ArchivesSpace.

**collection**: Collection name of digital object.

**creator**: Name of user that uploaded digital object to Hyrax or SPE_DAO system.

**contributor**: Name of user that aided in the description of the digital object.

**description**: IF the digital object is an image, the description provides additional searchable content as well as a depiction for accessibility purposes (i.e. utilizes a screen reader).  

**processing_activity**: Details on how digital objects were processed or a link to the location of processing documentation.

**representative_id**: A NOID for the representative file set when the object was managed in Hyrax. This field was useful during the post-Hyrax migration.

**file sets**: A key-value list of files as they were stored in Hyrax. Each key is a NOID minted by Hyrax and each value is the filename. This field was useful during the post-Hyrax migration.

## 9. Examples

### 9.1 Digital object example

```
	├── apap138/
	│   ├── 6w924x89w/
	│   │	├── mp3/
	│   │	├── ogg/
	│   │	├── vtt/
	│   │	├── content.txt
	│   │	├── manifest.json
	│   │	└── metadata.yml
	│   └── 84f1tH58w/
	│		├── webm/
	│		├── vtt/
	│		├── content.txt
	│		├── manifest.json
	│		└── metadata.yml
	├── ua200/
	│	└── 3n208fj07j/
	│		├── jpg/
	│		├── ocr/
	│		├── pdf/
	│		├── pptx/
	│		├── tiff/
	│		├── content.txt
	│		├── manifest.json
	│		├── metadata.yml
	│		└── thumbnail.jpg
	└── ua807/
		└── 5t34t462n/
			├── jpg/
			├── pdf/
			├── tiff/
			├── content.txt
			├── manifest.json
			├── metadata.yml
			└── thumbnail.jpg
```



## References

**[RFC2119]**
Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", IETF, March 1997.
DOI 10.17487/RFC2119
URL: [https://tools.ietf.org/html/rfc2119](https://tools.ietf.org/html/rfc2119)

**[RFC8174]**
Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", IETF, May 2017.
DOI 10.17487/RFC8174
URL: [https://tools.ietf.org/html/rfc8174](https://tools.ietf.org/html/rfc8174)

**[RFC7159]**
Bray, T., "JavaScript Object Notation (JSON)", RFC 7159, March 2014.
URL: [https://tools.ietf.org/html/rfc7159](https://tools.ietf.org/html/rfc7159

**[IIIF-Presentation-3.0]**
International Image Interoperability Framework (IIIF), "IIIF Presentation API 3.0", version 3.0, January 2023
URL: [https://iiif.io/api/presentation/3.0/](https://iiif.io/api/presentation/3.0/)

**[Wiedeman, 2023]** Wiedeman, Gregory. "Designing Digital Discovery and Access Systems for Archival Description," Issue 55, 2023-1-20. Available at: [https://journal.code4lib.org/articles/16963](https://journal.code4lib.org/articles/16963).

