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
						if pdf.lower().endswith(".pdf"):
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

							# Getting DPI for each image
							pageDPI = {}
							pdfimagesCmd = ["pdfimages", "-list", filepath]
							pdfimages = Popen(pdfimagesCmd, stdout=PIPE, stderr=PIPE)
							lineCount = -2
							for line in pdfimages.stdout:
								lineCount += 1
								if lineCount > 0:
									col = re.split("\\s+", line.decode().strip())
									pageDPI[lineCount] = f"{col[12]}x{col[13]}"

							# convert to images
							pageOrder = []
							pdf_reader = PdfReader(filepath)
							page_count = 0
							page_total = len(pdf_reader.pages)

							file = pdf

							for page in pdf_reader.pages:
								page_count += 1
								if len(page.images) != 1:
									raise ValueError(f"ERROR: During OCR prep, PDF page number {page_count} has multiple images.")
								page_rotation = page.get('/Rotate')
								for image in page.images:
									ext = os.path.splitext(image.name)[1]
									image_path = os.path.join(convertDir, f"{os.path.splitext(file)[0]}-{page_count}{ext}")
									if os.path.isfile(image_path):
										raise ValueError(f"ERROR: In extracting images for OCR, file already exists: {image_path}.")
									with open(image_path, "wb") as fp:
										fp.write(image.data)

									# fix sizing
									print (f"\tRestoring to {pageDPI[page_count]} dpi...")
									size_cmd = ['convert', '-units', 'pixelsperinch', '-density', pageDPI[page_count], image_path, image_path]
									if ext.lower() == "png":
										size_cmd.insert(1, '-units pixelsperinch')
									#print (f"\trunning {' '.join(size_cmd)}")
									size_resp = process(size_cmd)
									if size_resp != 0:
										raise ValueError(f'Error resizing file {image_path}')

									#address image rotation
									if page_rotation:
										print ("\tFixing image rotation...")
										img = Image.open(image_path)
										img_rotate = img.rotate(-abs(page_rotation), expand=1)
										img_rotate.save(image_path)
