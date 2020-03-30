import os
import random
from datetime import date
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image


class Main:
    def __init__(self, sig_bit, plane, key, image_path, cover_image_path, save_path):
        self.sig_bit = sig_bit
        self.plane = plane
        self.key = key

        self.image_path = image_path
        self.cover_image_path = cover_image_path
        self.save_path = save_path

        self.cover_image = Image.open(self.cover_image_path)
        self.dimensions = self.cover_image.size
        self.pixels = self.cover_image.load()
        bits = np.unpackbits(np.fromfile(self.image_path, dtype="uint8"))
        self.image = ''.join(str(i) for i in list(bits))

        # - Seeding
        self.shuffled_indices = self.ordering()
        self.image_bits = self.watermark()
        # - Conversion
        bits = self.add_length()
        # - Modify pixels
        for i in range(len(bits)):
            x = self.shuffled_indices[i] % self.dimensions[0]
            y = self.shuffled_indices[i] // self.dimensions[0]
            p = format(self.pixels[x, y][self.plane], 'b').zfill(8)

            # - Change if existing bit is 0, only if secret bit is 1
            if p[self.sig_bit] == "0":
                if bits[i] == "1":
                    self.pixels[x, y] = self.modify_pixel(self.pixels[x, y], 1)
            # - Change if existing bit is 1, only if secret bit is 0
            else:
                if bits[i] == "0":
                    self.pixels[x, y] = self.modify_pixel(self.pixels[x, y], 0)

        # - File handling
        if self.save_path.find('tif'):  # - Support for tiff
            self.cover_image.save(self.save_path, format='tiff', compression='None')
        else:
            self.cover_image.save(self.save_path, compression='None')

    def error_message(self, case):
        switch = {
            1: "Input not numerical",
            2: "Invalid file format"
        }
        self.display("Error {number}: {case}".format(number=case, case=switch.get(case)))
        self.display("\n")
        self.display("-" * 100)
        self.display("\n")

    def inputs(self):
        choice = self.radio_input("Customised embedding?", ["Yes", "No"])
        if choice == "Yes":
            try:
                key = int(self.entry_input("Please enter numerical key"))
            except ValueError:
                self.error_message(1)
                return self.inputs()
            sig_bit = int(self.entry_input("Enter significant bit"))
            plane = int(["Red", "Blue", "Green"].index(
                self.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
            key = 0
        return sig_bit, plane, key

    def config(self):
        # - Message & image file validation
        self.display("Fetching cover image file directory...")
        cover_image_path = filedialog.askopenfilename(title="Select cover image file",
                                                      filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                                 ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                                 ("bitmap files", "*bmp"), ("all files", "*.*")))
        if self.exit_application(cover_image_path):
            return self.config()

        self.display("Fetching image file directory...")
        image_path = filedialog.askopenfilename(title="Select image file",
                                                filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                           ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                           ("bitmap files", "*bmp"), ("all files", "*.*")))

        if self.exit_application(image_path):
            return self.config()

        return image_path, cover_image_path

    def initialising(self):
        cover_size = os.stat(self.cover_image_path).st_size
        image_size = os.stat(self.image_path).st_size
        if image_size > cover_size:
            return True
        return False

    def file_handle(self):
        self.display("Fetching save path...")
        save_path = filedialog.asksaveasfilename(defaultextension="*.bmp",
                                                 title="Save image file",
                                                 filetypes=(("bitmap files", "*bmp"), ("jpeg files", "*.jpg"),
                                                            ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                            ("png files", "*.png"), ("all files", "*.*")))
        if self.exit_application(save_path):
            self.file_handle()
        return save_path

    def ordering(self):
        shuffled_indices = list(range(self.dimensions[0] * self.dimensions[1]))
        random.seed(self.key)
        random.shuffle(shuffled_indices)
        return shuffled_indices

    def add_length(self):
        length = format(len(self.image_bits), 'b').zfill(100)
        return length + self.image_bits

    def modify_pixel(self, pixel, modifier):
        pixel = list(pixel)
        if self.plane == 0:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)

        if self.plane == 1:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)

        if self.plane == 2:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)
        return pixel[0], pixel[1], pixel[2]

    @staticmethod
    def exit_application(file):
        if file == "":
            msg_box = messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                             icon='warning')
            if msg_box == 'yes':
                raise SystemExit
            else:
                messagebox.showinfo('Return', 'You will now return to the application screen')
                return True

    def watermark(self):
        watermark = self.save_path[-3:].upper() + "/dylan/" + date.today().strftime("%Y-%m-%d")
        watermark = ''.join(format(ord(i), 'b').zfill(8) for i in watermark)
        index = random.randint(0, len(self.image))
        return self.image[:index] + watermark + self.image[index:]


if __name__ == "__main__":
    pass