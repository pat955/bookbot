import tkinter as tk
from tkinter import ttk, Frame, Text
import os
import json
from moveable_widgets import *
from defaults import *

class TextScrollCombo(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_path = 'books/'
        self.cache_path = 'cache.json'
        
    # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    # create a Text widget
        self.txt = tk.Text(self)
        self.txt.config(font=(FONT, HEADING_SIZE), highlightthickness=0, borderwidth=0, padx=10, pady=10, wrap='word', relief='sunken')

    # create a Scrollbar and associate it with txt
        self.scrollb = ttk.Scrollbar(self, command=self.txt.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = self.scrollb.set


    def insert(self, text):
        self.txt.insert('insert', text)
        self.txt.grid(row=0, column=0, sticky='nsew')
        self.txt.config(state='disabled')
    

    def set_scrollbar(self, book_path):
        with open(self.cache_path, 'r') as file:
            books_info = json.load(file)['books']
            if book_path in books_info:
                scrollbar_position = books_info[book_path]['scrollbar']
                self.scrollb.set(*books_info[book_path]['scrollbar'])
                self.txt.yview_moveto(scrollbar_position[0])