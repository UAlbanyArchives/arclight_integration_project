import os, re
import yaml
from subprocess import Popen, PIPE
from pypdf import PdfReader, PdfWriter

if os.name == "nt":
	root = "\\\\Lincoln\\Library\\SPE_DAO"
else:
	root = "/media/Library/SPE_DAO"


for col in os.listdir(root):
	colPath = os.path.join(root, col)
	if col == "ua531":
		if os.path.isdir(colPath):
			for objID in os.listdir(colPath):
				objPath = os.path.join(colPath, objID, "v1")
				metadataPath = os.path.join(objPath, "metadata.yml")
				pdfPath = os.path.join(objPath, "pdf")
				if os.path.exists(pdfPath):
					jpgPath = os.path.join(objPath, "jpg")

					pdfCount = 0
					for pdf in os.listdir(pdfPath):
						pdfFilePath = os.path.join(pdfPath, pdf)
						if os.path.isfile(pdfFilePath) and pdf.lower().endswith(".pdf"):
							pdfCount += 1

					if pdfCount != 1:
						raise Exception(f"ERROR: found {pdfCount} PDF files for {col}/{objID}")
					else:
						for pdf in os.listdir(pdfPath):
							filepath = os.path.join(pdfPath, pdf)
							filename = os.path.splitext(pdf)[0]
							#convertDir = os.path.join(jpgPath, filename)
							convertDir = jpgPath

							print (f"Processing {pdf} from {col}/{objID}...")

							with open(metadataPath, 'r') as yml_file:
								data = yaml.safe_load(yml_file)
							data['original_pdf'] = pdf
							with open(metadataPath, 'w') as yml_file:
								yaml.dump(data, yml_file)

							if not os.path.isdir(convertDir):
								os.mkdir(convertDir)
							outfile = os.path.join(convertDir, filename)

							pdfimagesCmd = ["pdftoppm", filepath, outfile, "-jpeg"]
							pdfimages = Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE)
							stdout, stderr = pdfimages.communicate()
