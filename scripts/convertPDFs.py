import os

if os.name == "nt":
    root_path = "\\\\Lincoln\\Library\\SPE_DAO"
else:
    root_path = "/media/Library/SPE_DAO"


obj_path = os.path.join(root_path, "examples", "apap362", "kjo56png0e")

skip_files = ["Thumbs.db"]

exts = {}
for root, dirs, files in os.walk(obj_path):
	for file in files:
		if file.startswith("."):
			continue
		if file.endswith(".LCK"):
			continue
		if file in skip_files:
			continue
		filename, ext = os.path.splitext(file)
		if ext in exts.keys():
			exts[ext] += 1
		else:
			exts[ext] = 1

print (exts)
