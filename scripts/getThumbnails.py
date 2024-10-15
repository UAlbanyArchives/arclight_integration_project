import os
import yaml
import requests

if os.name == "nt":
	root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
	root = "/media/Library/SPE_DAO"

root_url = 'https://archives.albany.edu/downloads/'

for col in os.listdir(root):
	if os.path.isdir(os.path.join(root, col)):
		for obj in os.listdir(os.path.join(root, col)):
			objPath = os.path.join(root, col, obj, "v1")
			metadataPath = os.path.join(objPath, "metadata.yml")

			with open(metadataPath, 'r') as file:
				metadata = yaml.safe_load(file)

			if metadata.get('resource_type') == "Audio":
				thumbnail_url = "https://archives.albany.edu/assets/audio-5133b642ee875760dbd85bfab48649d009efd4bd29db1165f891b48a90b4f37e.png"
			else:
				thumbnail_id = metadata.get('thumbnail_id')
				thumbnail_url = f"{root_url}{thumbnail_id}?file=thumbnail"

			if thumbnail_url:
				response = requests.get(thumbnail_url)
				if response.status_code == 200:
					with open(os.path.join(objPath, 'thumbnail.jpg'), 'wb') as img_file:
						img_file.write(response.content)
						print("Thumbnail downloaded and saved as thumbnail.jpg")
				else:
					print(f"Failed to download image. Status code: {response.status_code}")
			else:
				print("No thumbnail_id found in metadata.")
