from fpdf import FPDF
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


class Conversion:
    def __init__(self, app):
        self.app = app
        
        self._img_path = './data/default.png'
        self._charset = 'simple'
        self._invert = False
        self._colour = False
        self._resolution = 120
        self._bgcolour = (255, 255, 255)
        
        self._progress = 0
    
    @property
    def progress(self): return self._progress
    
    # SETTERS (call from outside)
    def change_image(self, new: str):
        self._img_path = new
    
    def change_charset(self, new: str):
        self._charset = new
    
    def change_inversion(self, new: bool):
        self._invert = new
    
    def change_coloured(self, new: bool):
        self._colour = new
    
    def change_resolution(self, new: int):
        self._resolution = new
    
        
    
    
    # CONVERSION FUNCTIONS
    def load_charset(self) -> list:
        if self._charset == 'simple':
            nums = np.genfromtxt('./data/charset1.txt', delimiter=',', dtype='int16')
            return [f'{num:c}' for num in nums]
        if self._charset == 'complex':
            nums = np.genfromtxt('./data/charset2.txt', delimiter=',', dtype='int16')
            return [f'{num:c}' for num in nums]
    
    def load_image(self) -> Image:
        with Image.open(self._img_path, 'r') as in_image:
            if in_image.mode != 'RGB':
                in_image.convert('RGB')
            return in_image.copy()
    
    def manipulate_image(self, image) -> Image:
        temp_image = ImageOps.grayscale(image)
        temp_image = ImageOps.scale(temp_image,
                                    self._resolution / temp_image.width)
        temp_image = temp_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        edges = temp_image.filter(ImageFilter.FIND_EDGES)
        edges = edges.filter(ImageFilter.CONTOUR)
        edges = ImageOps.posterize(edges, 7)
        
        merged_image = Image.blend(edges, temp_image, 0.5)
        
        return merged_image
    
    def get_colours(self, image):
        image = ImageOps.scale(image, self._resolution / image.width)
        array = np.asarray(image)
        return array
    
    
    # THE CONVERSION METHOD
    def run(self) -> tuple:
        
        if self._invert == True and self._colour == True:
            bgclr = (0, 0, 0)
        if self._invert == False and self._colour == True:
            bgclr = (255, 255, 255)
        if self._invert == True and self._colour == False:
            bgclr = (255, 255, 255)
        if self._invert == False and self._colour == False:
            bgclr = (255, 255, 255)
        
        charset = self.load_charset()
        image = self.load_image()
        
        manipulated = self.manipulate_image(image)
        
        palette = self.get_colours(image)
        
        array = np.asarray(manipulated)
        inv_array = np.asarray(ImageOps.invert(manipulated))
        
        font_size = 20
        
        out_font = ImageFont.truetype('Courier', font_size)
        out_image = Image.new('RGB',
                              (int(manipulated.width * font_size*1.5), int(manipulated.height * font_size*1.5)),
                              bgclr)
        draw = ImageDraw.Draw(out_image)
        out_text = ''
        
        for i in range(manipulated.height):
            for j in range(manipulated.width + 1):
                if j < manipulated.width:
                    if self._colour == True:
                        colour = palette[(i, j)][0], palette[(i, j)][1], palette[(i, j)][2]
                    if self._colour == False:
                        colour = (0,0,0)
                    if self._invert == True:
                        idx = int(int(inv_array[(i, j)]) / 255 * (len(charset) - 1))
                    if self._invert == False:
                        idx = int(int(array[(i, j)]) / 255 * (len(charset) - 1))
                    draw.text((j*(font_size*1.5), i*(font_size*1.5)), f'{charset[idx]}{charset[idx]}', font=out_font, fill=colour)
                    out_text += charset[idx]
                else:
                    #draw.text((j*(font_size), i*(font_size)), ' ', font=out_font, fill=colour)
                    out_text += '\n'
        
        return out_image.copy(), out_text

