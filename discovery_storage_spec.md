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

**archival component:** A unit of archival description, governed by [Describing Archives: A Content Standard](https://saa-ts-dacs.github.io/dacs/06_part_I/02_chapter_01.html) (TS-DACS). In common parlance, this could be an archival collection, series, subseries, file, or item. ArchivesSpace is the system of record for archival components. Each archival component may be described as a Resource or Archival Object in ArchivesSpace. Each archival component is a node in a hierarchical graph structure and may describe any meaningful aggregate of physical or digital objects. An archival component may have no linked digital objects or many linked digital objects.

**archival collection:** The top level "collection" containing many described or undescribed archival components. An archival collection is also an archival component and may have linked digital objects. Each archival collection MUST have a resource record in ArchivesSpace and a [collection identifier](#2-collection-identifiers) as described below.

**digital object:** A meaningful package or aggregate of digital content with accompanying metadata. Digital objects are a useful abstraction and can contain one or more works with or without a significant and meaningful structure or relationshipas between works. This could be a single JPG, a book or other object containing multiple files in a simple structure, or the contents of an entire hard drive with a complex hierarchical structure and works in many types of file formats. A single digital object MUST link to a single archival component.

**work:** An intellecual entity in a _common form_. Works are discrete entities that differ meaningfully in content from another work, yet the same work can substantially change and have different versions over time and may also be represented in different formats. Works are typically expressed either as a single file, or as a set of common files such as images. While works can have representations in multiple formats, a work is typically be expressed using a single format, like a set of JPGs, and typically cannot be a set of multiple different formats. A work is semantically the same as a [PCDM Object](https://pcdm.org/2016/04/18/models#Object).

**representation:** an instance of a work. Thus, a work can be represented in different formats such as a PDF file, a set of JPG files, a TXT file, etc. In the event that there are multiple, different file types for an archival object, a distinction between representation and version needs to be made. This distinction should be made based on the content of the object. If significant content changes exist between the two files, they should be considered two separate works. If the only distinction is file type, and the content remains the same, both files should be considered to be different representations of the same work. A common exception to this is an image set, which is a single work of images that each have different content. Derivative files such as thumbnails or transcripts of a video do not constitute a difference in content and should be considered derivative representations of the same work. If, for instance, a digtial object includes a video with dederivative files (i.e. a thumbnail, a clip, the video file, the transcript), all elements should be considered a single work with multiple representations. Each [PCDM Use Extension Entities](https://pcdm.org/2016/04/18/models#Object) is an example of a representation and is semantically the same as a representation.

**format:** The file format of the representation. For example, a document can appear as a ".docx" file and/or a ".pdf" file or an image could appear as a ".jpg" file and/or a ".png" file. There is no difference in the content of the object, other than data lossiness between formats (such as when a spreadsheet is converted to a PDF or image compression is applied). 

**thumbnail:** A representation image of the digital object. This is typically a smaller version of an image, the first page or a book or multi-page work, an icon, or a frame of a video.

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

All digital object identifiers MUST be the same, or a derivative of, the associated archival component's ref_id.

It is RECOMMENDED that since digial object and archival components will ideally have a one-to-one relationship, that a digital object identifiers is the exactly the same as the associated archival component's ref_id. However, to support legacy cases where digital objects only represent part of an archival component, digital object identifiers MAY also be the archival component's ref_id followed by an underscore (_) and a sequential identifier. For example:

	* 9dfb7fea77045eddb9fc90aca79ad3a7_1
	* 9dfb7fea77045eddb9fc90aca79ad3a7_2
	* 9dfb7fea77045eddb9fc90aca79ad3a7_3
	* 9dfb7fea77045eddb9fc90aca79ad3a7_4
	* 9dfb7fea77045eddb9fc90aca79ad3a7_5
	* 9dfb7fea77045eddb9fc90aca79ad3a7_6
	* 9dfb7fea77045eddb9fc90aca79ad3a7_7
	* 9dfb7fea77045eddb9fc90aca79ad3a7_8
	* 9dfb7fea77045eddb9fc90aca79ad3a7_9
	* 9dfb7fea77045eddb9fc90aca79ad3a7_10
	* 9dfb7fea77045eddb9fc90aca79ad3a7_11
	...

All digital object identifiers MUST be valid directory names in both Unix-based and Windows operating systems. Thus, they cannot contain characters such as `< > : " / \ | ? *` and are RECOMMENDED to be 36 characters or less.

Prior to SPE_DAO, digital objects used NOID identifiers from [noid-rails](https://github.com/samvera/noid-rails). These identifiers will be added to each object's `metadata.yml` as the `legacy_id` field. Any new objects uploaded after the transition will not have the `legacy_id` field.

## 4. Overview of SPE_DAO

SPE_DAO root MUST only contain collection folders named for valid Collection identifiers. Each collection folder must have an associated resource record in ArchivesSpace.

Each Collection folder may contain any number of Digital Object folders named using each object's NOID identifier.

### 4.2 Digital object generic structure example

	└── SPE_DAO/ (root)
		├── collection folder/
		│	├── ref_id/
		│	│	├── representation folder/
		│	│	├── representation folder/
		│	│	├── representation folder/
		│	│	├── representation folder/
		│	│	├── content.txt
		│	│	├── manifest.json
		│	│	├── metadata.yml
		│	│	└── thumbnail.jpg
		│	└── ref_id/
		│		├── representation folder/
		│		├── representation folder/
		│		├── representation folder/
		│		├── representation folder/
		│		├── content.txt
		│		├── manifest.json
		│		├── metadata.yml
		│		└── thumbnail.jpg
		└── collection folder/
			└── ref_id/
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
		│	├── 43e37dba59edb69e348b7a200350bdbc/
		│	├── 5181a71b9974988792db7764f65979cd/
		│	└── 0b08f3f857eec7d979f02d5663ea4e52/
		├── ger006/
		│	├── f2f49443c9cc14eec48402ae4f8c3026/
		│	├── 1837d1debf0594d7b478d11c0aea71a6/
		│	└── 8c63e8002860e0ebfc90af60e731027e/
		└── ua902.012/
			└── 96369731598e43ee001edac1b10487a2/


## 5. Representation folders

Digital objects often contain many different representations of the same content. This could be different file or image versions, or texual representations of files in HOCR, VTT, CSV, or plain text formats.

Each representation folder MUST be the file extension of the format it contains in all lower case EXCEPT for ALTO XML OCR data when the representation folder is `alto` and the extension is `.xml`. Three digit file extensions are preferred, with a common exception being `hocr`.

Pyramidal tiff files MUST use the `.ptif` file extension and thus MUST use the `ptif` representation folder.

Each representation folder SHOULD contain a complete representation, but some formats may be lossy. For example, the `txt` representation of a document will not contain the entire content for the object since it does not contain the visual representation, but it SHOULD contain the entire plain text representation of the object, instead of only some pages of the document.

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
* ptif
* png
* txt
* hocr
* alto
* vtt

### 5.1 Representation folder examples

```
	└── SPE_DAO/ (root)
		├── apap101/
		│	├── a3417ed6319fd6be114322a0b8d660ec/
		│	│	├── jpg/
		│	│	├── ptif/
		│	│	├── hocr/
		│	│	├── pdf/
		│	│	├── txt/
		│	│	├── content.txt
		│	│	├── manifest.json
		│	│	├── metadata.yml
		│	│	└── thumbnail.jpg
		│	├── 36b24b77b95343ca4f7c9ca42b646f05/
		│	│	├── jpg/
		│	│	├── hocr/
		│	│	├── pdf/
		│	│	├── ppt/
		│	│	├── ptif/
		│	│	├── txt/
		│	│	├── content.txt
		│	│	├── manifest.json
		│	│	├── metadata.yml
		│	│	└── thumbnail.jpg
		│	└── 62b4c399a3d9f7a70944349c8e7dd7d6/
		│		├── mp3/
		│		├── ogg/
		│		├── txt/
		│		├── vtt/
		│		├── content.txt
		│		├── manifest.json
		│		├── metadata.yml
		│		└── thumbnail.jpg
		└── ua500/
			└── 9989f1bbdc2e53e7f30f44aa2e108e43/
				├── txt/
				├── vtt/
				├── webm/
				├── content.txt
				├── manifest.json
				├── metadata.yml
				└── thumbnail.jpg
```

### 5.2 Serving priorities

* For objects with a `resource_type` of `Audio`, the `manifest.json` will serve OGG files with MP3 fallback.
* For objects with a `resource_type` of `Video`, the `manifest.json` will serve WEBM files.
* For objects with all other `resource_type` values, the `manifest.json` will prioritize image formats in this order:
	* ptif
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
* `content.txt` (text transcription)

More formats may be added later.

### 5.4 Canvas-level Alternative Renderings

For multi-page objects, it is also RECOMMENDED to include canvas level alternative renderings for each page. HOCR and VTT are preferred.
* hocr
* alto
* vtt
* txt

#### 5.4.1 Associations between Canvas-level Alternative Renderings

Associated HOCR and TXT file MUST have the same case-sensative filename as the files they represent.

#### 5.4.2 Examples of Associations between Canvas-level Alternative Renderings

```
	└── apap101/
		└── 1f399e4fea1fc44f9e94668945186318/
			├── jpg/
			│	├── page1.jpg
			│	├── page2.jpg
			│	└── page3.jpg
			├── pdf/
			│	└── document.pdf
			├── hocr/
			│	├── page1.hocr
			│	├── page2.hocr
			│	└── page3.hocr
			├── ptif/
			│	├── page1.ptif
			│	├── page2.ptif
			│	└── page3.ptif
			├── txt/
			│	├── page1.txt
			│	├── page2.txt
			│	└── page3.txt
			├── manifest.json
			├── metadata.yml
			└── thumbnail.jpg
```

## 6. Metadata files

Digital objects MUST contain the following files directly within the object directory:
* `metadata.yml`
* `manifest.json`

*metadata.yml* is a YAML file containing digital object level metadata.

*manifest.json* is valid [IIIF v3 Presentation API manifest](https://iiif.io/api/presentation/3.0/).

### 6.1 Text encoding and line endings

All text files within a digital object, such as `metadata.yml`, `content.txt`, `*.hocr`, `*.vtt`, and `manifest.json`, MUST use UTF-8 encoding and MUST use a line feed character (LF or \n) for line endings.

### 6.2 `metadata.yml`

* `metadata.yml` must be a valid [YAML file](https://yaml.org/spec/1.2.2/).

Fields contained in `metadata.yml` are defined in [5. `metadata.yml` fields](#5.)

### 6.3 `manifest.json`

* `manifest.json` must be a valid JSON file according to [[rfc7159]](https://tools.ietf.org/html/rfc7159).
* `manifest.json` must be a valid IIIF manifest according to the [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)

### 6.4 `content.txt`

Content files contain plain text that represents the digital object and should be indexed into Solr for discovery. If a digital object has any representative text, then it MUST contain a `content.txt` file. The object SHOULD also have canvas-level text in representation folders such as `txt` for unstructured per-canvas text, or `hocr` for HOCR or `vtt` for VTT captions to support text highlighing and captioning.

## 7. Full-Text Indexing Prioritization

All digital objects will be indexed into ArcLight's Solr core for full-text discovery. This is the order of prioritization:

1. The `context.txt` file if it is present within a digital object folder.
2. A single file within a `txt` representation folder. This will be skipped if there is multiple per-canvas files.
3. All the text from HOCR files within a `hocr` representation folder.

## 8. `metadata.yml` fields

### 8.1 Controlled `metadata.yml` fields

These fields have strict requirements as they support for automated processes.

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

**preservation_package**: (REQUIRED) Identifier for the preservation package that includes the presevation files used for the digital object. This field was previously named "accession".

**date_published**: (REQUIRED) The date the digital object was first made publicly available. Previously, this field was named date_uploaded. This field MUST be an ISO 8601 compliant date with the "T" separator, such as "2018-12-21T15:30:08+00:00".

**license**: (REQUIRED) Licensing and distribution information governing access to the digital object. This field MUST be the canonical URL for a Creative Commons license or "Unknown". If "Unknown" is used, a valid rights_statement field is REQUIRED. Examples:
* https://creativecommons.org/licenses/by-nc-sa/4.0/
* https://creativecommons.org/licenses/by-nc-nd/4.0/
* https://creativecommons.org/licenses/by/4.0/
* https://creativecommons.org/publicdomain/zero/1.0/
* Unknown

**rights_statement**: (OPTIONAL) This field is REQUIRED when the value for license is "Unknown." Known copyright status of the digital object. If used this field MUST be the canonical URL for a [RightsStatements.org](https://rightsstatements.org). Examples:
* https://rightsstatements.org/page/InC-EDU/1.0/

**behavior**: (OPTIONAL) Sets the [IIIF behavior](https://iiif.io/api/cookbook/recipe/0011-book-3-behavior/) at the object level. If this is not present, it will default to `individuals`. Options:
* unordered
* individuals
* continuous
* paged

**visibility**: (OPTIONAL) Denotes whether a digital object will be read and indexed into ArcLight. If not present the value will be treated as `open`. MUST be one of the following values:
* open
* closed

**original_file**: (OPTIONAL) This field is REQUIRED for born-digital files. Name of original file that was created and used.

**original_file_legacy**: (OPTIONAL) Name of original file for a born-digital file. In legacy use, this field denotes the file that was uploaded to Hyrax for both digitized and born-digital objects. For example, this was often the name of a PDF created after the digitization of a physical object and may not be meaningful. This field is deprecated and will be replaced by original_file and original_format post-Hyrax.

**original_format**: (OPTIONAL) Format (Doc, Png, Jpg, Ppt etc.) of the file before it was uploaded to Hyrax

**legacy_id**: (OPTIONAL) The legacy NOID ID for the object minted by Hyrax.

**coverage**: (OPTIONAL) Determines if the digital object is the only file that represents the archival object (the whole) or if it is one component of multiple (a part) that make up the archival object. This value is used in ArcLight to determine if the digital object is fully representative of the archival component. If the coverage field is not present, the coverage value will be treated as `whole`. 
  
### 8.2 Uncontrolled `metadata.yml` fields

`metadata.yml` MAY have any number of metadata fields that are not used for automated purposes, but will be included in the `manifest.json` and later indexed into ArcLight. None of these fields are required and many are present due to legacy systems and practices.

**title**: The file name of the digital object.

**date_display**: The date of creation determined and added to the archival object by the archivist, not necessarily the date the digital object was created.

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
	│	├── 6w924x89w/
	│	│	├── mp3/
	│	│	├── ogg/
	│	│	├── vtt/
	│	│	├── txt/
	│	│	├── content.txt
	│	│	├── manifest.json
	│	│	└── metadata.yml
	│	└── 84f1tH58w/
	│		├── webm/
	│		├── vtt/
	│		├── txt/
	│		├── content.txt
	│		├── manifest.json
	│		└── metadata.yml
	├── ua200/
	│	└── 3n208fj07j/
	│		├── jpg/
	│		├── hocr/
	│		├── pdf/
	│		├── pptx/
	│		├── ptif/
	│		├── txt/
	│		├── content.txt
	│		├── manifest.json
	│		├── metadata.yml
	│		└── thumbnail.jpg
	└── ua807/
		└── 5t34t462n/
			├── jpg/
			├── pdf/
			├── ptif/
			├── txt/
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

