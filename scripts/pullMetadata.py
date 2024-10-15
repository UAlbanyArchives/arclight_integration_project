import os
import sys
import json
import yaml
import requests
from urllib.parse import urlparse

root = "\\\\Lincoln\\Library\\SPE_DAO"

fields = [
    "id",
    "create_date",
    "modified_date",
    "archivesspace_record",
    "collecting_area",
    "collection_number",
    "collection",
    "coverage",
    "record_parent",
    "processing_activity",
    "extent",
    "resource_type",
    "creator",
    "contributor",
    "description",
    "abstract",
    "keyword",
    "license",
    "rights_statement",
    "date_created",
    "publisher",
    "subject",
    "language",
    "identifier",
    "master_format",
    "bibliographic_citation"
]

if sys.argv[1].lower().startswith("http"):
	path = urlparse(sys.argv[1]).path
	noid = path.rstrip('/').split('/')[-1]
	hyraxURL = sys.argv[1]
else:
	noid = sys.argv[1]
	hyraxURL = "https://archives.albany.edu/concern/daos/" + sys.argv[1]

jsonURL = hyraxURL + "?format=json"
response = requests.get(jsonURL)
if not response.status_code == 200:
	raise Exception(f"Failed to fetch JSON data, status code: {response.status_code}")
else:
	json_data = response.json()

	colID = json_data["collection_number"]
	colPath = os.path.join(root, colID)
	objPath = os.path.join(colPath, noid)
	if not os.path.isdir(colPath):
		os.mkdir(colPath)
	if not os.path.isdir(objPath):
		os.mkdir(objPath)
	yaml_filename = os.path.join(objPath, "metadata.yml")

	yml_data = {}
	for field in fields:
		value = json_data.get(field, None)
		yml_data[field] = value if value is not None else ""

	# Write the data to a YAML file
	with open(yaml_filename, 'w') as yaml_file:
		yaml.dump(yml_data, yaml_file, default_flow_style=False)
