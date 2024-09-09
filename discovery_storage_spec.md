# Digital Object Discovery Storage Specification (0.1)
This is a display version of the specification, which is managed and versioned with markdown in a [Github repository](https://github.com/UAlbanyArchives/arclight_intergration_project).

## Contributors
* Gregory Wiedeman
* Katherine Mules
* Mark Wolfe
* Meghan Slaff

## 1. Introduction

### 1.1 Purpose

The M.E. Grenander Department of Special Collections, Archives, & Preservation at the University at Albany, SUNY Libraries has found that Digital Asset Management Systems (DAMS) or digital repositories do not meet the needs of an archival repository [[Wiedeman, 2023](https://journal.code4lib.org/articles/16963)]. Additionally, UAlbany Libraries have struggled o adapt and maintain an open source digital repository to better meet its needs.

Instead of a traditional digital repository, UAlbany is migrating its digital objects described by archival description to filesystem storage. This "Digital Object Discovery Storage" or "SPE_DAO" will be both human readable and editable via a mounted network filesystem, but also well-structured to enable reliable automated use. This specification governs this storage so we can create software to store and access the digital object stored in SPE_DAO, and also so that this storage can be audited or validated against.

The digital objects stored in SPE_DAO will be made available though a International Image Interoperability Framework (IIIF) image server and indexed in ArcLight. This work is part of the [ArcLight Integration Project](https://archives.albany.edu/web/arclight_integration/), made possible in part by the Institute of Museum and Library Services award [LG-256722-OLS-24](https://www.imls.gov/grants/awarded/lg-256722-ols-24). 

### 1.2 Status of this Document 

Working draft

### 1.3 License

[CC0 - “No Rights Reserved”](https://creativecommons.org/share-your-work/public-domain/cc0/) !["CC0 Public Domain logo"](https://i.creativecommons.org/p/zero/1.0/88x31.png)

### 1.4 Requirements
The key words “MAY”, “MUST”, “MUST NOT” ,“RECOMMENDED”, “REQUIRED”, “OPTIONAL”, “SHOULD”, and “SHOULD NOT” in this document are to be interpreted as described in BCP 14 [RFC2119](https://tools.ietf.org/html/rfc2119) [RFC8174](https://tools.ietf.org/html/rfc8174) when, and only when, they appear in all capitals, as shown here.

### 1.5 Terminology
The following terms have precise definitions as used in this documnent:

**SPE_DAO:** an abbreviation for Digital Object Discovery Storage. This is the storage location defined in this specification.

**archival component:** A unit of archival description, governed by [Describing Archives: A Content Standard](https://saa-ts-dacs.github.io/dacs/06_part_I/02_chapter_01.html) (TS-DACS). In common parlance, this could be an archival collection, series, subseries, file, or item. ArchivesSpace is the system of record for archival components. Each archival component may be described as a Collection or Archival Object in ArchivesSpace. Each archival component is a node in a hierarchical graph structure and may describe any meaningful aggregate of physical or digital objects. An archival component may have no linked digital objects or many linked digital objects.

**archival collection:** The top level "collection" containing many described or undescribed archival components. Each archival collection has a Collection record in ArchivesSpace and a [collection identifier](#2-collection-identifiers) as described below.

**digital object:** A meaningful unit of digital content with accompanying metadata. Digital objects are discrete entities that differ meaningfully in content from another digital object, yet the same digital object can substantially change and have different versions over time and may also be represented in different formats. Digital objects are a useful abstraction and can contain a single digital file, a book or other object containing multiple files in a simple structure, or the contents of an entire hard drive with a complex hierarchical structure. A single digital object MUST link to a single archival component.

**version:** The unique individual object that is uploaded to Hyrax is the version. There can be multiple versions of the same object, but there are enough discrepencies in the content to justify creating another digital object with its own unique identifier, instead of uploading multiple objects to the same ID. File format changes do not qualify as a large enough discrepency. For the preexisting digital objects in our current system, there will be at least one version folder with accompanying metadata. The new system will create another version utilizing the metadata and the new IIIF formatsw. Both will be saved for historical data and review.

**format:** There are various forms that files can appear in. For example, a document can appear as a ".docx" file and/or a ".pdf" file or an image could appear as a ".jpg" file and/or a ".png" file. There is no difference in the content of the object, other than data lossiness between formats (such as when a spreadsheet is converted to a PDF or image compression is applied). 

**thumbnail:** The thumbnail image previews the IIIF file of the digital object. It is a representative image of the file, otherwise referred to as a "smaller version" of the object, but tneither of these descriptions should beconfused with the definitions of "representation" or "version" seen above. Though thumbnails will be included in the metadata files for the migration, they do nots serve the same purpose as the representation or version files. 

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

**NOID:** Stands for "Nice Opaque IDentifier" [NOID](https://metacpan.org/dist/Noid/view/noid) creates globally unique names for identification. Prior to SPE_DAO, Hyrax generated these identifiers which will be maintained during the migtation. Any new objects uploaded after the transition will be given NOIDs generated by our system using the same minter state.

## 4. Overview of SPE_DAO

The format folders will be named after the corresponding file extension suchas ".pptx" ".docx" ".pdf" etc. In the above structure several objects may exist within a single object (such as multiple different photos within a single pdf), all files will appear in the files that are most appropriate. The "original file" will be saved in the format folder that matches its type, and the Hyrax-generated PDF file will appear in the PDF folder. 

### 4.1 Digital object generic structure example

	└── SPE_DAO/ (root)
		├── collection folder/
		│   ├── NOID/
		│   │   └── version folder/
		│   │       ├── format folder/
		│   │       ├── format folder/
		│   │       ├── format folder/
		│   │       ├── content.hocr
		│   │       ├── content.txt
		│   │       ├── content.vtt
		│   │       ├── manifest.json
		│   │       ├── metadata.yml
		│   │       └── thumbnail.jpg
		│   └── NOID/
		│       └── version folder/
		│           ├── format folder/
		│           ├── format folder/
		│           ├── format folder/
		│           ├── content.hocr
		│           ├── content.txt
		│           ├── content.vtt
		│           ├── manifest.json
		│           ├── metadata.yml
		│           └── thumbnail.jpg
		└── collection folder/
			└── NOID/
				└── version folder/
					├── format folder/
					├── format folder/
					├── format folder/
					├── content.hocr
					├── content.txt
					├── content.vtt
					├── manifest.json
					├── metadata.yml
					└── thumbnail.jpg

### 4.2 Collection folders

### 4.3 Versions
	
Digital objects can and will change over time. Any change to a digital object, including content or metadata, MUST result in an additional version folder.

* Version folders MUST begin with a lower case "v" directly followed by a sequential integer.
* All digital objects MUST contain a `v1` version folder.
* The number of version folders is not limited, `v10` is valid, as is `v9999`.

The most recent version of a digital object MUST be the largest integer in the version folders once the leading `v`s are removed.
* `v11` is more recent than `v5`
	
The most recent version of a digital object MUST contain all the files for a digital Object

Previous versions MUST not contain any files that were unchanged in the next sequential version.
* This means that all unchanged files MUST be moved to the next version folder during a change. Only the previous version of changed files MUST stay in the previous version folder.

#### 4.3.1 Example with multiple versions

In this example, the `metadata.yml` changed for version 2, and the `thumbnail.jpg` file changed in version 3.

	└── apap101/
		└── 1n79hq253/
			├── v1/
			│   └── metadata.yml
			├── v2/
			│   └── thumbnail.jpg
			└── v3/
				├── jpg/
				├── pdf/
				├── content.hocr
				├── manifest.json
				├── metadata.yml
				└── thumbnail.jpg
				
### 4.4 Format folders


### 4.5. Text files

The most recent version of a digital objects MUST contain the following files directly within the version directory (`v1`, `v2`, etc.):
* `metadata.yml`
* `manifest.json`
	
Additonally, The most recent digital object MUST contain one content text file from this set:
* `content.hocr`
*` content.vtt`
*` content.txt`
Of this set, it is RECOMMENDED to have either an HOCR or VTT file.

#### 4.5.1 Text encoding and line endings

All text files within a digital object, such as `metadata.yml`, `content.txt`, `content.hocr`, `content.vtt`, and `manifest.json`, MUST use UTF-8 encoding and MUST use a line feed character (LF or \n) for line endings.

#### 4.5.2 `metadata.yml`

* `metadata.yml` must be a valid [YAML file](https://yaml.org/spec/1.2.2/).

Fields contained in `metadata.yml` are defined in [5. `metadata.yml` fields](#5.)

#### 4.5.3 `manifest.json`

* `manifest.json` must be a valid JSON file according to [[rfc7159]](https://tools.ietf.org/html/rfc7159).
* `manifest.json` must be a valid IIIF manifest according to the [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)

#### 4.5.3 Content files

Content files contain text that can be indexed into Solr for discovery. It is RECOMMENDED to use structured formats such as HOCR or VTT to support IIIF annotations and captioning, but an unstructured `content.txt` file is also permitted for legacy digital objects.

## 5. `metadata.yml` fields

**identifier**: The digital object identifier for the Object
**date_created**:

## 6. Examples


### 6.1 Digital object example

	├── apap138/
	│   ├── 6w924x89w/
	│   │   └── v1/
	│   │       ├── mp3/
	│   │       ├── content.vtt
	│   │       ├── manifest.json
	│   │       └── metadata.yml
	│   └── 84f1tH58w/
	│       └── v1/
	│           ├── mp3/
	│           ├── content.vtt
	│           ├── manifest.json
	│           └── metadata.yml
	└── ua807/
		└── 5t34t462n/
			└── v1/
				├── jpg/
				├── pdf/
				├── tiff/
				├── content.hocr
				├── manifest.json
				├── metadata.yml
				└── thumbnail.jpg
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

