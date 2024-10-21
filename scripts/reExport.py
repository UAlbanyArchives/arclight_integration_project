import os

if os.name == "nt":
    root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root = "/media/Library/SPE_DAO"

object_ids = []

for col in os.listdir(root):
	colDir = os.path.join(root, col)
	if os.path.isdir(colDir):
		for obj in os.listdir(colDir):
			object_ids.append(obj)

print (object_ids)
