#!/usr/bin/python

from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io


class SdmOcrProcessor:

    def __init__(self):

        self.tool = pyocr.get_available_tools()[0]
        self.lang = self.tool.get_available_languages()[0]
        self.ocr_text = ''

    def process_pdf(self, pdf_path):

        # TODO: detect if the PDF is text or not, if it is,
        # just read the text and put it in the ocr_text variable.

        req_image = []
        final_text = []

        image_pdf = Image(filename=pdf_path, resolution=300)
        image_jpeg = image_pdf.convert('jpeg')

        for img in image_jpeg.sequence:
            img_page = Image(image=img)
            req_image.append(img_page.make_blob('jpeg'))

        for img in req_image:
            txt = tool.image_to_string(
                    PI.open(io.BytesIO(img)),
                    lang=lang,
                    builder=pyocr.builders.TextBuilder()
            )

            final_text.append(txt)

        self.ocr_text = final_text(join)


