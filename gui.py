import tkinter as tk
import os
import json
import shutil 
import ebooklib
from PyPDF2 import PdfReader
from functools import partial
from tkinter import Canvas, Frame, Button, Tk, Text, ttk, Checkbutton, Entry, Label, Radiobutton, Menu, filedialog
from PIL import Image, ImageTk
from pathlib import Path
from ebooklib import epub
from moveable_widgets import *
from defaults import *
# Fix apply for resize
# Pictures
# Logo
# Clean up code
# Add documentation
# Search
# Bookmark
# Highlight
# Keybinds
# Back to top button
# Change book menu, three dots?
# BUggY BEANS show sidebar
# Add error handling
# Pdf support
# theme with fonts and sizes

class Window():
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("BookBot")
        self.__root.configure(background=COLOR)
        self.__root.protocol("WM_DELETE_WINDOW", self._quit)
        self.__root.attributes('-zoomed', True)
        self.__root.columnconfigure(0, weight=1)
        self.__root.rowconfigure(0, weight=1)
        self.current_book = None
        self.open_note_book = False

        if not os.path.exists('books/'):
            os.makedirs('books')

    # Frames and textscrollcombos
        self.text_container = make_basic_full_frame(self.__root)
    
        self.text_frame = TextScrollCombo(self.text_container, bg=COLOR)
        self.text_frame.grid(column=0, row=0, sticky="nsew")
    
        self.all_books_menu = TextScrollCombo(self.text_container, bg=COLOR)
        
        self.option_frame = Frame(self.text_container, bg=COLOR, highlightthickness=1)
        self.option_frame.grid(column=1, row=0, sticky="ens")

        make_resizable(self.option_frame, self.text_container)
        
    # Menus
        #Main Menus
        self.menubar = Menu(self.__root, bg=COLOR, bd=1, font=(FONT, FONT_SIZE1), activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.settings_menu = Menu(self.menubar, tearoff=0, bg=BUTTON_COLOR, font=(FONT, FONT_SIZE1), activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.books_menu = Menu(self.menubar, tearoff=0, bg=BUTTON_COLOR, font=(FONT, FONT_SIZE1), activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.helpmenu = Menu(self.menubar, tearoff=0, bg=BUTTON_COLOR, font=(FONT, FONT_SIZE1), activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)

    # Settings
        self.settings_menu.add_command(label="Fullscreen", command=self.fullscreen)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label='Set default theme', command=self.donothing)
        self.settings_menu.add_command(label="Hide Sidebar", command=self.option_frame.grid_forget)
        #lambda
        self.settings_menu.add_command(label="Show sidebar", command=self.option_frame.grid(column=1, row=0, sticky="ens"))
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Exit", command=self._quit)
        
    # Book menu
        self.books_menu.add_command(label="Go to all books", command=self.go_to_books)
        self.books_menu.add_separator()
        self.books_menu.add_command(label="Clear Text", command=self.clear_text_frame)
        self.books_menu.add_command(label="Clear Cache", command=self.clear_cache)
        self.books_menu.add_command(label="Add book", command=self.add_book)
        self.books_menu.add_command(label="Remove book", command=self.remove_book)

    # Help Menu
        self.helpmenu.add_command(label="Contact", command=self.donothing)
        self.helpmenu.add_command(label="About", command=self.info)

        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)
        self.menubar.add_cascade(label="Books", menu=self.books_menu)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.__root.config(menu=self.menubar)

    # Buttons
        self.all_books_button = Button(self.option_frame, text='All Books', bg=BUTTON_COLOR, command=self.go_to_books, highlightthickness=0, font=(FONT, FONT_SIZE1), activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.all_books_button.pack(side='top', fill='x')

        self.add_n_read_button = Button(self.option_frame, text='Add n\' Read Book', bg=BUTTON_COLOR, command=self.add_and_read, highlightthickness=0, font=(FONT, FONT_SIZE1))
        self.add_n_read_button.pack(side='top', fill='x', pady=10)

        self.refresh_button = Button(self.option_frame, text='Refresh', bg=BUTTON_COLOR, command=self.check_entries, highlightthickness=0, font=(FONT, FONT_SIZE1))
        self.refresh_button.pack(side='top', fill='x')

        self.ph = Button(self.option_frame, text='Placeholder button', bg=BUTTON_COLOR, command=self.donothing, highlightthickness=0, font=(FONT, FONT_SIZE1))
        self.ph.pack(side='top', fill='x', pady=10)

        self.notes_button = Button(self.option_frame, text='Notebook', bg=BUTTON_COLOR, command=self.notes_by_book, highlightthickness=0, font=(FONT, FONT_SIZE1))
        self.notes_button.pack(side='top', fill='x')

    # Entries and Labels
        self.text_size_label = Label(self.option_frame, text='Text Size', bg=COLOR, font=(FONT, FONT_SIZE1))
        self.text_size_label.pack(side='top', fill='x', pady=5)

        self.text_size_entry = Entry(self.option_frame, bg=BUTTON_COLOR, highlightthickness=0)
        self.text_size_entry.pack(side="top", fill="x")

        self.padding_label = Label(self.option_frame, text='Padding', bg=COLOR, font=(FONT, FONT_SIZE1))
        self.padding_label.pack(side='top', fill='x', pady=5)

        self.padding_entry = Entry(self.option_frame, bg=BUTTON_COLOR, highlightthickness=0)
        self.padding_entry.pack(side="top", fill="x")

    # Checkboxes
        self.center_var = tk.BooleanVar()
        self.center = Checkbutton(self.option_frame, bg=COLOR, highlightthickness=0, command=self.center_text_clicked, text='Center text', font=(FONT, FONT_SIZE1), fg=FONT_COLOR, variable=self.center_var)
        self.center.pack(side='top', fill='x', pady=10)
    
    # Notes 
        self.notes = Frame(self.option_frame, highlightthickness=0, bd=0, width=1, highlightbackground=BUTTON_COLOR)
        self.notes_text = Text(self.notes, state='normal', wrap='word', font=(FONT, FONT_SIZE1), fg=FONT_COLOR, bg=COLOR, width=1)
        
    # Themes
        self.themes_button = Menu(self.__root, tearoff=0, bg=BUTTON_COLOR, font=(FONT, FONT_SIZE1))
        i = 0
        with open('themes.txt', 'r') as file:
            for theme in file:
                
                name, color, font_color, button_color, active_background, active_font = theme.strip('\n').split(', ')
                i += 1
                self.themes_button.add_radiobutton(label=name, command=partial(self.change_theme, color, font_color, button_color, active_background, active_font), value=i, indicator=0)
        self.menubar.add_cascade(label="Themes", menu=self.themes_button)

    # Make basic cache file 
        if not os.path.exists('cache.json'):
            with open('cache.json', 'w') as file:
                json.dump({'books': {'notes': ''}}, file, indent=4)

        self.__root.mainloop()


    def update_notes(self):
        if self.open_note_book:
            self.notes_text.delete('1.0', 'end')
            self.notes_text.insert('insert', self.get_notes())


    def notes_by_book(self):
        if self.open_note_book:
            self.notes_text.config(state='disabled')
            self.notes_text.delete('1.0', 'end')
            self.notes.pack_forget()
            self.open_note_book = False
        else:
            self.notes_text.config(state='normal')
            self.notes.pack(side='bottom', fill='both', expand=True, pady=15)
            self.notes_text.insert('insert', self.get_notes())
            self.notes_text.pack(fill='both', expand=True, anchor='n')
            self.open_note_book = True
        

    def info(self):
        self.clear_text_frame()
        self.text_frame.insert('This is my first actual coding project so i apologize for any bugs!\nUpload txt files and read them, change theme and enter fullscreen.\nMy GitHub: @pat955')


    def remove_book(self):
        pass


    def add_and_read(self):
        path = self.add_book()
        if path:
            self.read_book(f'books/{path.split('/')[-1]}')


    def add_book(self):
        path = filedialog.askopenfilename(initialdir = str(Path.home() / "Downloads"))
        if path:
            try:
                shutil.move(path, "books/")
            except:
                pass
            return path


    def clear_text_frame(self):
        self.text_frame = TextScrollCombo(self.text_container)
        self.text_frame.txt.config(bg=COLOR, fg=FONT_COLOR, font=(FONT, FONT_SIZE2))
        self.text_frame.grid(column=0, row=0, sticky="nsew")


    def go_to_books(self):
        self.text_frame.grid_forget()
        self.all_books_menu.txt = Frame(self.all_books_menu, bg=COLOR)
        self.all_books_menu.txt.grid(row=0, column=0, sticky='nsew')
        self.all_books_menu.grid(column=0, row=0, sticky="nsew")
        i = 0
        j = 0
        for file in os.scandir('books/'):
            if  i % 6 == 0:
                j += 1
                i = 0
            
            path =f'books/{file.name}'
            button = Button(self.all_books_menu.txt, text=f'{file.name.split('.')[0].replace('_', ' ').capitalize()}', bg=BUTTON_COLOR, font=(FONT, FONT_SIZE2), fg=FONT_COLOR, activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT, command=partial(self.read_book, path), width=16)
            button.grid(row=j, column=i, sticky='n', pady=10, padx=20)
            i += 1


    def clear_cache(self):
        os.remove('cache.json')
        if not os.path.exists('cache.json'):
            with open('cache.json', 'w') as file:
                json.dump({'books': {'notes': ''}}, file, indent=4)


    def get_notes(self):
        with open('cache.json', 'r') as file:
            file_data = json.load(file)
            notes = ''
            if self.current_book is None:
                return file_data['books']['notes']
                
            try:
                return file_data['books'][self.current_book]['notes']
            except:
                pass
            return notes
            

    def save_book_attributes(self):
        file_data = None
        with open('cache.json', 'r+') as file:
            file_data = json.load(file)

        notes = self.notes_text.get("1.0", 'end')
        if self.current_book is not None:

            if self.current_book not in file_data['books']:
                file_data['books'][self.current_book] = {}

            file_data['books'][self.current_book]['scrollbar'] = self.text_frame.scrollb.get()

            if notes != '':
                file_data['books'][self.current_book]['notes'] = notes
        else:
            if notes != '':
                file_data['books']['notes'] = notes

        with open('cache.json', 'w') as file:
            json.dump(file_data, file, indent=4)


    def read_pdf(self, path):
        with open(path, 'rb') as file:
            pdf = PdfReader(file)
            i = 0
            for page in pdf.pages:
                i += 1
                self.text_frame.insert(f'{page.extract_text()}  ---{i}---\n')
        self.text_frame.txt.config(state='disabled')
        self.text_frame.set_scrollbar(path)


    def read_book(self, path):
        self.save_book_attributes()
        self.current_book = path

        self.clear_text_frame()
        self.check_entries()
        self.all_books_menu.grid_forget()
        self.text_frame.grid(column=0, row=0, sticky="nsew")
        self.update_notes()

        if path.endswith('.pdf'):
            self.read_pdf(path)
            return

        with open(path, 'r') as file:            
            self.text_frame.insert(file.read())
        self.text_frame.txt.config(state='disabled')
        self.text_frame.set_scrollbar(path)
    

    def fullscreen(self):
        self.__root.attributes("-fullscreen", True)
        self.__root.bind("<Escape>", lambda x: self.__root.attributes("-fullscreen", False))


    def change_theme(self, color, font_color, button_color, active_background, active_font):
        global COLOR
        global FONT_COLOR
        global BUTTON_COLOR
        global ACTIVEBACKGROUND
        global ACTIVEFONT

        COLOR = color
        FONT_COLOR = font_color
        BUTTON_COLOR = button_color
        ACTIVEBACKGROUND = active_background
        ACTIVEFONT = active_font
        frames = [self.__root, self.option_frame, self.notes, self.text_frame, self.menubar, self.all_books_menu, self.all_books_menu.txt, *(self.text_container.winfo_children())]
        self.option_frame.config(bg=COLOR)
        self.text_frame.config(bg=COLOR)
        self.menubar.config(activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)


        self.settings_menu.config(activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.books_menu.config(activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.helpmenu.config(activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        self.themes_button.config(activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
        
        for frame in frames:
            for widget in frame.winfo_children():
                try:
                    widget.config(bg=COLOR)
                except:
                    pass

                try: 
                    widget.config(fg=FONT_COLOR)
                except Exception as e:
                    pass
                if type(widget) == Checkbutton:
                    widget.config(activebackground=COLOR, activeforeground=ACTIVEFONT)

                elif type(widget) == Button:
                    widget.config(bg=BUTTON_COLOR, activebackground=ACTIVEBACKGROUND, activeforeground=ACTIVEFONT)
                elif type(widget) == Entry:
                    widget.config(bg=BUTTON_COLOR)

                widget.update()

    
    def check_entries(self):
        entries = {
            self.text_size_entry: self.change_text_size,
            self.padding_entry: self.change_padding,
            }
        for entry, func in entries.items():
            if entry.get():
                func()
       

    def change_padding(self):
        self.text_frame.txt.config(padx=self.padding_entry.get())


    def change_text_size(self):
        self.text_frame.txt.configure(font=(FONT, self.text_size_entry.get()))


    def center_text_clicked(self):
        if self.center_var.get():
            self.text_frame.txt.tag_configure("center", justify='center')
            self.text_frame.txt.tag_add("center", "1.0", "end")
        else:
            self.text_frame.txt.tag_delete('center')
        self.text_frame.grid()


    def clear_text(self):
        # Not in use
        self.text_frame.txt.delete('1.0', 'end')
        

    def _quit(self):
        self.save_book_attributes()
        self.__root.quit()
        self.__root.destroy()


    def donothing():
        return


class TextScrollCombo(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    # create a Text widget
        self.txt = tk.Text(self)
        self.txt.config(font=(FONT, FONT_SIZE2), highlightthickness=0, borderwidth=0, padx=10, pady=10, wrap='word', relief='sunken')

    # create a Scrollbar and associate it with txt
        self.scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = self.scrollb.set


    def insert(self, text):
        self.txt.insert('insert', text)
        self.txt.grid(row=0, column=0, sticky='nsew')
        self.txt.config(state='disabled')
    

    def set_scrollbar(self, book_path):
        with open('cache.json', 'r') as file:
            books_info = json.load(file)['books']
            if book_path in books_info:
                scrollbar_position = books_info[book_path]['scrollbar']
                self.scrollb.set(*books_info[book_path]['scrollbar'])
                self.txt.yview_moveto(scrollbar_position[0])