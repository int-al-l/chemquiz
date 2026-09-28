import fitz

pdf = fitz.open("C:/Users/anton/Downloads/Synthware-catalog-2018.pdf")

page = pdf[29]

blocks = page.get_text("dict")["blocks"]

glassware = {}

for block in blocks:

    if "lines" not in block:
        continue

    for line in block["lines"]:

        for span in line["spans"]:

            text = span["text"].strip()

            if (
                span["font"] == "Arial,Bold"
                and span["size"] == 10.5
                and text.isupper()
            ):
                while text in glassware:
                    text = text + "1"
                y0 = span["bbox"][1]
                glassware[text] = y0


#img + result
parseimages = page.get_image_info(xrefs=True)

images = {}

for image in parseimages:
    images[image["xref"]] = image["bbox"][1]
       
    #(65.3299560546875, 103.47496032714844, 268.862060546875, 118.0279541015625)
    #(65.3284912109375, 451.1598205566406, 268.860595703125, 465.71282958984375)
correct_images = {}
parse_glass = {}
for glass in glassware:
    for image in images:
        if images[image] >= glassware[glass]:
            correct_images[image] = images[image]
    parse_glass[glass] = min(correct_images, key=correct_images.get)
    correct_images.clear()
print(parse_glass)    

for name, xref in parse_glass.items():

    image = pdf.extract_image(xref)

    filename = name.replace("/", "_") + "." + image["ext"]

    with open(filename, "wb") as f:
        f.write(image["image"])
