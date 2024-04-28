import tkinter as tk
import tkinter.filedialog as fd
from tkinter.messagebox import askyesno
import os
class TextEditor:
    untitled = "Untitled"
    def __init__(self,master):
        self.save_path = ""

        self.window = master
        self.menuBar = tk.Menu(master=self.window)
        self.window.title(self.get_title(self.untitled))
        self.window.config(menu=self.menuBar)
        self.textBox = tk.Text(master=self.window)
        self.textBox.bind("<<Modified>>", self.on_content_changed)
        self.textBox.grid()
        self.menu_file = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_file.add_command(label="New",command=lambda:self.new_file())
        self.menu_file.add_command(label="New Window",command=lambda:self.new_window())
        self.menu_file.add_command(label="Open",command=lambda:self.open_file())
        self.menu_file.add_command(label="Save", command=lambda:self.save())
        self.menu_file.add_command(label="Save As", command=lambda:self.save(True))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit",command=lambda:self.exit())

        self.menu_edit = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_edit.add_command(label="Undo")
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Cut")
        self.menu_edit.add_command(label="Copy")
        self.menu_edit.add_command(label="Paste")
        self.menu_edit.add_command(label="Delete")
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Find")
        self.menu_edit.add_command(label="Find Next")
        self.menu_edit.add_command(label="Find Previous")
        self.menu_edit.add_command(label="Replace")
        self.menu_edit.add_command(label="Go To")
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Select All")

        self.menu_format = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_format.add_command(label="Word Wrap")
        self.menu_format.add_command(label="Font")

        self.menu_view = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_zoom = tk.Menu(master=self.menu_view,tearoff=False)
        self.menu_zoom.add_command(label="Zoom In")
        self.menu_zoom.add_command(label="Zoom Out")
        self.menu_zoom.add_command(label="Restore Default Zoom")
        self.menu_view.add_cascade(menu=self.menu_zoom,label="Zoom")
        self.menu_view.add_command(label="Status Bar")

        self.menuBar.add_cascade(menu=self.menu_file,label="File")
        self.menuBar.add_cascade(menu=self.menu_edit,label="Edit")
        self.menuBar.add_cascade(menu=self.menu_format,label="Format")
        self.menuBar.add_cascade(menu=self.menu_view,label="View")

        self.window.mainloop()
    
    def get_title(self,name):
        return name + " - Notepad"

    def ask_save(self):
        flag = self.textBox.edit_modified()
        if flag:
            answer = askyesno("Notepad",
                               f"Do you want to save changes to {self.save_path if len(self.save_path) != 0 else self.untitled}")
            if answer:
                self.save()

    def new_file(self):
        self.ask_save()
        self.save_path = ""
        self.window.title(self.get_title(self.untitled))
        self.textBox.delete("1.0",tk.END)
        self.textBox.edit_modified(False)
    
    def new_window(self):
        TextEditor(tk.Tk())

    def open_file(self):
        self.ask_save()
        self.save_path = fd.askopenfilename(
            filetypes=[("txt","*.txt"),("all","*.*")])
        if self.save_path != "":
            f = open(self.save_path,'r')
            line = f.readline()
            text = ""
            while line:
                text = text + line
                line = f.readline()
            self.textBox.delete("1.0",tk.END)
            self.textBox.insert("1.0",text)
            self.textBox.edit_modified(False)
            self.window.title(self.get_title(os.path.basename(self.save_path)))
            
    def save(self, saveAs=False):
        if self.save_path == "" or saveAs:
            self.save_path = fd.asksaveasfilename(
                filetypes=[("txt","*.txt"),("all","*.*")])
        if self.save_path != "":
            text = self.textBox.get("1.0", tk.END)
            f = open(self.save_path,'w')
            f.write(text)
            self.window.title(self.get_title(os.path.basename(self.save_path)))
            self.textBox.edit_modified(False)

    def exit(self):
        self.ask_save()
        self.window.destroy()
    
    def on_content_changed(self,event):
        flag = self.textBox.edit_modified()
        if flag:
            old_title = self.window.title()
            self.window.title("*" + old_title)
        
        
t1 = TextEditor(tk.Tk())
