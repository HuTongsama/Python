import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox

import os
from enum import Enum
class FindWindow:
    class Direction(Enum):
        Down = 0,
        Up = 1
    def __init__(self,textEditor):

        self.find_str = tk.StringVar()
        self.down = tk.BooleanVar(value=True)
        self.up = tk.BooleanVar(value=False)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.loop = tk.BooleanVar(value=False)

        self.editor = textEditor
        self.window = tk.Toplevel(master=textEditor.window)
        self.window.protocol("WM_DELETE_WINDOW", lambda:self.window.withdraw())
        self.window.geometry(f"400x150+200+200")
        self.window.withdraw()
        self.window.title("Find")
        self.lbl_find_what = tk.Label(master=self.window,text="Find what:")
        self.lbl_find_what.grid(row=0,column=0)
        self.ent_input = tk.Entry(master=self.window,textvariable=self.find_str)
        self.ent_input.grid(row=0,column=1,padx=5,pady=10)
        self.btn_find_next = tk.Button(master=self.window,text="Find Next",width=10,relief="groove",command=lambda:self.find_next())
        self.btn_find_next.grid(row=0,column=2,padx=10)
        self.btn_cancel = tk.Button(master=self.window,text="Cancel",width=10,relief="groove",command=lambda:self.window.withdraw())
        self.btn_cancel.grid(row=1,column=2,padx=10)
        self.ckbtn_case_sensitive = tk.Checkbutton(master=self.window,text="Match case",variable=self.case_sensitive)
        self.ckbtn_case_sensitive.grid(row=1,column=0,sticky="w")
        self.ckbtn_loop = tk.Checkbutton(master=self.window,text="Loop",variable=self.loop)
        self.ckbtn_loop.grid(row=2,column=0,sticky="w")
        self.fra_direction = tk.Frame(master=self.window)
        self.fra_direction.grid(row=1,rowspan=2,column=1,pady=10)
        self.lbl_direction = tk.Label(master=self.fra_direction,relief="groove")
        self.lbl_direction.pack()
        self.lbl_dir_text = tk.Label(master=self.lbl_direction,text="Direction")
        self.lbl_dir_text.grid(row=0,column=0)
        self.ckbtn_dir_down = tk.Checkbutton(master=self.lbl_direction,text="Down",variable=self.down,command=lambda:self.down_checked())
        self.ckbtn_dir_down.grid(row=1,column=1,sticky="w")
        self.ckbtn_dir_up = tk.Checkbutton(master=self.lbl_direction,text="Up",variable=self.up,command=lambda:self.up_checked())
        self.ckbtn_dir_up.grid(row=1,column=0,sticky="w")

        
        
    
    def open(self,direction = None):
        if direction:
            if direction == self.Direction.Down:
                if self.up.get():
                    self.up.set(False)
                self.down.set(True)
            else:
                if self.down.get():
                    self.down.set(False)
                self.up.set(True)
        self.window.deiconify()

    def down_checked(self):
        self.down.set(True)
        if self.up.get():
            self.up.set(False)
        
    def up_checked(self):
        self.up.set(True)
        if self.down.get():
            self.down.set(False)
           
    def get_config(self):
        direction = self.Direction.Down if self.down.get() else self.Direction.Up
        return {
            "text":self.find_str.get(),
            "direction":direction,
            "case_sensitive":self.case_sensitive.get(),
            "loop":self.loop.get()
            }
    
    def find_next(self):
        config = self.get_config()
        self.editor.find_content(
            config["text"],config["direction"],
            config["case_sensitive"],config["loop"])

        
class TextEditor:
    untitled = "Untitled"
    def __init__(self,master):
        self.save_path = ""
        self.sel_start = tk.END
        self.sel_end = tk.END
        self.window = master
        self.menuBar = tk.Menu(master=self.window)
        self.window.title(self.get_title(self.untitled))
        self.window.config(menu=self.menuBar)
        self.textBox = tk.Text(master=self.window,undo=True)
        self.textBox.bind("<<Modified>>", self.on_content_changed)
        self.textBox.bind("<<Selection>>", self.on_selection_changed)
        self.textBox.bind("<Button-1>",self.remove_highlight)
        ys = ttk.Scrollbar(self.window, orient = "vertical",
                            command = self.textBox.yview)
        self.textBox["yscrollcommand"] = ys.set
        self.textBox.grid(row=0, column=0)
        ys.grid(row=0, column=1,sticky="ns")
        self.menu_file = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_file.add_command(label="New",command=lambda:self.new_file())
        self.menu_file.add_command(label="New Window",command=lambda:self.new_window())
        self.menu_file.add_command(label="Open",command=lambda:self.open_file())
        self.menu_file.add_command(label="Save", command=lambda:self.save())
        self.menu_file.add_command(label="Save As", command=lambda:self.save(True))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit",command=lambda:self.exit())

        self.menu_edit = tk.Menu(master=self.menuBar,tearoff=False)
        self.menu_edit.add_command(label="Undo",command=lambda:self.undo())
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Cut",command=lambda:self.cut_text())
        self.menu_edit.add_command(label="Copy",command=lambda:self.copy_text())
        self.menu_edit.add_command(label="Paste",command=lambda:self.paste_text())
        self.menu_edit.add_command(label="Delete",command=lambda:self.delete_text())
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Find",command=lambda:self.find())
        self.menu_edit.add_command(label="Find Next",command=lambda:self.find_next())
        self.menu_edit.add_command(label="Find Previous",command=lambda:self.find_previous())
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

        self.find_window = FindWindow(self)
        self.window.mainloop()
    
    def get_title(self,name):
        return name + " - Notepad"

    def ask_save(self):
        flag = self.textBox.edit_modified()
        if flag:
            answer = messagebox.askyesno("Notepad",
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
            self.textBox.mark_set(tk.INSERT,"1.0")  
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
    
    def undo(self):
        try:
            self.textBox.edit_undo()
        except tk.TclError:
            pass     

    def cut_text(self):
        self.copy_text()
        self.delete_text()
            
    def copy_text(self):
        if self.sel_start != tk.END:
            text = self.textBox.get(self.sel_start,self.sel_end)
            self.window.clipboard_clear()
            self.window.clipboard_append(text)

    def paste_text(self):
        cursor_pos = self.textBox.index("insert")
        text = self.window.clipboard_get()
        self.textBox.insert(cursor_pos,text)
    
    def delete_text(self):
        self.textBox.delete(self.sel_start,self.sel_end)

    def remove_highlight(self,event = None):
         self.textBox.tag_remove("highlight","1.0",tk.END)
       
    def find_content(self,content,direction,
                     case_sensitive,loop):
        cursor_pos = self.textBox.index(tk.INSERT)
        found_pos = None
        end_index = None
        mark_pos = None
        if direction == FindWindow.Direction.Down:
            if not loop: 
                end_index = tk.END
            found_pos = self.textBox.search(index=cursor_pos,pattern=content,
                                forwards=True,stopindex=end_index,nocase=not case_sensitive)
            mark_pos = found_pos + f"+{len(content)}c"
        else:
            if not loop:
                end_index = "1.0"
            found_pos = self.textBox.search(index=cursor_pos,pattern=content,
                                backwards=True,stopindex=end_index,nocase=not case_sensitive)
            mark_pos = found_pos

        if found_pos:
            self.remove_highlight() 
            self.textBox.tag_add("highlight", found_pos, f"{found_pos}+{len(content)}c")
            self.textBox.tag_config("highlight",foreground="white",background="SystemHighlight")
            self.textBox.mark_set(tk.INSERT, mark_pos) # Move the cursor to the end of the found text
            self.textBox.see(found_pos)  # Scroll to show the found text
        else:
            messagebox.showinfo("Notepad", f"Cannot find \"{content}\"")
        
    def find(self):     
        self.find_window.open()

    def find_next(self):
        self.find_window.open(FindWindow.Direction.Down)

    def find_previous(self):
        self.find_window.open(FindWindow.Direction.Up)

    def replace(self):
        pass

    def goto(self):
        pass

    def select_all(self):
        pass

    def on_content_changed(self,event):
        flag = self.textBox.edit_modified()
        if flag:
            old_title = self.window.title()
            if old_title[0] != '*':
                self.window.title("*" + old_title)
        
    def on_selection_changed(self,event):
        sel_range = self.textBox.tag_ranges("sel")
        if len(sel_range) > 0:
            self.sel_start , self.sel_end = sel_range
        else:
            self.sel_start = tk.END
            self.sel_end = tk.END

def main():
    t1 = TextEditor(tk.Tk())
    
if __name__ == "__main__":
    main()