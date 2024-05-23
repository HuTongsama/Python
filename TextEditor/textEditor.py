import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox
from tkinter import font

import os
from enum import Enum

class FindWindowBase:
    class Direction(Enum):
        Down = 0,
        Up = 1

    def __init__(self,textEditor):

        self.find_str = tk.StringVar()
        self.find_str.trace_add("write",self.enable_find)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.loop = tk.BooleanVar(value=False)

        self.editor = textEditor
        self.window = tk.Toplevel(master=textEditor.window)
        self.window.protocol("WM_DELETE_WINDOW", lambda:self.window.withdraw())
        self.window.geometry(f"350x150+200+200")
        self.window.withdraw()
        self.window.title("Find")
        self.lbl_find_what = tk.Label(master=self.window,text="Find what:")
        self.lbl_find_what.grid(row=0,column=0,sticky="w",padx=5)
        self.ent_input = tk.Entry(master=self.window,textvariable=self.find_str)
        self.ent_input.grid(row=0,column=1,padx=5,pady=10)
        self.btn_find_next = tk.Button(master=self.window,text="Find Next",width=10,relief="groove",command=lambda:self.find_next())
        self.btn_find_next.grid(row=0,column=2,padx=10)
        self.btn_cancel = tk.Button(master=self.window,text="Cancel",width=10,relief="groove",command=lambda:self.window.withdraw())
        self.btn_cancel.grid(row=1,column=2,padx=10)
        self.btn_find_next.config(state="disabled")
        self.ckbtn_case_sensitive = tk.Checkbutton(master=self.window,text="Match case",variable=self.case_sensitive)
        self.ckbtn_case_sensitive.grid(row=1,column=0,sticky="w")
        self.ckbtn_loop = tk.Checkbutton(master=self.window,text="Loop",variable=self.loop)
        self.ckbtn_loop.grid(row=2,column=0,sticky="w")

    def enable_find(self,*args):
        if self.find_str.get():
            self.btn_find_next.config(state="normal")
        else:
            self.btn_find_next.config(state="disabled")

    def open(self):
        self.window.deiconify()
         
    def get_config(self):
        return {
            "text":self.find_str.get(),
            "direction":self.Direction.Down,
            "case_sensitive":self.case_sensitive.get(),
            "loop":self.loop.get()
            }
    
    def find_next(self):
        config = self.get_config()
        result = self.editor.find_content(
            config["text"],config["direction"],
            config["case_sensitive"],config["loop"])
        if not result:
            messagebox.showinfo("Notepad", f"Cannot find \"{config["text"]}\"")
            self.window.focus_set()
        return result

class FindWindow(FindWindowBase):
    class Direction(Enum):
        Down = 0,
        Up = 1
    def __init__(self,textEditor):
        super().__init__(textEditor)
        self.down = tk.BooleanVar(value=True)
        self.up = tk.BooleanVar(value=False)
       
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
        super().open()

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
        config = super().get_config()
        config["direction"] = direction
        return config
       
class ReplaceWindow(FindWindowBase):
    def __init__(self, textEditor):
        super().__init__(textEditor)

        self.replace_str = tk.StringVar()
        self.replace_str.trace_add("write",self.enable_replace)
        self.found_pos = None

        self.window.title("Replace")
        self.btn_replace = tk.Button(master=self.window,text="Replace",width=10,relief="groove",command=lambda:self.replace())
        self.btn_replace.config(state="disabled")
        self.btn_replace_all = tk.Button(master=self.window,text="Replace All",width=10,relief="groove",command=lambda:self.replace_all())
        self.btn_replace_all.config(state="disabled")
        self.lbl_replace_with = tk.Label(master=self.window,text="Replace with:")
        self.ent_replace = tk.Entry(master=self.window,textvariable=self.replace_str)
       
        self.btn_find_next.grid(row=0,column=2,padx=10)
        self.lbl_replace_with.grid(row=1,column=0,sticky="w",padx=5)
        self.ent_replace.grid(row=1,column=1,padx=5)     
        self.btn_replace.grid(row=1,column=2,padx=10)
        self.btn_replace_all.grid(row=2,column=2,padx=10)
        self.ckbtn_case_sensitive.grid(row=2,column=0,sticky="w")
        self.btn_cancel.grid(row=3,column=2,padx=10)   
        self.ckbtn_loop.grid(row=3,column=0,sticky="w")
        
        
    def enable_replace(self,*args):
        if self.replace_str.get() and self.find_str.get():
            self.btn_replace.config(state="normal")
            self.btn_replace_all.config(state="normal")
        else:
            self.btn_replace.config(state="disabled")
            self.btn_replace_all.config(state="disabled")

    def replace(self):
        if self.found_pos:
            len_found = len(self.find_str.get())
            end_pos = self.found_pos + f"+{len_found}c"
            self.editor.textBox.replace(self.found_pos,end_pos,self.replace_str.get())
        
        self.found_pos = self.find_next()

    def replace_all(self):
        textBox = self.editor.textBox
        textBox.mark_set(tk.INSERT, "1.0")
        content = self.find_str.get()
        all_results = []
        start = "1.0"
        while True:
            found_pos = textBox.search(index=start,stopindex=tk.END,
                                       pattern=content,
                                       forwards=True,
                                       nocase=not self.case_sensitive.get())
            start = found_pos + f"+{len(content)}c"
            if not found_pos:
                break
            all_results.append(found_pos)
        if len(all_results) > 0:
            len_found = len(content)
            for result in all_results:
               end_pos = result + f"+{len_found}c"
               textBox.replace(result,end_pos,self.replace_str.get())       
        else:
            messagebox.showinfo("Notepad", f"Cannot find \"{content}\"")
            self.window.focus_set()

class GotoWindow: 
    def __init__(self,textEditor):
        self.editor = textEditor
        self.window = tk.Toplevel(master=textEditor.window)
        self.window.bind("<Button>",self.hide_warning)
    
        self.window.protocol("WM_DELETE_WINDOW", lambda:self.close())
        self.window.geometry(f"290x130+200+200")
        self.window.withdraw()
        self.window.title("Go To Line")
        
        self.lbl_input = tk.Label(master=self.window,text="Line number:")
        self.input = tk.StringVar()
        vcmd = (self.window.register(self.input_check), '%P')
        self.unit_count = 38
        self.ent_input = tk.Entry(master=self.window,width=self.unit_count,textvariable=self.input,
                                  validate="key",validatecommand=vcmd)
        self.ent_input.bind("<KeyPress>",self.hide_warning)
        self.fra_button = tk.Frame(master=self.window)
        self.btn_goto = tk.Button(master=self.fra_button,width=12,text="go to",command=lambda:self.goto())
        self.btn_cancel = tk.Button(master=self.fra_button,width=12,text="cancel",command=lambda:self.close())
        self.win_warning = None

        self.lbl_input.grid(row=0,column=0,padx=10,pady=5,sticky="w")
        self.ent_input.grid(row=1,column=0,padx=10,pady=5,sticky="w")      
        self.fra_button.grid(row=2,column=0,columnspan=2,padx=5,pady=5,sticky="e")    
        self.btn_goto.grid(row=0,column=0,padx=5,pady=5,sticky="w")
        self.btn_cancel.grid(row=0,column=1,padx=5,pady=5,sticky="w")
        
                      
    def show_warning(self):
        self.win_warning = tk.Toplevel(self.window)    
        entry_font = font.Font(font=self.ent_input['font'])
        text_height = entry_font.metrics('linespace')
        x = self.ent_input.winfo_rootx()
        y = self.ent_input.winfo_rooty() + text_height
        self.win_warning.geometry(
         f"+{x}+{y}")
        self.win_warning.wm_overrideredirect(True)
        canvas = tk.Canvas(master=self.win_warning,width=220,height=80)
        canvas.bind("<Button>",self.hide_warning)
        
        padding = 5
        width = self.ent_input.winfo_width()*0.8
        self.ent_input.update_idletasks()
        pos = self.ent_input.index(tk.INSERT)
        start_x = pos / self.unit_count * self.ent_input.winfo_width()
        if start_x == 0:
            start_x = padding
        x1,y1 = start_x, padding
        x2,y2 = x1 + 0.5 * text_height , y1 + text_height
        x3,y3 = width, y2
        x4,y4 = x3, y3 + text_height * 3
        x5,y5 = x1,y4
        x6,y6 = x1,y1
        canvas.configure(bg="white", highlightthickness=0)       
        canvas.create_polygon(
            x1,y1,
            x2,y2,
            x3,y3,
            x4,y4,
            x5,y5,
            x6,y6,
            outline="black", fill="white"
        )
        
        canvas.create_text(
            x1,y2,
            anchor="nw",
            text=" Unacceptable character.\n You can only type a number here.",
            width=width,
            fill="black"
        )
        canvas.pack()

    def hide_warning(self,event):
        if self.win_warning:
            self.win_warning.destroy()
        self.win_warning = None

    def input_check(self, content):
        if content.isdigit() or content == '':
            return True
        self.show_warning()
        return False
    
    def open(self):        
        self.window.deiconify()
        self.ent_input.focus_set()
    
    def close(self):
        self.window.withdraw()
       
    def goto(self):
        line = self.ent_input.get()
        end_position = self.editor.textBox.index('end-1c')
        max_count = int(end_position.split('.')[0])
        cur_count = int(line)
        if cur_count > 0 and cur_count <= max_count:
            line = line + ".0"
            self.editor.textBox.mark_set(tk.INSERT, line)
        else:
            messagebox.showinfo("Notepad - Goto Line",
                                            "The line number is beyond the total number of lines")
        self.close()
        
           

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
        self.menu_edit.add_command(label="Replace",command=lambda:self.replace())
        self.menu_edit.add_command(label="Go To",command=lambda:self.goto())
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Select All",command=lambda:self.select_all())

        # self.menu_format = tk.Menu(master=self.menuBar,tearoff=False)
        # self.menu_format.add_command(label="Word Wrap")
        # self.menu_format.add_command(label="Font")

        # self.menu_view = tk.Menu(master=self.menuBar,tearoff=False)
        # self.menu_zoom = tk.Menu(master=self.menu_view,tearoff=False)
        # self.menu_zoom.add_command(label="Zoom In")
        # self.menu_zoom.add_command(label="Zoom Out")
        # self.menu_zoom.add_command(label="Restore Default Zoom")
        # self.menu_view.add_cascade(menu=self.menu_zoom,label="Zoom")
        # self.menu_view.add_command(label="Status Bar")

        self.menuBar.add_cascade(menu=self.menu_file,label="File")
        self.menuBar.add_cascade(menu=self.menu_edit,label="Edit")
        #self.menuBar.add_cascade(menu=self.menu_format,label="Format")
        #self.menuBar.add_cascade(menu=self.menu_view,label="View")

        self.find_window = FindWindow(self)
        self.replace_window = ReplaceWindow(self)
        self.goto_window = GotoWindow(self)
        self.textBox.focus_set()
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
        if direction == FindWindowBase.Direction.Down:
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
        
        return found_pos
        
    def find(self):     
        self.find_window.open()

    def find_next(self):
        self.find_window.open(FindWindow.Direction.Down)

    def find_previous(self):
        self.find_window.open(FindWindow.Direction.Up)

    def replace(self):
        self.replace_window.open()

    def goto(self):
        self.goto_window.open()

    def select_all(self):
        self.textBox.tag_add("sel", "1.0", tk.END)

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
    #t = tk.Text()
    #t.replace()
    
if __name__ == "__main__":
    main()