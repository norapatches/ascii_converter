from data.ascii import Conversion
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

CURRENT_DIR = os.getcwd()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ASCII converter')
        self.geometry('1400x750')
        self.minsize(900,475)
        
        self.converter = Conversion(self)
        
        self.variables = {
            'imgpath' : tk.StringVar(value='./data/default.png'),
            'charset' : tk.BooleanVar(value=False),
            'invert' : tk.BooleanVar(value=False),
            'colour' : tk.BooleanVar(value=False),
            'resolution' : tk.IntVar(value=120)
        }
        self.frames = {
            'left' : ttk.Frame(self),
            'center' : ttk.Frame(self),
            'right' : ttk.Frame(self)
        }
    
    def load_image(self):
        fpath = filedialog.askopenfilename(title='choose image',
                                           filetypes=(('PNG', '*.png'), ('JPG', '*.jpg *.jpeg')))
        if fpath:
            self.variables['imgpath'].set(value=fpath)
            self.converter.change_image(fpath)
            with Image.open(fpath) as new_img:
                self.original_img = new_img.copy()
                self.original_img_ratio = new_img.width / new_img.height
                self.original_img_tk = ImageTk.PhotoImage(self.original_img)
                
            canvas_ratio = self.before_canvas.winfo_width() / self.before_canvas.winfo_height()
            if canvas_ratio > self.original_img_ratio:
                height = int(self.before_canvas.winfo_height())
                width = int(height * self.original_img_ratio)
            else:
                width = int(self.before_canvas.winfo_width())
                height = int(width / self.original_img_ratio)
        
            resized_img = self.original_img.resize((width, height))
            self.resized_tk = ImageTk.PhotoImage(resized_img)
            
            self.before_canvas.create_image(
                int(self.before_canvas.winfo_width() / 2),
                int(self.before_canvas.winfo_height() / 2),
                anchor = 'center',
                image= self.resized_tk
            )    
    
    def set_charset(self):
        if self.variables['charset'].get() == True:
            self.converter.change_charset('complex')
        else:
            self.converter.change_charset('simple')
    
    def set_invert(self):
        self.converter.change_inversion(self.variables['invert'].get())
    
    def set_colour(self):
        self.converter.change_coloured(self.variables['colour'].get())
    
    def set_reso(self):
        self.converter.change_resolution(self.variables['resolution'].get())
    
    
    def place_frames(self):
        self.frames['left'].propagate(False)
        self.frames['left'].place(relx=0, rely=0, relwidth=0.45, relheight=1)
        
        self.frames['center'].propagate(False)
        self.frames['center'].place(relx=0.45, rely=0, relwidth=0.1, relheight=1)
        
        self.frames['right'].propagate(False)
        self.frames['right'].place(relx=0.55, rely=0, relwidth=0.45, relheight=1)
    
    def draw_left_frame(self):
        with Image.open(self.variables['imgpath'].get()) as in_img:
            self.original_img = in_img.copy()
            self.original_img_ratio = in_img.width / in_img.height
            self.original_img_tk = ImageTk.PhotoImage(self.original_img)
        self.open_button = ttk.Button(self.frames['left'],
                                      text='open image',
                                      command=self.load_image)
        self.before_canvas = tk.Canvas(self.frames['left'],
                                       background='black')
        self.open_button.pack(pady=5)
        self.before_canvas.pack(expand=True, fill='both')
        self.before_canvas.bind('<Configure>', self.resize_before_image)
    
    def draw_center_frame(self):
        inner_frame_1 = ttk.Frame(self.frames['center'])
        inner_frame_2 = ttk.Frame(self.frames['center'])
        inner_frame_3 = ttk.Frame(self.frames['center'])
        
        options_label = ttk.Label(inner_frame_1, text='SETTINGS')
        size_label = ttk.Label(inner_frame_2, text='RESOLUTION')
        save_label = ttk.Label(inner_frame_3, text='SAVE RESULT')
        
        checkboxes = [
            ttk.Checkbutton(inner_frame_1, text='complex', variable=self.variables['charset'], command=self.set_charset),
            ttk.Checkbutton(inner_frame_1, text='invert', variable=self.variables['invert'], command=self.set_invert),
            ttk.Checkbutton(inner_frame_1, text='colour', variable=self.variables['colour'], command=self.set_colour)
        ]
        sizes = [
            ('XXS', 40),
            ('XS', 60),
            ('S', 80),
            ('M', 120),
            ('L', 160),
            ('XL', 240),
            ('XXL', 320)
        ]
        self.savebuttons = [
            ttk.Button(inner_frame_3, text='PNG', state='disabled', command=self.save_result_png),
            ttk.Button(inner_frame_3, text='TXT', state='disabled', command=self.save_result_txt)
        ]
        
        inner_frame_1.pack(expand=True)
        options_label.pack(pady=10)
        
        inner_frame_2.pack(expand=True)
        size_label.pack(pady=10)
        
        for box in checkboxes:
            box.pack(anchor='w')
        
        for tag, val in sizes:
            radiobox = ttk.Radiobutton(inner_frame_2, text=tag, value=val, variable=self.variables['resolution'], command=self.set_reso)
            radiobox.pack(anchor='w')
        
        inner_frame_3.pack(expand=True)
        save_label.pack(pady=10)
        
        for btn in self.savebuttons:
            btn.pack(anchor='w')
    
    def draw_right_frame(self):
        with Image.open(self.variables['imgpath'].get()) as in_img:
            self.result_img = in_img.copy()
            self.result_img_ratio = in_img.width / in_img.height
        self.convert_button = ttk.Button(self.frames['right'],
                                         text='convert image',
                                         command= self.run_conversion)
        self.after_canvas = tk.Canvas(self.frames['right'],
                                      background='black')
        self.convert_button.pack(pady=5)
        self.after_canvas.pack(expand=True, fill='both')
        self.after_canvas.bind('<Configure>', self.resize_after_image)
    
    
    def run_conversion(self):
        self.result_img, self.result_txt = self.converter.run()
        self.result_img_ratio = self.result_img.width / self.result_img.height
        
        for btn in self.savebuttons:
            btn.configure(state='normal')
        
        canvas_ratio = self.after_canvas.winfo_width() / self.after_canvas.winfo_height()
        if canvas_ratio > self.result_img_ratio:
            height = int(self.after_canvas.winfo_height())
            width = int(height * self.result_img_ratio)
        else:
            width = int(self.after_canvas.winfo_width())
            height = int(width / self.result_img_ratio)
    
        resized_img = self.result_img.resize((width, height))
        self.out_resized_tk = ImageTk.PhotoImage(resized_img)
        
        self.after_canvas.create_image(
            int(self.after_canvas.winfo_width() / 2),
            int(self.after_canvas.winfo_height() / 2),
            anchor = 'center',
            image= self.out_resized_tk
        )
    
    def save_result_txt(self):
        outfname = filedialog.asksaveasfilename(initialdir=CURRENT_DIR, defaultextension='txt', initialfile='result.txt')
        if outfname:
            with open(outfname, 'w') as file:
                file.write(self.result_txt)
    
    def save_result_png(self):
        outfname = filedialog.asksaveasfilename(initialdir=CURRENT_DIR, defaultextension='png', initialfile='result.png')
        if outfname:
            self.result_img.save(outfname)
    
    def resize_after_image(self, event):
        canvas_ratio = event.width / event.height
        
        if canvas_ratio > self.result_img_ratio:
            height = int(event.height)
            width = int(height * self.result_img_ratio)
        else:
            width = int(event.width)
            height = int(width / self.result_img_ratio)
        
        resized_img = self.result_img.resize((width, height))
        self.out_resized_tk = ImageTk.PhotoImage(resized_img)
        
        self.after_canvas.create_image(
            int(event.width / 2),
            int(event.height / 2),
            anchor = 'center',
            image= self.out_resized_tk
        )
    
    def resize_before_image(self, event):
        canvas_ratio = event.width / event.height
        
        if canvas_ratio > self.original_img_ratio:
            height = int(event.height)
            width = int(height * self.original_img_ratio)
        else:
            width = int(event.width)
            height = int(width / self.original_img_ratio)
        
        resized_img = self.original_img.resize((width, height))
        self.resized_tk = ImageTk.PhotoImage(resized_img)
        
        self.before_canvas.create_image(
            int(event.width / 2),
            int(event.height / 2),
            anchor = 'center',
            image= self.resized_tk
        )
    
    
    def run(self):
        self.place_frames()
        self.draw_left_frame()
        self.draw_center_frame()
        self.draw_right_frame()
        self.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
