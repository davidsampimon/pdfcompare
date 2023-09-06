import os
import shutil
import pypdfium2
from PIL import ImageChops, Image, ImageDraw
from datetime import datetime


class PdfPair:
    def __init__(self, pdf_a, pdf_b):
        self.pdf_a = pdf_a
        self.pdf_b = pdf_b
        self.export_folder = "./export"
        self.tmp = "./tmp"
        self.run = None
        self.fmt = r"%Y%m%d - %H%M%S"

    @property
    def output_folder(self):
        return f"{self.export_folder}/{self.run}"
    
    @property
    def tmp_dirs(self):
        return [f"{self.tmp}/pdf_a", f"{self.tmp}/pdf_b"]

    def _setup_folders(self):
        os.makedirs(self.output_folder)
        for tmp_dir in self.tmp_dirs:
            os.makedirs(tmp_dir)
    
    def _pdf_to_jpg(self, filepath, outputpath):
        pdf = pypdfium2.PdfDocument(filepath)
        page_indices = [i for i in range(len(pdf))]
        renderer = pdf.render(pypdfium2.PdfBitmap.to_pil, page_indices=page_indices)
        for index, image in zip(page_indices, renderer):
            image.save(f"{outputpath}/Pagina {index + 1}.jpg")
        
    def _compare_images(self, image_a, image_b):
        filename = os.path.basename(image_a)
        im1 = Image.open(image_a)
        im2 = Image.open(image_b)
        diff = ImageChops.difference(im1, im2)
        if diff.getbbox():
            red_layer = Image.new("RGB", diff.size, "red")
            red_diff = ImageChops.multiply(red_layer, diff)
            composite = Image.blend(red_diff, im1, 0.7)
            self._draw_bounding_box(composite, diff.getbbox())
            composite.save(f"{self.output_folder}/{filename}")
    
    def _draw_bounding_box(self, image, bbox):
        top_left = (bbox[0], bbox[1])
        bottom_right = (bbox[2], bbox[3])
        draw = ImageDraw.Draw(image)
        draw.rectangle([top_left, bottom_right], outline="Red", width=2)


    def compare(self):
        self.run = datetime.now().strftime(self.fmt)
        try:
            self._setup_folders()
            print("Creating images of pdf A...")
            self._pdf_to_jpg(self.pdf_a, self.tmp_dirs[0])
            print("Creating images of pdf B...")
            self._pdf_to_jpg(self.pdf_b, self.tmp_dirs[1])
            filenames = [os.listdir(tmp_dir) for tmp_dir in self.tmp_dirs]
            print("Comparing images...")
            for i in range(len(filenames[0])):
                image_a = f"{self.tmp_dirs[0]}/{filenames[0][i]}"
                image_b = f"{self.tmp_dirs[1]}/{filenames[1][i]}"
                self._compare_images(image_a, image_b)
        finally:
            shutil.rmtree(self.tmp)
            print("Done")


def main():
    pdf_pair = PdfPair("./input/NIKS NIEUWS  4 sept DRUKWERK2.pdf", "./input/NIKS NIEUWS  3 sept DRUKWERK.pdf")
    pdf_pair.compare()


if __name__ == "__main__":
    main()
